import math
import numpy as np
import matplotlib.pyplot as plt

# ==========================
# ПАРАМЕТРИ ЗАДАЧІ
# ==========================
interval_start = 5.0
interval_end = 6.0
initial_guess = 5.5
tolerance = 1e-4
max_iterations = 100


# ==========================
# ЦІЛЬОВА ФУНКЦІЯ ТА ПОХІДНІ
# ==========================

def target_function(x):
    return x ** 4 - 5.74 * x ** 3 + 8.18 * x - 3.48


def target_function_derivative(x):
    return 4.0 * x ** 3 - 17.22 * x ** 2 + 8.18


def target_function_second_derivative(x):
    return 12.0 * x ** 2 - 34.44 * x


# ==========================
# ДОПОМІЖНІ ФУНКЦІЇ
# ==========================

def max_abs_on_interval(func, a, b, n_points=1000):
    xs = np.linspace(a, b, n_points)
    values = np.abs(func(xs))
    return float(np.max(values))


def min_abs_on_interval(func, a, b, n_points=1000):
    xs = np.linspace(a, b, n_points)
    values = np.abs(func(xs))
    return float(np.min(values))


def print_iterations_table(values, title):
    print(title)
    print("-" * 50)
    print("{:>3s} | {:>15s} | {:>15s}".format("k", "x_k", "Delta"))
    print("-" * 50)
    for k, x_k in enumerate(values):
        if k == 0:
            delta_str = "-"
        else:
            delta = abs(values[k] - values[k - 1])
            delta_str = f"{delta:.10f}"
        print("{:3d} | {:15.10f} | {:>15s}".format(k, x_k, delta_str))
    print("-" * 50)
    print()


# ==========================
# ФУНКЦІЯ ДЛЯ ГРАФІКІВ
# ==========================
def build_plots(a, b, root_val):
    """
    Будує графіки: f(x) та її похідних.
    """
    try:
        # Налаштування стилю (безпечний варіант)
        plt.style.use('bmh')
    except:
        pass  # Якщо стиль не знайдено, використовуємо дефолтний

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Графік 1: Функція f(x) ---
    x_range = np.linspace(a - 0.5, b + 0.5, 400)
    y_range = target_function(x_range)

    ax1.plot(x_range, y_range, label='f(x)', color='blue', linewidth=2)
    ax1.axhline(0, color='black', linewidth=1)

    # Виділяємо робочий інтервал [5, 6]
    ax1.axvline(a, color='green', linestyle='--', label=f'[{a}, {b}]')
    ax1.axvline(b, color='green', linestyle='--')

    # Відмічаємо корінь
    ax1.plot(root_val, target_function(root_val), 'ro', markersize=8, label=f'Корінь')

    ax1.set_title("Локалізація кореня", fontsize=14)
    ax1.set_xlabel("x")
    ax1.set_ylabel("f(x)")
    ax1.legend()
    ax1.grid(True)

    # --- Графік 2: Похідні ---
    x_interval = np.linspace(a, b, 200)
    y_prime = target_function_derivative(x_interval)
    y_double_prime = target_function_second_derivative(x_interval)

    ax2.plot(x_interval, y_prime, label="f'(x)", color='purple')
    ax2.plot(x_interval, y_double_prime, label="f''(x)", color='orange', linestyle='-.')

    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_title("Похідні на проміжку ізоляції", fontsize=14)
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()


# ==========================
# МЕТОД РЕЛАКСАЦІЇ
# ==========================

def relaxation_parameters(a, b):
    m1 = min_abs_on_interval(target_function_derivative, a, b)
    M1 = max_abs_on_interval(target_function_derivative, a, b)
    tau_opt = 2.0 / (M1 + m1)
    q0 = (M1 - m1) / (M1 + m1)
    return m1, M1, tau_opt, q0


def iterate_relaxation(x0, eps, tau, nmax):
    values = [x0]
    for _ in range(nmax):
        x_next = values[-1] - tau * target_function(values[-1])
        values.append(x_next)
        if abs(values[-1] - values[-2]) <= eps:
            break
    return values


def relaxation_apriori_steps(q0, x0, root, eps):
    if not (0.0 < q0 < 1.0):
        return None
    distance = abs(x0 - root)
    if distance <= 0.0:
        return 0
    n_real = math.log(distance / eps) / math.log(1.0 / q0)
    return int(math.ceil(n_real) + 1)


# ==========================
# МЕТОД НЬЮТОНА
# ==========================

def newton_parameters(a, b):
    m1 = min_abs_on_interval(target_function_derivative, a, b)
    M2 = max_abs_on_interval(target_function_second_derivative, a, b)
    L = M2 / (2.0 * m1)
    return m1, M2, L


def iterate_newton(x0, eps, nmax):
    values = [x0]
    for _ in range(nmax):
        x_current = values[-1]
        f_value = target_function(x_current)
        f_derivative = target_function_derivative(x_current)
        if f_derivative == 0.0:
            break
        x_next = x_current - f_value / f_derivative
        values.append(x_next)
        if abs(values[-1] - values[-2]) <= eps:
            break
    return values


def newton_apriori_steps(L, x0, root, eps, max_steps=20):
    if L <= 0.0:
        return None
    error = abs(x0 - root)
    steps = 0
    while error > eps and steps < max_steps:
        error = L * error * error
        steps += 1
    return steps


# ==========================
# ГОЛОВНА ФУНКЦІЯ (MAIN)
# ==========================

if __name__ == "__main__":
    # 1. Еталонний корінь
    coeffs = [1.0, -5.74, 0.0, 8.18, -3.48]
    roots = np.roots(coeffs)
    positive_real_roots = [
        float(r.real) for r in roots if abs(r.imag) < 1e-8 and r.real > 0.0
    ]
    largest_root = max(positive_real_roots)

    print("=== Nonlinear equation solving ===")
    print(f"Equation root (reference) ≈ {largest_root:.10f}\n")

    # 2. Метод релаксації
    print("=== Relaxation method ===")
    m1_r, M1_r, tau_opt, q_r = relaxation_parameters(interval_start, interval_end)
    print(f"tau = {tau_opt:.6f}, q = {q_r:.6f}")

    # Апріорна оцінка (Релаксація)
    n_apr_rel = relaxation_apriori_steps(q_r, initial_guess, largest_root, tolerance)
    if n_apr_rel is not None:
        print(f"Apriori estimate: n >= {n_apr_rel}")

    values_relax = iterate_relaxation(initial_guess, tolerance, tau_opt, max_iterations)
    print_iterations_table(values_relax, "Relaxation iterations table")
    print(f"Result: {values_relax[-1]:.10f}\n")

    # 3. Метод Ньютона
    print("=== Newton method ===")
    m1_n, M2_n, L_n = newton_parameters(interval_start, interval_end)

    # Апріорна оцінка (Ньютон)
    n_apr_newt = newton_apriori_steps(L_n, initial_guess, largest_root, tolerance)
    if n_apr_newt is not None:
        print(f"Apriori estimate: n >= {n_apr_newt}")
    else:
        print("Apriori estimate not available.")

    values_newton = iterate_newton(initial_guess, tolerance, max_iterations)
    print_iterations_table(values_newton, "Newton iterations table")
    newton_root = values_newton[-1]
    print(f"Result: {newton_root:.10f}\n")

    # 4. Побудова графіків
    print("Building plots...")
    build_plots(interval_start, interval_end, newton_root)