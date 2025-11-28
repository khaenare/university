import numpy as np

# ==========================================================
# Лабораторна робота №2: Розв’язання СЛАР чисельними методами
# Варіант 3: Метод Гаусса (з вибором головного елемента),
#            Метод прогонки, Метод Зейделя
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
# Метод Гаусса з вибором головного елемента (по матриці)
# ==========================
def gauss_complete_pivot_fixed(A, b):
    A = A.copy()
    b = b.copy()

    n = len(A)
    index = np.arange(n)  # відстежуємо перестановки стовпців

    # прямий хід з повним вибором головного елемента
    for k in range(n - 1):
        # шукаємо максимум за модулем у підматриці A[k:, k:]
        sub = np.abs(A[k:, k:])
        p, q = divmod(sub.argmax(), sub.shape[1])
        p += k
        q += k

        if A[p, q] == 0:
            raise ValueError("Система не має єдиного розв’язку (нульовий головний елемент).")

        # переставляємо рядки p і k
        A[[k, p]] = A[[p, k]]
        b[[k, p]] = b[[p, k]]

        # переставляємо стовпці q і k
        A[:, [k, q]] = A[:, [q, k]]
        index[[k, q]] = index[[q, k]]

        # виключення Гаусса
        for i in range(k + 1, n):
            factor = A[i, k] / A[k, k]
            A[i, k:] -= factor * A[k, k:]
            b[i] -= factor * b[k]

    # зворотний хід
    x_local = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x_local[i] = (b[i] - np.dot(A[i, i + 1:], x_local[i + 1:])) / A[i, i]

    # повертаємо компоненти у вихідний порядок (з урахуванням перестановок стовпців)
    x = np.zeros(n)
    x[index] = x_local
    return x




# ==========================
# Метод прогонки (Томаса) для тридіагональної матриці
# ==========================
def thomas_method(A, b):
    n = len(A)
    a = np.zeros(n)  # піддіагональ
    c = np.zeros(n)  # головна діагональ
    d = np.zeros(n)  # наддіагональ

    for i in range(n):
        if i > 0:
            a[i] = A[i, i - 1]
        c[i] = A[i, i]
        if i < n - 1:
            d[i] = A[i, i + 1]

    P = np.zeros(n)
    Q = np.zeros(n)

    # прямий хід
    P[0] = -d[0] / c[0]
    Q[0] = b[0] / c[0]

    for i in range(1, n):
        denom = c[i] + a[i] * P[i - 1]
        if i < n - 1:
            P[i] = -d[i] / denom
        else:
            P[i] = 0.0
        Q[i] = (b[i] - a[i] * Q[i - 1]) / denom

    # зворотний хід
    x = np.zeros(n)
    x[-1] = Q[-1]
    for i in range(n - 2, -1, -1):
        x[i] = P[i] * x[i + 1] + Q[i]

    return x


# ==========================
# Метод Зейделя
# ==========================
def seidel_method(A, b, eps=1e-6, max_iter=1000):
    n = len(A)
    x = np.zeros(n)

    for iteration in range(1, max_iter + 1):
        x_new = x.copy()

        for i in range(n):
            s1 = np.dot(A[i, :i], x_new[:i])
            s2 = np.dot(A[i, i + 1:], x[i + 1:])
            x_new[i] = (b[i] - s1 - s2) / A[i, i]

        diff = np.linalg.norm(x_new - x, np.inf)
        print(f"Ітерація {iteration}: x = {x_new}, ||Δx|| = {diff:.6e}")
        x = x_new

        if diff < eps:
            print(f"Збіжність досягнута за {iteration} ітерацій.")
            return x, iteration

    print("Максимальна кількість ітерацій перевищена.")
    return x, max_iter


# ==========================
# Головна частина
# ==========================
def main():
    n = 4
    eps_str = input("Введіть точність ε (наприклад 1e-6): ")
    eps = float(eps_str) if eps_str.strip() != "" else 1e-6

    A, b = generate_tridiagonal_dd_matrix(n, seed=7)

    print_initial_data(A, b)

    # Метод Гаусса
    print("1. МЕТОД ГАУССА (з вибором головного елемента)")
    print("==============================================================")
    x_gauss = gauss_complete_pivot_fixed(A, b)

    for i, xi in enumerate(x_gauss, start=1):
        print(f"x{i} = {xi:.8f}")
    print("==============================================================\n")

    # Метод прогонки
    print("2. МЕТОД ПРОГОНКИ")
    print("==============================================================")
    x_thomas = thomas_method(A, b)
    for i, xi in enumerate(x_thomas, start=1):
        print(f"x{i} = {xi:.8f}")
    print("==============================================================\n")

    # Метод Зейделя
    print("3. МЕТОД ЗЕЙДЕЛЯ")
    print("==============================================================")
    x_seidel, iters = seidel_method(A, b, eps=eps)
    for i, xi in enumerate(x_seidel, start=1):
        print(f"x{i} = {xi:.8f}")
    print("==============================================================")
    print(f"Збіжність досягнута за {iters} ітерацій.")
    print("==============================================================\n")

    # Перевірка точності
    x_true = np.linalg.solve(A, b)
    print("Перевірка точності (numpy.linalg.solve):")
    print("x =", x_true)
    print("Різниця з методом Гаусса (||Δx||) =", np.linalg.norm(x_true - x_gauss))
    print("Різниця з методом прогонки (||Δx||) =", np.linalg.norm(x_true - x_thomas))
    print("Різниця з методом Зейделя (||Δx||)  =", np.linalg.norm(x_true - x_seidel))


if __name__ == "__main__":
    main()
