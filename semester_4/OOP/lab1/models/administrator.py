from models.person import Person
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from models.course import Course
    from models.teacher import Teacher
    from models.student import Student

class Administrator(Person):
    """
    Клас, що представляє адміністратора системи.
    """

    def __init__(self, name: str, surname: str, email: str, admin_id: int):
        super().__init__(name, surname, email)
        self._admin_id = admin_id
        self._courses: List['Course'] = []
        self._teachers: List['Teacher'] = []
        self._students: List['Student'] = []

    @property
    def admin_id(self) -> int:
        return self._admin_id

    def create_course(self, course_id: str, title: str, description: str) -> 'Course':
        """
        Створює новий курс.
        """
        from models.course import Course
        course = Course(course_id, title, description)
        self._courses.append(course)
        return course

    def assign_teacher_to_course(self, teacher: 'Teacher', course: 'Course') -> str:
        """
        Призначає викладача на курс.
        """
        teacher.add_course(course)
        return f"Teacher {teacher.get_full_name()} assigned to course {course.title}"

    def add_course(self, course: 'Course') -> str:
        """
        Додає курс у систему, якщо його ще немає.
        """
        if course not in self._courses:
            self._courses.append(course)
            return f"Course {course.title} added."
        return f"Course {course.title} already exists."

    def add_teacher(self, teacher: 'Teacher') -> str:
        """
        Додає викладача у систему, якщо його ще немає.
        """
        if teacher not in self._teachers:
            self._teachers.append(teacher)
            return f"Teacher {teacher.get_full_name()} added."
        return f"Teacher {teacher.get_full_name()} already exists."

    def register_student(self, student: 'Student') -> str:
        """
        Реєструє студента в системі, якщо його ще не зареєстровано.
        """
        if student not in self._students:
            self._students.append(student)
            return f"Student {student.get_full_name()} registered."
        return f"Student {student.get_full_name()} is already registered."

    @property
    def courses(self) -> List['Course']:
        return self._courses

    @property
    def teachers(self) -> List['Teacher']:
        return self._teachers

    @property
    def students(self) -> List['Student']:
        return self._students
