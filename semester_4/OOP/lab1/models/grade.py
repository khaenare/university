from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.student import Student
    from models.assignment import Assignment

class Grade:
    """
    Клас, що представляє оцінку за завдання.
    """

    def __init__(self, student: 'Student', assignment: 'Assignment', grade_value: float):
        self._student = student
        self._assignment = assignment
        self._grade_value = self._validate_grade(grade_value)

    @property
    def student(self) -> 'Student':
        return self._student

    @property
    def assignment(self) -> 'Assignment':
        return self._assignment

    @property
    def grade_value(self) -> float:
        return self._grade_value

    def update_grade(self, new_value: float) -> None:
        """
        Оновлює значення оцінки.
        """
        self._grade_value = self._validate_grade(new_value)
        print(f"Grade updated to {new_value} for {self._student.get_full_name()} on assignment {self._assignment.title}")

    def _validate_grade(self, value: float) -> float:
        """
        Перевіряє коректність оцінки (0 ≤ x ≤ max_grade).
        """
        if not 0 <= value <= self._assignment.max_grade:
            raise ValueError(f"Grade {value} must be between 0 and {self._assignment.max_grade}")
        return value
