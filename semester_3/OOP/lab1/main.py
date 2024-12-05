from models.student import Student
from models.teacher import Teacher
from models.administrator import Administrator
from models.online_course import OnlineCourse
from models.onsite_course import OnsiteCourse
from models.schedule import Schedule

def main():
    # Создаем администратора
    admin = Administrator("Иван", "Иванов", "admin@example.com", 1)

    # Создаем преподавателя
    teacher = Teacher("Петр", "Петров", "teacher@example.com", 101)

    # Создаем онлайн-курс
    online_course = OnlineCourse("CS101", "Введение в программирование", "Основы программирования на Python", "Online Platform")

    # Создаем очный курс
    onsite_course = OnsiteCourse("MA101", "Математический анализ", "Основы математического анализа", "Аудитория 101")

    # Администратор назначает преподавателя на курс
    admin.assign_teacher_to_course(teacher, online_course)
    admin.assign_teacher_to_course(teacher, onsite_course)

    # Создаем студента
    student = Student("Алексей", "Смирнов", "student@example.com", 1001)

    # Студент записывается на курсы
    student.enroll_course(online_course)
    student.enroll_course(onsite_course)

    # Преподаватель создает задание
    teacher.create_assignment(online_course, "Домашнее задание 1", "2024-12-31", 100)

    # Студент отправляет решение задания
    student.submit_assignment(1, "Мое решение")

    # Преподаватель выставляет оценку
    teacher.assign_grade(student, online_course, 95)

    # Выводим средний балл студента
    print(f"Средний балл студента {student.get_full_name()}: {student.calculate_gpa()}")

    # Работа с расписанием
    schedule = Schedule()
    schedule.add_event({"title": "Лекция по программированию", "date": datetime.now().date()})
    today_events = schedule.get_today_events()
    print("События на сегодня:")
    for event in today_events:
        print(event.get('title'))

if __name__ == "__main__":
    from datetime import datetime
    main()
