from models.person import Person
from models.course import Course
from typing import List, Dict

class Student(Person):
    """
    Класс, представляющий студента.
    """

    def __init__(self, name: str, surname: str, email: str, student_id: int):
        super().__init__(name, surname, email)
        self._student_id = student_id
        self._courses: List[Course] = []
        self._grades: Dict[str, float] = {}

    def enroll_course(self, course: 'Course'):
        """
        Записывает студента на курс.
        """
        if course not in self._courses:
            self._courses.append(course)
            course.add_student(self)
        else:
            print(f"Студент уже записан на курс {course.title}")

    def submit_assignment(self, assignment_id: int, submission: str):
        """
        Отправляет решение задания.
        """
        # Здесь можно реализовать логику отправки задания
        print(f"Задание {assignment_id} отправлено студентом {self.get_full_name()}")

    def calculate_gpa(self) -> float:
        """
        Вычисляет средний балл студента.
        """
        if not self._grades:
            return 0.0
        total = sum(self._grades.values())
        return total / len(self._grades)

    def add_grade(self, course_title: str, grade_value: float):
        """
        Добавляет оценку по курсу.
        """
        self._grades[course_title] = grade_value

    def get_grades(self) -> Dict[str, float]:
        """
        Возвращает словарь оценок студента.
        """
        return self._grades
