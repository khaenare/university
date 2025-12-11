import numpy as np
import matplotlib.pyplot as plt

# --- ВХІДНІ ДАНІ (Варіант: f(x)=sqrt(x), 15 вузлів Чебишева на [0, 10]) ---
x_nodes = np.array([0.0274, 0.2447, 0.6699, 1.2843, 2.0611, 2.9663, 3.9604, 5.0000,
                    6.0396, 7.0337, 7.9389, 8.7157, 9.3301, 9.7553, 9.9726])
y_nodes = np.array([0.1655, 0.4947, 0.8185, 1.1333, 1.4356, 1.7223, 1.9901, 2.2361,
                    2.4576, 2.6521, 2.8176, 2.9522, 3.0545, 3.1233, 3.1579])


def f_exact(x):
    return np.sqrt(x)


def df_exact(x):
    return 0.5 / np.sqrt(x)


def d2f_exact(x):
    return -0.25 / (x ** 1.5)


# --- МЕТОДИ ОБЧИСЛЕННЯ ---

def solve_tridiagonal(A, b):
    """Метод прогонки для розв'язання СЛАР Ax=b."""
    n = len(b)
    alpha = np.zeros(n)
    beta = np.zeros(n)

    # Прямий хід
    alpha[0] = -A[0, 1] / A[0, 0]
    beta[0] = b[0] / A[0, 0]

    for i in range(1, n - 1):
        denom = A[i, i] + A[i, i - 1] * alpha[i - 1]
        alpha[i] = -A[i, i + 1] / denom
        beta[i] = (b[i] - A[i, i - 1] * beta[i - 1]) / denom

    # Останній елемент прямого ходу
    denom = A[n - 1, n - 1] + A[n - 1, n - 2] * alpha[n - 2]
    beta[n - 1] = (b[n - 1] - A[n - 1, n - 2] * beta[n - 2]) / denom

    # Зворотний хід
    x = np.zeros(n)
    x[n - 1] = beta[n - 1]
    for i in range(n - 2, -1, -1):
        x[i] = alpha[i] * x[i + 1] + beta[i]

    return x


def build_natural_spline(x, y):
    """
    Побудова природного кубічного сплайна.
    Повертає коефіцієнти a, b, c, d для кожного інтервалу.
    S_i(x) = a_i + b_i(x-x_i) + c_i(x-x_i)^2 + d_i(x-x_i)^3
    """
    n = len(x) - 1  # кількість інтервалів
    h = np.diff(x)  # кроки сітки

    # Побудова СЛАР для c_i (моменти / 2)
    # Розмір внутрішньої системи n-1 (від 1 до n-1)
    # Але для зручності зробимо для всіх c_0...c_n, де c_0=c_n=0

    dim = n - 1
    A = np.zeros((dim, dim))
    rhs = np.zeros(dim)

    for i in range(dim):
        # i тут відповідає вузлу x_{i+1}
        # Рівняння: h_i * c_i + 2(h_i + h_{i+1}) * c_{i+1} + h_{i+1} * c_{i+2} = ...
        # В індексах матриці (0..dim-1):

        hi = h[i]
        hi_next = h[i + 1]

        A[i, i] = 2 * (hi + hi_next)
        if i > 0:
            A[i, i - 1] = hi
        if i < dim - 1:
            A[i, i + 1] = hi_next

        # Права частина
        rhs[i] = 6 * ((y[i + 2] - y[i + 1]) / hi_next - (y[i + 1] - y[i]) / hi)

    # Розв'язок системи для других похідних (моментів M)
    M_internal = solve_tridiagonal(A, rhs)

    M = np.zeros(n + 1)
    M[1:-1] = M_internal
    # M[0] = 0, M[n] = 0 - умови природного сплайна

    # Перерахунок у коефіцієнти полінома
    # a_i = y_i
    # c_i = M_i / 2
    # d_i = (M_{i+1} - M_i) / (6 * h_i)
    # b_i = (y_{i+1} - y_i)/h_i - h_i * (2*M_i + M_{i+1}) / 6

    a = y[:-1]
    b = np.zeros(n)
    c = np.zeros(n)
    d = np.zeros(n)

    for i in range(n):
        c[i] = M[i] / 2.0
        d[i] = (M[i + 1] - M[i]) / (6.0 * h[i])
        b[i] = (y[i + 1] - y[i]) / h[i] - h[i] * (2.0 * M[i] + M[i + 1]) / 6.0

    return a, b, c, d


# --- ВИКОНАННЯ ---
a, b, c, d = build_natural_spline(x_nodes, y_nodes)

