from models.person import Person
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from models.course import Course

class Student(Person):
    """
    Клас, що представляє студента.
    """

    def __init__(self, name: str, surname: str, email: str, student_id: int):
        super().__init__(name, surname, email)
        self._student_id = student_id
        self._courses: List['Course'] = []
        self._grades: Dict[str, float] = {}

    def enroll_course(self, course: 'Course'):
        """
        Записує студента на курс.
        """
        if course not in self._courses:
            self._courses.append(course)
            course.add_student(self)
        else:
            print(f"Student is already enrolled in the course {course.title}")

    def submit_assignment(self, assignment: 'Assignment', submission: str):
        """
        Відправляє рішення завдання.
        """
        assignment.add_submission(self._student_id, submission)
        print(f"Assignment '{assignment.title}' submitted by {self.get_full_name()}")

    def calculate_gpa(self) -> float:
        """
        Обчислює середній бал студента.
        """
        if not self._grades:
            return 0.0
        total = sum(self._grades.values())
        return total / len(self._grades)

    def add_grade(self, course_title: str, grade_value: float):
        """
        Додає оцінку по курсу.
        """
        self._grades[course_title] = grade_value

    def get_grades(self) -> Dict[str, float]:
        """
        Повертає словник оцінок студента.
        """
        return self._grades

    def submit_assignment(self, assignment: 'Assignment', submission: str):
        """
        Відправляє вирішине завдання
        """
        assignment.add_submission(self._student_id, submission)
        print(f"Assignment '{assignment.title}' submitted by {self.get_full_name()}")

    def view_assignments(self):
        """
        Відображає список курсів на яких записан студент
        """
        print("\nYour Assignments:")
        for course in self._courses:
            print(f"\nCourse: {course.title}")
            if course.assignments:
                for assignment in course.assignments:
                    status = "Submitted" if self._student_id in assignment.submissions else "Not Submitted"
                    print(f"- [{status}] {assignment.assignment_id}: {assignment.title}, Due: {assignment.due_date}")
            else:
                print("No assignments for this course.")
