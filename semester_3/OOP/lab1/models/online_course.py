from models.course import Course

class OnlineCourse(Course):
    """
    Клас, що представляє онлайн-курс.
    """

    def __init__(self, course_id: str, title: str, description: str, platform: str):
        super().__init__(course_id, title, description)
        self.platform = platform

    def get_course_info(self) -> str:
        """
        Повертає інформацію про онлайн-курс.
        """
        return f"{self.title} is available on {self.platform}"
