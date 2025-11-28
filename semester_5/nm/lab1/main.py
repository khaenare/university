import math
import numpy as np

# ==========================
# ПАРАМЕТРИ ЗАДАЧІ
# ==========================
# interval_start, interval_end - початковий проміжок [a, b], на якому
# шукаємо найбільший додатній корінь.
# initial_guess - початкове наближення x0 (однакове для обох методів).
# tolerance - задана точність epsilon.
# max_iterations - максимальна кількість ітерацій на випадок, якщо
# метод з якихось причин не збігається досить швидко.
interval_start = 5.0  # a
interval_end = 6.0    # b
initial_guess = 5.5   # x0
tolerance = 1e-4      # epsilon
max_iterations = 100


# ==========================
# ЦІЛЬОВА ФУНКЦІЯ ТА ПОХІДНІ
# ==========================

def target_function(x):
    """
    Нелінійне рівняння:
    f(x) = x^4 - 5.74 x^3 + 8.18 x - 3.48.
    Корені цього рівняння ми й шукаємо.
    """
    return x ** 4 - 5.74 * x ** 3 + 8.18 * x - 3.48


def target_function_derivative(x):
    """
    Перша похідна:
    f'(x) = 4 x^3 - 17.22 x^2 + 8.18.
    Використовується:
      - для оцінки m1, M1 в методі релаксації,
      - в методі Ньютона в знаменнику f'(x_n).
    """
    return 4.0 * x ** 3 - 17.22 * x ** 2 + 8.18


def target_function_second_derivative(x):
    """
    Друга похідна:
    f''(x) = 12 x^2 - 34.44 x.
    Використовується в теоретичній оцінці збіжності методу Ньютона
    (константа L = M2 / (2 m1)).
    """
    return 12.0 * x ** 2 - 34.44 * x


# ==========================
# ДОПОМІЖНІ ФУНКЦІЇ
# ==========================

def max_abs_on_interval(func, a, b, n_points=1000):
    """
    Обчислює max |func(x)| на відрізку [a, b].
    Реалізація проста:
      - беремо рівномірну сітку з n_points точок,
      - рахуємо значення func у всіх цих точках,
      - повертаємо максимум за модулем.
    Це потрібно, щоб оцінити M1 або M2 для похідних.
    """
    xs = np.linspace(a, b, n_points)
    values = np.abs(func(xs))
    return float(np.max(values))


def min_abs_on_interval(func, a, b, n_points=1000):
    """
    Обчислює min |func(x)| на відрізку [a, b].
    Аналог max_abs_on_interval, але беремо мінімум.
    Використовується для оцінки m1 = min |f'(x)|.
    """
    xs = np.linspace(a, b, n_points)
    values = np.abs(func(xs))
    return float(np.min(values))


def print_iterations_table(values, title):
    """
    Друкує таблицю ітерацій:
      k, x_k, Delta = |x_k - x_(k-1)|.
    Масив values містить послідовність наближень x_0, x_1, ..., x_n.
    Ця таблиця потім практично один-в-один переноситься в звіт.
    """
    print(title)
    print("-" * 50)
    print("{:>3s} | {:>15s} | {:>15s}".format("k", "x_k", "Delta"))
    print("-" * 50)
    for k, x_k in enumerate(values):
        if k == 0:
            # Для першого наближення немає попереднього, тому Delta = "-"
            delta_str = "-"
        else:
            delta = abs(values[k] - values[k - 1])
            delta_str = f"{delta:.10f}"
        print("{:3d} | {:15.10f} | {:>15s}".format(k, x_k, delta_str))
    print("-" * 50)
    print()


# ==========================
# МЕТОД РЕЛАКСАЦІЇ
# ==========================

def relaxation_parameters(a, b):
    """
    Обчислює параметри для методу релаксації на відрізку [a, b]:
      m1 = min_{[a,b]} |f'(x)|
      M1 = max_{[a,b]} |f'(x)|
      tau_opt = 2 / (M1 + m1)  - оптимальний крок релаксації
      q0 = (M1 - m1) / (M1 + m1) - оцінка коефіцієнта стиску
    Це повністю відповідає теорії, яку ти будеш описувати в розділі "Теорія".
    """
    m1 = min_abs_on_interval(target_function_derivative, a, b)
    M1 = max_abs_on_interval(target_function_derivative, a, b)
    tau_opt = 2.0 / (M1 + m1)
    q0 = (M1 - m1) / (M1 + m1)
    return m1, M1, tau_opt, q0


