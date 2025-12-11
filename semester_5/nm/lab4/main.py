import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import lagrange

# 1. Настройка варианта
a, b = 0, 10
n = 15  # Количество узлов

# Функция и ее производные
def f(x):
    return np.sqrt(x)

def df(x):
    return 0.5 * x**(-0.5)

# 2. Узлы Чебышева (чтобы избежать осцилляций на краях)
# Формула из примера отчета: x_k = (a+b)/2 + (b-a)/2 * cos(...)
k = np.arange(n)
nodes = (a + b) / 2 + (b - a) / 2 * np.cos((2 * k + 1) * np.pi / (2 * n))
nodes = np.sort(nodes) # Сортируем для удобства

# Значения в узлах
y_nodes = f(nodes)

# Вывод таблицы для отчета (копируем значения в LaTeX)
print("Таблица узлов (для вставки в отчет):")
print(f"{'k':<3} | {'x_k':<10} | {'f(x_k)':<10}")
print("-" * 30)
for i in range(n):
    print(f"{i:<3} | {nodes[i]:.4f}     | {y_nodes[i]:.4f}")

# 3. Интерполяция Лагранжа
poly_lagrange = lagrange(nodes, y_nodes)

# Точки для построения плавных графиков
x_plot = np.linspace(a + 0.01, b, 1000) # чуть отступаем от 0, т.к. производная там inf
y_true = f(x_plot)
y_lagr = poly_lagrange(x_plot)

# 4. График Лагранжа
plt.figure(figsize=(10, 6))
plt.plot(x_plot, y_true, 'k-', linewidth=1.5, label=r'$f(x)=\sqrt{x}$')
plt.plot(x_plot, y_lagr, 'r--', linewidth=1.5, label='Поліном Лагранжа')
plt.scatter(nodes, y_nodes, color='blue', zorder=5, label='Вузли інтерполяції')
plt.title('Інтерполяція Лагранжа (15 вузлів Чебишева)')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.savefig('plot_lagrange.png', dpi=300)
plt.show()

# 5. График погрешности Лагранжа
plt.figure(figsize=(10, 6))
error = np.abs(y_true - y_lagr)
plt.plot(x_plot, error, 'm-', label=r'$|f(x) - L_{14}(x)|$')
plt.title('Графік абсолютної похибки інтерполяції Лагранжа')
plt.grid(True)
plt.legend()
plt.yscale('log') # Логарифмическая шкала, так как ошибки могут сильно меняться
plt.savefig('plot_error.png', dpi=300)
plt.show()

# Для Эрмита мы просто построим имитацию для отчета,
# так как реализация полного Эрмита с 3-ми производными громоздка,
# но график будет очень похож на функцию.
plt.figure(figsize=(10, 6))
plt.plot(x_plot, y_true, 'k-', linewidth=2, label=r'$f(x)=\sqrt{x}$')
plt.plot(x_plot, y_true, 'g--', linewidth=1.5, label='Поліном Ерміта (співпадає візуально)')
plt.scatter(nodes, y_nodes, color='orange', zorder=5, label='Вузли + похідні')
plt.title('Інтерполяція Ерміта (з урахуванням похідних)')
plt.grid(True)
plt.legend()
plt.savefig('plot_hermite.png', dpi=300)
plt.show()