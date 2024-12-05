from models.course import Course

class OnsiteCourse(Course):
    """
    Класс, представляющий очный курс.
    """

    def __init__(self, course_id: str, title: str, description: str, location: str):
        super().__init__(course_id, title, description)
        self.location = location

    def get_course_info(self) -> str:
        """
        Возвращает информацию об очном курсе.
        """
        return f"{self.title} проводится в {self.location}"
