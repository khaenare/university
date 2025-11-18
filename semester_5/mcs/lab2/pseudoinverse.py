import numpy as np

def pseudo_inverse_moore_penrose(A, eps=1e-6, max_iter=50):
    """
    Стійка реалізація псевдообернення за формулою Мура–Пенроуза
    з Tikhonov-регуляризацією та поступовим зменшенням δ.
    Використовується формула:
        A⁺ = (Aᵀ A + δ I)⁻¹ Aᵀ
    """

    m, n = A.shape
    I = np.eye(n)

    # Початкове значення δ (регуляризація)
    delta = 1.0

    A_T = A.T
    A_TA = A_T @ A

    A_pinv_prev = None

    for _ in range(max_iter):
        # Обчислюємо псевдообернену з поточним δ
        A_pinv = np.linalg.solve(A_TA + delta * I, A_T)

        # Перевірка стабільності і збіжності
        if A_pinv_prev is not None:
            if np.linalg.norm(A_pinv - A_pinv_prev, ord='fro') < eps:
                break

        A_pinv_prev = A_pinv
        delta *= 0.5  # плавно зменшуємо регуляризацію

    return A_pinv


def is_pseudoinverse(A, A_plus, tol=1e-5):
    """
    Перевіряє умови Мура–Пенроуза.
    """
    c1 = np.allclose(A @ A_plus @ A, A, atol=tol)
    c2 = np.allclose(A_plus @ A @ A_plus, A_plus, atol=tol)
    c3 = np.allclose((A @ A_plus).T, A @ A_plus, atol=tol)
    c4 = np.allclose((A_plus @ A).T, A_plus @ A, atol=tol)

    return c1 and c2 and c3 and c4
