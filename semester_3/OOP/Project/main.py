import tkinter as tk
from tkinter import filedialog, messagebox

class DocumentConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер документов")
        self.root.geometry("400x200")
        
        # Элементы интерфейса
        self.label_file = tk.Label(root, text="Выберите файл:")
        self.label_file.pack(pady=5)

        self.file_entry = tk.Entry(root, width=40)
        self.file_entry.pack(pady=5)

        self.browse_button = tk.Button(root, text="Обзор", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.format_label = tk.Label(root, text="Выберите формат:")
        self.format_label.pack(pady=5)

        self.format_options = ["TXT", "PDF", "DOCX"]
        self.format_var = tk.StringVar(value=self.format_options[0])
        self.format_menu = tk.OptionMenu(root, self.format_var, *self.format_options)
        self.format_menu.pack(pady=5)

        self.convert_button = tk.Button(root, text="Конвертировать", command=self.convert_file)
        self.convert_button.pack(pady=10)

        self.status_label = tk.Label(root, text="", fg="green")
        self.status_label.pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def convert_file(self):
        input_file = self.file_entry.get()
        target_format = self.format_var.get()

        if not input_file:
            messagebox.showerror("Ошибка", "Выберите файл для конвертации.")
            return

        # Здесь будет логика конвертации
        self.status_label.config(text=f"Файл {input_file} успешно конвертирован в {target_format}.")
        messagebox.showinfo("Успех", f"Файл успешно конвертирован в {target_format}!")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentConverterApp(root)
    root.mainloop()
