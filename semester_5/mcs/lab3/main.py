import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Функція для зчитування експериментальних даних
# ============================================================

exp_data = np.loadtxt("y4.txt")  # 4 рядки, N точок

# ============================================================
# Відомі параметри моделі
# ============================================================

c1 = 0.14
c2 = 0.3
c3 = 0.2
m2 = 28.0

# Початкове наближення параметрів β = (c4, m1, m3)
beta0 = np.array([0.1, 13.0, 23.0])

# Часовий інтервал
t0 = 0.0
tk = 50.0
dt = 0.2
time = np.arange(t0, tk + dt, dt)
N = len(time)

# ============================================================
# Матриця A(β)
# ============================================================

def build_A(beta):
    c4, m1, m3 = beta

    A = np.array([
        [0,          1,                     0,         0,                     0,         0],
        [-(c2 + c1)/m1, 0,                 c2/m1,      0,                     0,         0],
        [0,          0,                     0,         1,                     0,         0],
        [c2/m2,      0, -(c2 + c3)/m2,      0,         c3/m2,     0],
        [0,          0,                     0,         0,                     0,         1],
        [0,          0,                     c3/m3,     0, -(c3 + c4)/m3,      0]
    ])

    return A

# ============================================================
# Похідні ∂(Ay)/∂β
# Вони входять у систему чутливості dU/dt = A U + (∂A/∂β) y
# ============================================================

def dA_dBeta(beta):
    c4, m1, m3 = beta

    # dA/dc4
    dA_dc4 = np.zeros((6, 6))
    dA_dc4[5, 4] = -1.0 / m3

    # dA/dm1
    dA_dm1 = np.zeros((6, 6))
    dA_dm1[1, 0] = (c1 + c2) / (m1**2)
    dA_dm1[1, 2] = -c2 / (m1**2)

    # dA/dm3
    dA_dm3 = np.zeros((6, 6))
    dA_dm3[5, 4] = (c3 + c4) / (m3**2)
    dA_dm3[5, 2] = -c3 / (m3**2)

    return [dA_dc4, dA_dm1, dA_dm3]

# ============================================================
# RK4 для dy/dt = A y
# ============================================================

def rk4_step(y, beta, dt):
    A = build_A(beta)

    k1 = A @ y
    k2 = A @ (y + dt * k1 / 2)
    k3 = A @ (y + dt * k2 / 2)
    k4 = A @ (y + dt * k3)

    return y + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)

# ============================================================
# Чисельне інтегрування чутливості dU/dt = A U + Σ (dA/db_i) y
# ============================================================

def rk4_step_U(U, y, beta, dt):
    A = build_A(beta)
    dA = dA_dBeta(beta)

    def F(Uloc, yloc):
        S = np.zeros_like(Uloc)
        for i in range(3):
            S[:, i] = dA[i] @ yloc
        return A @ Uloc + S

    k1_U = F(U, y)
    k2_U = F(U + dt*k1_U/2, y)
    k3_U = F(U + dt*k2_U/2, y)
    k4_U = F(U + dt*k3_U, y)

    return U + (dt/6)*(k1_U + 2*k2_U + 2*k3_U + k4_U)

# ============================================================
# Функція якості для одного ряду
# ============================================================

def compute_cost(exp_signal, model_signal):
    return np.sum((exp_signal - model_signal)**2) * dt

# ============================================================
# Оцінка Δβ
# ============================================================

def compute_delta_beta(exp_signal, Y, U_list):
    # Матриця інтегралів ∫ Uᵀ U dt
    M = np.zeros((3, 3))
    b = np.zeros(3)

    for k in range(N):
        U = U_list[k]
        y_diff = exp_signal[k] - Y[k, 4]  # беремо координату y5 (3-тя маса)

        M += (U.T @ U) * dt
        b += (U.T @ np.array([0, 0, 0, 0, y_diff, 0])) * dt

    # Проверка на сингулярность матрицы
    if np.linalg.det(M) == 0:
        print("Матрица M сингулярна, выполняется регуляризация.")
        # Регуляризация с добавлением маленького значения на диагонали
        M += np.eye(3) * 1e-6

    return np.linalg.solve(M, b)


# ============================================================
# Повний прогін для одного спостереження
# ============================================================

def run_one_observation(exp_signal, beta_initial):
    beta = beta_initial.copy()

    y = np.zeros(6)
    U = np.zeros((6, 3))

    Y = np.zeros((N, 6))
    U_list = []

    for k in range(N):
        Y[k] = y
        U_list.append(U.copy())

        y = rk4_step(y, beta, dt)
        U = rk4_step_U(U, y, beta, dt)

    I = compute_cost(exp_signal, Y[:, 4])

    dB = compute_delta_beta(exp_signal, Y, U_list)

    return I, dB, Y

# ============================================================
# ТЕСТ ВСІХ 4 РЯДКІВ
# ============================================================

results = []
for i in range(4):
    exp_signal = exp_data[i]
    I, dB, Y = run_one_observation(exp_signal, beta0)
    results.append((I, dB, i+1))

# Вибираємо найкращий варіант
best = min(results, key=lambda x: x[0])

print(f"НАЙКРАЩИЙ РЯДОК СПОСТЕРЕЖЕНЬ: {best[2]}")
print(f"Функція якості: {best[0]}")
print(f"Δβ: {best[1]}")

import matplotlib.pyplot as plt

# ============================================================
# Графики для каждого из 4 рядов
# ============================================================

def plot_comparison(exp_signal, Y, row_index):
    plt.figure(figsize=(10, 6))
    plt.plot(time, exp_signal, label=f"Спостереження (ряд {row_index})", color='b')
    plt.plot(time, Y[:, 4], label=f"Модель (ряд {row_index})", color='r', linestyle='--')
    plt.xlabel('Час (s)')
    plt.ylabel('Зміщення (y)')
    plt.title(f'Порівняння сигналу для рядка {row_index}')
    plt.legend()
    plt.grid(True)
    plt.show()

# Проводимо порівняння для кожного ряду
for i in range(4):
    exp_signal = exp_data[i]
    I, dB, Y = run_one_observation(exp_signal, beta0)
    plot_comparison(exp_signal, Y, i+1)
