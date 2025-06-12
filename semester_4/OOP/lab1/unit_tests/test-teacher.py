import unittest
from models.teacher import Teacher
from models.course import Course
from models.assignment import Assignment
from models.student import Student
from models.grade import Grade

class TestTeacher(unittest.TestCase):
    def test_add_course(self):
        teacher = Teacher("Anna", "Grey", "anna@example.com", 1)
        course = Course(201, "Physics", "Physics course")
        teacher.add_course(course)
        self.assertIn(course, teacher._courses_taught)
        self.assertEqual(course.teacher, teacher)

    def test_create_assignment(self):
        teacher = Teacher("Mike", "Green", "mike@example.com", 2)
        course = Course(202, "Biology", "Bio course")
        teacher.add_course(course)

        assignment = teacher.create_assignment(course, "Lab Report", "2025-10-15", 100)
        self.assertEqual(len(course.assignments), 1)
        self.assertEqual(course.assignments[0].title, "Lab Report")
        self.assertEqual(assignment.assignment_id, 1)


    def test_assign_grade_for_assignment(self):
        teacher = Teacher("Max", "Red", "max@example.com", 4)
        student = Student("Lucy", "Pink", "lucy@example.com", 6)
        course = Course(204, "History", "Hist course")

        teacher.add_course(course)
        assignment = teacher.create_assignment(course, "Essay", "2025-11-30", 50)
        student.enroll_course(course)

        teacher.assign_grade_for_assignment(student, course, assignment.assignment_id, 47.0)
        self.assertEqual(assignment.grades[student.student_id], 47.0)

if __name__ == '__main__':
    unittest.main()
