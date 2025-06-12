import unittest
from models.administrator import Administrator
from models.course import Course
from models.teacher import Teacher
from models.student import Student

class TestAdministrator(unittest.TestCase):
    def test_add_course(self):
        admin = Administrator("Admin", "Root", "admin@example.com", 999)
        course = Course(301, "Programming", "Python basics")
        admin.add_course(course)
        self.assertIn(course, admin.courses)

    def test_add_teacher(self):
        admin = Administrator("Admin", "Root", "admin@example.com", 999)
        teacher = Teacher("Alan", "Turing", "turing@example.com", 10)
        admin.add_teacher(teacher)
        self.assertIn(teacher, admin.teachers)

    def test_register_student(self):
        admin = Administrator("Admin", "Root", "admin@example.com", 999)
        student = Student("Ada", "Lovelace", "ada@example.com", 20)
        admin.register_student(student)
        self.assertIn(student, admin.students)

    def test_multiple_registrations(self):
        admin = Administrator("Admin", "Root", "admin@example.com", 999)

        c1 = Course(1, "Math", "Algebra")
        c2 = Course(2, "Biology", "Cells")

        admin.add_course(c1)
        admin.add_course(c2)

        self.assertEqual(len(admin.courses), 2)
        self.assertEqual(admin.courses[0].title, "Math")
        self.assertEqual(admin.courses[1].title, "Biology")

if __name__ == '__main__':
    unittest.main()
