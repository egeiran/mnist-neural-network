import numpy as np

from data import load_data

def init_params(sizes):
    """
    Initialiserer vekter og biaser for et nevralt nettverk.
    sizes: Liste over antall noder i hvert lag (inkludert input- og output-lag)
    Returnerer:
    - Ws: Liste over vektmatriser for hvert lag
    - bs: Liste over bias-vektorer for hvert lag
    """
    Ws = []
    bs = []
    for n_in, n_out in zip(sizes[:-1], sizes[1:]): 
        W = np.random.randn(n_in, n_out) * np.sqrt(1 / n_in)
        b = np.zeros((n_out))

        Ws.append(W)
        bs.append(b)

    return Ws, bs

def sigmoid(z): 
    """
    Sigmoid-aktiveringsfunksjon. 
    Den tar en numpy-array som input og returnerer en numpy-array med samme form, der hver verdi er transformert med sigmoid-funksjonen.
    Den gir tall mellom 0 og 1, og brukes ofte som aktiveringsfunksjon i nevrale nettverk.
    """
    return 1 / (1 + np.exp(-z))

def sigmoid_prime(z):
    """
    Derivert av sigmoid-funksjonen.
    Den tar en numpy-array som input og returnerer en numpy-array med samme form, der hver verdi er den deriverte av sigmoid-funksjonen evaluert ved den opprinnelige verdien.
    """
    s = sigmoid(z)
    return s * (1 - s)

def forward(X, Ws, bs):
    """
    Utfører fremoverpropagering gjennom et nevralt nettverk.
    X: Input-data (numpy-array)
    Ws: Liste over vektmatriser for hvert lag
    bs: Liste over bias-vektorer for hvert lag
    Returnerer:
    - A_out: Output fra det siste laget (numpy-array)
    - Zs: Liste over lineære kombinasjoner (Z) for hvert lag
    - As: Liste over aktiveringer (A) for hvert lag
    """
    As = [X] # Start med input som første aktivering
    Zs = []  # Liste for å lagre Z-verdier for hvert lag
    for W, b in zip(Ws, bs):
        Z = As[-1] @ W + b    # Beregner lineær kombinasjon for laget
        Zs.append(Z)          # Lagre Z for dette laget
        As.append(sigmoid(Z)) # Lagre aktivering for dette laget
        assert Z.shape == (X.shape[0], W.shape[1]), f"Feil form på Z: {Z.shape}"

    return As[-1], Zs, As

def loss(A_out, Y):
    """
    Beregner gjennomsnittlig kvadratfeil mellom nettverkets output og de faktiske etikettene.
    A_out: Output fra det siste laget (numpy-array)
    Y: Faktiske etiketter (numpy-array)
    Returnerer gjennomsnittlig kvadratfeil.
    """
    return np.mean(np.sum((A_out - Y) ** 2, axis=1))

def backward(Y, Zs, As, Ws):
    """
    Utfører bakoverpropagering for å beregne gradientene av vekter og biaser.
    Y: Faktiske etiketter (numpy-array)
    Zs: Liste over lineære kombinasjoner (Z) for hvert lag
    As: Liste over aktiveringer (A) for hvert lag
    Ws: Liste over vektmatriser for hvert lag
    Returnerer:
    - dWs: Liste over gradienter for vekter
    - dbs: Liste over gradienter for biaser
    """
    m = Y.shape[0]  # Antall eksempler i batchen
    dWs = []        # Liste for å lagre gradienter for vekter
    dbs = []        # Liste for å lagre gradienter for biaser

    # Beregn feilen for output-laget
    # delta ser ut som (m, n_out), der m er antall eksempler og n_out er antall noder i output-laget
    delta = (As[-1] - Y) * sigmoid_prime(Zs[-1]) * 2 # Feil for output-laget


    # Bakoverpropager gjennom lagene
    for l in reversed(range(len(Ws))):
        # dW ser ut som (n_in, n_out), der n_in er antall noder i forrige lag og n_out er antall noder i dette laget
        dW = As[l].T @ delta / m        # Gradient for vekter
        # db ser ut som (n_out,), der n_out er antall noder i dette laget
        db = np.sum(delta, axis=0) / m  # Gradient for biaser

        dWs.insert(0, dW)               # Sett inn i starten av listen
        dbs.insert(0, db)               # Sett inn i starten av listen

        assert dW.shape == Ws[l].shape
        assert db.shape == (Ws[l].shape[1],)

        if l > 0:
            delta = (delta @ Ws[l].T) * sigmoid_prime(Zs[l - 1])  # Feil for neste lag

    return dWs, dbs

