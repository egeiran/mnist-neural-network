"""
Fasiten til tools/check_web_model.ts: kjører de ekte bildene gjennom NumPy og
skriver ut svarene, så JS-siden kan sammenlignes mot dem.

    python tools/check_web_model.py > /tmp/expected.json
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.export_web import sigmoid, forward  # noqa: E402

run = np.load(ROOT / "artifacts" / "run.npz")
manifest = json.loads((ROOT / "web" / "src" / "data" / "run.json").read_text())["model"]

images = np.concatenate(
    [run["batch_images"], run["showcase_images"], run["worst_images"]]
).astype(np.float64)

out = forward(images, run["W1_final"], run["b1_final"], run["W2_final"], run["b2_final"])

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
