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
        self._course_id = course_id
        self._title = title
        self._description = description
        self._assignments: List[Assignment] = []
        self._students: List['Student'] = []
        self._teacher: 'Teacher' = None

    @property
    def course_id(self) -> str:
        return self._course_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def assignments(self) -> List[Assignment]:
        return self._assignments

    @property
    def students(self) -> List['Student']:
        return self._students

    @property
    def teacher(self) -> 'Teacher':
        return self._teacher

    def add_student(self, student: 'Student') -> None:
        """
        Додає студента на курс.
        """
        if student not in self._students:
            self._students.append(student)
            print(f"Student {student.get_full_name()} added to course {self._title}")
        else:
            print(f"Student {student.get_full_name()} is already enrolled in course {self._title}")

    def remove_student(self, student: 'Student') -> None:
        """
        Видаляє студента з курсу.
        """
        if student in self._students:
            self._students.remove(student)
            print(f"Student {student.get_full_name()} removed from course {self._title}")
        else:
            print(f"Student {student.get_full_name()} is not found in course {self._title}")

    def add_assignment(self, assignment: Assignment) -> None:
        """
        Додає завдання до курсу.
        """
        self._assignments.append(assignment)
        print(f"Assignment '{assignment.title}' added to course {self._title}.")

    def get_average_grade(self) -> float:
        """
        Обчислює середню оцінку по курсу.
        """
        total = 0
        count = 0
        for student in self._students:
            grades_dict = student.get_grades()
            grades_list = grades_dict.get(self, [])  # ключ — об'єкт Course
            for grade in grades_list:
                total += grade.grade_value
                count += 1
        return total / count if count > 0 else 0.0

    def set_teacher(self, teacher: 'Teacher') -> None:
        """
        Призначає викладача на курс.
        """
        self._teacher = teacher
