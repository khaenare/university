from image_io import read_grayscale_image
from utils import augment_with_ones

# Зчитуємо вхідне зображення
X = read_grayscale_image("x3.bmp")

# Формуємо розширену матрицю
X_tilde = augment_with_ones(X)

print("Стара форма X:", X.shape)
print("Нова форма  X̃:", X_tilde.shape)

# Перевірка, що останній рядок — одиниці
print("Унікальні значення останнього рядка:",
      set(X_tilde[-1].round(5)))
