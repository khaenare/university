import numpy as np
import csv
from datetime import datetime
import time
import matplotlib.pyplot as plt
import os


def make_logs_folder():
    """Створює папку logs, якщо її ще немає."""
    if not os.path.exists("logs"):
        os.makedirs("logs")


def load_observations(filename):
    """
    Зчитує виміряні дані з файлу.
    Передбачається, що файл містить рядки значень (по змінних).
    Повертає масив розмірністю (N_часу, n_змінних).
    """
    with open(filename, "r") as f:
        rows = []
        for line in f:
            # Пропускаємо порожні рядки або рядки з метаданими, якщо такі є
            clean_line = line.strip()
            if not clean_line:
                continue
            # Якщо у файлі є текстові мітки типу , їх варто видалити вручну перед запуском,
            # або ж скрипт спробує розпарсити числа.
            try:
                values = [float(v) for v in clean_line.split()]
                rows.append(values)
            except ValueError:
                continue

    return np.array(rows).T


def numerical_jacobian(y_vec_func, beta_names, beta_dict, delta=1e-5):
    """
    Обчислює чисельну похідну d(Ay)/d_beta методом центральної різниці.
    Повертає матрицю розміру (число станів x кількість параметрів).
    """
    y0 = y_vec_func(beta_dict)
    n_state = len(y0)
    n_beta = len(beta_names)
    jac = np.zeros((n_state, n_beta))

    for j, name in enumerate(beta_names):
        original = beta_dict[name]

        beta_dict[name] = original + delta
        y_plus = y_vec_func(beta_dict)

        beta_dict[name] = original - delta
        y_minus = y_vec_func(beta_dict)

        beta_dict[name] = original  # відновлення параметра

        jac[:, j] = (y_plus - y_minus) / (2.0 * delta)

    return jac


def rk4_step_sensitivity(a_matrix, source_term, u_current, dt):
    """Крок методу Рунге-Кутти 4-го порядку для рівняння чутливостей."""
    b_vec = np.array(source_term)
    k1 = dt * (a_matrix @ u_current + b_vec)
    k2 = dt * (a_matrix @ (u_current + 0.5 * k1) + b_vec)
    k3 = dt * (a_matrix @ (u_current + 0.5 * k2) + b_vec)
    k4 = dt * (a_matrix @ (u_current + k3) + b_vec)
    return u_current + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


def rk4_step_state(a_matrix, y_current, dt):
    """Крок Рунге-Кутти для основної системи станів."""
    k1 = dt * (a_matrix @ y_current)
    k2 = dt * (a_matrix @ (y_current + 0.5 * k1))
    k3 = dt * (a_matrix @ (y_current + 0.5 * k2))
    k4 = dt * (a_matrix @ (y_current + k3))
    return y_current + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


