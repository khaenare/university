import tkinter as tk
from tkinter import messagebox, ttk
from models.administrator import Administrator
from models.teacher import Teacher
from models.student import Student
from models.online_course import OnlineCourse
from models.onsite_course import OnsiteCourse

class UniversityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Management System")

        # Ініціалізація даних
        self.administrators = [Administrator("Admin", "Adminov", "admin@example.com", 1)]
        self.teachers = []
        self.students = []
        self.courses = []
        self.current_user = None

        # Головне вікно
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()
        self.create_main_window()

    def create_main_window(self):
        # Очищення вікна
        self.clear_window()
        label = tk.Label(self.main_frame, text="Select your role:", font=("Arial", 16))
        label.pack(pady=20)

        # Кнопки вибору ролі
        admin_btn = tk.Button(self.main_frame, text="Administrator", width=20, command=self.admin_login)
        teacher_btn = tk.Button(self.main_frame, text="Teacher", width=20, command=self.teacher_login)
        student_btn = tk.Button(self.main_frame, text="Student", width=20, command=self.student_login)
        exit_btn = tk.Button(self.main_frame, text="Exit", width=20, command=self.root.quit)

        admin_btn.pack(pady=5)
        teacher_btn.pack(pady=5)
        student_btn.pack(pady=5)
        exit_btn.pack(pady=5)

    def clear_window(self):
        # Видалення всіх віджетів з головного фрейму
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Адміністратор
    def admin_login(self):
        # Вхід як адміністратор
        self.current_user = self.administrators[0]
        self.create_admin_menu()

    def create_admin_menu(self):
        # Створення меню адміністратора
        self.clear_window()
        label = tk.Label(self.main_frame, text=f"Administrator Menu ({self.current_user.get_full_name()})",
                         font=("Arial", 16))
        label.pack(pady=20)

        register_teacher_btn = tk.Button(self.main_frame, text="Register Teacher", width=30,
                                         command=self.register_teacher)
        register_student_btn = tk.Button(self.main_frame, text="Register Student", width=30,
                                         command=self.register_student)
        create_course_btn = tk.Button(self.main_frame, text="Create Course", width=30, command=self.create_course)
        assign_teacher_btn = tk.Button(self.main_frame, text="Assign Teacher to Course", width=30,
                                       command=self.assign_teacher_to_course)
        view_courses_btn = tk.Button(self.main_frame, text="View Courses", width=30, command=self.view_courses)
        logout_btn = tk.Button(self.main_frame, text="Logout", width=30, command=self.logout)

        create_course_btn.pack(pady=5)
        assign_teacher_btn.pack(pady=5)
        register_teacher_btn.pack(pady=5)
        register_student_btn.pack(pady=5)
        view_courses_btn.pack(pady=5)
        logout_btn.pack(pady=5)

    def register_teacher(self):
        # Реєстрація викладача
        self.clear_window()
        label = tk.Label(self.main_frame, text="Register Teacher", font=("Arial", 16))
        label.pack(pady=10)

        name_label = tk.Label(self.main_frame, text="First Name:")
        name_entry = tk.Entry(self.main_frame)
        surname_label = tk.Label(self.main_frame, text="Last Name:")
        surname_entry = tk.Entry(self.main_frame)
        email_label = tk.Label(self.main_frame, text="Email:")
        email_entry = tk.Entry(self.main_frame)

        name_label.pack()
        name_entry.pack()
        surname_label.pack()
        surname_entry.pack()
        email_label.pack()
        email_entry.pack()

        register_btn = tk.Button(self.main_frame, text="Register", command=lambda: self.submit_register_teacher(
            name_entry.get(), surname_entry.get(), email_entry.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_admin_menu)

        register_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_register_teacher(self, name, surname, email):
        # Підтвердження реєстрації викладача
        teacher_id = len(self.teachers) + 1
        teacher = Teacher(name, surname, email, teacher_id)
        self.teachers.append(teacher)
        messagebox.showinfo("Success",
                            f"Teacher '{teacher.get_full_name()}' registered successfully with ID {teacher_id}.")
        self.create_admin_menu()

    def register_student(self):
        # Реєстрація студента
        self.clear_window()
        label = tk.Label(self.main_frame, text="Register Student", font=("Arial", 16))
        label.pack(pady=10)

        name_label = tk.Label(self.main_frame, text="First Name:")
        name_entry = tk.Entry(self.main_frame)
        surname_label = tk.Label(self.main_frame, text="Last Name:")
        surname_entry = tk.Entry(self.main_frame)
        email_label = tk.Label(self.main_frame, text="Email:")
        email_entry = tk.Entry(self.main_frame)

        name_label.pack()
        name_entry.pack()
        surname_label.pack()
        surname_entry.pack()
        email_label.pack()
        email_entry.pack()

        register_btn = tk.Button(self.main_frame, text="Register", command=lambda: self.submit_register_student(
            name_entry.get(), surname_entry.get(), email_entry.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_admin_menu)

        register_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_register_student(self, name, surname, email):
        # Підтвердження реєстрації студента
        student_id = len(self.students) + 1
        student = Student(name, surname, email, student_id)
        self.students.append(student)
        messagebox.showinfo("Success",
                            f"Student '{student.get_full_name()}' registered successfully with ID {student_id}.")
        self.create_admin_menu()

    def create_course(self):
        # Створення курсу
        self.clear_window()
        label = tk.Label(self.main_frame, text="Create Course", font=("Arial", 16))
        label.pack(pady=10)

        course_id_label = tk.Label(self.main_frame, text="Course ID:")
        course_id_entry = tk.Entry(self.main_frame)
        title_label = tk.Label(self.main_frame, text="Title:")
        title_entry = tk.Entry(self.main_frame)
        description_label = tk.Label(self.main_frame, text="Description:")
        description_entry = tk.Entry(self.main_frame)
        type_label = tk.Label(self.main_frame, text="Type (online/onsite):")
        type_entry = tk.Entry(self.main_frame)

        course_id_label.pack()
        course_id_entry.pack()
        title_label.pack()
        title_entry.pack()
        description_label.pack()
        description_entry.pack()
        type_label.pack()
        type_entry.pack()

        submit_btn = tk.Button(self.main_frame, text="Create", command=lambda: self.submit_create_course(
            course_id_entry.get(), title_entry.get(), description_entry.get(), type_entry.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_admin_menu)

        submit_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_create_course(self, course_id, title, description, course_type):
        # Підтвердження створення курсу
        if course_type.lower() == 'online':
            platform = "Online Platform"
            course = OnlineCourse(course_id, title, description, platform)
        elif course_type.lower() == 'onsite':
            location = "Campus"
            course = OnsiteCourse(course_id, title, description, location)
        else:
            messagebox.showerror("Error", "Invalid course type.")
            return

        self.courses.append(course)
        messagebox.showinfo("Success", f"Course '{title}' created successfully.")
        self.create_admin_menu()

    def assign_teacher_to_course(self):
        # Призначення викладача на курс
        self.clear_window()
        label = tk.Label(self.main_frame, text="Assign Teacher to Course", font=("Arial", 16))
        label.pack(pady=10)

        if not self.teachers:
            messagebox.showerror("Error", "No teachers available.")
            self.create_admin_menu()
            return
        if not self.courses:
            messagebox.showerror("Error", "No courses available.")
            self.create_admin_menu()
            return

        teacher_label = tk.Label(self.main_frame, text="Select Teacher:")
        teacher_label.pack()
        teacher_var = tk.StringVar()
        teacher_menu = ttk.Combobox(self.main_frame, textvariable=teacher_var)
        teacher_menu['values'] = [f"{t._teacher_id}: {t.get_full_name()}" for t in self.teachers]
        teacher_menu.pack()

        course_label = tk.Label(self.main_frame, text="Select Course:")
        course_label.pack()
        course_var = tk.StringVar()
        course_menu = ttk.Combobox(self.main_frame, textvariable=course_var)
        course_menu['values'] = [f"{c.course_id}: {c.title}" for c in self.courses]
        course_menu.pack()

        assign_btn = tk.Button(self.main_frame, text="Assign",
                               command=lambda: self.submit_assign_teacher(teacher_var.get(), course_var.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_admin_menu)

        assign_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_assign_teacher(self, teacher_info, course_info):
        # Підтвердження призначення викладача
        try:
            teacher_id = int(teacher_info.split(":")[0])
            course_id = course_info.split(":")[0]
            teacher = self.get_teacher_by_id(teacher_id)
            course = self.get_course_by_id(course_id)
            if teacher and course:
                self.current_user.assign_teacher_to_course(teacher, course)
                messagebox.showinfo("Success", f"Teacher {teacher.get_full_name()} assigned to course {course.title}.")
            else:
                messagebox.showerror("Error", "Invalid teacher or course.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self.create_admin_menu()

    def view_courses(self):
        # Перегляд курсів
        self.clear_window()
        label = tk.Label(self.main_frame, text="Courses", font=("Arial", 16))
        label.pack(pady=10)

        courses_list = tk.Listbox(self.main_frame, width=50)
        for course in self.courses:
            course_type = "Online" if isinstance(course, OnlineCourse) else "Onsite"
            courses_list.insert(tk.END, f"{course.course_id}: {course.title} ({course_type})")
        courses_list.pack()

        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_admin_menu)
        back_btn.pack(pady=5)


    #-----------------------------------------------------------------------------------------------------
    # Викладач
    def teacher_login(self):
        # Вікно входу для викладача
        self.clear_window()
        label = tk.Label(self.main_frame, text="Teacher Login", font=("Arial", 16))
        label.pack(pady=10)

        if not self.teachers:
            messagebox.showerror("Error", "No teachers registered.")
            self.create_main_window()
            return

        # Вибір викладача зі списку зареєстрованих
        teacher_label = tk.Label(self.main_frame, text="Select your ID:")
        teacher_label.pack()
        teacher_var = tk.StringVar()
        teacher_menu = ttk.Combobox(self.main_frame, textvariable=teacher_var)
        teacher_menu['values'] = [f"{t._teacher_id}: {t.get_full_name()}" for t in self.teachers]
        teacher_menu.pack()

        login_btn = tk.Button(self.main_frame, text="Login",
                              command=lambda: self.submit_teacher_login(teacher_var.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_main_window)

        login_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_teacher_login(self, teacher_info):
        # Обробка входу викладача
        try:
            teacher_id = int(teacher_info.split(":")[0])
            teacher = self.get_teacher_by_id(teacher_id)
            if teacher:
                self.current_user = teacher
                self.create_teacher_menu()
            else:
                messagebox.showerror("Error", "Teacher not found.")
                self.create_main_window()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_main_window()

    def create_teacher_menu(self):
        # Створення меню викладача
        self.clear_window()
        label = tk.Label(self.main_frame, text=f"Teacher Menu ({self.current_user.get_full_name()})",
                         font=("Arial", 16))
        label.pack(pady=20)

        create_assignment_btn = tk.Button(self.main_frame, text="Create Assignment", width=30,
                                          command=self.create_assignment)
        assign_grade_btn = tk.Button(self.main_frame, text="Assign Grade", width=30, command=self.assign_grade)
        assign_grade_assignment_btn = tk.Button(self.main_frame, text="Assign Grade for Assignment", width=30,
                                                command=self.assign_grade_for_assignment)
        view_courses_btn = tk.Button(self.main_frame, text="View Courses", width=30, command=self.view_teacher_courses)
        logout_btn = tk.Button(self.main_frame, text="Logout", width=30, command=self.logout)

        create_assignment_btn.pack(pady=5)
        assign_grade_btn.pack(pady=5)
        assign_grade_assignment_btn.pack(pady=5)
        view_courses_btn.pack(pady=5)
        logout_btn.pack(pady=5)

    # Методи для викладача
    def create_assignment(self):
        # Створення завдання
        self.clear_window()
        label = tk.Label(self.main_frame, text="Create Assignment", font=("Arial", 16))
        label.pack(pady=10)

        if not self.current_user._courses_taught:
            messagebox.showerror("Error", "You are not assigned to any courses.")
            self.create_teacher_menu()
            return

        # Вибір курсу
        course_label = tk.Label(self.main_frame, text="Select Course:")
        course_label.pack()
        course_var = tk.StringVar()
        course_menu = ttk.Combobox(self.main_frame, textvariable=course_var)
        course_menu['values'] = [f"{c.course_id}: {c.title}" for c in self.current_user._courses_taught]
        course_menu.pack()

        # Поля для введення деталей завдання
        title_label = tk.Label(self.main_frame, text="Assignment Title:")
        title_entry = tk.Entry(self.main_frame)
        due_date_label = tk.Label(self.main_frame, text="Due Date (YYYY-MM-DD):")
        due_date_entry = tk.Entry(self.main_frame)
        max_grade_label = tk.Label(self.main_frame, text="Max Grade:")
        max_grade_entry = tk.Entry(self.main_frame)

        title_label.pack()
        title_entry.pack()
        due_date_label.pack()
        due_date_entry.pack()
        max_grade_label.pack()
        max_grade_entry.pack()

        create_btn = tk.Button(self.main_frame, text="Create", command=lambda: self.submit_create_assignment(
            course_var.get(), title_entry.get(), due_date_entry.get(), max_grade_entry.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_teacher_menu)

        create_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_create_assignment(self, course_info, title, due_date, max_grade):
        # Підтвердження створення завдання
        try:
            course_id = course_info.split(":")[0]
            course = self.get_course_by_id(course_id)
            if not course:
                messagebox.showerror("Error", "Course not found.")
                self.create_teacher_menu()
                return

            assignment_id = len(course.assignments) + 1
            assignment = Assignment(assignment_id, title, due_date, float(max_grade))
            course.add_assignment(assignment)
            messagebox.showinfo("Success", f"Assignment '{title}' created for course {course.title}.")
            self.create_teacher_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_teacher_menu()

    def assign_grade(self):
        # Виставлення оцінки за курс
        self.clear_window()
        label = tk.Label(self.main_frame, text="Assign Grade", font=("Arial", 16))
        label.pack(pady=10)

        if not self.current_user._courses_taught:
            messagebox.showerror("Error", "You are not assigned to any courses.")
            self.create_teacher_menu()
            return

        # Вибір курсу
        course_label = tk.Label(self.main_frame, text="Select Course:")
        course_label.pack()
        course_var = tk.StringVar()
        course_menu = ttk.Combobox(self.main_frame, textvariable=course_var)
        course_menu['values'] = [f"{c.course_id}: {c.title}" for c in self.current_user._courses_taught]
        course_menu.pack()

        assign_btn = tk.Button(self.main_frame, text="Next",
                               command=lambda: self.select_student_for_grade(course_var.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_teacher_menu)

        assign_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def select_student_for_grade(self, course_info):
        # Вибір студента для виставлення оцінки
        try:
            course_id = course_info.split(":")[0]
            course = self.get_course_by_id(course_id)
            if not course:
                messagebox.showerror("Error", "Course not found.")
                self.create_teacher_menu()
                return

            if not course.students:
                messagebox.showerror("Error", "No students enrolled in this course.")
                self.create_teacher_menu()
                return

            self.clear_window()
            label = tk.Label(self.main_frame, text="Select Student", font=("Arial", 16))
            label.pack(pady=10)

            student_label = tk.Label(self.main_frame, text="Select Student:")
            student_label.pack()
            student_var = tk.StringVar()
            student_menu = ttk.Combobox(self.main_frame, textvariable=student_var)
            student_menu['values'] = [f"{s._student_id}: {s.get_full_name()}" for s in course.students]
            student_menu.pack()

            grade_label = tk.Label(self.main_frame, text="Enter Grade:")
            grade_entry = tk.Entry(self.main_frame)
            grade_label.pack()
            grade_entry.pack()

            submit_btn = tk.Button(self.main_frame, text="Assign Grade", command=lambda: self.submit_assign_grade(
                student_var.get(), course_id, grade_entry.get()))
            back_btn = tk.Button(self.main_frame, text="Back", command=self.create_teacher_menu)

            submit_btn.pack(pady=5)
            back_btn.pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_teacher_menu()

    def submit_assign_grade(self, student_info, course_id, grade_value):
        # Підтвердження виставлення оцінки
        try:
            student_id = int(student_info.split(":")[0])
            student = self.get_student_by_id(student_id)
            course = self.get_course_by_id(course_id)
            if student and course:
                self.current_user.assign_grade(student, course, float(grade_value))
                messagebox.showinfo("Success",
                                    f"Grade {grade_value} assigned to {student.get_full_name()} for course {course.title}.")
            else:
                messagebox.showerror("Error", "Invalid student or course.")
            self.create_teacher_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_teacher_menu()

    def assign_grade_for_assignment(self):
        # Виставлення оцінки за завдання
        self.clear_window()
        label = tk.Label(self.main_frame, text="Assign Grade for Assignment", font=("Arial", 16))
        label.pack(pady=10)

        if not self.current_user._courses_taught:
            messagebox.showerror("Error", "You are not assigned to any courses.")
            self.create_teacher_menu()
            return

        # Вибір курсу
        course_label = tk.Label(self.main_frame, text="Select Course:")
        course_label.pack()
        course_var = tk.StringVar()
        course_menu = ttk.Combobox(self.main_frame, textvariable=course_var)
        course_menu['values'] = [f"{c.course_id}: {c.title}" for c in self.current_user._courses_taught]
        course_menu.pack()

        next_btn = tk.Button(self.main_frame, text="Next",
                             command=lambda: self.select_assignment_for_grade(course_var.get()))
        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_teacher_menu)

        next_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def select_assignment_for_grade(self, course_info):
        # Вибір завдання
        try:
            course_id = course_info.split(":")[0]
            course = self.get_course_by_id(course_id)
            if not course:
                messagebox.showerror("Error", "Course not found.")
                self.create_teacher_menu()
                return

            if not course.assignments:
                messagebox.showerror("Error", "No assignments in this course.")
                self.create_teacher_menu()
                return

            self.clear_window()
            label = tk.Label(self.main_frame, text="Select Assignment", font=("Arial", 16))
            label.pack(pady=10)

            assignment_label = tk.Label(self.main_frame, text="Select Assignment:")
            assignment_label.pack()
            assignment_var = tk.StringVar()
            assignment_menu = ttk.Combobox(self.main_frame, textvariable=assignment_var)
            assignment_menu['values'] = [f"{a.assignment_id}: {a.title}" for a in course.assignments]
            assignment_menu.pack()

            next_btn = tk.Button(self.main_frame, text="Next",
                                 command=lambda: self.select_student_for_assignment_grade(course_id,
                                                                                          assignment_var.get()))
            back_btn = tk.Button(self.main_frame, text="Back", command=self.create_teacher_menu)

            next_btn.pack(pady=5)
            back_btn.pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_teacher_menu()

    def select_student_for_assignment_grade(self, course_id, assignment_info):
        # Вибір студента для виставлення оцінки за завдання
        try:
            assignment_id = int(assignment_info.split(":")[0])
            course = self.get_course_by_id(course_id)
            assignment = next((a for a in course.assignments if a.assignment_id == assignment_id), None)
            if not assignment:
                messagebox.showerror("Error", "Assignment not found.")
                self.create_teacher_menu()
                return

            if not course.students:
                messagebox.showerror("Error", "No students enrolled in this course.")
                self.create_teacher_menu()
                return

            self.clear_window()
            label = tk.Label(self.main_frame, text="Select Student", font=("Arial", 16))
            label.pack(pady=10)

            student_label = tk.Label(self.main_frame, text="Select Student:")
            student_label.pack()
            student_var = tk.StringVar()
            student_menu = ttk.Combobox(self.main_frame, textvariable=student_var)
            student_menu['values'] = [f"{s._student_id}: {s.get_full_name()}" for s in course.students]
            student_menu.pack()

            grade_label = tk.Label(self.main_frame, text="Enter Grade:")
            grade_entry = tk.Entry(self.main_frame)
            grade_label.pack()
            grade_entry.pack()

            submit_btn = tk.Button(self.main_frame, text="Assign Grade",
                                   command=lambda: self.submit_assign_grade_for_assignment(
                                       student_var.get(), course_id, assignment_id, grade_entry.get()))
            back_btn = tk.Button(self.main_frame, text="Back", command=self.create_teacher_menu)

            submit_btn.pack(pady=5)
            back_btn.pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_teacher_menu()

    def submit_assign_grade_for_assignment(self, student_info, course_id, assignment_id, grade_value):
        # Підтвердження виставлення оцінки за завдання
        try:
            student_id = int(student_info.split(":")[0])
            student = self.get_student_by_id(student_id)
            course = self.get_course_by_id(course_id)
            assignment = next((a for a in course.assignments if a.assignment_id == assignment_id), None)
            if student and course and assignment:
                assignment.assign_grade(student_id, float(grade_value))
                messagebox.showinfo("Success",
                                    f"Grade {grade_value} assigned to {student.get_full_name()} for assignment '{assignment.title}' in course {course.title}.")
            else:
                messagebox.showerror("Error", "Invalid student, course, or assignment.")
            self.create_teacher_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_teacher_menu()

    def view_teacher_courses(self):
        # Перегляд курсів викладача
        self.clear_window()
        label = tk.Label(self.main_frame, text="Your Courses", font=("Arial", 16))
        label.pack(pady=10)

        if not self.current_user._courses_taught:
            messagebox.showinfo("Info", "You are not assigned to any courses.")
            self.create_teacher_menu()
            return

        courses_list = tk.Listbox(self.main_frame, width=50)
        for course in self.current_user._courses_taught:
            courses_list.insert(tk.END, f"{course.course_id}: {course.title}")
        courses_list.pack()

        back_btn = tk.Button(self.main_frame, text="Back", command=self.create_teacher_menu)
        back_btn.pack(pady=5)


    #-------------------------------------------------------------------------------------------
    # Студент
    def student_login(self):
        # Вікно входу для студента
        self.clear_window()
        label = tk.Label(self.main_frame, text="Вхід студента", font=("Arial", 16))
        label.pack(pady=10)

        if not self.students:
            messagebox.showerror("Помилка", "Немає зареєстрованих студентів.")
            self.create_main_window()
            return

        # Вибір студента зі списку зареєстрованих
        student_label = tk.Label(self.main_frame, text="Виберіть ваш ID:")
        student_label.pack()
        student_var = tk.StringVar()
        student_menu = ttk.Combobox(self.main_frame, textvariable=student_var)
        student_menu['values'] = [f"{s._student_id}: {s.get_full_name()}" for s in self.students]
        student_menu.pack()

        login_btn = tk.Button(self.main_frame, text="Увійти",
                              command=lambda: self.submit_student_login(student_var.get()))
        back_btn = tk.Button(self.main_frame, text="Назад", command=self.create_main_window)

        login_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_student_login(self, student_info):
        # Обробка входу студента
        try:
            student_id = int(student_info.split(":")[0])
            student = self.get_student_by_id(student_id)
            if student:
                self.current_user = student
                self.create_student_menu()
            else:
                messagebox.showerror("Помилка", "Студента не знайдено.")
                self.create_main_window()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))
            self.create_main_window()

    def create_student_menu(self):
        # Створення меню студента
        self.clear_window()
        label = tk.Label(self.main_frame, text=f"Меню студента ({self.current_user.get_full_name()})",
                         font=("Arial", 16))
        label.pack(pady=20)

        enroll_course_btn = tk.Button(self.main_frame, text="Записатися на курс", width=30,
                                      command=self.enroll_in_course)
        view_courses_btn = tk.Button(self.main_frame, text="Переглянути записані курси", width=30,
                                     command=self.view_student_courses)
        view_assignments_btn = tk.Button(self.main_frame, text="Переглянути завдання", width=30,
                                         command=self.view_student_assignments)
        submit_assignment_btn = tk.Button(self.main_frame, text="Здати завдання", width=30,
                                          command=self.submit_assignment)
        view_grades_btn = tk.Button(self.main_frame, text="Переглянути оцінки", width=30,
                                    command=self.view_student_grades)
        logout_btn = tk.Button(self.main_frame, text="Вийти", width=30, command=self.logout)

        enroll_course_btn.pack(pady=5)
        view_courses_btn.pack(pady=5)
        view_assignments_btn.pack(pady=5)
        submit_assignment_btn.pack(pady=5)
        view_grades_btn.pack(pady=5)
        logout_btn.pack(pady=5)

    # Методи для студента
    def enroll_in_course(self):
        # Запис на курс
        self.clear_window()
        label = tk.Label(self.main_frame, text="Запис на курс", font=("Arial", 16))
        label.pack(pady=10)

        available_courses = [c for c in self.courses if self.current_user not in c.students]
        if not available_courses:
            messagebox.showinfo("Інформація", "Немає доступних курсів для запису.")
            self.create_student_menu()
            return

        course_label = tk.Label(self.main_frame, text="Виберіть курс:")
        course_label.pack()
        course_var = tk.StringVar()
        course_menu = ttk.Combobox(self.main_frame, textvariable=course_var)
        course_menu['values'] = [f"{c.course_id}: {c.title}" for c in available_courses]
        course_menu.pack()

        enroll_btn = tk.Button(self.main_frame, text="Записатися",
                               command=lambda: self.submit_enroll_course(course_var.get()))
        back_btn = tk.Button(self.main_frame, text="Назад", command=self.create_student_menu)

        enroll_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def submit_enroll_course(self, course_info):
        # Підтвердження запису на курс
        try:
            course_id = course_info.split(":")[0]
            course = self.get_course_by_id(course_id)
            if course:
                self.current_user.enroll_course(course)
                messagebox.showinfo("Успіх", f"Ви записалися на курс {course.title}.")
            else:
                messagebox.showerror("Помилка", "Курс не знайдено.")
            self.create_student_menu()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))
            self.create_student_menu()

    def view_student_assignments(self):
        # Перегляд завдань студента
        self.clear_window()
        label = tk.Label(self.main_frame, text="Ваші завдання", font=("Arial", 16))
        label.pack(pady=10)

        assignments = []
        for course in self.current_user._courses:
            for assignment in course.assignments:
                status = "Submitted" if self.current_user._student_id in assignment.submissions else "Not Submitted"
                assignments.append(f"{course.title} - {assignment.title} [{status}]")

        if not assignments:
            messagebox.showinfo("Інформація", "Немає доступних завдань.")
            self.create_student_menu()
            return

        assignments_list = tk.Listbox(self.main_frame, width=70)
        for a in assignments:
            assignments_list.insert(tk.END, a)
        assignments_list.pack()

        back_btn = tk.Button(self.main_frame, text="Назад", command=self.create_student_menu)
        back_btn.pack(pady=5)

    def submit_assignment(self):
        # Здача завдання
        self.clear_window()
        label = tk.Label(self.main_frame, text="Здати завдання", font=("Arial", 16))
        label.pack(pady=10)

        if not self.current_user._courses:
            messagebox.showinfo("Інформація", "Ви не записані на жодний курс.")
            self.create_student_menu()
            return

        course_label = tk.Label(self.main_frame, text="Виберіть курс:")
        course_label.pack()
        course_var = tk.StringVar()
        course_menu = ttk.Combobox(self.main_frame, textvariable=course_var)
        course_menu['values'] = [f"{c.course_id}: {c.title}" for c in self.current_user._courses]
        course_menu.pack()

        next_btn = tk.Button(self.main_frame, text="Далі",
                             command=lambda: self.select_assignment_to_submit(course_var.get()))
        back_btn = tk.Button(self.main_frame, text="Назад", command=self.create_student_menu)

        next_btn.pack(pady=5)
        back_btn.pack(pady=5)

    def select_assignment_to_submit(self, course_info):
        # Вибір завдання для здачі
        try:
            course_id = course_info.split(":")[0]
            course = self.get_course_by_id(course_id)
            if not course:
                messagebox.showerror("Помилка", "Курс не знайдено.")
                self.create_student_menu()
                return

            assignments = [a for a in course.assignments if self.current_user._student_id not in a.submissions]
            if not assignments:
                messagebox.showinfo("Інформація", "Немає завдань для здачі.")
                self.create_student_menu()
                return

            self.clear_window()
            label = tk.Label(self.main_frame, text="Виберіть завдання для здачі", font=("Arial", 16))
            label.pack(pady=10)

            assignment_label = tk.Label(self.main_frame, text="Виберіть завдання:")
            assignment_label.pack()
            assignment_var = tk.StringVar()
            assignment_menu = ttk.Combobox(self.main_frame, textvariable=assignment_var)
            assignment_menu['values'] = [f"{a.assignment_id}: {a.title}" for a in assignments]
            assignment_menu.pack()

            submission_label = tk.Label(self.main_frame, text="Введіть відповідь:")
            submission_entry = tk.Entry(self.main_frame)
            submission_label.pack()
            submission_entry.pack()

            submit_btn = tk.Button(self.main_frame, text="Здати", command=lambda: self.submit_assignment_submission(
                course_id, assignment_var.get(), submission_entry.get()))
            back_btn = tk.Button(self.main_frame, text="Назад", command=self.create_student_menu)

            submit_btn.pack(pady=5)
            back_btn.pack(pady=5)
        except Exception as e:
            messagebox.showerror("Помилка", str(e))
            self.create_student_menu()

    def submit_assignment_submission(self, course_id, assignment_info, submission):
        # Підтвердження здачі завдання
        try:
            assignment_id = int(assignment_info.split(":")[0])
            course = self.get_course_by_id(course_id)
            assignment = next((a for a in course.assignments if a.assignment_id == assignment_id), None)
            if assignment:
                self.current_user.submit_assignment(assignment, submission)
                messagebox.showinfo("Успіх", f"Завдання '{assignment.title}' здано.")
            else:
                messagebox.showerror("Помилка", "Завдання не знайдено.")
            self.create_student_menu()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))
            self.create_student_menu()

    def view_student_grades(self):
        # Перегляд оцінок студента
        self.clear_window()
        label = tk.Label(self.main_frame, text="Ваші оцінки", font=("Arial", 16))
        label.pack(pady=10)

        grades = self.current_user.get_grades()
        if not grades:
            messagebox.showinfo("Інформація", "Немає доступних оцінок.")
            self.create_student_menu()
            return

        grades_list = tk.Listbox(self.main_frame, width=50)
        for course_title, grade in grades.items():
            grades_list.insert(tk.END, f"{course_title}: {grade}")
        grades_list.pack()

        back_btn = tk.Button(self.main_frame, text="Назад", command=self.create_student_menu)
        back_btn.pack(pady=5)


    #--------------------------------------------------------------------------------------------
    # Додаткові методи для отримання об'єктів за ID
    def get_teacher_by_id(self, teacher_id):
        for teacher in self.teachers:
            if teacher._teacher_id == teacher_id:
                return teacher
        return None

    def get_student_by_id(self, student_id):
        for student in self.students:
            if student._student_id == student_id:
                return student
        return None

    def get_course_by_id(self, course_id):
        for course in self.courses:
            if course.course_id == course_id:
                return course
        return None

    # Метод виходу з системи
    def logout(self):
        self.current_user = None
        self.create_main_window()

    # Запуск програми
if __name__ == "__main__":
    root = tk.Tk()
    app = UniversityApp(root)
    root.mainloop()
