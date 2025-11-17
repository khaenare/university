import numpy as np
from PIL import Image

def read_grayscale_image(path):
    """
    Зчитує BMP-зображення, переводить у відтінки сірого
    та повертає його як матрицю float у діапазоні [0, 1].
    """
    img = Image.open(path).convert("L")   # переведення у grayscale
    arr = np.asarray(img, dtype=np.float32)
    arr = arr / 255.0                     # нормалізація до діапазону [0, 1]
    return arr

def save_grayscale_image(path, matrix):
    """
    Зберігає матрицю значень [0, 1] як BMP-файл у форматі grayscale.
    Значення автоматично обрізаються до допустимого діапазону.
    """
    matrix = np.clip(matrix, 0.0, 1.0)    # гарантія коректного діапазону
    img = Image.fromarray((matrix * 255).astype(np.uint8), mode="L")
    img.save(path)
