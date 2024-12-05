from models.course import Course

class OnsiteCourse(Course):
    """
    Клас, що представляє очний курс.
    """

    def __init__(self, course_id: str, title: str, description: str, location: str):
        super().__init__(course_id, title, description)
        self.location = location

    def get_course_info(self) -> str:
        """
        Повертає інформацію про очний курс.
        """
        return f"{self.title} is held at {self.location}"
