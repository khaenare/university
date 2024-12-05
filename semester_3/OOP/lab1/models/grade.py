class Grade:
    """
    Класс, представляющий оценку за задание.
    """

    def __init__(self, student: 'Student', assignment: 'Assignment', grade_value: float):
        self.student = student
        self.assignment = assignment
        self.grade_value = grade_value

    def update_grade(self, new_value: float):
        """
        Обновляет значение оценки.
        """
        self.grade_value = new_value
        print(f"Оценка обновлена до {new_value} для студента {self.student.get_full_name()} по заданию {self.assignment.title}")

# Избегаем циклического импорта
from models.student import Student
from models.assignment import Assignment
