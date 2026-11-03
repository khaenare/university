"""Дискретне косинусне перетворення (DCT-II) блоками 8×8 у матричній формі.

Для блоку X розміром N×N:
    пряме      Y = C · X · Cᵀ
    обернене   X = Cᵀ · Y · C
де C — матриця DCT:  C[k, n] = α(k) · cos(π · (2n + 1) · k / (2N)),
α(0) = √(1/N), α(k) = √(2/N) для k > 0.

Рядок k матриці — косинусна хвиля частоти k. Множення C · X рахує DCT
кожного стовпця блоку, а · Cᵀ — кожного рядка, тобто разом це 2D DCT.
Матриця ортонормована (C · Cᵀ = I), тому обернена до неї — транспонована.
Y[0, 0] — середня яскравість блоку (DC), чим далі від лівого верхнього
кута, тим вища частота коливань яскравості.
"""
import numpy as np

BLOCK = 8


def dct_matrix(n: int = BLOCK) -> np.ndarray:
    k = np.arange(n)[:, None]                      # номер частоти — рядок матриці
    x = np.arange(n)[None, :]                      # номер пікселя — стовпець
    c = np.sqrt(2 / n) * np.cos(np.pi * (2 * x + 1) * k / (2 * n))
    c[0, :] = np.sqrt(1 / n)                       # α(0) інший, щоб рядок мав одиничну довжину
    return c


C = dct_matrix()


def to_blocks(image: np.ndarray) -> np.ndarray:
    """(H, W) → (H/8, W/8, 8, 8): масив блоків 8×8."""
    h, w = image.shape
    if h % BLOCK or w % BLOCK:
        raise ValueError(f"Для DCT розміри зображення мають ділитися на {BLOCK}, отримано {h}×{w}")
    return image.reshape(h // BLOCK, BLOCK, w // BLOCK, BLOCK).swapaxes(1, 2)


def from_blocks(blocks: np.ndarray) -> np.ndarray:
    """Зворотне до to_blocks: блоки → зображення."""
    rows, cols = blocks.shape[:2]
    return blocks.swapaxes(1, 2).reshape(rows * BLOCK, cols * BLOCK)


def dct2(image: np.ndarray) -> np.ndarray:
    """Пряме DCT кожного блоку 8×8; коефіцієнти лежать на місці своїх блоків."""
    return from_blocks(C @ to_blocks(image) @ C.T)    # @ множить матриці для всіх блоків одразу


def idct2(coeffs: np.ndarray) -> np.ndarray:
    """Обернене DCT кожного блоку 8×8."""
    return from_blocks(C.T @ to_blocks(coeffs) @ C)


def group_by_frequency(coeffs: np.ndarray) -> np.ndarray:
    """Для показу: збирає однакові частоти всіх блоків поруч (DC усіх блоків — у лівому
    верхньому куті), тоді видно, що енергія зосереджена в низьких частотах."""
    blocks = to_blocks(coeffs)                          # (рядок блоку, стовпець блоку, u, v)
    rows, cols = blocks.shape[:2]
    return blocks.transpose(2, 0, 3, 1).reshape(BLOCK * rows, BLOCK * cols)
