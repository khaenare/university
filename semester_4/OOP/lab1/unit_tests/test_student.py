import unittest
from models.student import Student
from models.course import Course
from models.assignment import Assignment
from models.grade import Grade

class TestStudent(unittest.TestCase):
    def test_enroll_and_calculate_gpa(self):
        student = Student("John", "Doe", "john@example.com", 1)
        course = Course(101, "Math", "Basic math course")
        assignment = Assignment(1, "Test Assignment", "2025-12-01", 100)

        grade1 = Grade(student, assignment, 90)
        grade2 = Grade(student, assignment, 80)

        student.enroll_course(course)
        student.add_grade(course, grade1)
        student.add_grade(course, grade2)

        gpa = student.calculate_gpa()
        self.assertEqual(gpa, 85.0)

    def test_gpa_no_grades(self):
        student = Student("Jane", "Smith", "jane@example.com", 2)
        gpa = student.calculate_gpa()
        self.assertEqual(gpa, 0.0)

    def test_enroll_course_twice(self):
        student = Student("Alex", "Brown", "alex@example.com", 3)
        course = Course(102, "Science", "Science course")
        student.enroll_course(course)
        student.enroll_course(course)
        self.assertEqual(len(student._courses), 1)

    def test_view_assignments(self):
        student = Student("Eva", "White", "eva@example.com", 4)
        course = Course(103, "History", "History course")
        assignment = Assignment(1, "Essay", "2025-11-30", 100)

        course.assignments.append(assignment)
        student.enroll_course(course)

        try:
            student.view_assignments()
        except Exception as e:
            self.fail(f"view_assignments() raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
