from models.person import Person
from models.assignment import Assignment
from models.grade import Grade
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.course import Course
    from models.student import Student


class Teacher(Person):
    """
    Клас, що представляє викладача.
    """

    def __init__(self, name: str, surname: str, email: str, teacher_id: int):
        super().__init__(name, surname, email)
        self._teacher_id = teacher_id
        self._courses_taught: List['Course'] = []

    @property
    def teacher_id(self) -> int:
        """
        Повертає ідентифікатор викладача.
        """
        return self._teacher_id

    def add_course(self, course: 'Course'):
        """
        Додає курс до списку викладацьких курсів.
        """
        if course not in self._courses_taught:
            self._courses_taught.append(course)
            course.set_teacher(self)
            print(f"Course {course.title} added to teacher {self.get_full_name()}")
        else:
            print(f"Course {course.title} is already assigned to teacher {self.get_full_name()}.")

    def create_assignment(self, course: 'Course', title: str, due_date: str, max_grade: float) -> Optional[Assignment]:
        """
        Створює нове завдання для курсу.
        """
        if course in self._courses_taught:
            assignment_id = len(course.assignments) + 1
            assignment = Assignment(assignment_id, title, due_date, max_grade)
            course.add_assignment(assignment)
            print(f"Assignment '{title}' created for course {course.title}")
            return assignment
        else:
            print(f"Error: Teacher {self.get_full_name()} does not teach course {course.title}")
            return None

    def assign_grade(self, student: 'Student', course: 'Course', grade_value: float):
        """
        Виставляє оцінку студенту за курс.
        """
        if course in self._courses_taught and student in course.students:
            grade = Grade(student, None, grade_value)
            student.add_grade(course, grade)
            print(f"Grade {grade_value} assigned to {student.get_full_name()} for course {course.title}")
        else:
            print(f"Error: Cannot assign grade. Teacher does not teach course {course.title} or student is not enrolled.")

    def assign_grade_for_assignment(self, student: 'Student', course: 'Course', assignment_id: int, grade_value: float):
        """
        Виставляє оцінку студенту за конкретне завдання курсу.
        """
        if course not in self._courses_taught:
            print(f"Error: Teacher {self.get_full_name()} does not teach course {course.title}")
            return

        assignment = next((a for a in course.assignments if a.assignment_id == assignment_id), None)
        if assignment:
            assignment.assign_grade(student.student_id, grade_value)
            print(f"Grade {grade_value} assigned to {student.get_full_name()} for assignment '{assignment.title}' in course {course.title}")
        else:
            print(f"Error: Assignment with ID {assignment_id} not found in course {course.title}")