def grad_check(seed=0):
    np.random.seed(seed)
    sizes = [5, 4, 3]
    Ws, bs = init_params(sizes)
    X = np.random.randn(2, 5)
    Y = np.eye(3)[[0, 2]]
    eps = 1e-5

    # Kjør backprop en gang på de urørte vektene
    A_out, Zs, As = forward(X, Ws, bs)
    dWs, dbs = backward(Y, Zs, As, Ws)

    # Sjekk noen tilfeldige vekter
    for _ in range(5):
        l = np.random.randint(len(Ws))          # Velg et tilfeldig lag (type: int)
        i = np.random.randint(Ws[l].shape[0])   # Velg en tilfeldig rad i vektmatrisen (type: int)
        j = np.random.randint(Ws[l].shape[1])   # Velg en tilfeldig kolonne i vektmatrisen (type: int)

        gammel = Ws[l][i, j]  # Lagre den gamle verdien

        Ws[l][i, j] = gammel + eps
        loss_plus = loss(forward(X, Ws, bs)[0], Y)

        Ws[l][i, j] = gammel - eps
        loss_minus = loss(forward(X, Ws, bs)[0], Y)

        Ws[l][i, j] = gammel  # Sett tilbake den gamle verdien

        numerisk = (loss_plus - loss_minus) / (2 * eps)
        analytisk = dWs[l][i, j]
        rel_diff = np.abs(numerisk - analytisk) / max(np.abs(numerisk), np.abs(analytisk))

        assert rel_diff < 1e-6, f"Gradient check feilet for lag {l}, element ({i}, {j}): numerisk={numerisk}, analytisk={analytisk}, relativ forskjell={rel_diff}"

        # print(f"Layer {l}, Element ({i}, {j}): Numerisk = {numerisk}, Analytisk = {analytisk}, Relativ forskjell = {rel_diff}")
        # print(f"  -- W[{l}][{i},{j}]  num={numerisk:.8f}  ana={analytisk:.8f}  rel={rel_diff:.2e}")



if __name__ == "__main__":
    sizes = [784, 128, 10]
    Ws, bs = init_params(sizes)
    assert Ws[0].shape == (784, 128)
    assert bs[0].shape == (128,)

    assert np.isclose(sigmoid(0), 0.5)
    assert np.isclose(sigmoid_prime(0), 0.25)

    print("Sigmoid test:", sigmoid(np.array([-10, 0, 10]))) # Skal gi noe rundt [0, 0.5, 1]
    print("Sigmoid derivative test:", sigmoid_prime(np.array([-10, 0, 10]))) # Skal gi noe rundt [0, 0.25, 0]

    print("Weights:")
    for W in Ws:
        print(W.shape)
    print("Biases:")
    for b in bs:
        print(b.shape)

    print(Ws[0].std()) # Standardavviket til vektene i første lag
    print(Ws[1].std()) # Standardavviket til vektene i andre lag

    X_train, X_test, Y_train, y_test = load_data()

    A_out, Zs, As = forward(X_train[:5], Ws, bs)

    print(A_out.shape)      # (5, 10)
    print(len(Zs))         # 2
    print(len(As))         # 3
    print(A_out[0])         # ti tall rundt 0.5

    print("Loss:", loss(A_out, Y_train[:5]))

    dWs, dbs = backward(Y_train[:5], Zs, As, Ws)
    for i, (dW, db) in enumerate(zip(dWs, dbs)):
        print(f"Layer {i}: dW shape: {dW.shape}, db shape: {db.shape}")

    print("Gradient check:")
    grad_check()