from models.person import Person
from models.assignment import Assignment
from typing import List, TYPE_CHECKING

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

    def assign_grade(self, student: 'Student', course: 'Course', grade_value: float):
        """
        Виставляє оцінку студенту по курсу.
        """
        if course in self._courses_taught and student in course.students:
            student.add_grade(course.title, grade_value)
            print(f"Grade {grade_value} assigned to {student.get_full_name()} for course {course.title}")
        else:
            print(f"Error: Teacher does not teach course {course.title} or student is not enrolled.")

    def create_assignment(self, course: 'Course', title: str, due_date: str, max_grade: float):
        """
        Створює нове завдання для курсу.
        """
        if course in self._courses_taught:
            assignment_id = len(course.assignments) + 1
            new_assignment = Assignment(assignment_id, title, due_date, max_grade)
            course.add_assignment(new_assignment)
            print(f"Assignment '{title}' created for course {course.title}")
        else:
            print(f"Error: Teacher does not teach course {course.title}")

    def add_course(self, course: 'Course'):
        """
        Додає курс до списку викладацьких курсів.
        """
        if course not in self._courses_taught:
            self._courses_taught.append(course)
            course.set_teacher(self)
        else:
            print(f"Course {course.title} is already assigned.")

    def assign_grade_for_assignment(self, student: 'Student', course: 'Course', assignment_id: int, grade_value: float):
        """
        Виставляє оцінку студенту по курсу за конкретне завдання
        """
        assignment = next((a for a in course.assignments if a.assignment_id == assignment_id), None)
        if assignment:
            assignment.assign_grade(student._student_id, grade_value)
            print(f"Grade {grade_value} assigned to {student.get_full_name()} for assignment '{assignment.title}' in course {course.title}")
        else:
            print("Assignment not found.")
