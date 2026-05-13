import numpy as np
import matplotlib.pyplot as plt


# ==========================================================
# Лабораторна робота №2: Розв’язання СЛАР чисельними методами
# Варіант 3: Метод Гаусса, Метод прогонки, Метод Зейделя
# + ВІЗУАЛІЗАЦІЯ РЕЗУЛЬТАТІВ
# ==========================================================

def generate_tridiagonal_dd_matrix(n, seed=7):
    np.random.seed(seed)
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(max(0, i - 1), min(n, i + 2)):
            A[i, j] = np.random.randint(-9, 10)
        # забезпечуємо діагональну домінантність
        A[i, i] = abs(A[i, i]) + sum(abs(A[i, j]) for j in range(n) if j != i)
    b = np.random.randint(-9, 10, size=n)
    return A, b


def print_initial_data(A, b):
    print("Матриця A (тридіагональна, діагонально домінантна):")
    print(A)
    print("\nВектор b:")
    print(b)
    print("\nПеревірка діагональної домінантності:")
    print("--------------------------------------")
    for i in range(len(A)):
        diag = abs(A[i, i])
        others = sum(abs(A[i, j]) for j in range(len(A)) if j != i)
        mark = "✓" if diag >= others else "✗"
        print(f"Рядок {i + 1}: |a{i + 1}{i + 1}| = {diag:.1f} ≥ {others:.1f} = Σ|aij|  {mark}")
    det_a = np.linalg.det(A)
    print(f"\nВизначник det(A) = {det_a}")
    print("==============================================================\n")


# ==========================
# Метод Гаусса з вибором головного елемента
# ==========================
def gauss_complete_pivot_fixed(A, b):
    A = A.copy()
    b = b.copy()
    n = len(A)
    index = np.arange(n)

    for k in range(n - 1):
        sub = np.abs(A[k:, k:])
        p, q = divmod(sub.argmax(), sub.shape[1])
        p += k
        q += k

        if A[p, q] == 0:
            raise ValueError("Нульовий головний елемент.")

        A[[k, p]] = A[[p, k]]
        b[[k, p]] = b[[p, k]]
        A[:, [k, q]] = A[:, [q, k]]
        index[[k, q]] = index[[q, k]]

        for i in range(k + 1, n):
            factor = A[i, k] / A[k, k]
            A[i, k:] -= factor * A[k, k:]
            b[i] -= factor * b[k]

    x_local = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x_local[i] = (b[i] - np.dot(A[i, i + 1:], x_local[i + 1:])) / A[i, i]

    x = np.zeros(n)
    x[index] = x_local
    return x


# ==========================
# Метод прогонки (Томаса)
# ==========================
def thomas_method(A, b):
    n = len(A)
    a = np.zeros(n)
    c = np.zeros(n)
    d = np.zeros(n)
    for i in range(n):
        if i > 0: a[i] = A[i, i - 1]
        c[i] = A[i, i]
        if i < n - 1: d[i] = A[i, i + 1]

    P = np.zeros(n)
    Q = np.zeros(n)
    P[0] = -d[0] / c[0]
    Q[0] = b[0] / c[0]

    for i in range(1, n):
        denom = c[i] + a[i] * P[i - 1]
        P[i] = -d[i] / denom if i < n - 1 else 0.0
        Q[i] = (b[i] - a[i] * Q[i - 1]) / denom

    x = np.zeros(n)
    x[-1] = Q[-1]
    for i in range(n - 2, -1, -1):
        x[i] = P[i] * x[i + 1] + Q[i]
    return x


# ==========================
# Метод Зейделя (Оновлений для збору історії помилок)
# ==========================
def seidel_method(A, b, eps=1e-6, max_iter=1000):
    n = len(A)
    x = np.zeros(n)
    errors = []  # Список для збереження похибки на кожному кроці

    for iteration in range(1, max_iter + 1):
        x_new = x.copy()
        for i in range(n):
            s1 = np.dot(A[i, :i], x_new[:i])
            s2 = np.dot(A[i, i + 1:], x[i + 1:])
            x_new[i] = (b[i] - s1 - s2) / A[i, i]

        diff = np.linalg.norm(x_new - x, np.inf)
        errors.append(diff)  # Додаємо похибку в історію

        print(f"Ітерація {iteration}: ||Δx|| = {diff:.6e}")
        x = x_new

        if diff < eps:
            print(f"Збіжність досягнута за {iteration} ітерацій.")
            return x, iteration, errors

    print("Максимальна кількість ітерацій перевищена.")
    return x, max_iter, errors