def build_system_matrix(params):
    """Формує матрицю A (6x6) для моделі трьох мас та чотирьох пружин."""
    c1 = params["c1"]
    c2 = params["c2"]
    c3 = params["c3"]
    c4 = params["c4"]
    m1 = params["m1"]
    m2 = params["m2"]
    m3 = params["m3"]

    # Рівняння руху:
    # y1' = y2
    # y2' = (-(c1+c2)*y1 + c2*y3) / m1
    # y3' = y4
    # y4' = (c2*y1 - (c2+c3)*y3 + c3*y5) / m2
    # y5' = y6
    # y6' = (c3*y3 - (c3+c4)*y5) / m3

    return np.array([
        [0, 1, 0, 0, 0, 0],
        [-(c1 + c2) / m1, 0, c2 / m1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [c2 / m2, 0, -(c2 + c3) / m2, 0, c3 / m2, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0, c3 / m3, 0, -(c3 + c4) / m3, 0],
    ])


def simulate_model(params, y0, t_grid, dt=0.2):
    """Чисельно інтегрує модель з параметрами params по часовій сітці."""
    A = build_system_matrix(params)
    y = np.zeros((len(t_grid), len(y0)))
    y[0] = y0

    y_curr = y0.copy()
    for k in range(1, len(t_grid)):
        y_curr = rk4_step_state(A, y_curr, dt)
        y[k] = y_curr

    return y


def identify_parameters(meas_data,
                        fixed_params,
                        beta_names,
                        beta_initial,
                        eps,
                        dt=0.2,
                        max_iterations=50):
    """
    Метод параметричної ідентифікації через функції чутливості.
    Ітераційно уточнює параметри beta до мінімуму функції якості I(beta).
    """
    make_logs_folder()
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Створення csv-файлу з логами
    log_csv = os.path.join("logs", f"approximation_log_{timestamp}.csv")
    with open(log_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["iteration"] + beta_names + ["cost"])

    beta_dict = beta_initial.copy()
    n_state = meas_data.shape[1]
    n_beta = len(beta_names)

    iteration = 0

    # Функція Ay для чисельної похідної
    def ay_of_beta(beta_dict_local, y_vec):
        params_local = {**fixed_params, **beta_dict_local}
        A_local = build_system_matrix(params_local)
        return A_local @ y_vec

    while iteration < max_iterations:

        # Матриця A з поточними beta
        params_current = {**fixed_params, **beta_dict}
        A = build_system_matrix(params_current)

        # Матриця чутливостей, інтегральні складові та показник якості
        U = np.zeros((n_state, n_beta))
        gram_matrix = np.zeros((n_beta, n_beta))
        rhs_vector = np.zeros(n_beta)
        cost_value = 0.0

        # Початковий стан моделі беремо з першого виміру
        y_model = meas_data[0].copy()

        for k in range(meas_data.shape[0]):
            y_meas = meas_data[k]

            # Локальна функція Ay(beta)
            def local_ay(beta_tmp):
                return ay_of_beta(beta_tmp, y_model)

            # d(Ay)/d_beta
            src = numerical_jacobian(local_ay, beta_names, beta_dict)

            # Накопичення інтегралів (матриця Грама та права частина)
            gram_matrix += U.T @ U
            rhs_vector += U.T @ (y_meas - y_model)

            diff = y_meas - y_model
            cost_value += diff @ diff

            # Кроки Рунге-Кутти для U та y
            U = rk4_step_sensitivity(A, src, U, dt)
            y_model = rk4_step_state(A, y_model, dt)

        # Множимо на dt — чисельне інтегрування
        gram_matrix *= dt
        rhs_vector *= dt
        cost_value *= dt

        # Лог у файл
        with open(log_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([iteration] +
                            [beta_dict[name] for name in beta_names] +
                            [cost_value])

        # Вивід у консоль для контролю
        print(f"Iter {iteration}: Cost {cost_value:.4e}, Beta {[round(beta_dict[n], 4) for n in beta_names]}")

        # Розв'язання системи лінійних рівнянь для знаходження поправки delta_beta
        # Regularization (опціонально, якщо матриця погано обумовлена, можна додати + eye*1e-8)
        try:
            delta_beta = np.linalg.inv(gram_matrix) @ rhs_vector
        except np.linalg.LinAlgError:
            print("Singular matrix encountered.")
            break

        for j, name in enumerate(beta_names):
            beta_dict[name] += delta_beta[j]

        # Умова зупинки
        if cost_value < eps or np.linalg.norm(delta_beta) < np.sqrt(eps):
            break

        iteration += 1

    total_time = time.time() - start_time

    # Запис фінального резюме
    summary_txt = os.path.join("logs", f"summary_{timestamp}.txt")
    with open(summary_txt, "w") as f:
        f.write("Parameter Identification Results (Variant 1)\n")
        f.write("--------------------------------\n\n")
        f.write("Identified parameters:\n")
        for name in beta_names:
            f.write(f"{name}: {beta_dict[name]:.6f}\n")
        f.write(f"\nCost function: {cost_value:.6e}\n")
        f.write(f"Iterations: {iteration}\n")
        f.write(f"Execution time: {total_time:.2f} s\n")

    return beta_dict, iteration, total_time, cost_value


def plot_comparison(measured, simulated, t_grid, filename_prefix):
    """Будує графіки моделі та вимірів для всіх шести компонент."""
    make_logs_folder()
    # Згідно з моделлю: y1, v1, y3, v3, y5, v5
    labels = ["y1 (pos)", "y1 (vel)", "y3 (pos)", "y3 (vel)", "y5 (pos)", "y5 (vel)"]

    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    axes = axes.flatten()

    for i, (ax, lbl) in enumerate(zip(axes, labels)):
        # Відображаємо виміряні точки
        if i < measured.shape[1]:
            ax.plot(t_grid, measured[:, i], "r.", label="measured", markersize=3)
        # Відображаємо модельну криву
        ax.plot(t_grid, simulated[:, i], "b-", label="model")

        ax.set_title(lbl)
        ax.set_xlabel("t")
        ax.grid(True)
        ax.legend()

    plt.tight_layout()
    out_path = os.path.join("logs", f"{filename_prefix}_comparison.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Graph saved to {out_path}")


def main():
    make_logs_folder()

    # 1. Зчитуємо вимірювання (Варіант 1, файл y4.txt)
    # Переконайтеся, що файл y4.txt знаходиться у тій же папці
    filename = "y4.txt"
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return

    data = load_observations(filename)

    # Перевірка розмірності даних
    if data.shape[1] != 6:
        print(f"Warning: Expected 6 state variables, got {data.shape[1]}")

    dt = 0.2
    # Створюємо часову сітку на основі кількості точок у файлі
    t_grid = np.arange(0.0, dt * data.shape[0], dt)

    # 2. Відомі параметри (Варіант 1)
    # c1 = 0.14, c2 = 0.3, c3 = 0.2, m2 = 28
    known_params = {"c1": 0.14, "c2": 0.3, "c3": 0.2, "m2": 28.0}

    # 3. Параметри, які треба оцінити (Варіант 1)
    # beta = (c4, m1, m3)
    beta_names = ["c4", "m1", "m3"]

    # Початкове наближення: beta0 = (0.1, 13, 23)
    beta_initial = {"c4": 0.1, "m1": 13.0, "m3": 23.0}

    print("Starting identification for Variant 1...")
    print(f"Known: {known_params}")
    print(f"Initial guess: {beta_initial}")

    # 4. Запуск ідентифікації параметрів
    identified_beta, iters, elapsed, cost = identify_parameters(
        meas_data=data,
        fixed_params=known_params,
        beta_names=beta_names,
        beta_initial=beta_initial,
        eps=1e-6,
        dt=dt,
        max_iterations=50,
    )

    # 5. Симуляція моделі з оціненими параметрами
    final_params = {**known_params, **identified_beta}
    model_solution = simulate_model(final_params, data[0], t_grid, dt=dt)

    # 6. Вивід результатів у консоль
    print("\nParameter Identification Results")
    print("--------------------------------")
    print("Initial beta:")
    for name in beta_names:
        print(f"  {name}: {beta_initial[name]:.6f}")

    print("\nEstimated beta:")
    for name in beta_names:
        print(f"  {name}: {identified_beta[name]:.6f}")

    print("\nMetrics:")
    print(f"  Cost function I(beta): {cost:.6e}")
    print(f"  Iterations: {iters}")
    print(f"  Time: {elapsed:.2f} s")

    # 7. Побудова графіків
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_comparison(data, model_solution, t_grid, f"variant1_{timestamp}")

    print("\nPlots and logs saved in 'logs' folder.")


if __name__ == "__main__":
    main()