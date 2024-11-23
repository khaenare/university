from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def convert_docx_to_pdf(input_file):
    """
    Конвертирует файл DOCX в PDF.
    """
    output_file = os.path.splitext(input_file)[0] + ".pdf"

    # Открываем документ DOCX
    doc = Document(input_file)

    # Создаем PDF-файл
    pdf = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    margin = 50  # Поля страницы
    y = height - margin

    # Функция для добавления текста в PDF
    def add_text_to_pdf(text, font="Helvetica", font_size=12, line_spacing=14):
        nonlocal y
        pdf.setFont(font, font_size)
        for line in text.split("\n"):
            if y < margin:  # Если текст выходит за границу страницы
                pdf.showPage()
                pdf.setFont(font, font_size)
                y = height - margin
            pdf.drawString(margin, y, line)
            y -= line_spacing

    # Перебираем содержимое документа
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            add_text_to_pdf(text)
            y -= 10  # Добавляем небольшой отступ между абзацами

    # Обработка таблиц
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            add_text_to_pdf(row_text, font="Courier", font_size=10)
        y -= 20  # Отступ между таблицами

    # Сохраняем PDF
    pdf.save()
    print(f"Файл успешно конвертирован в {output_file}")
