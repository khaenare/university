# Імпорт потрібних бібліотек
var('x')
y = function('y')(x)
# Задаємо диференціальне рівняння
de = diff(y, x, 2) - 2*diff(y, x) + 2*y == (x + exp(x)) * sin(x)
# Початкові умови для кожної точки
ics_1 = [0, 1, 2] # для точки (1, 2)
ics_2 = [0, -1, -4] # для точки (-1, -4)
ics_3 = [0, -2, -2] # для точки (-2, -2)
ics_4 = [0, 2, -4] # для точки (2, -4)
# Розв'язуємо диференціальне рівняння
sol = desolve(de, y)
# Розв'язуємо рівняння для кожної точки
sol1 = desolve(de, y, ics=ics_1)

sol2 = desolve(de, y, ics=ics_2)
sol3 = desolve(de, y, ics=ics_3)
sol4 = desolve(de, y, ics=ics_4)
# Виводимо результати для кожного розв'язку
show(sol1)
show(sol2)
show(sol3)
show(sol4)
show(sol)
# Побудова графіків для кожного розв'язку на інтервалі від -10 до 10
p1 = plot(sol1, (x, -10, 10), color='blue', legend_label='(1, 2)')
p2 = plot(sol2, (x, -10, 10), color='green', legend_label='(-1, -4)')
p3 = plot(sol3, (x, -10, 10), color='red', legend_label='(-2, -2)')
p4 = plot(sol4, (x, -10, 10), color='purple', legend_label='(2, -4)')
# Виведення графіків на одній системі координат
(p1 + p2 + p3 + p4).show()
