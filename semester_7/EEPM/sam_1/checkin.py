# швидка перевірка розв'язків (запускати окремо, у звіт не вставляти)
import numpy as np
from scipy.integrate import solve_ivp

print("--- Задача 1 ---")
K = 120
r = 0.015
for P0 in (60, 180):
    P = lambda t: K * P0 / (P0 + (K - P0) * np.exp(-r * K * t))
    t = 0.5
    h = 1e-6
    dP = (P(t + h) - P(t - h)) / (2 * h)       # похідна чисельно
    print("P0 =", P0, " P(0) =", P(0), " dP/dt - r*P*(K-P) =", round(dP - r * P(t) * (K - P(t)), 6), " P(2) =", round(P(2), 3))

print("--- Задача 2 ---")
b = np.array([0, 0, 0.19, 0.44, 0.5, 0.5, 0.45])
for k in (1, 0.88):
    L = np.zeros((7, 7))
    L[0, :] = b * k
    for i in range(6):
        L[i + 1, i] = 0.87
    L[6, 6] = 0.8
    lam = max(np.linalg.eigvals(L).real)
    # просто множимо вектор на матрицю багато разів
    x = np.ones(7)
    for n in range(3000):
        new = L @ x
        ratio = new.sum() / x.sum()
        x = new / new.sum()
    print("lambda з eig =", round(lam, 5), " з циклу =", round(ratio, 5), " H =", round((1 - 1 / lam) * 100, 3))
    print("структура, %:", np.round(x * 100, 2))

print("--- Задача 3 ---")
f = lambda x, y: 4 * x - x * y - x**2
g = lambda x, y: -3 * y + 6 * x * y
for p in [(0, 0), (4, 0), (1 / 2, 7 / 2)]:
    print("точка", p, " f, g в ній:", round(f(*p), 10), round(g(*p), 10))
sol = solve_ivp(lambda t, z: [f(*z), g(*z)], [0, 200], [2, 1], rtol=1e-10)
print("модель 2, кінцева точка:", sol.y[:, -1].round(4), " (очікуємо 0.5 3.5)")
