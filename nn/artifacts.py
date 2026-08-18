"""Trener nettverket og lagrer alt scenene trenger til artifacts/run.npz.

Kjøres én gang: `make artifacts`. Alle tall som vises i videoen kommer herfra,
slik at det som står på skjermen faktisk er fra en ekte kjøring.
"""

import io
from contextlib import redirect_stdout

import numpy as np

from nn.data import load_data
from nn.network import backward, forward, init_params, loss, sigmoid, sigmoid_prime

SEED = 42
SIZES = [784, 128, 10]
LR = 1.0
BATCH_SIZE = 32
EPOCHS = 10
OUT = "artifacts/run.npz"


def grad_check_rows(seed=0, n=5):
    """Samme som network.grad_check, men returnerer tallene i stedet for å asserte."""
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    sizes = [5, 4, 3]
    Ws, bs = init_params(sizes)
    X = np.random.randn(2, 5)
    Y = np.eye(3)[[0, 2]]
    eps = 1e-5

    _, Zs, As = forward(X, Ws, bs)
    dWs, _ = backward(Y, Zs, As, Ws)

    rows = []
    seen = set()
    while len(rows) < n:
        l = int(rng.integers(len(Ws)))
        i = int(rng.integers(Ws[l].shape[0]))
        j = int(rng.integers(Ws[l].shape[1]))
        if (l, i, j) in seen:
            continue
        seen.add((l, i, j))

        gammel = Ws[l][i, j]
        Ws[l][i, j] = gammel + eps
        loss_plus = loss(forward(X, Ws, bs)[0], Y)
        Ws[l][i, j] = gammel - eps
        loss_minus = loss(forward(X, Ws, bs)[0], Y)
        Ws[l][i, j] = gammel

        numerisk = (loss_plus - loss_minus) / (2 * eps)
        analytisk = dWs[l][i, j]
        if abs(numerisk) < 1e-4:  # hopp over nesten-null-gradienter, gir stygg rel.feil
            continue
        rel = abs(numerisk - analytisk) / max(abs(numerisk), abs(analytisk))
        rows.append((l, i, j, numerisk, analytisk, rel))

    return np.array([[r[3], r[4], r[5]] for r in rows]), np.array(
        [[r[0], r[1], r[2]] for r in rows]
    )


def pick_showcase_digits(X_test, y_test, pred, A_out):
    """Plukker ut digits til scene 1: en tydelig 5 + fire rotete."""
    conf = A_out[np.arange(len(pred)), pred]

    # En ren, selvsikker femmer
    fives = np.where((y_test == 5) & (pred == 5))[0]
    clean_five = fives[np.argmax(conf[fives])]

    messy = []
    # En 4-er som ligner en 9-er (feilklassifisert, eller lav confidence)
    for true_d, wrong_d in [(4, 9), (7, 1), (3, 5), (9, 4)]:
        cand = np.where((y_test == true_d) & (pred == wrong_d))[0]
        if len(cand) == 0:  # falle tilbake til den mest usikre riktige
            cand = np.where(y_test == true_d)[0]
            cand = cand[np.argsort(conf[cand])][:1]
        else:
            cand = cand[np.argsort(-conf[cand])][:1]
        messy.append(int(cand[0]))

    idx = [int(clean_five)] + messy
    return np.array(idx)


