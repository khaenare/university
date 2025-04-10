from models.student import Student
from models.teacher import Teacher
from models.administrator import Administrator
from models.online_course import OnlineCourse
from models.onsite_course import OnsiteCourse
from models.schedule import Schedule
from system_interface import SystemInterface

from datetime import datetime

def demo():
    # Створюємо адміністратора
    admin = Administrator("Іван", "Іванов", "admin@example.com", 1)

    # Створюємо викладача
    teacher = Teacher("Петро", "Петров", "teacher@example.com", 101)

    # Створюємо онлайн-курс
    online_course = OnlineCourse("CS101", "Introduction to Programming", "Basics of Python programming", "Online Platform")

    # Створюємо очний курс
    onsite_course = OnsiteCourse("MA101", "Calculus", "Basics of calculus", "Room 101")

    # Адміністратор призначає викладача на курс
    admin.assign_teacher_to_course(teacher, online_course)
    admin.assign_teacher_to_course(teacher, onsite_course)

    # Створюємо студента
    student = Student("Олексій", "Смирнов", "student@example.com", 1001)

    # Студент записується на курси
    student.enroll_course(online_course)
    student.enroll_course(onsite_course)

    # Викладач створює завдання та зберігаємо його в змінну
    assignment = teacher.create_assignment(online_course, "Homework 1", "2024-12-31", 100)

    # Студент відправляє рішення завдання (тепер передається об'єкт завдання)
    student.submit_assignment(assignment, "My solution")

    # Викладач виставляє оцінку
    teacher.assign_grade(student, online_course, 95)

    # Виводимо середній бал студента
    print(f"Average GPA for {student.get_full_name()}: {student.calculate_gpa()}")

    # Робота з розкладом
    schedule = Schedule()
    schedule.add_event({"title": "Programming Lecture", "date": datetime.now().date()})
    today_events = schedule.get_today_events()
    print("Today's events:")
    for event in today_events:
        print(event.get('title'))


def main():
    system = SystemInterface()
    system.run()

if __name__ == "__main__":
    print("\nSelect the mode to run the console program: ")
    print("1. Demonstrative mode")
    print("2. Interactive mode")
    choice = input("Select an option: ").strip().lower()
    if choice == "1":
        demo()
    else:
        main()