# --- ГЕНЕРАЦІЯ LATEX ВИВОДУ (ДЛЯ ЗВІТУ) ---
print("-" * 30)
print("ВСТАВИТИ В LATEX (ТАБЛИЦЯ КОЕФІЦІЄНТІВ):")
print(r"\begin{longtable}{|c|c|c|c|c|}")
print(r"\hline")
print(r"$i$ & $a_i$ & $b_i$ & $c_i$ & $d_i$ \\ \hline")
for i in range(len(a)):
    print(f"{i} & {a[i]:.5f} & {b[i]:.5f} & {c[i]:.5f} & {d[i]:.5f} \\\\ \\hline")
print(r"\end{longtable}")
print("-" * 30)

print("ВСТАВИТИ В LATEX (ЯВНИЙ ВИГЛЯД СПЛАЙНІВ):")
print(r"\begin{itemize}")
for i in range(len(a)):
    # Формування рядка з урахуванням знаків
    sb = "+" if b[i] >= 0 else "-"
    sc = "+" if c[i] >= 0 else "-"
    sd = "+" if d[i] >= 0 else "-"

    eq = (f"S_{{{i}}}(x) = {a[i]:.4f} {sb} {abs(b[i]):.4f}(x - {x_nodes[i]:.4f}) "
          f"{sc} {abs(c[i]):.4f}(x - {x_nodes[i]:.4f})^2 "
          f"{sd} {abs(d[i]):.4f}(x - {x_nodes[i]:.4f})^3")

    print(r"\item " + f"На відрізку $[{x_nodes[i]:.4f}; {x_nodes[i + 1]:.4f}]$:\n" +
          r"$$" + eq + r"$$")
print(r"\end{itemize}")
print("-" * 30)

# --- ПОБУДОВА ГРАФІКІВ ---
x_dense = np.linspace(x_nodes[0], x_nodes[-1], 1000)
y_spline = np.zeros_like(x_dense)
y_spline_d1 = np.zeros_like(x_dense)
y_spline_d2 = np.zeros_like(x_dense)

for k, x_val in enumerate(x_dense):
    # Знаходимо потрібний інтервал
    idx = np.searchsorted(x_nodes, x_val) - 1
    if idx < 0: idx = 0
    if idx >= len(a): idx = len(a) - 1

    dx = x_val - x_nodes[idx]
    y_spline[k] = a[idx] + b[idx] * dx + c[idx] * dx ** 2 + d[idx] * dx ** 3
    y_spline_d1[k] = b[idx] + 2 * c[idx] * dx + 3 * d[idx] * dx ** 2
    y_spline_d2[k] = 2 * c[idx] + 6 * d[idx] * dx

# Точні значення
y_true = f_exact(x_dense)
y_true_d1 = df_exact(x_dense)
y_true_d2 = d2f_exact(x_dense)

# Похибки
err = np.abs(y_true - y_spline)
err_d1 = np.abs(y_true_d1 - y_spline_d1)
err_d2 = np.abs(y_true_d2 - y_spline_d2)

# Компоновка графіків (як у прикладі студента 1)
plt.figure(figsize=(14, 10))

# 1. Функція
plt.subplot(2, 2, 1)
plt.plot(x_dense, y_true, 'b-', label=r'$f(x)=\sqrt{x}$')
plt.plot(x_dense, y_spline, 'r--', label=r'$S(x)$')
plt.scatter(x_nodes, y_nodes, color='black', s=20, zorder=5, label='Вузли')
plt.title("Функція та сплайн")
plt.legend()
plt.grid(True)

# 2. Перша похідна
plt.subplot(2, 2, 2)
plt.plot(x_dense, y_true_d1, 'b-', label=r"$f'(x)$")
plt.plot(x_dense, y_spline_d1, 'r--', label=r"$S'(x)$")
plt.title("Перша похідна")
plt.legend()
plt.grid(True)

# 3. Друга похідна
plt.subplot(2, 2, 3)
plt.plot(x_dense, y_true_d2, 'b-', label=r"$f''(x)$")
plt.plot(x_dense, y_spline_d2, 'r--', label=r"$S''(x)$")
plt.title("Друга похідна")
plt.legend()
plt.grid(True)

# 4. Похибки (логарифмічна шкала для кращої видимості)
plt.subplot(2, 2, 4)
plt.plot(x_dense, err, label=r"$|f - S|$")
plt.plot(x_dense, err_d1, label=r"$|f' - S'|$")
plt.plot(x_dense, err_d2, label=r"$|f'' - S''|$")
plt.title("Абсолютні похибки")
plt.yscale('log')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("spline_graph.png", dpi=300)
print("Графік збережено як spline_graph.png")
plt.show()
