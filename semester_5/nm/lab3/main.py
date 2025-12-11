import numpy as np
import math

# --- налаштування ---
EPSILON = 0.01

# матриця
A_input = np.array([
    [6, 1, 2, 0, 1],
    [1, 5, 1, 0, 0],
    [2, 1, 7, 1, 1],
    [0, 0, 1, 4, 2],
    [1, 0, 1, 2, 3]
], dtype=float)


def jacobi_method(A, eps=0.01):
    n = A.shape[0]
    Mk = A.copy()
    iteration = 0

    # Обчислюємо початкове відхилення (t(A))
    # Сума квадратів усіх недіагональних елементів
    t_A = np.sum(Mk ** 2) - np.sum(np.diag(Mk) ** 2)

    print("Jacobi rotation method:")
    print("A(0) =")
    print(Mk)
    print(f"t(A(0)) = {t_A:.12f}")
    print("-" * 20)

    while t_A > eps:
        iteration += 1
        print(f"iteration {iteration}:")

        # 1. Пошук максимального за модулем недіагонального елемента
        max_el = 0.0
        p, q = 0, 0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(Mk[i, j]) > max_el:
                    max_el = abs(Mk[i, j])
                    p, q = i, j

        print(f"p={p} q={q} |a_pq|={max_el:.12f}")
        print(f"a_pp={Mk[p, p]:.12f} a_qq={Mk[q, q]:.12f}")

        # 2. Обчислення кута повороту phi
        # Формула: 0.5 * arctg( 2*a_pq / (a_pp - a_qq) )
        if abs(Mk[p, p] - Mk[q, q]) < 1e-15:
            phi = math.pi / 4 * (1 if Mk[p, q] > 0 else -1)
        else:
            phi = 0.5 * math.atan(2 * Mk[p, q] / (Mk[p, p] - Mk[q, q]))

        c = math.cos(phi)
        s = math.sin(phi)
        print(f"phi={phi:.12f} c={c:.12f} s={s:.12f}")

        # 3. Перерахунок елементів матриці (обертання)
        # Зберігаємо старі значення, які зміняться
        M_pp = Mk[p, p]
        M_qq = Mk[q, q]
        M_pq = Mk[p, q]

        # Перераховуємо діагональні елементи p та q
        Mk[p, p] = c ** 2 * M_pp + s ** 2 * M_qq + 2 * c * s * M_pq
        Mk[q, q] = s ** 2 * M_pp + c ** 2 * M_qq - 2 * c * s * M_pq

        # Явно обнуляємо елементи (p, q) та (q, p)
        Mk[p, q] = 0.0
        Mk[q, p] = 0.0

        # Перераховуємо інші елементи в рядках/стовпцях p та q
        for i in range(n):
            if i != p and i != q:
                M_ip = Mk[i, p]
                M_iq = Mk[i, q]

                # Формули обертання
                Mk[i, p] = c * M_ip + s * M_iq
                Mk[p, i] = Mk[i, p]  # симетрія

                Mk[i, q] = -s * M_ip + c * M_iq
                Mk[q, i] = Mk[i, q]  # симетрія

        # Виведення поточного стану
        print(f"A({iteration}) =")
        print(Mk)

        # Перераховуємо критерій зупинки
        t_A = np.sum(Mk ** 2) - np.sum(np.diag(Mk) ** 2)
        print(f"t(A({iteration})) = {t_A:.12f}")
        print()

    print("Done.")
    print(f"Eigenvalues (diag): {np.diag(Mk)}")
    return np.diag(Mk)


# Запуск
if __name__ == "__main__":
    jacobi_method(A_input, eps=EPSILON)