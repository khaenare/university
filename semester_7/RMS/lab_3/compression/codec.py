"""Спільне для DCT і DWT: читання зображення, зменшення кількості коефіцієнтів, PSNR.

Стиснення однакове для обох методів:
    1) центруємо яскравість навколо нуля (x − 128, як у JPEG);
    2) пряме перетворення → коефіцієнти;
    3) залишаємо не більше заданої частки найбільших за модулем коефіцієнтів, решту обнуляємо;
    4) обернене перетворення + 128, округлення й обрізання до 0…255.
Обидва методи отримують однаковий ліміт коефіцієнтів, тож їх якість можна чесно
порівняти. Нульові коефіцієнти (однотонні області) не зберігаються — тому метод,
якому вистачає менше коефіцієнтів, може використати менше за ліміт.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from .dct import dct2, idct2
from .haar import dwt2, idwt2

SIZE = 512
METHODS = {"DCT": (dct2, idct2), "DWT": (dwt2, idwt2)}
EPS = 1e-9        # менші за модулем коефіцієнти — похибка обчислень, а не інформація


@dataclass
class Result:
    coeffs: np.ndarray      # збережені коефіцієнти (решта — нулі)
    restored: np.ndarray    # відновлене зображення, 0…255
    kept: int               # скільки ненульових коефіцієнтів збережено
    psnr: float

    @property
    def ratio(self) -> float:
        """Коефіцієнт стиснення за кількістю коефіцієнтів (не розмір файлу)."""
        return self.coeffs.size / self.kept if self.kept else float("inf")


def _to_gray(image: Image.Image) -> Image.Image:
    """Будь-який режим Pillow → 8-бітні відтінки сірого."""
    if image.mode.startswith("I;16"):                       # 16 біт: 0…65535 → 0…255
        return Image.fromarray((np.asarray(image, dtype=float) / 257).round().astype(np.uint8))
    if image.mode in ("I", "F"):                            # 32 біти: розтягуємо фактичний діапазон
        values = np.asarray(image, dtype=float)
        values = (values - values.min()) / (np.ptp(values) or 1) * 255
        return Image.fromarray(values.round().astype(np.uint8))
    if "A" in image.mode or "transparency" in image.info:  # прозорі ділянки — на білому тлі
        image = Image.alpha_composite(Image.new("RGBA", image.size, "white"), image.convert("RGBA"))
    return image.convert("L")


def load_image(path) -> np.ndarray:
    """Будь-яке зображення → відтінки сірого 512×512 (центральний квадрат), значення 0…255.
    Якщо файл не вдається прочитати — ValueError із зрозумілим повідомленням."""
    try:
        with Image.open(path) as image:
            gray = _to_gray(ImageOps.exif_transpose(image))
            square = ImageOps.fit(gray, (SIZE, SIZE), Image.LANCZOS)
    except (OSError, Image.DecompressionBombError) as error:
        raise ValueError(f"«{Path(path).name}» не вдалося відкрити як зображення") from error
    return np.asarray(square, dtype=float)


def keep_largest(coeffs: np.ndarray, fraction: float) -> np.ndarray:
    """Залишає не більше частки fraction найбільших за модулем коефіцієнтів, решту обнуляє.
    Нульові коефіцієнти не зберігаються: якщо значущих менше за ліміт — зберігаються всі значущі."""
    if not 0 < fraction <= 1:
        raise ValueError(f"Частка коефіцієнтів має бути в межах (0; 1], отримано {fraction}")
    magnitudes = np.abs(coeffs).ravel()
    keep = min(max(1, round(fraction * magnitudes.size)), int(np.count_nonzero(magnitudes > EPS)))
    kept = np.zeros(magnitudes.size)
    if keep:
        largest = np.argpartition(magnitudes, -keep)[-keep:]   # індекси keep найбільших, без повного сортування
        kept[largest] = coeffs.ravel()[largest]
    return kept.reshape(coeffs.shape)


def analyze(image: np.ndarray, method: str) -> np.ndarray:
    """Пряме перетворення зображення, центрованого навколо нуля (x − 128, як у JPEG)."""
    return METHODS[method][0](image - 128)


def compress(image: np.ndarray, method: str, fraction: float, coeffs: np.ndarray | None = None) -> Result:
    """Стиснення й відновлення. coeffs — уже пораховане analyze(image, method),
    щоб не повторювати пряме перетворення, коли змінюється лише частка."""
    if coeffs is None:
        coeffs = analyze(image, method)
    kept = keep_largest(coeffs, fraction)
    restored = np.clip(np.round(METHODS[method][1](kept) + 128), 0, 255)
    return Result(kept, restored, int(np.count_nonzero(kept)), psnr(image, restored))


def psnr(original: np.ndarray, restored: np.ndarray) -> float:
    """PSNR = 10 · log10(255² / MSE), MSE — середній квадрат різниці пікселів, дБ."""
    mse = np.mean((original - restored) ** 2)
    return float("inf") if mse == 0 else 10 * np.log10(255 ** 2 / mse)


def format_db(value: float) -> str:
    """PSNR для показу: 31.6412 → '31.64', нескінченність → '∞'."""
    return "∞" if value == float("inf") else f"{value:.2f}"
