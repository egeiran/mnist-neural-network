"""
Fasiten til tools/check_web_model.ts: kjører de ekte bildene gjennom NumPy og
skriver ut svarene, så JS-siden kan sammenlignes mot dem.

    python tools/check_web_model.py > /tmp/expected.json

Sjekker samtidig at bildene i bom-seksjonen hører sammen med bildetekstene
sine. Siden parer worst[i] med worstImages[i], og hvis de to listene kommer i
ulik rekkefølge, feiler ingenting — bildet ser bare ikke ut som teksten sier.
Derfor kjøres hvert bilde gjennom nettverket her og sammenlignes med det
metadataen påstår.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.export_web import forward  # noqa: E402

run = np.load(ROOT / "artifacts" / "run.npz")
manifest = json.loads((ROOT / "web" / "src" / "data" / "run.json").read_text())["model"]

images = np.concatenate(
    [run["batch_images"], run["showcase_images"], run["worst_images"]]
).astype(np.float64)

out = forward(images, run["W1_final"], run["b1_final"], run["W2_final"], run["b2_final"])

# ── bilde og bildetekst må høre sammen ──────────────────────────────────────
web = json.loads((ROOT / "web" / "src" / "data" / "run.json").read_text())
mismatched = []
for i, meta in enumerate(web["worst"]):
    img = (
        np.frombuffer(base64.b64decode(web["worstImages"][i]), dtype=np.uint8).astype(
            np.float64
        )
        / 255.0
    )
    # NB: eget variabelnavn — `out` over holder fasiten for alle 57 bildene.
    prediction = forward(
        img[None, :],
        run["W1_final"],
        run["b1_final"],
        run["W2_final"],
        run["b2_final"],
    )[0]
    if (
        int(prediction.argmax()) != meta["pred"]
        or abs(float(prediction.max()) - meta["confidence"]) > 2e-3
    ):
        mismatched.append(i)

if mismatched:
    raise SystemExit(
        f"worst og worstImages er ute av synk på indeks {mismatched} — "
        "sorter dem med samme rekkefølge i export_web.py"
    )
print(f"bom-seksjonen: {len(web['worst'])} bilder parer med riktig bildetekst", file=sys.stderr)

json.dump(
    {
        "manifest": manifest,
        "images": [
            base64.b64encode(
                np.clip(img * 255.0, 0, 255).astype(np.uint8).tobytes()
            ).decode("ascii")
            for img in images
        ],
        "out": out.tolist(),
    },
    sys.stdout,
)
