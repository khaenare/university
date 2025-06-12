from models.course import Course

class OnsiteCourse(Course):
    """
    Клас, що представляє очний курс.
    """

    def __init__(self, course_id: str, title: str, description: str, location: str):
        super().__init__(course_id, title, description)
        self._location = location

    @property
    def location(self) -> str:
        return self._location

    @location.setter
    def location(self, value: str):
        if not value:
            raise ValueError("Location cannot be empty")
        self._location = value

    def get_course_info(self) -> str:
        """
        Повертає інформацію про очний курс.
        """
        return f"{self.title} is held at {self.location}"

    def __str__(self) -> str:
        return f"OnsiteCourse({self.title} at {self.location})"
