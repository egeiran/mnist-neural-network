"""Kjører en kommando på nytt hver gang en .py-fil under scenes/ eller nn/ endres.

    python tools/watch.py "PYTHONPATH=. .venv/bin/manim -spql scenes/s04_sigmoid.py S04Sigmoid"

Brukes normalt via Makefile: `make watch S=s04_sigmoid C=S04Sigmoid`.
Lagrer du mens en render fortsatt går, drepes den og en ny startes.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCH_DIRS = [ROOT / "scenes", ROOT / "nn"]
POLL = 0.3


def snapshot() -> dict[Path, float]:
    out = {}
    for d in WATCH_DIRS:
        for p in d.rglob("*.py"):
            try:
                out[p] = p.stat().st_mtime
            except OSError:
                pass
    return out


def start(cmd: str) -> subprocess.Popen:
    print(f"\n── {time.strftime('%H:%M:%S')}  rendrer …", flush=True)
    # Egen prosessgruppe, slik at vi får drept både skallet og manim under det.
    return subprocess.Popen(cmd, shell=True, cwd=ROOT, start_new_session=True)


def stop(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass


def main() -> None:
    # SIGTERM skal rydde like pent som ctrl-c, ellers blir manim gående videre.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    cmd = " ".join(sys.argv[1:]).strip()
    if not cmd:
        sys.exit("bruk: python tools/watch.py \"<kommando>\"")

    print(f"ser på: {', '.join(str(d.relative_to(ROOT)) for d in WATCH_DIRS)}  (ctrl-c avslutter)")
    proc = start(cmd)
    state = snapshot()
    try:
        while True:
            time.sleep(POLL)
            new = snapshot()
            if new != state:
                state = new
                stop(proc)
                proc = start(cmd)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        stop(proc)
        print("\nferdig")


if __name__ == "__main__":
    main()
