# Імпорт бібліотек
var('x y')
# Визначаємо рівняння y' = 2xy / (x^2 + y^2)
f(x, y) = 2*x*y / (x^2 + y^2)
# Побудова поля напрямків з діапазоном для x і y від -10 до 10
direction_field = plot_slope_field(f(x, y), (x, -10, 10), (y, -10, 10))
# Використовуємо числовий метод для розв'язання задач Коші в обидва напрямки
# Перше початкове значення (1, 2)
sol1_positive = desolve_rk4(f(x, y), y, ics=[1, 2], ivar=x, step=0.1, end_points=10)
sol1_negative = desolve_rk4(f(x, y), y, ics=[1, 2], ivar=x, step=0.1, end_points=-10)
# Друге початкове значення (-1, 4)
sol2_positive = desolve_rk4(f(x, y), y, ics=[-1, 4], ivar=x, step=0.1, end_points=10)
sol2_negative = desolve_rk4(f(x, y), y, ics=[-1, 4], ivar=x, step=0.1, end_points=-10)

# Третє початкове значення (-1, -2)
sol3_positive = desolve_rk4(f(x, y), y, ics=[-1, -2], ivar=x, step=0.1, end_points=10)
sol3_negative = desolve_rk4(f(x, y), y, ics=[-1, -2], ivar=x, step=0.1, end_points=-10)
# Четверте початкове значення (2, -4)
sol4_positive = desolve_rk4(f(x, y), y, ics=[2, -4], ivar=x, step=0.1, end_points=10)
sol4_negative = desolve_rk4(f(x, y), y, ics=[2, -4], ivar=x, step=0.1, end_points=-10)
# Створюємо графіки для всіх розв'язків задач Коші з пунктирними лініями
solution_plots = line(sol1_positive, color='blue', legend_label='(1, 2)', linestyle='--') + \

line(sol1_negative, color='blue', linestyle='--') + \
line(sol2_positive, color='green', legend_label='(-1, 4)', linestyle='--') + \
line(sol2_negative, color='green', linestyle='--') + \
line(sol3_positive, color='red', legend_label='(-1, -2)', linestyle='--') + \
line(sol3_negative, color='red', linestyle='--') + \
line(sol4_positive, color='purple', legend_label='(2, -4)', linestyle='--') + \
line(sol4_negative, color='purple', linestyle='--')
# Додаємо поле напрямків до графіків розв'язків задач Коші
full_plot = direction_field + solution_plots
# Виводимо остаточний графік
full_plot.show(ymin=-10, ymax=10)
