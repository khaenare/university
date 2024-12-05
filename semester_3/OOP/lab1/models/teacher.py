from models.person import Person
from models.course import Course
from typing import List

class Teacher(Person):
    """
    Класс, представляющий преподавателя.
    """

    def __init__(self, name: str, surname: str, email: str, teacher_id: int):
        super().__init__(name, surname, email)
        self._teacher_id = teacher_id
        self._courses_taught: List[Course] = []

    def assign_grade(self, student: 'Student', course: 'Course', grade_value: float):
        """
        Выставляет оценку студенту по курсу.
        """
        if course in self._courses_taught and student in course.students:
            student.add_grade(course.title, grade_value)
            print(f"Оценка {grade_value} выставлена студенту {student.get_full_name()} по курсу {course.title}")
        else:
            print(f"Ошибка: Преподаватель не ведет курс {course.title} или студент не записан на этот курс.")

    def create_assignment(self, course: 'Course', title: str, due_date: str, max_grade: float):
        """
        Создает новое задание для курса.
        """
        if course in self._courses_taught:
            assignment_id = len(course.assignments) + 1
            new_assignment = Assignment(assignment_id, title, due_date, max_grade)
            course.add_assignment(new_assignment)
            print(f"Задание '{title}' создано для курса {course.title}")
        else:
            print(f"Ошибка: Преподаватель не ведет курс {course.title}")

    def add_course(self, course: 'Course'):
        """
        Добавляет курс в список преподаваемых курсов.
        """
        if course not in self._courses_taught:
            self._courses_taught.append(course)
            course.set_teacher(self)
        else:
            print(f"Курс {course.title} уже в списке преподаваемых.")

from models.assignment import Assignment  # Избегаем циклического импорта
