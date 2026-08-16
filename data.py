from sklearn.datasets import fetch_openml
import matplotlib.pyplot as plt
import numpy as np

def load_data():
    """
    Laster inn MNIST-data og returnerer trent og testdata.
    """
    X, y = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)
    X = X.astype(np.float32) / 255.0
    y = y.astype(int)

    split = 60000
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:] 
    y_train = one_hot_encode(y_train, 10) # One-hot encoded training data, test data remains

    return X_train, X_test, y_train, y_test

def test_data(X, y): 
    for i in range(5):
        plt.subplot(1, 5, i + 1)
        plt.imshow(X[i].reshape(28, 28), cmap='gray')
        plt.title(f'{y[i]}')
        plt.axis('off')
    plt.show()


def one_hot_encode(y, num_classes):
    """
    Konverterer en vektor av etiketter til one-hot encoding.
    y: numpy-array med etiketter (0-9)
    num_classes: antall klasser (10 for MNIST)
    Returnerer en numpy-array med shape (len(y), num_classes) der hver rad er en one-hot vektor.
    """
    return np.eye(num_classes, dtype=np.float32)[y]

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_data()
    print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)
    print(X_train.min(), X_train.max())

    test_data(X_train, np.argmax(y_train, axis=1))  # Visualiser noen treningsdata