def iterate_relaxation(x0, eps, tau, nmax):
    """
    Виконує ітерації методу релаксації:
      x_{n+1} = x_n - tau * f(x_n).
    Параметри:
      x0     - початкове наближення,
      eps    - epsilon, умова зупинки по |x_n - x_(n-1)| <= eps,
      tau    - параметр релаксації (тут беремо tau_opt),
      nmax   - верхня межа кількості ітерацій (страховка).

    Повертає список всіх наближень values = [x0, x1, ..., x_n].
    """
    values = [x0]
    for _ in range(nmax):
        x_next = values[-1] - tau * target_function(values[-1])
        values.append(x_next)
        # Апостеріорний критерій збіжності:
        # якщо різниця між двома сусідніми наближеннями менша за eps,
        # зупиняємося.
        if abs(values[-1] - values[-2]) <= eps:
            break
    return values


def relaxation_apriori_steps(q0, x0, root, eps):
    """
    Апріорна оцінка кількості кроків для методу релаксації.
    Теоретична оцінка базується на нерівності:
      |x_n - x*| <= q0^n * |x_0 - x*|.

    Вирішуємо відносно n:
      q0^n <= eps / |x_0 - x*|
      n >= ln(|x_0 - x*| / eps) / ln(1 / q0).

    Параметри:
      q0   - коефіцієнт стиску (0 < q0 < 1),
      x0   - початкове наближення,
      root - "еталонний" корінь (ми його рахуємо окремо через np.roots),
      eps  - задана точність.

    Повертає ціле число n (округлене вгору), або None, якщо q0 не в (0, 1).
    """
    if not (0.0 < q0 < 1.0):
        return None
    distance = abs(x0 - root)
    if distance <= 0.0:
        # Випадок, коли x0 вже дорівнює кореню.
        return 0
    n_real = math.log(distance / eps) / math.log(1.0 / q0)
    # Додаємо +1, як у варіанті одногрупниці, для гарантованої оцінки.
    return int(math.ceil(n_real) + 1)


# ==========================
# МЕТОД НЬЮТОНА
# ==========================

def newton_parameters(a, b):
    """
    Обчислює параметри для теоретичної оцінки методу Ньютона на [a, b]:
      m1 = min_{[a,b]} |f'(x)|
      M2 = max_{[a,b]} |f''(x)|
      L  = M2 / (2 m1)
    Далі в теорії використовується нерівність:
      |x_{n+1} - x*| <= L * |x_n - x*|^2.
    """
    m1 = min_abs_on_interval(target_function_derivative, a, b)
    M2 = max_abs_on_interval(target_function_second_derivative, a, b)
    L = M2 / (2.0 * m1)
    return m1, M2, L


def iterate_newton(x0, eps, nmax):
    """
    Реалізація класичного методу Ньютона:
      x_{n+1} = x_n - f(x_n) / f'(x_n).

    Параметри:
      x0   - початкове наближення,
      eps  - epsilon, умова зупинки по |x_n - x_(n-1)| <= eps,
      nmax - максимальна кількість ітерацій.

    Повертає список наближень values = [x0, x1, ..., x_n].
    """
    values = [x0]
    for _ in range(nmax):
        x_current = values[-1]
        f_value = target_function(x_current)
        f_derivative = target_function_derivative(x_current)

        # Якщо f'(x_n) = 0, то формула Ньютона не визначена.
        # На практиці це означає, що метод "зламався".
        if f_derivative == 0.0:
            break

        x_next = x_current - f_value / f_derivative
        values.append(x_next)

        # Апостеріорний критерій:
        if abs(values[-1] - values[-2]) <= eps:
            break
    return values


def newton_apriori_steps(L, x0, root, eps, max_steps=20):
    """
    Апріорна оцінка кількості кроків для методу Ньютона.

    Маємо нерівність:
      |x_{n+1} - x*| <= L * |x_n - x*|^2.

    Для оцінки "вручну" робимо покрокову оцінку:
      E_0 = |x0 - x*|
      E_1 <= L * E_0^2
      E_2 <= L * E_1^2
      ...
    Поки E_k > eps, збільшуємо k. Якщо k перевищує max_steps,
    повертаємо це значення як грубу верхню оцінку.

    Параметри:
      L         - константа з теорії,
      x0        - початкове наближення,
      root      - "еталонний" корінь,
      eps       - задана точність,
      max_steps - максимальна кількість кроків для теоретичної оцінки.

    Повертає приблизну кількість кроків k, необхідних для досягнення eps.
    """
    if L <= 0.0:
        return None
    error = abs(x0 - root)
    steps = 0
    while error > eps and steps < max_steps:
        error = L * error * error
        steps += 1
    return steps