# ==========================
# Функції для побудови графіків
# ==========================

def plot_seidel_convergence(errors):
    """Будує графік залежності похибки від номера ітерації"""
    plt.figure(figsize=(8, 5))
    iterations = range(1, len(errors) + 1)
    plt.plot(iterations, errors, marker='o', linestyle='-', color='b', label='Метод Зейделя')
    plt.yscale('log')  # Логарифмічна шкала для кращої видимості збіжності
    plt.grid(True, which="both", ls="--")
    plt.xlabel('Номер ітерації')
    plt.ylabel('Похибка ||x^(k) - x^(k-1)|| (log scale)')
    plt.title('Графік збіжності методу Зейделя')
    plt.legend()
    plt.show()


def plot_solutions_comparison(x_gauss, x_thomas, x_seidel, x_numpy):
    """Стовпчаста діаграма для порівняння розв'язків"""
    indices = np.arange(len(x_gauss))
    width = 0.2

    plt.figure(figsize=(10, 6))
    plt.bar(indices - 1.5 * width, x_gauss, width, label='Гаусс')
    plt.bar(indices - 0.5 * width, x_thomas, width, label='Прогонка')
    plt.bar(indices + 0.5 * width, x_seidel, width, label='Зейдель')
    plt.bar(indices + 1.5 * width, x_numpy, width, label='Numpy (Exact)', alpha=0.5, color='gray')

    plt.xlabel('Індекс невідомого (x_i)')
    plt.ylabel('Значення')
    plt.title('Порівняння розв\'язків різними методами')
    plt.xticks(indices, [f'x{i + 1}' for i in indices])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


def visualize_matrix_structure(A):
    """Візуалізація структури матриці (теплова карта)"""
    plt.figure(figsize=(6, 5))
    plt.imshow(np.abs(A), cmap='Blues', interpolation='nearest')
    plt.colorbar(label='Модуль значення елемента')
    plt.title('Візуалізація матриці коефіцієнтів A')

    # Додаємо текстові значення в клітинки
    rows, cols = A.shape
    for i in range(rows):
        for j in range(cols):
            if A[i, j] != 0:
                plt.text(j, i, f"{A[i, j]:.0f}", ha="center", va="center",
                         color="black" if np.abs(A[i, j]) < 5 else "white")

    plt.xticks(range(cols), [f'{j + 1}' for j in range(cols)])
    plt.yticks(range(rows), [f'{i + 1}' for i in range(rows)])
    plt.xlabel('Стовпці')
    plt.ylabel('Рядки')
    plt.show()


# ==========================
# Головна частина
# ==========================
def main():
    n = 4
    # Можна змінити на input(), якщо потрібно вводити вручну
    eps = 1e-6
    print(f"Точність для методу Зейделя: {eps}")

    A, b = generate_tridiagonal_dd_matrix(n, seed=7)
    print_initial_data(A, b)

    # 1. Візуалізація матриці
    #visualize_matrix_structure(A)

    # 2. Обчислення
    x_gauss = gauss_complete_pivot_fixed(A, b)
    x_thomas = thomas_method(A, b)
    x_seidel, iters, errors_history = seidel_method(A, b, eps=eps)
    x_numpy = np.linalg.solve(A, b)

    # Вивід результатів
    print("\nРЕЗУЛЬТАТИ:")
    print(f"Гаусс:    {x_gauss}")
    print(f"Прогонка: {x_thomas}")
    print(f"Зейдель:  {x_seidel}")
    print(f"Numpy:    {x_numpy}")

    # 3. Графік збіжності Зейделя
    plot_seidel_convergence(errors_history)

    # 4. Порівняння результатів
    plot_solutions_comparison(x_gauss, x_thomas, x_seidel, x_numpy)


if __name__ == "__main__":
    main()