import os

import numpy as np
import matplotlib.pyplot as plt

from nn.network import init_params, forward, backward, loss
from nn.data import load_data
from nn.weightviz import LiveWeights

if __name__ == "__main__":
    print()
    print("Neural network for MNIST dataset")
    print()
    print("="*64)
    print()
    # Init
    sizes = [784, 128, 10]
    Ws, bs = init_params(sizes)

    # Get training data
    X_train, X_test, y_train, y_test = load_data()

    lr = 1.0
    split = 60000
    batch_size = 32
    epochs = 10

    # LIVE=1: se vektene bli til mens den trener
    live = LiveWeights() if os.environ.get("LIVE", "0") not in ("0", "") else None
    step = 0

    # Traning loop
    for e in range(epochs):
        losses = []

        # Permute data to make sure its random
        perm = np.random.permutation(len(X_train))
        X_shuffled = X_train[perm]
        y_shuffled = y_train[perm]
        for i in range(0, split, batch_size):
            X = X_shuffled[i:i + batch_size]
            y = y_shuffled[i:i + batch_size]

            A_out, Zs, As = forward(X, Ws, bs)
            dWs, dbs = backward(y, Zs, As, Ws)

            l = loss(A_out, y)
            losses.append(l)

            for j in range(len(Ws)):
                Ws[j] -= lr * dWs[j]
                bs[j] -= lr * dbs[j]

            if live is not None:
                live.update(Ws[0], step, extra=f"   epoch {e + 1}/{epochs}   loss {l:.3f}")
            step += 1

        losses = np.array(losses)
        if e == 0:
            print("First loss =", losses[0])
        print("Epoch", e + 1, "- mean loss:", np.mean(losses))

        A_out, _, _ = forward(X_test, Ws, bs)
        pred = np.argmax(A_out, axis=1)
        acc = np.mean(pred == y_test)

        print("-- Pred:", pred, "Accuracy:", acc)
        print()



    print()
    print("="*64)
    print()
    print("First 5 losses:", losses[:5])
    print("Last 5 losses:", losses[-5:])

    m_i = []
    for i in range(len(y_test)):
        if pred[i] != y_test[i]:
            m_i.append(i)

    # 2D 10 col and 10 row array of which guesses were wrong and what the correct answer was
    wrong_guesses = np.zeros((10, 10), dtype=int)
    for i in m_i:
        wrong_guesses[y_test[i], pred[i]] += 1
    print("Wrong guesses (rows = correct, cols = guessed):")
    # map with 0 to 9 as row and col labels
    print("   ", end="")
    for i in range(10):
        print(f"{i:>3}", end="")
    print()
    for i in range(10):
        print(f"{i:>3}", end="")
        for j in range(10):
            print(f"{wrong_guesses[i, j]:>3}", end="")
        print()

    confidence = A_out[m_i, pred[m_i]]      # hvor sikker den var på sitt (gale) svar
    worst = np.array(m_i)[np.argsort(-confidence)][:20]

    show_worst = False
    if show_worst:
        for i in range(0, 20, 5):
            for j in range(5):
                plt.subplot(1, 5, j + 1)
                plt.imshow(X_test[worst[i+j]].reshape(28, 28), cmap='gray')
                plt.title(f'Fasit: {y_test[worst[i+j]]}, Gjett: {pred[worst[i+j]]}', rotation="vertical")
                plt.axis('off')
            plt.show()