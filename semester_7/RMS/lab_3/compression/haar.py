"""Дискретне вейвлет-перетворення Хаара (DWT), двовимірне, багаторівневе.

Один крок для пари сусідніх пікселів (a, b):
    s = (a + b) / √2    — сума: низькі частоти, згладжене зображення
    d = (a − b) / √2    — різниця: високі частоти, деталі й краї
Обернений крок:  a = (s + d) / √2,  b = (s − d) / √2.
Ділення на √2 робить перетворення ортонормованим — енергія зберігається.

Крок застосовується до рядків, потім до стовпців → 4 підсмуги:
    LL — зменшена вдвічі копія зображення   |  HL — вертикальні деталі
    LH — горизонтальні деталі               |  HH — діагональні деталі
Наступний рівень розкладає лише LL, тому після кількох рівнів майже вся
енергія зосереджена в маленькому LL у лівому верхньому куті.
"""
import numpy as np

LEVELS = 5        # 512 → LL 16×16; глибше PSNR майже не зростає (перевірено експериментом)
SQRT2 = np.sqrt(2)


def _forward_step(a: np.ndarray) -> np.ndarray:
    lo = (a[:, 0::2] + a[:, 1::2]) / SQRT2         # рядки: суми пар — ліворуч
    hi = (a[:, 0::2] - a[:, 1::2]) / SQRT2         #        різниці — праворуч
    a = np.hstack([lo, hi])
    lo = (a[0::2, :] + a[1::2, :]) / SQRT2         # стовпці: суми — вгорі
    hi = (a[0::2, :] - a[1::2, :]) / SQRT2         #          різниці — внизу
    return np.vstack([lo, hi])


def _inverse_step(c: np.ndarray) -> np.ndarray:
    h, w = c.shape[0] // 2, c.shape[1] // 2
    a = np.empty_like(c)
    a[0::2, :] = (c[:h] + c[h:]) / SQRT2           # спершу скасовуємо крок по стовпцях
    a[1::2, :] = (c[:h] - c[h:]) / SQRT2
    out = np.empty_like(a)
    out[:, 0::2] = (a[:, :w] + a[:, w:]) / SQRT2   # потім по рядках
    out[:, 1::2] = (a[:, :w] - a[:, w:]) / SQRT2
    return out


def _check(shape: tuple[int, int], levels: int):
    """Кожен рівень ділить розмір навпіл, тому сторони мають ділитися на 2^levels."""
    step = 2 ** levels
    if levels < 0 or shape[0] % step or shape[1] % step:
        raise ValueError(f"Для {levels} рівнів Хаара розміри мають ділитися на {step}, "
                         f"отримано {shape[0]}×{shape[1]}")


def dwt2(image: np.ndarray, levels: int = LEVELS) -> np.ndarray:
    """Пряме перетворення: кожен рівень розкладає ліву верхню чверть (LL) попереднього."""
    _check(image.shape, levels)
    coeffs = image.astype(float).copy()
    h, w = coeffs.shape
    for _ in range(levels):
        coeffs[:h, :w] = _forward_step(coeffs[:h, :w])
        h, w = h // 2, w // 2
    return coeffs


def idwt2(coeffs: np.ndarray, levels: int = LEVELS) -> np.ndarray:
    """Обернене перетворення: від найменшого LL до повного розміру."""
    _check(coeffs.shape, levels)
    image = coeffs.astype(float).copy()
    h, w = image.shape[0] >> levels, image.shape[1] >> levels
    for _ in range(levels):
        h, w = h * 2, w * 2
        image[:h, :w] = _inverse_step(image[:h, :w])
    return image
