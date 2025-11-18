import numpy as np
from image_io import read_grayscale_image
from utils import augment_with_ones
from pseudoinverse import pseudo_inverse_moore_penrose, is_pseudoinverse

# Зчитуємо X
X = read_grayscale_image("x3.bmp")
X_tilde = augment_with_ones(X)

# Перетворюємо у 2D матрицю
A = X_tilde

print("Форма A:", A.shape)

# Обчислюємо псевдообернену
A_plus = pseudo_inverse_moore_penrose(A)
print("Форма A⁺:", A_plus.shape)

# Перевірка умов Мура–Пенроуза
print("Чи є A⁺ псевдооберненою матрицею:", is_pseudoinverse(A, A_plus))
