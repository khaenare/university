from models.administrator import Administrator
from models.teacher import Teacher
from models.student import Student
from models.online_course import OnlineCourse
from models.onsite_course import OnsiteCourse
from models.schedule import Schedule

class SystemInterface:
    def __init__(self):
        self.administrators = []
        self.teachers = []
        self.students = []
        self.courses = []
        self.schedule = Schedule()
        self.current_user = None

        # Инициализируем систему с одним администратором
        self.setup_initial_data()

    def setup_initial_data(self):
        # Создаем администратора по умолчанию
        admin = Administrator("Admin", "Adminov", "admin@example.com", 1)
        self.administrators.append(admin)

    def run(self):
        while True:
            print("\nWelcome to the University Management System")
            print("1. Login")
            print("2. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                self.login()
            elif choice == '2':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def login(self):
        print("\nLogin")
        print("Select role:")
        print("1. Administrator")
        print("2. Teacher")
        print("3. Student")
        role_choice = input("Select your role: ")

        if role_choice == '1':
            self.admin_menu()
        elif role_choice == '2':
            self.teacher_menu()
        elif role_choice == '3':
            self.student_menu()
        else:
            print("Invalid role. Please try again.")


#------------------------------------------------------------------
  

    def admin_menu(self):
        # Добавим новые пункты меню
        while True:
            print(f"\nAdministrator Menu ({self.current_user.get_full_name()})")
            print("1. Create Course")
            print("2. Assign Teacher to Course")
            print("3. Register Teacher")
            print("4. Register Student")
            print("5. View Courses")
            print("6. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                self.create_course()
            elif choice == '2':
                self.assign_teacher_to_course()
            elif choice == '3':
                self.register_teacher()
            elif choice == '4':
                self.register_student()
            elif choice == '5':
                self.view_courses()
            elif choice == '6':
                self.current_user = None
                break
            else:
                print("Invalid choice. Please try again.")

      def register_teacher(self):
        print("\nRegister Teacher")
        name = input("Enter first name: ")
        surname = input("Enter last name: ")
        email = input("Enter email: ")
        teacher_id = len(self.teachers) + 1
        teacher = Teacher(name, surname, email, teacher_id)
        self.teachers.append(teacher)
        print(f"Teacher '{teacher.get_full_name()}' registered successfully with ID {teacher_id}.")

    def register_student(self):
        print("\nRegister Student")
        name = input("Enter first name: ")
        surname = input("Enter last name: ")
        email = input("Enter email: ")
        student_id = len(self.students) + 1
        student = Student(name, surname, email, student_id)
        self.students.append(student)
        print(f"Student '{student.get_full_name()}' registered successfully with ID {student_id}.")


    def create_course(self):
        print("\nCreate Course")
        course_id = input("Enter course ID: ")
        title = input("Enter course title: ")
        description = input("Enter course description: ")
        course_type = input("Enter course type (online/onsite): ")

        if course_type.lower() == 'online':
            platform = input("Enter platform: ")
            course = OnlineCourse(course_id, title, description, platform)
        elif course_type.lower() == 'onsite':
            location = input("Enter location: ")
            course = OnsiteCourse(course_id, title, description, location)
        else:
            print("Invalid course type.")
            return

        self.courses.append(course)
        print(f"Course '{title}' created successfully.")

    def assign_teacher_to_course(self):
        print("\nAssign Teacher to Course")
        if not self.teachers:
            print("No teachers available.")
            return
        if not self.courses:
            print("No courses available.")
            return

        self.view_teachers()
        teacher_id = input("Enter teacher ID: ")
        teacher = self.get_teacher_by_id(int(teacher_id))
        if not teacher:
            print("Teacher not found.")
            return

        self.view_courses()
        course_id = input("Enter course ID: ")
        course = self.get_course_by_id(course_id)
        if not course:
            print("Course not found.")
            return

        self.current_user.assign_teacher_to_course(teacher, course)

    def view_courses(self):
        print("\nCourses:")
        for course in self.courses:
            print(f"- {course.course_id}: {course.title} ({'Online' if isinstance(course, OnlineCourse) else 'Onsite'})")

    def view_teachers(self):
        print("\nTeachers:")
        for teacher in self.teachers:
            print(f"- {teacher._teacher_id}: {teacher.get_full_name()}")

    def get_teacher_by_id(self, teacher_id):
        for teacher in self.teachers:
            if teacher._teacher_id == teacher_id:
                return teacher
        return None

    def get_course_by_id(self, course_id):
        for course in self.courses:
            if course.course_id == course_id:
                return course
        return None

#------------------------------------------------------------------


    def teacher_menu(self):
        if not self.teachers:
            print("No teachers registered.")
            return

        self.view_teachers()
        teacher_id = input("Enter your teacher ID: ")
        teacher = self.get_teacher_by_id(int(teacher_id))
        if not teacher:
            print("Teacher not found.")
            return

        self.current_user = teacher
        while True:
            print(f"\nTeacher Menu ({self.current_user.get_full_name()})")
            print("1. Create Assignment")
            print("2. Assign Grade")
            print("3. View Courses")
            print("4. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                self.create_assignment()
            elif choice == '2':
                self.assign_grade()
            elif choice == '3':
                self.view_teacher_courses()
            elif choice == '4':
                self.current_user = None
                break
            else:
                print("Invalid choice. Please try again.")

    def create_assignment(self):
        print("\nCreate Assignment")
        if not self.current_user._courses_taught:
            print("You are not assigned to any courses.")
            return

        self.view_teacher_courses()
        course_id = input("Enter course ID: ")
        course = self.get_course_by_id(course_id)
        if not course or course not in self.current_user._courses_taught:
            print("Invalid course.")
            return

        title = input("Enter assignment title: ")
        due_date = input("Enter due date (YYYY-MM-DD): ")
        max_grade = float(input("Enter max grade: "))
        self.current_user.create_assignment(course, title, due_date, max_grade)

    def assign_grade(self):
        print("\nAssign Grade")
        if not self.current_user._courses_taught:
            print("You are not assigned to any courses.")
            return

        self.view_teacher_courses()
        course_id = input("Enter course ID: ")
        course = self.get_course_by_id(course_id)
        if not course or course not in self.current_user._courses_taught:
            print("Invalid course.")
            return

        if not course.students:
            print("No students enrolled in this course.")
            return

        print("\nStudents:")
        for student in course.students:
            print(f"- {student._student_id}: {student.get_full_name()}")

        student_id = int(input("Enter student ID: "))
        student = self.get_student_by_id(student_id)
        if not student or student not in course.students:
            print("Invalid student.")
            return

        grade_value = float(input("Enter grade value: "))
        self.current_user.assign_grade(student, course, grade_value)

    def view_teacher_courses(self):
        print("\nYour Courses:")
        for course in self.current_user._courses_taught:
            print(f"- {course.course_id}: {course.title}")




#------------------------------------------------------------------




    def student_menu(self):
        if not self.students:
            print("No students registered.")
            return

        self.view_students()
        student_id = input("Enter your student ID: ")
        student = self.get_student_by_id(int(student_id))
        if not student:
            print("Student not found.")
            return

        self.current_user = student
        while True:
            print(f"\nStudent Menu ({self.current_user.get_full_name()})")
            print("1. Enroll in Course")
            print("2. View Enrolled Courses")
            print("3. View Grades")
            print("4. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                self.enroll_in_course()
            elif choice == '2':
                self.view_student_courses()
            elif choice == '3':
                self.view_student_grades()
            elif choice == '4':
                self.current_user = None
                break
            else:
                print("Invalid choice. Please try again.")

    def enroll_in_course(self):
        print("\nAvailable Courses:")
        for course in self.courses:
            if self.current_user not in course.students:
                print(f"- {course.course_id}: {course.title}")
        course_id = input("Enter course ID to enroll: ")
        course = self.get_course_by_id(course_id)
        if not course:
            print("Course not found.")
            return

        self.current_user.enroll_course(course)

    def view_student_courses(self):
        print("\nYour Courses:")
        for course in self.current_user._courses:
            print(f"- {course.course_id}: {course.title}")

    def view_student_grades(self):
        print("\nYour Grades:")
        grades = self.current_user.get_grades()
        if not grades:
            print("No grades available.")
        else:
            for course_title, grade in grades.items():
                print(f"- {course_title}: {grade}")

    def view_students(self):
        print("\nStudents:")
        for student in self.students:
            print(f"- {student._student_id}: {student.get_full_name()}")

    def get_student_by_id(self, student_id):
        for student in self.students:
            if student._student_id == student_id:
                return student
        return None