def main():
    np.random.seed(SEED)
    Ws, bs = init_params(SIZES)

    W1_init = Ws[0].copy()

    X_train, X_test, y_train, y_test = load_data()
    y_test_oh = np.eye(10, dtype=np.float32)[y_test]

    # --- Utrent tilstand (scene 6) -------------------------------------
    demo_i = 0
    while np.argmax(y_train[demo_i]) != 5:
        demo_i += 1
    demo_x = X_train[demo_i : demo_i + 1]
    demo_y = y_train[demo_i : demo_i + 1]

    A_out_untrained, Zs_u, As_u = forward(demo_x, Ws, bs)
    untrained_out = A_out_untrained[0].copy()
    untrained_loss = float(loss(A_out_untrained, demo_y))
    untrained_hidden = As_u[1][0].copy()

    # Ekte gradienter på en utrent batch (scene 8)
    Xb, Yb = X_train[:BATCH_SIZE], y_train[:BATCH_SIZE]
    _, Zsb, Asb = forward(Xb, Ws, bs)
    dWs_b, dbs_b = backward(Yb, Zsb, Asb, Ws)
    dW1_init, dW2_init = dWs_b[0].copy(), dWs_b[1].copy()

    # --- Trening -------------------------------------------------------
    split = 60000
    batch_losses = []
    epoch_loss = []
    epoch_acc = []
    first_loss = None

    for e in range(EPOCHS):
        losses = []
        perm = np.random.permutation(len(X_train))
        X_shuffled, y_shuffled = X_train[perm], y_train[perm]

        for i in range(0, split, BATCH_SIZE):
            X = X_shuffled[i : i + BATCH_SIZE]
            y = y_shuffled[i : i + BATCH_SIZE]

            A_out, Zs, As = forward(X, Ws, bs)
            dWs, dbs = backward(y, Zs, As, Ws)

            l = loss(A_out, y)
            losses.append(l)

            for j in range(len(Ws)):
                Ws[j] -= LR * dWs[j]
                bs[j] -= LR * dbs[j]

        losses = np.array(losses)
        batch_losses.append(losses)
        if first_loss is None:
            first_loss = float(losses[0])
        epoch_loss.append(float(losses.mean()))

        A_out, _, _ = forward(X_test, Ws, bs)
        pred = np.argmax(A_out, axis=1)
        acc = float(np.mean(pred == y_test))
        epoch_acc.append(acc)
        print(f"epoch {e + 1:>2} — loss {epoch_loss[-1]:.4f}  acc {acc * 100:.2f}%")

    # --- Etter trening -------------------------------------------------
    A_out, Zs_t, As_t = forward(X_test, Ws, bs)
    pred = np.argmax(A_out, axis=1)
    conf = A_out[np.arange(len(pred)), pred]

    wrong = np.where(pred != y_test)[0]
    worst = wrong[np.argsort(-conf[wrong])][:20]

    show_idx = pick_showcase_digits(X_test, y_test, pred, A_out)

    # Trent forward-pass på demo-bildet
    A_out_trained, _, As_dt = forward(demo_x, Ws, bs)
    trained_out = A_out_trained[0].copy()
    trained_loss = float(loss(A_out_trained, demo_y))
    trained_hidden = As_dt[1][0].copy()

    # Konfusjonstabell
    confusion = np.zeros((10, 10), dtype=int)
    for i in wrong:
        confusion[y_test[i], pred[i]] += 1

    gc_values, gc_index = grad_check_rows(seed=0, n=5)

    # Selve grad_check-utskriften, for scene 9
    buf = io.StringIO()
    with redirect_stdout(buf):
        for (num, ana, rel), (l, i, j) in zip(gc_values, gc_index):
            print(f"W[{int(l)}][{int(i)},{int(j)}]  num={num:.8f}  ana={ana:.8f}  rel={rel:.2e}")

    np.savez_compressed(
        OUT,
        # scene 1 / 2
        showcase_idx=show_idx,
        showcase_images=X_test[show_idx],
        showcase_labels=y_test[show_idx],
        demo_image=demo_x[0],
        # scene 6
        untrained_out=untrained_out,
        untrained_loss=untrained_loss,
        untrained_hidden=untrained_hidden,
        trained_out=trained_out,
        trained_loss=trained_loss,
        trained_hidden=trained_hidden,
        target_onehot=demo_y[0],
        # scene 8
        dW1_init=dW1_init,
        dW2_init=dW2_init,
        db1_init=dbs_b[0],
        db2_init=dbs_b[1],
        # scene 9
        gradcheck_values=gc_values,
        gradcheck_index=gc_index,
        gradcheck_text=buf.getvalue(),
        # scene 10
        batch_losses=np.concatenate(batch_losses),
        epoch_loss=np.array(epoch_loss),
        epoch_acc=np.array(epoch_acc),
        first_loss=first_loss,
        # scene 11
        W1_init=W1_init,
        W1_final=Ws[0],
        W2_final=Ws[1],
        b1_final=bs[0],
        b2_final=bs[1],
        worst_idx=worst,
        worst_images=X_test[worst],
        worst_true=y_test[worst],
        worst_pred=pred[worst],
        worst_conf=conf[worst],
        confusion=confusion,
        n_weights=sum(W.size for W in Ws) + sum(b.size for b in bs),
    )

    print()
    print(f"lagret {OUT}")
    print(f"  første loss:  {first_loss:.4f}")
    print(f"  epoch 1 acc:  {epoch_acc[0] * 100:.2f}%")
    print(f"  epoch 10 acc: {epoch_acc[-1] * 100:.2f}%")
    print(f"  parametre:    {sum(W.size for W in Ws) + sum(b.size for b in bs):,}")
    print(buf.getvalue())


if __name__ == "__main__":
    main()
