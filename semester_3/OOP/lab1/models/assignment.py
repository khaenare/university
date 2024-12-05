class Assignment:
    """
    Клас, що представляє завдання курсу.
    """

    def __init__(self, assignment_id: int, title: str, due_date: str, max_grade: float):
        self.assignment_id = assignment_id
        self.title = title
        self.due_date = due_date
        self.max_grade = max_grade

    def is_due(self) -> bool:
        """
        Перевіряє, чи минув термін здачі завдання.
        """
        # Для простоти припустимо, що due_date у форматі 'YYYY-MM-DD'
        from datetime import datetime
        due = datetime.strptime(self.due_date, '%Y-%m-%d')
        return datetime.now() > due
