import numpy as np
from PIL import Image

def read_grayscale_image(path):
    """
    Зчитує BMP-файл, конвертує його в grayscale і нормалізує пікселі.
    Повертає матрицю numpy.
    """
    img = Image.open(path).convert('L')  # Конвертируем в grayscale
    img_data = np.array(img) / 255.0    # Нормализуем значения пикселей
    return img_data

def save_grayscale_image(path, matrix):
    """
    Преобразует матрицу numpy обратно в изображение и сохраняет как BMP.
    """
    img_data = np.clip(matrix * 255, 0, 255).astype(np.uint8)  # Преобразуем обратно в диапазон [0, 255]
    img = Image.fromarray(img_data)
    img.save(path)

