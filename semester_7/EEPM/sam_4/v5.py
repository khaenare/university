import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Варіант 5. Виробнича функція Кобба-Дугласа F(K, L) = A * K^alpha * L^beta
K = np.array([1125, 1230, 1170, 1150, 1190, 1235, 1250, 1115, 1150, 1160])
L = np.array([3160, 3195, 3120, 3130, 3200, 3220, 3250, 3190, 3235, 3180])
q = np.array([4105, 4260, 4115, 4105, 4225, 4275, 4320, 4115, 4185, 4135])
p, w1, w2 = 6, 1, 3        # ціна продукції, ціна капіталу, ціна праці
TC, q0 = 7000, 8000

# МНК для ln q = ln A + alpha ln K + beta ln L
X = np.column_stack([np.ones(len(q)), np.log(K), np.log(L)])
c, *_ = np.linalg.lstsq(X, np.log(q), rcond=None)
A, a, b = np.exp(c[0]), c[1], c[2]
y = np.log(q)
R2 = 1 - ((y - X @ c)**2).sum() / ((y - y.mean())**2).sum()
F = lambda K, L: A * K**a * L**b
print(f"F(K, L) = {A:.4f} * K^{a:.4f} * L^{b:.4f},  R^2 = {R2:.4f}")
print(f"alpha + beta = {a + b:.4f}  (< 1 - спадна віддача від масштабу)")
print("середня похибка, %:", round(np.mean(np.abs(F(K, L) - q) / q) * 100, 3))

# 1) максимізація прибутку, K <= max K, L <= max L
Kmax, Lmax = K.max(), L.max()
profit = lambda x: p * F(x[0], x[1]) - w1 * x[0] - w2 * x[1]
res = minimize(lambda x: -profit(x), [K.mean(), L.mean()], bounds=[(1, Kmax), (1, Lmax)])
K1, L1 = res.x
print(f"\n1) Максимізація прибутку (K <= {Kmax}, L <= {Lmax})")
print(f"   p*MPK = {p * a * F(Kmax, Lmax) / Kmax:.3f} > w1 = {w1},  p*MPL = {p * b * F(Kmax, Lmax) / Lmax:.3f} > w2 = {w2}")
print(f"   K = {K1:.1f}, L = {L1:.1f}, q = {F(K1, L1):.1f}, прибуток = {profit(res.x):.1f}")

# 2) максимізація випуску при w1*K + w2*L = TC
K2 = a / (a + b) * TC / w1
L2 = b / (a + b) * TC / w2
print(f"\n2) Максимізація випуску при TC = {TC}")
print(f"   K = {K2:.1f}, L = {L2:.1f}, q max = {F(K2, L2):.1f}, перевірка TC = {w1 * K2 + w2 * L2:.1f}")

# 3) мінімізація витрат при F(K, L) = q0;  умова оптимуму K/L = alpha*w2 / (beta*w1)
r = a * w2 / (b * w1)
L3 = (q0 / (A * r**a))**(1 / (a + b))
K3 = r * L3
print(f"\n3) Мінімізація витрат при q0 = {q0}")
print(f"   K = {K3:.1f}, L = {L3:.1f}, TC min = {w1 * K3 + w2 * L3:.1f}, перевірка q = {F(K3, L3):.1f}")

# графік: ізокванти та ізокости для задач 2 і 3
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
for i, (Ko, Lo, cost, title) in enumerate(((K2, L2, TC, '2) max q при TC = 7000'),
                                           (K3, L3, w1 * K3 + w2 * L3, '3) min TC при q0 = 8000'))):
    qo = F(Ko, Lo)
    LL = np.linspace(Lo * 0.3, Lo * 2.2, 300)
    ax[i].plot((qo / (A * LL**b))**(1 / a), LL, 'b', label=f'ізокванта q = {qo:.0f}')
    KK = np.linspace(0, cost / w1, 100)
    ax[i].plot(KK, (cost - w1 * KK) / w2, 'r', label=f'ізокоста TC = {cost:.0f}')
    ax[i].plot(Ko, Lo, 'ko')
    ax[i].annotate(f'({Ko:.0f}; {Lo:.0f})', (Ko, Lo), (Ko + 150, Lo + 100))
    ax[i].set_xlim(0, cost / w1 * 1.05)
    ax[i].set_ylim(0, cost / w2 * 1.05)
    ax[i].set_xlabel('K')
    ax[i].set_ylabel('L')
    ax[i].set_title(title)
    ax[i].grid(alpha=.4)
    ax[i].legend()
plt.tight_layout()
plt.savefig('isoquants.png', dpi=150)
