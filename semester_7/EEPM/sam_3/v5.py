import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import brentq

# Варіант 5, субсидія для споживача sub = 0.7
P = np.array([1.23, 2.05, 2.78, 3.45, 4.99, 5.26, 6.13, 7.5])
Qd = np.array([105, 80, 65, 53, 38, 34, 22, 17])
Qs = np.array([10, 26, 37, 50, 73, 80, 90, 110])
sub = 0.7

def r2(y, f):
    return 1 - ((y - f)**2).sum() / ((y - y.mean())**2).sum()

# 1. Апроксимація (МНК)
# попит: Qd = a * exp(b*P)  ->  ln Qd = ln a + b*P
b_d, ln_a = np.polyfit(P, np.log(Qd), 1)
a_d = np.exp(ln_a)
# пропозиція: Qs = c*P + d
c_s, d_s = np.polyfit(P, Qs, 1)

D = lambda p: a_d * np.exp(b_d * p)
S = lambda p: c_s * p + d_s
print(f"Попит:      Qd = {a_d:.4f} * exp({b_d:.4f} P),  R^2 = {r2(Qd, D(P)):.4f}")
print(f"Пропозиція: Qs = {c_s:.4f} P {d_s:+.4f},  R^2 = {r2(Qs, S(P)):.4f}")

# для порівняння - лінійний попит
k, m = np.polyfit(P, Qd, 1)
print(f"(лінійний попит: R^2 = {r2(Qd, k * P + m):.4f} - гірше)")

# 2. Рівновага: D(P) = S(P)
Pe = brentq(lambda p: D(p) - S(p), 0.5, 8)
Qe = S(Pe)
print(f"\nРівновага: P* = {Pe:.4f},  Q* = {Qe:.4f}")

# стабільність (павутиноподібна модель): |S'(P*)| / |D'(P*)| < 1
dD = b_d * D(Pe)
dS = c_s
print(f"D'(P*) = {dD:.4f},  S'(P*) = {dS:.4f},  |S'/D'| = {abs(dS / dD):.4f}")
p = Pe + 0.5                      # відхиляємо ціну і дивимось, чи повернеться
for t in range(6):
    p = brentq(lambda x: D(x) - S(p), 0.01, 20)   # Qd(P_t) = Qs(P_{t-1})
    print(f"  t={t + 1}: P = {p:.4f}")

# 3. Субсидія для споживача: попит зсувається вгору на sub -> D(P - sub) = S(P)
P1 = brentq(lambda p: D(p - sub) - S(p), 0.5, 9)
Q1 = S(P1)
print(f"\nПісля субсидії: Q1 = {Q1:.4f}")
print(f"  ціна продавця   Ps = {P1:.4f}  (було {Pe:.4f}, {P1 - Pe:+.4f})")
print(f"  ціна покупця    Pd = {P1 - sub:.4f}  ({P1 - sub - Pe:+.4f})")
print(f"  витрати держави sub*Q1 = {sub * Q1:.4f}")

# графік в осях (Q, P)
pp = np.linspace(0.8, 8, 300)
plt.figure(figsize=(8, 5.5))
plt.plot(Qd, P, 'o', color='tab:blue', label='Попит (дані)')
plt.plot(Qs, P, 's', color='tab:red', label='Пропозиція (дані)')
plt.plot(D(pp), pp, color='tab:blue', label='Qd(P)')
plt.plot(S(pp), pp, color='tab:red', label='Qs(P)')
plt.plot(D(pp - sub), pp, '--', color='tab:blue', label=f'Qd після субсидії (+{sub})')
plt.plot(Qe, Pe, 'ko', markersize=8)
plt.annotate(f'E({Qe:.1f}; {Pe:.2f})', (Qe, Pe), (Qe - 22, Pe + 0.15))
plt.plot(Q1, P1, 'go', markersize=8)
plt.annotate(f'E1({Q1:.1f}; {P1:.2f})', (Q1, P1), (Q1 + 4, P1 + 0.2))
plt.plot([Q1, Q1], [0, P1], 'g:')
plt.plot([0, Q1], [P1 - sub, P1 - sub], 'g:')
plt.plot([0, Q1], [P1, P1], 'g:')
plt.text(1, P1 + 0.08, 'Ps', color='g')
plt.text(1, P1 - sub + 0.08, 'Pd', color='g')
plt.xlim(0, 120)
plt.ylim(0, 8)
plt.xlabel('Q')
plt.ylabel('P')
plt.title('Попит, пропозиція і ринкова рівновага (варіант 5)')
plt.grid(alpha=.4)
plt.legend()
plt.tight_layout()
plt.savefig('market.png', dpi=150)
