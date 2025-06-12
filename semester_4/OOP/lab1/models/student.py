from models.person import Person
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from models.course import Course
    from models.assignment import Assignment
    from models.grade import Grade

class Student(Person):
    """
    Клас, що представляє студента.
    """

    def __init__(self, name: str, surname: str, email: str, student_id: int):
        super().__init__(name, surname, email)
        self._student_id = student_id
        self._courses: List['Course'] = []
        self._grades: Dict[str, List['Grade']] = {}


    @property
    def student_id(self) -> int:
        return self._student_id

    def enroll_course(self, course: 'Course'):
        """
        Записує студента на курс.
        """
        if course not in self._courses:
            self._courses.append(course)
            course.add_student(self)
            self._log(f"added to course {course.title}")
        else:
            self._log(f"is already enrolled in course {course.title}")

    def submit_assignment(self, assignment: 'Assignment', submission: str):
        """
        Відправляє вирішене завдання.
        """
        assignment.add_submission(self._student_id, submission)
        self._log(f"submitted assignment '{assignment.title}'")

    def add_grade(self, course: 'Course', grade: 'Grade'):
        """
        Додає оцінку по курсу.
        """
        if course.title not in self._grades:
            self._grades[course.title] = []
        self._grades[course.title].append(grade)

        self._log(f"received grade {grade.grade_value} in course {course.title}")

    def calculate_gpa(self) -> float:
        """
        Обчислює середній бал (GPA) студента.
        """
        grades = [g.grade_value for grade_list in self._grades.values() for g in grade_list]
        return round(sum(grades) / len(grades), 2) if grades else 0.0

    def get_grades(self) -> Dict[str, List['Grade']]:
        """
        Повертає словник оцінок.
        """
        return self._grades.copy()

    def view_assignments(self):
        """
        Виводить список завдань для кожного курсу.
        """
        print("\nYour Assignments:")
        for course in self._courses:
            print(f"\nCourse: {course.title}")
            if course.assignments:
                for assignment in course.assignments:
                    submitted = self._student_id in assignment.submissions
                    status = "Submitted" if submitted else "Not Submitted"
                    print(f"- [{status}] {assignment.assignment_id}: {assignment.title}, Due: {assignment.due_date}")
            else:
                print("No assignments for this course.")

    def _log(self, message: str):
        print(f"Student {self.get_full_name()} {message}")
