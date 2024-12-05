from typing import List, TYPE_CHECKING
from models.assignment import Assignment

if TYPE_CHECKING:
    from models.student import Student
    from models.teacher import Teacher

class Course:
    """
    Клас, що представляє навчальний курс.
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
        Додає студента на курс.
        """
        if student not in self.students:
            self.students.append(student)
            print(f"Student {student.get_full_name()} added to course {self.title}")
        else:
            print(f"Student {student.get_full_name()} is already enrolled in course {self.title}")

    def remove_student(self, student: 'Student'):
        """
        Видаляє студента з курсу.
        """
        if student in self.students:
            self.students.remove(student)
            print(f"Student {student.get_full_name()} removed from course {self.title}")
        else:
            print(f"Student {student.get_full_name()} is not found in course {self.title}")

    def add_assignment(self, assignment: Assignment):
        """
        Додає завдання до курсу.
        """
        self.assignments.append(assignment)

    def get_average_grade(self) -> float:
        """
        Обчислює середню оцінку по курсу.
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
        Призначає викладача на курс.
        """
        self.teacher = teacher
