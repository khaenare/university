import numpy as np

def augment_with_ones(X):
    """
    Додає рядок одиниць до матриці X.
    Використовується для урахування вільного члена у лінійній моделі.
    """
    ones = np.ones((1, X.shape[1]), dtype=np.float32)  # рядок ones
    X_tilde = np.vstack([X, ones])                     # розширена матриця
    return X_tilde
