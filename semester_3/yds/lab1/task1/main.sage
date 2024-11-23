# Імпорт бібліотек
var('x y')
# Визначаємо рівняння y' = cos(y - x)
f(x, y) = cos(y - x)
# Побудова поля напрямків з діапазоном по осі x від -10 до 10 і по осі y від -10 до 10
direction_field = plot_slope_field(f(x, y), (x, -10, 10), (y, -10, 10))
# Використовуємо числовий метод для розв'язання задач Коші в обох напрямках з
меншим кроком
# Перше початкове значення (1, 2)
sol1_positive = desolve_rk4(f(x, y), y, ics=[1, 2], ivar=x, step=0.05, end_points=10)
sol1_negative = desolve_rk4(f(x, y), y, ics=[1, 2], ivar=x, step=0.05, end_points=-10)
# Друге початкове значення (-1, 2)
sol2_positive = desolve_rk4(f(x, y), y, ics=[-1, 2], ivar=x, step=0.05, end_points=10)
sol2_negative = desolve_rk4(f(x, y), y, ics=[-1, 2], ivar=x, step=0.05, end_points=-10)
# Третє початкове значення (-1, -2)
sol3_positive = desolve_rk4(f(x, y), y, ics=[-1, -2], ivar=x, step=0.05, end_points=10)
sol3_negative = desolve_rk4(f(x, y), y, ics=[-1, -2], ivar=x, step=0.05, end_points=-10)
# Четверте початкове значення (1, -2)
sol4_positive = desolve_rk4(f(x, y), y, ics=[1, -2], ivar=x, step=0.05, end_points=10)
sol4_negative = desolve_rk4(f(x, y), y, ics=[1, -2], ivar=x, step=0.05, end_points=-10)
# Створюємо графіки для всіх розв'язків задач Коші в обох напрямках
solution_plots = list_plot(sol1_positive, color='blue', legend_label='(1, 2)') + \

list_plot(sol1_negative, color='blue') + \
list_plot(sol2_positive, color='green', legend_label='(-1, 2)') + \
list_plot(sol2_negative, color='green') + \
list_plot(sol3_positive, color='red', legend_label='(-1, -2)') + \
list_plot(sol3_negative, color='red') + \
list_plot(sol4_positive, color='purple', legend_label='(1, -2)') + \
list_plot(sol4_negative, color='purple')

# Додаємо поле напрямків до графіків розв'язків задач Коші
full_plot = direction_field + solution_plots
# Виводимо остаточний графік
full_plot.show()
