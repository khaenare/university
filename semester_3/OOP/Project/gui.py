import tkinter as tk
from tkinter import filedialog, messagebox
from converters import convert_txt_to_pdf
import os

class DocumentConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер документов")
        self.root.geometry("600x400")

        # Элементы интерфейса
        self.label_file = tk.Label(root, text="Выберите файл:")
        self.label_file.pack(pady=10)

        self.file_entry = tk.Entry(root, width=50)
        self.file_entry.pack(pady=10)

        self.browse_button = tk.Button(root, text="Обзор", command=self.browse_file)
        self.browse_button.pack(pady=10)

        self.format_label = tk.Label(root, text="Выберите формат:")
        self.format_label.pack(pady=10)

        self.format_options = ["TXT", "PDF", "DOCX"]
        self.format_var = tk.StringVar(value=self.format_options[0])
        self.format_menu = tk.OptionMenu(root, self.format_var, *self.format_options)
        self.format_menu.pack(pady=10)

        self.convert_button = tk.Button(root, text="Конвертировать", command=self.convert_file)
        self.convert_button.pack(pady=20)

        self.status_label = tk.Label(root, text="", fg="green")
        self.status_label.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.update_format_options(file_path)

    def update_format_options(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lower()[1:]
        valid_formats = [fmt for fmt in self.format_options if fmt.lower() != file_extension]

        self.format_var.set(valid_formats[0] if valid_formats else "")
        menu = self.format_menu["menu"]
        menu.delete(0, "end")
        for fmt in valid_formats:
            menu.add_command(label=fmt, command=lambda value=fmt: self.format_var.set(value))

    def convert_file(self):
        input_file = self.file_entry.get()
        target_format = self.format_var.get()

        if not input_file:
            messagebox.showerror("Ошибка", "Выберите файл для конвертации.")
            return

        if not target_format:
            messagebox.showerror("Ошибка", "Нет доступных форматов для конвертации.")
            return

        try:
            if target_format == "PDF":
                convert_txt_to_pdf(input_file)
            else:
                raise NotImplementedError(f"Конвертация в {target_format} еще не реализована.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить конвертацию: {e}")
            return

        self.status_label.config(text=f"Файл {input_file} успешно конвертирован в {target_format}.")
        messagebox.showinfo("Успех", f"Файл успешно конвертирован в {target_format}!")
