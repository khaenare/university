class Assignment:
    """
    Класс, представляющий задание курса.
    """

    def __init__(self, assignment_id: int, title: str, due_date: str, max_grade: float):
        self.assignment_id = assignment_id
        self.title = title
        self.due_date = due_date
        self.max_grade = max_grade

    def is_due(self) -> bool:
        """
        Проверяет, истек ли срок сдачи задания.
        """
        # Для простоты предположим, что due_date в формате 'YYYY-MM-DD'
        from datetime import datetime
        due = datetime.strptime(self.due_date, '%Y-%m-%d')
        return datetime.now() > due
