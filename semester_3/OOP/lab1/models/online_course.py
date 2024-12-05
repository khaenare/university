from models.course import Course

class OnlineCourse(Course):
    """
    Класс, представляющий онлайн-курс.
    """

    def __init__(self, course_id: str, title: str, description: str, platform: str):
        super().__init__(course_id, title, description)
        self.platform = platform

    def get_course_info(self) -> str:
        """
        Возвращает информацию об онлайн-курсе.
        """
        return f"{self.title} доступен на платформе {self.platform}"
