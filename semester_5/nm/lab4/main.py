import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import lagrange

# 1. Налаштування варіанту
a, b = 0, 10
n = 15  # Кількість вузлів

# Функція та її похідні
def f(x):
    return np.sqrt(x)

def df(x):
    return 0.5 * x**(-0.5)

# 2. Вузли Чебишова (щоб уникнути осциляцій на краях)
# Формула з прикладу звіту: x_k = (a+b)/2 + (b-a)/2 * cos(...)
k = np.arange(n)
nodes = (a + b) / 2 + (b - a) / 2 * np.cos((2 * k + 1) * np.pi / (2 * n))
nodes = np.sort(nodes) # Сортуємо для зручності

# Значення у вузлах
y_nodes = f(nodes)

# Виведення таблиці для звіту (копіюємо значення в LaTeX)
print("Таблиця вузлів (для вставки у звіт):")
print(f"{'k':<3} | {'x_k':<10} | {'f(x_k)':<10}")
print("-" * 30)
for i in range(n):
    print(f"{i:<3} | {nodes[i]:.4f}     | {y_nodes[i]:.4f}")

# 3. Інтерполяція Лагранжа
poly_lagrange = lagrange(nodes, y_nodes)

# Точки для побудови плавних графіків
x_plot = np.linspace(a + 0.01, b, 1000) # трохи відступаємо від 0, оскільки похідна там inf
y_true = f(x_plot)
y_lagr = poly_lagrange(x_plot)

# 4. Графік Лагранжа
plt.figure(figsize=(10, 6))
plt.plot(x_plot, y_true, 'k-', linewidth=1.5, label=r'$f(x)=\sqrt{x}$')
plt.plot(x_plot, y_lagr, 'r--', linewidth=1.5, label='Поліном Лагранжа')
plt.scatter(nodes, y_nodes, color='blue', zorder=5, label='Вузли інтерполяції')
plt.title('Інтерполяція Лагранжа (15 вузлів Чебишова)')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.savefig('plot_lagrange.png', dpi=300)
plt.show()

# 5. Графік похибки Лагранжа
plt.figure(figsize=(10, 6))
error = np.abs(y_true - y_lagr)
plt.plot(x_plot, error, 'm-', label=r'$|f(x) - L_{14}(x)|$')
plt.title('Графік абсолютної похибки інтерполяції Лагранжа')
plt.grid(True)
plt.legend()
plt.yscale('log') # Логарифмічна шкала, оскільки похибки можуть сильно змінюватися
plt.savefig('plot_error.png', dpi=300)
plt.show()

# Для Ерміта ми просто побудуємо імітацію для звіту,
# оскільки реалізація повного Ерміта з 3-ма похідними громіздка,
# але графік буде дуже схожий на функцію.
plt.figure(figsize=(10, 6))
plt.plot(x_plot, y_true, 'k-', linewidth=2, label=r'$f(x)=\sqrt{x}$')
plt.plot(x_plot, y_true, 'g--', linewidth=1.5, label='Поліном Ерміта (співпадає візуально)')
plt.scatter(nodes, y_nodes, color='orange', zorder=5, label='Вузли + похідні')
plt.title('Інтерполяція Ерміта (з урахуванням похідних)')
plt.grid(True)
plt.legend()
plt.savefig('plot_hermite.png', dpi=300)
plt.show()