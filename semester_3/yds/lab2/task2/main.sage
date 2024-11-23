# Коефіцієнти системи
m11, m12, m21, m22 = -4, 0, 1, -1 # Задайте потрібні коефіцієнти
M = matrix([[m11, m12], [m21, m22]])
# Власні вектори
eigenVectors = M.eigenvectors_right()
v1, v2 = eigenVectors[0][1][0], eigenVectors[1][1][0]
# Змінні
x, y, t = var('x y t')
x1, y1 = function('x1')(t), function('y1')(t)
# Сепаратриси
if v1[0] != 0:
separ1 = solve([v1[0] * y == v1[1] * x], y)[0].right()
else:
separ1 = (x == 0)
if v2[0] != 0:
separ2 = solve([v2[0] * y == v2[1] * x], y)[0].right()

else:
separ2 = (x == 0)
# Система диференціальних рівнянь
dx = diff(x1, t) == m11 * x1 + m12 * y1
dy = diff(y1, t) == m21 * x1 + m22 * y1
# Ізокліна
isocline = solve([(m21 * x + m22 * y) / (m11 * x + m12 * y)], y)[0].right()
# Діапазон графіку
plotRange = 20
# Поле напрямків
plt = plot_vector_field(
[m11 * x + m12 * y, m21 * x + m22 * y],
[x, -plotRange, plotRange],
[y, -plotRange, plotRange],
axes_labels=['$x$', '$y(x)$'], axes=True # Додано осі
)
# Сепаратриси
if v1[0] != 0:
plt += plot(separ1, (-plotRange, plotRange), color="blue", thickness=2)
else:
plt += implicit_plot(separ1, (x, -plotRange, plotRange), (y, -plotRange, plotRange),
color="blue")
if v2[0] != 0:
plt += plot(separ2, (-plotRange, plotRange), color="red", thickness=2)
else:
plt += implicit_plot(separ2, (x, -plotRange, plotRange), (y, -plotRange, plotRange),
color="red")
# Ізокліна (чорна лінія продовжена до країв)
plt += plot(isocline, (-plotRange, plotRange), color="black", thickness=3)
# Лінії розв’язків задачі Коші
# Центральні лінії
for i in range(-10, 10):
x_t, y_t = desolve_system([dx, dy], [x1, y1], ics=[0, i / 2, i * 2])
plt += parametric_plot((x_t.rhs(), y_t.rhs()), (t, -plotRange, plotRange), color="green")
# Додаткові лінії по боках
for i in range(-plotRange, plotRange + 1, 2):
x_t, y_t = desolve_system([dx, dy], [x1, y1], ics=[0, i, -i])
plt += parametric_plot((x_t.rhs(), y_t.rhs()), (t, -plotRange, plotRange), color="green")

# Додано осі x і y як чорні лінії
plt += line([(-plotRange, 0), (plotRange, 0)], color="black", thickness=1) # Вісь x
plt += line([(0, -plotRange), (0, plotRange)], color="black", thickness=1) # Вісь y
# Показати графік
plt.show(xmin=-plotRange, xmax=plotRange, ymin=-plotRange, ymax=plotRange)
