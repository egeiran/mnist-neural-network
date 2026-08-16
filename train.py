import numpy as np
import matplotlib.pyplot as plt

from network import init_params, forward, backward, loss
from data import load_data

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

    confidence = A_out[m_i, pred[m_i]]      # hvor sikker den var på sitt (gale) svar
    worst = np.array(m_i)[np.argsort(-confidence)][:20]

    for i in range(0, 20, 5):
        for j in range(5):
            plt.subplot(1, 5, j + 1)
            plt.imshow(X_test[worst[i+j]].reshape(28, 28), cmap='gray')
            plt.title(f'Fasit: {y_test[worst[i+j]]}, Gjett: {pred[worst[i+j]]}', rotation="vertical")
            plt.axis('off')
        plt.show()