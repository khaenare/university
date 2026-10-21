import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Задача 1. Ізольована популяція, варіант 5
# dP/dt = 0.015 * P * (120 - P),  P(0) = 60 та P(0) = 180
r = 0.015
K = 120

# Стаціонарні точки: dP/dt = 0 => P = 0 і P = 120
# при 0 < P < 120 похідна додатна (популяція зростає), при P > 120 від'ємна (спадає)
# тобто P = 0 нестійка, P = 120 стійка
print("Стаціонарні точки: P = 0 (нестійка), P = 120 (стійка)")

# Розв'язок (відокремлення змінних, початкова умова P(0) = P0):
# P(t) = K*P0 / (P0 + (K - P0)*exp(-r*K*t))
def P(t, P0):
    return K * P0 / (P0 + (K - P0) * np.exp(-r * K * t))

# чисельність при t = 2
for P0 in (60, 180):
    print("P0 =", P0, " P(2) =", round(P(2, P0), 2))

# при t -> inf exp(-r*K*t) -> 0, тому P -> K = 120 в обох випадках
print("границя при t -> inf:", round(P(100, 60), 2), round(P(100, 180), 2))

# перевірка: розв'язуємо рівняння чисельно і порівнюємо з формулою
for P0 in (60, 180):
    sol = solve_ivp(lambda t, p: r * p * (K - p), [0, 2], [P0], rtol=1e-10)
    print("перевірка чисельно, P0 =", P0, " P(2) =", round(sol.y[0][-1], 2))

# графіки
t = np.linspace(0, 4, 300)

plt.figure(figsize=(12, 4.5))

plt.subplot(1, 2, 1)
plt.plot(t, P(t, 60), 'b', label='P(0) = 60')
plt.axhline(K, color='gray', linestyle='--', label='P = 120')
plt.plot(2, P(2, 60), 'ko')
plt.ylim(0, 140)
plt.title('P(0) = 60')
plt.xlabel('t, місяці')
plt.ylabel('P(t)')
plt.grid()
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(t, P(t, 180), 'r', label='P(0) = 180')
plt.axhline(K, color='gray', linestyle='--', label='P = 120')
plt.plot(2, P(2, 180), 'ko')
plt.ylim(100, 190)
plt.title('P(0) = 180')
plt.xlabel('t, місяці')
plt.ylabel('P(t)')
plt.grid()
plt.legend()

plt.tight_layout()
plt.savefig('izol.png', dpi=150)
