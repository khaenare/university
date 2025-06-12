from datetime import datetime
from typing import Dict

class Assignment:
    """
    Клас, що представляє завдання курсу.
    """

    def __init__(self, assignment_id: int, title: str, due_date: str, max_grade: float):
        self._assignment_id = assignment_id
        self._title = title
        self._due_date = due_date
        self._max_grade = max_grade
        self._submissions: Dict[int, str] = {}  # {student_id: submission}
        self._grades: Dict[int, float] = {}     # {student_id: grade_value}

    @property
    def assignment_id(self) -> int:
        return self._assignment_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def due_date(self) -> str:
        return self._due_date

    @property
    def max_grade(self) -> float:
        return self._max_grade

    @property
    def submissions(self) -> Dict[int, str]:
        return self._submissions

    @property
    def grades(self) -> Dict[int, float]:
        return self._grades

    def is_due(self) -> bool:
        """
        Перевіряє, чи минув термін здачі завдання.
        """
        due = datetime.strptime(self._due_date, '%Y-%m-%d')
        return datetime.now() > due

    def add_submission(self, student_id: int, submission: str) -> str:
        """
        Додає розв'язок студента. Якщо уже є — замінює.
        """
        self._submissions[student_id] = submission
        return f"Submission from student {student_id} received."

    def assign_grade(self, student_id: int, grade_value: float) -> str:
        """
        Виставляє оцінку студенту за це завдання. Перевіряє, чи не перевищує max_grade.
        """
        if grade_value > self._max_grade:
            return f"Error: Grade {grade_value} exceeds max allowed {self._max_grade}."
        self._grades[student_id] = grade_value
        return f"Grade {grade_value} assigned to student {student_id}."
