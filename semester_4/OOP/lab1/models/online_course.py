from models.course import Course

class OnlineCourse(Course):
    """
    Клас, що представляє онлайн-курс.
    """

    def __init__(self, course_id: str, title: str, description: str, platform: str):
        super().__init__(course_id, title, description)
        self._platform = platform

    @property
    def platform(self) -> str:
        return self._platform

    @platform.setter
    def platform(self, value: str):
        if not value:
            raise ValueError("Platform name cannot be empty")
        self._platform = value

    def get_course_info(self) -> str:
        """
        Повертає інформацію про онлайн-курс.
        """
        return f"{self.title} is available on {self.platform}"

    def __str__(self) -> str:
        return f"OnlineCourse({self.title} on {self.platform})"
