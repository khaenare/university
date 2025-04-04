class Assignment:
    """
    Клас, що представляє завдання курсу.
    """

    def __init__(self, assignment_id: int, title: str, due_date: str, max_grade: float):
        self.assignment_id = assignment_id
        self.title = title
        self.due_date = due_date
        self.max_grade = max_grade
        self.submissions = {}  # {student_id: submission}
        self.grades = {}       # {student_id: grade_value}

    def is_due(self) -> bool:
        """
        Перевіряє, чи минув термін здачі завдання.
        """
        from datetime import datetime
        due = datetime.strptime(self.due_date, '%Y-%m-%d')
        return datetime.now() > due

    def add_submission(self, student_id: int, submission: str):
        """
        Добавляет решение от студента.
        """
        self.submissions[student_id] = submission

    def assign_grade(self, student_id: int, grade_value: float):
        """
        Присвоює оцінку студенту за це завдання.
        """
        self.grades[student_id] = grade_value
