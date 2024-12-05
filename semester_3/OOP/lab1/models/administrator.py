from models.person import Person

class Administrator(Person):
    """
    Класс, представляющий администратора системы.
    """

    def __init__(self, name: str, surname: str, email: str, admin_id: int):
        super().__init__(name, surname, email)
        self._admin_id = admin_id

    def create_course(self, course_id: str, title: str, description: str) -> 'Course':
        """
        Создает новый курс.
        """
        new_course = Course(course_id, title, description)
        print(f"Курс '{title}' создан администратором {self.get_full_name()}")
        return new_course

    def assign_teacher_to_course(self, teacher: 'Teacher', course: 'Course'):
        """
        Назначает преподавателя на курс.
        """
        teacher.add_course(course)
        print(f"Преподаватель {teacher.get_full_name()} назначен на курс {course.title}")

from models.course import Course  # Избегаем циклического импорта
