import numpy as np


def check_moore_penrose_conditions(A: np.ndarray, A_plus: np.ndarray, tolerance: float = 1e-8) -> bool:
    """
    Verifies the four Moore-Penrose conditions for the pseudo-inverse of matrix A.
    """
    # Condition 1: A * A⁺ * A ≈ A
    condition_1 = np.allclose(A @ A_plus @ A, A, atol=tolerance)

    # Condition 2: A⁺ * A * A⁺ ≈ A⁺
    condition_2 = np.allclose(A_plus @ A @ A_plus, A_plus, atol=tolerance)

    # Condition 3: A * A⁺ is symmetric
    condition_3 = np.allclose(A @ A_plus, (A @ A_plus).T, atol=tolerance)

    # Condition 4: A⁺ * A is symmetric
    condition_4 = np.allclose(A_plus @ A, (A_plus @ A).T, atol=tolerance)

    print("Checking Moore-Penrose conditions:")
    print(f"1) A * A⁺ * A ≈ A: {condition_1}")
    print(f"2) A⁺ * A * A⁺ ≈ A⁺: {condition_2}")
    print(f"3) A * A⁺ is symmetric: {condition_3}")
    print(f"4) A⁺ * A is symmetric: {condition_4}")

    return condition_1 and condition_2 and condition_3 and condition_4


def moore_penrose_pseudo_inverse(A: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    """
    Computes the Moore-Penrose pseudo-inverse of matrix A using the regularization technique.
    """
    ATA = A.T @ A
    identity = np.eye(A.shape[1])

    # Regularization to handle singular matrices
    pinv = np.linalg.inv(ATA + epsilon * identity) @ A.T
    return pinv


def greville_pseudo_inverse(A: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    """
    Computes the Greville pseudo-inverse of matrix A using a different regularization method.
    """
    ATA = A.T @ A
    pinv = np.linalg.inv(ATA + epsilon * np.eye(A.shape[1])) @ A.T
    return pinv