# ==========================
# ОСНОВНА ЧАСТИНА СКРИПТА
# ==========================

if __name__ == "__main__":
    # 1) Знаходимо всі корені многочлена за допомогою np.roots.
    #    Це робиться тільки для того, щоб мати "еталонне" значення
    #    найбільшого додатнього кореня (для оцінок і порівняння).
    coeffs = [1.0, -5.74, 0.0, 8.18, -3.48]
    roots = np.roots(coeffs)

    # Вибираємо тільки дійсні додатні корені.
    positive_real_roots = [
        float(r.real)
        for r in roots
        if abs(r.imag) < 1e-8 and r.real > 0.0
    ]
    largest_root = max(positive_real_roots)

    # Загальна інформація про задачу.
    print("=== Nonlinear equation solving ===")
    print("Equation: x^4 - 5.74 x^3 + 8.18 x - 3.48 = 0")
    print(f"Interval [a, b] = [{interval_start}, {interval_end}]")
    print(f"Initial guess x0 = {initial_guess}")
    print(f"Epsilon = {tolerance:.1e}")
    print(f"Largest positive root (reference) ≈ {largest_root:.10f}")
    print()

    # ------------------------------
    # МЕТОД РЕЛАКСАЦІЇ
    # ------------------------------
    m1_relax, M1_relax, tau_opt, q_relax = relaxation_parameters(
        interval_start, interval_end
    )

    print("=== Relaxation method ===")
    print(f"m1 = min|f'(x)| ≈ {m1_relax:.6f}")
    print(f"M1 = max|f'(x)| ≈ {M1_relax:.6f}")
    print(f"tau_opt = 2 / (M1 + m1) ≈ {tau_opt:.6f}")
    print(f"q0 = (M1 - m1) / (M1 + m1) ≈ {q_relax:.6f}")
    print(f"Stopping rule: |x_n - x_(n-1)| <= epsilon = {tolerance:.1e}")

    # Апріорна оцінка числа кроків.
    n_apriori_relax = relaxation_apriori_steps(
        q_relax, initial_guess, largest_root, tolerance
    )
    if n_apriori_relax is not None:
        print(f"Apriori estimate for number of iterations: n >= {n_apriori_relax}")
    else:
        print("Apriori estimate for relaxation is not available (q0 not in (0, 1)).")
    print()

    # Реальні ітерації методу релаксації.
    values_relax = iterate_relaxation(initial_guess, tolerance, tau_opt, max_iterations)
    print_iterations_table(values_relax, "Relaxation iterations table")
    relax_root = values_relax[-1]
    print(f"Relaxation method root ≈ {relax_root:.10f}")
    print(f"Number of iterations (actual) = {len(values_relax) - 1}")
    print()

    # ------------------------------
    # МЕТОД НЬЮТОНА
    # ------------------------------
    m1_newton, M2_newton, L_newton = newton_parameters(
        interval_start, interval_end
    )

    print("=== Newton method ===")
    print(f"m1 = min|f'(x)| ≈ {m1_newton:.6f}")
    print(f"M2 = max|f''(x)| ≈ {M2_newton:.6f}")
    print(f"L = M2 / (2 * m1) ≈ {L_newton:.6f}")
    print(f"Stopping rule: |x_n - x_(n-1)| <= epsilon = {tolerance:.1e}")

    # Апріорна оцінка числа кроків для Ньютона.
    n_apriori_newton = newton_apriori_steps(
        L_newton, initial_guess, largest_root, tolerance
    )
    if n_apriori_newton is not None:
        print(
            "Apriori estimate for number of iterations (Newton): "
            f"n >= {n_apriori_newton}"
        )
    else:
        print("Apriori estimate for Newton method is not available.")
    print()

    # Реальні ітерації методу Ньютона.
    values_newton = iterate_newton(initial_guess, tolerance, max_iterations)
    print_iterations_table(values_newton, "Newton iterations table")
    newton_root = values_newton[-1]
    print(f"Newton method root ≈ {newton_root:.10f}")
    print(f"Number of iterations (actual) = {len(values_newton) - 1}")
    print()

