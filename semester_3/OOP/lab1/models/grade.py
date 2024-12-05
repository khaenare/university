from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.student import Student
    from models.assignment import Assignment

class Grade:
    """
    Клас, що представляє оцінку за завдання.
    """

    def __init__(self, student: 'Student', assignment: 'Assignment', grade_value: float):
        self.student = student
        self.assignment = assignment
        self.grade_value = grade_value

    def update_grade(self, new_value: float):
        """
        Оновлює значення оцінки.
        """
        self.grade_value = new_value
        print(f"Grade updated to {new_value} for {self.student.get_full_name()} on assignment {self.assignment.title}")
