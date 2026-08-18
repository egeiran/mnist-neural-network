"""Genererer all voiceover på forhånd, med retry, og legger den i manim-voiceover sin cache.

ElevenLabs svarer av og til "heavy traffic", og manim avbryter hele rendringen hvis ett
kall feiler midt i en scene. Derfor gjør vi lyden ferdig først: når cachen er full,
leser rendringen bare fra disk og kan ikke ryke på et API-kall.

    VOICEOVER=1 .venv/bin/python prepare_vo.py

Kjør så mange ganger du vil — allerede genererte replikker koster ingenting.
"""

from __future__ import annotations

import ast
import os
import pathlib
import sys
import time

SCENES = sorted(pathlib.Path("scenes").glob("s[0-9][0-9]_*.py"))
MAX_TRIES = 6
BACKOFF = [5, 15, 30, 60, 120]


def literal(node: ast.AST) -> str:
    """Teksten i et narrate()-argument (sammensatte strenger og f-strenger)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        out = ""
        for v in node.values:
            if isinstance(v, ast.Constant):
                out += str(v.value)
            elif isinstance(v, ast.FormattedValue):
                out += format_value(v)
        return out
    return ""


def format_value(node: ast.FormattedValue) -> str:
    """Scenene setter bare inn ett tall: antall parametre."""
    import numpy as np

    data = np.load("artifacts/run.npz")
    return f"{int(data['n_weights']):,}"


def narration_lines() -> list[tuple[str, str]]:
    lines = []
    for path in SCENES:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "narrate"
                and node.args
            ):
                text = " ".join(literal(node.args[0]).split())
                if text:
                    lines.append((path.stem, text))
    return lines


def main() -> int:
    if os.environ.get("VOICEOVER", "0").lower() in ("0", "", "false", "no"):
        print("VOICEOVER=1 må være satt")
        return 1

    sys.path.insert(0, ".")
    from scenes.common import speech_service

    svc = speech_service()
    lines = narration_lines()
    total_chars = sum(len(t) for _, t in lines)
    print(f"{len(lines)} replikker, {total_chars:,} tegn")
    print(f"stemme {svc.voice.voice_id}  ·  modell {svc.model}")
    print()

    generated = 0
    for i, (scene, text) in enumerate(lines, 1):
        head = text[:58] + ("…" if len(text) > 58 else "")
        for attempt in range(MAX_TRIES):
            try:
                before = svc.get_cached_result(
                    {
                        "input_text": text,
                        "service": "elevenlabs",
                        "config": {
                            "model": svc.model,
                            "voice": svc.voice.model_dump(exclude_none=True),
                        },
                    },
                    pathlib.Path(svc.cache_dir),
                )
                svc._wrap_generate_from_text(text)
                mark = "cache" if before is not None else "ny   "
                generated += before is None
                print(f"  [{i:>2}/{len(lines)}] {mark} {scene[:3]}  {head}")
                break
            except Exception as e:
                if attempt == MAX_TRIES - 1:
                    print(f"  [{i:>2}/{len(lines)}] FEILET etter {MAX_TRIES} forsøk: {e}")
                    return 1
                wait = BACKOFF[min(attempt, len(BACKOFF) - 1)]
                print(f"  [{i:>2}/{len(lines)}] forsøk {attempt + 1} feilet ({e}) — venter {wait}s")
                time.sleep(wait)

    print()
    print(f"ferdig — {generated} nye replikker generert, {len(lines) - generated} fra cache")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
