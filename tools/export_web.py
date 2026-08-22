"""
Pakker ut alt nettsiden trenger fra artifacts/run.npz.

Poenget er at ingen tall på mnist.eivindgeiran.no skrives for hånd. Retrener du
og kjører `make artifacts` på nytt, kjører du dette etterpå, og siden forteller
om den nye kjøringen i stedet for den gamle.

    python tools/export_web.py

Skriver til web/public/model/ (vekter, binært) og web/src/data/ (tall, JSON).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
NPZ = ROOT / "artifacts" / "run.npz"
MODEL_DIR = ROOT / "web" / "public" / "model"
DATA_DIR = ROOT / "web" / "src" / "data"


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def forward(X: np.ndarray, W1, b1, W2, b2) -> np.ndarray:
    return sigmoid(sigmoid(X @ W1 + b1) @ W2 + b2)


def quantize_check(run) -> tuple[np.ndarray, float, float]:
    """
    Vektene sendes til nettleseren som float16 for å halvere nedlastingen.
    Denne funksjonen sjekker at det faktisk ikke koster noe: den kjører alle
    ekte MNIST-bildene som ligger i npz-en gjennom både float64-nettverket og
    float16-utgaven, og returnerer største avvik.

    Grunnen til at det er trygt: største vekt er ~2.8, og float16 har ~3
    signifikante siffer, så absoluttfeilen per vekt er under 0.001. Summert over
    784 innganger med typisk aktivering rundt 0.13 blir det noen tusendeler på
    z — flere størrelsesordener fra å endre hvilken klasse som vinner.
    """
    W1, b1 = run["W1_final"], run["b1_final"]
    W2, b2 = run["W2_final"], run["b2_final"]

    # Alle ekte bildene vi har for hånden: treningsbatchen, showcase og bommene.
    X = np.concatenate(
        [run["batch_images"], run["showcase_images"], run["worst_images"]]
    ).astype(np.float64)

    exact = forward(X, W1, b1, W2, b2)
    half = forward(
        X,
        W1.astype(np.float16).astype(np.float64),
        b1.astype(np.float16).astype(np.float64),
        W2.astype(np.float16).astype(np.float64),
        b2.astype(np.float16).astype(np.float64),
    )

    max_prob_diff = float(np.abs(exact - half).max())
    disagreements = int((exact.argmax(1) != half.argmax(1)).sum())
    return X, max_prob_diff, disagreements


def write_weights(run) -> dict:
    """
    Skriver W1, b1, W2, b2 etter hverandre i én float16-fil, little-endian.
    Nettleseren leser den med én fetch og deler den opp igjen på lengdene som
    ligger i manifestet.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    parts = [
        ("W1", run["W1_final"], [784, 128]),
        ("b1", run["b1_final"], [128]),
        ("W2", run["W2_final"], [128, 10]),
        ("b2", run["b2_final"], [10]),
    ]

    blob = bytearray()
    layout = []
    for name, arr, shape in parts:
        # "<f2" = little-endian float16, som er det DataView-en i nettleseren leser.
        flat = np.ascontiguousarray(arr, dtype="<f2").ravel()
        layout.append({"name": name, "shape": shape, "offset": len(blob) // 2})
        blob += flat.tobytes()

    (MODEL_DIR / "mnist-784-128-10.f16").write_bytes(bytes(blob))
    return {
        "file": "/model/mnist-784-128-10.f16",
        "dtype": "float16",
        "bytes": len(blob),
        "layout": layout,
    }


def digits_to_base64(images: np.ndarray) -> list[str]:
    """
    28x28 gråtoner som 784 bytes base64 hver. Enklere enn PNG, og nettleseren
    tegner dem uansett rett inn i en ImageData.
    """
    import base64

    out = []
    for img in images:
        b = np.clip(np.asarray(img) * 255.0, 0, 255).astype(np.uint8)
        out.append(base64.b64encode(b.tobytes()).decode("ascii"))
    return out


def main() -> None:
    if not NPZ.exists():
        raise SystemExit(
            f"fant ikke {NPZ.relative_to(ROOT)} — kjør `make artifacts` først"
        )

    run = np.load(NPZ)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    _, max_prob_diff, disagreements = quantize_check(run)
    if disagreements:
        raise SystemExit(
            f"float16 endret prediksjonen på {disagreements} bilder — "
            "bytt til float32 i write_weights() før du publiserer"
        )
    print(f"float16-sjekk: største avvik i sannsynlighet {max_prob_diff:.2e}, "
          f"0 endrede prediksjoner")

    manifest = write_weights(run)
    print(f"vekter: {manifest['bytes'] / 1024:.0f} KB → {manifest['file']}")

    epoch_acc = run["epoch_acc"].astype(float)
    epoch_loss = run["epoch_loss"].astype(float)

    # Treningskurven har 18 750 punkter. Nettsiden trenger ikke alle — vi tar
    # median i vinduer, som holder på formen uten å sende 150 KB JSON.
    batch = run["batch_losses"].astype(float)
    window = len(batch) // 240
    trimmed = batch[: window * 240].reshape(240, window)
    loss_curve = np.median(trimmed, axis=1)

    # W1 sier hva hver skjult nøytron ser etter. Vi tar de som har rukket å
    # spesialisere seg mest — størst spredning i vektene — for de er de eneste
    # som ser ut som noe i det hele tatt.
    W1 = run["W1_final"]
    interest = W1.std(axis=0)
    picked = np.argsort(interest)[::-1][:12]
    filters = []
    for j in picked:
        w = W1[:, j]
        lim = float(np.abs(w).max())
        filters.append({"neuron": int(j), "limit": lim, "w": [round(float(v), 4) for v in w]})

    worst = []
    order = np.argsort(run["worst_conf"])[::-1]
    for i in order:
        worst.append(
            {
                "index": int(run["worst_idx"][i]),
                "true": int(run["worst_true"][i]),
                "pred": int(run["worst_pred"][i]),
                "confidence": round(float(run["worst_conf"][i]), 4),
            }
        )

    # confusion i run.npz teller BARE bommene (nn/artifacts.py løper over `wrong`),
    # så diagonalen er null ved konstruksjon. Vi regner ut de vanligste
    # forvekslingene her, så siden kan si noe konkret i stedet for å antyde at
    # dette er en vanlig konfusjonsmatrise.
    conf = run["confusion"].astype(int)
    pairs = [
        {"true": int(i), "pred": int(j), "count": int(conf[i, j])}
        for i in range(10)
        for j in range(10)
        if i != j and conf[i, j] > 0
    ]
    pairs.sort(key=lambda d: -d["count"])

    payload = {
        "model": manifest,
        "errorTotal": int(conf.sum()),
        "testSize": 10000,
        "topConfusions": pairs[:5],
        "architecture": [784, 128, 10],
        "parameters": int(run["n_weights"]),
        "epochs": len(epoch_acc),
        "batchSize": 32,
        "learningRate": 1.0,
        "stepsPerEpoch": int(run["steps_per_epoch"]),
        "firstLoss": round(float(run["first_loss"]), 4),
        "finalAccuracy": round(float(epoch_acc[-1]), 4),
        "firstEpochAccuracy": round(float(epoch_acc[0]), 4),
        "finalLoss": round(float(epoch_loss[-1]), 4),
        "epochAccuracy": [round(float(v), 4) for v in epoch_acc],
        "epochLoss": [round(float(v), 4) for v in epoch_loss],
        "lossCurve": [round(float(v), 4) for v in loss_curve],
        "confusion": run["confusion"].astype(int).tolist(),
        "gradcheck": str(run["gradcheck_text"]),
        "float16MaxProbDiff": float(f"{max_prob_diff:.3e}"),
        "worst": worst,
        "worstImages": digits_to_base64(run["worst_images"]),
        "sampleImages": digits_to_base64(run["batch_images"]),
        "sampleLabels": run["batch_labels"].astype(int).tolist(),
        "filters": filters,
    }

    out = DATA_DIR / "run.json"
    out.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    size = out.stat().st_size / 1024
    print(f"data:   {size:.0f} KB → web/src/data/run.json")
    print(
        f"kjøringen siden beskriver: {payload['finalAccuracy'] * 100:.2f} % "
        f"etter {payload['epochs']} epoker, {payload['parameters']:,} parametre"
    )


if __name__ == "__main__":
    main()
