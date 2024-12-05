

from typing import List
from models.assignment import Assignment

class Course:
    """
    Класс, представляющий учебный курс.
    """

    def __init__(self, course_id: str, title: str, description: str):
        self.course_id = course_id
        self.title = title
        self.description = description
        self.assignments: List[Assignment] = []
        self.students: List['Student'] = []
        self.teacher: 'Teacher' = None

    def add_student(self, student: 'Student'):
        """
        Добавляет студента на курс.
        """
        if student not in self.students:
            self.students.append(student)
            print(f"Студент {student.get_full_name()} добавлен на курс {self.title}")
        else:
            print(f"Студент {student.get_full_name()} уже записан на курс {self.title}")

    def remove_student(self, student: 'Student'):
        """
        Удаляет студента с курса.
        """
        if student in self.students:
            self.students.remove(student)
            print(f"Студент {student.get_full_name()} удален с курса {self.title}")
        else:
            print(f"Студент {student.get_full_name()} не найден на курсе {self.title}")

    def add_assignment(self, assignment: Assignment):
        """
        Добавляет задание к курсу.
        """
        self.assignments.append(assignment)

    def get_average_grade(self) -> float:
        """
        Вычисляет среднюю оценку по курсу.
        """
        total = 0
        count = 0
        for student in self.students:
            grades = student.get_grades()
            if self.title in grades:
                total += grades[self.title]
                count += 1
        return total / count if count > 0 else 0.0

    def set_teacher(self, teacher: 'Teacher'):
        """
        Назначает преподавателя на курс.
        """
        self.teacher = teacher

# Избегаем циклического импорта
from models.student import Student
from models.teacher import Teacher
