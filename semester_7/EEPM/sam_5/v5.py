import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.set_printoptions(precision=4, suppress=True)

# ---------- 5.1. Модель Леонтьєва для двох галузей ----------
# рядок - кому пішла продукція галузі: [промисловість, с/г], кінцеве споживання
x = np.array([[820, 450],
              [350, 400]])
y_old = np.array([970, 750])
X_old = x.sum(axis=1) + y_old           # повний випуск за минулий рік
A2 = x / X_old                          # a_ij = x_ij / X_j
y_new = np.array([1150, 700])
X_new = np.linalg.solve(np.eye(2) - A2, y_new)
print("5.1")
print("повний випуск минулого року X =", X_old)
print("матриця прямих витрат A =\n", A2)
print("новий попит y =", y_new, " ->  новий повний випуск X =", X_new.round(2))
print("перевірка X - A X =", (X_new - A2 @ X_new).round(2))

# ---------- 5.2. Аналіз матриці A ----------
A = np.array([[0.1, 0.5, 0.1],
              [0.3, 0.2, 0.1],
              [0.3, 0.1, 0.4]])
E = np.eye(3)
s = np.array([0.3, 0.4, 0.5])

ev = np.linalg.eigvals(A)
print("\n5.2")
print("власні числа:", ev.round(4))
print("коефіцієнти характеристичного полінома det(lambda*E - A):", np.poly(A).round(4))

# число Фробеніуса - найбільше (дійсне, додатне) власне число
vals, vecs = np.linalg.eig(A)
k = np.argmax(vals.real)
lam = vals[k].real
right = np.abs(vecs[:, k].real); right /= right.sum()
vals_t, vecs_t = np.linalg.eig(A.T)
left = np.abs(vecs_t[:, np.argmax(vals_t.real)].real); left /= left.sum()
print("число Фробеніуса lambda* =", round(lam, 4))
print("правий вектор Фробеніуса (A x = lambda x):", right.round(4))
print("лівий вектор Фробеніуса  (p A = lambda p):", left.round(4))
print("lambda* < 1 -> матриця продуктивна" if lam < 1 else "lambda* >= 1 -> матриця не продуктивна")

# матриця повних витрат
B = np.linalg.inv(E - A)
print("матриця повних витрат B = (E - A)^-1 =\n", B)

# збіжність ряду E + A + A^2 + ... + A^N
S, P, N = E.copy(), E.copy(), 0
errs = []
while True:
    errs.append(np.abs(B - S).max())
    if errs[-1] < 0.01:
        break
    N += 1
    P = P @ A
    S = S + P
print(f"ряд збігається до B з точністю 0.01 при N = {N}, max|B - S_N| = {errs[-1]:.5f}")
print("S_N =\n", S)

# вектор цін: p = p A + s  ->  p = s B
prices = s @ B
print("вектор цін p = s B =", prices.round(4))
print("перевірка p - p A =", (prices - prices @ A).round(4))

# графік збіжності ряду
plt.figure(figsize=(7, 4))
plt.semilogy(range(len(errs)), errs, 'o-')
plt.axhline(0.01, color='r', linestyle='--', label='точність 0.01')
plt.xlabel('N')
plt.ylabel('max |B - (E + A + ... + A^N)|')
plt.title('Збіжність ряду до матриці повних витрат')
plt.grid(alpha=.4)
plt.legend()
plt.tight_layout()
plt.savefig('series.png', dpi=150)
