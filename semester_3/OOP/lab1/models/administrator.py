from models.person import Person
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.course import Course
    from models.teacher import Teacher

class Administrator(Person):
    """
    Клас, що представляє адміністратора системи.
    """

    def __init__(self, name: str, surname: str, email: str, admin_id: int):
        super().__init__(name, surname, email)
        self._admin_id = admin_id

    def create_course(self, course_id: str, title: str, description: str) -> 'Course':
        """
        Створює новий курс.
        """
        new_course = Course(course_id, title, description)
        print(f"Course '{title}' created by administrator {self.get_full_name()}")
        return new_course

    def assign_teacher_to_course(self, teacher: 'Teacher', course: 'Course'):
        """
        Призначає викладача на курс.
        """
        teacher.add_course(course)
        print(f"Teacher {teacher.get_full_name()} assigned to course {course.title}")
