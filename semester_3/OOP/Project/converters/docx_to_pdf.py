from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

# Регистрация шрифта с поддержкой кириллицы
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

def convert_docx_to_pdf(input_file):
    """
    Конвертирует файл DOCX в PDF с корректным отображением текста и таблиц.
    """
    output_file = os.path.splitext(input_file)[0] + ".pdf"

    # Открываем документ DOCX
    doc = Document(input_file)

    # Настраиваем PDF-документ
    pdf = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    def add_text_to_pdf(text, font="DejaVuSans", font_size=12, line_spacing=14, indent=20):
        """
        Добавляет текст в PDF с автоматическим переносом строк, контролем выхода за границы страницы
        и поддержкой табуляции (отступа).
        """
        nonlocal y
        pdf.setFont(font, font_size)

        for line_index, line in enumerate(text.split("\n")):
            # Добавляем отступ только для первой строки абзаца
            current_indent = indent if line_index == 0 else 0
            words = line.split(" ")
            current_line = ""
            for word in words:
                if pdf.stringWidth(current_line + word, font, font_size) > width - 2 * margin - current_indent:
                    if y < margin + line_spacing:  # Если места на странице нет
                        pdf.showPage()
                        pdf.setFont(font, font_size)
                        y = height - margin
                    pdf.drawString(margin + current_indent, y, current_line.strip())
                    y -= line_spacing
                    current_line = word + " "
                    current_indent = 0  # После первой строки отступ больше не нужен
                else:
                    current_line += word + " "
            # Печатаем последнюю строку
            if current_line.strip():
                if y < margin + line_spacing:  # Если места на странице нет
                    pdf.showPage()
                    pdf.setFont(font, font_size)
                    y = height - margin
                pdf.drawString(margin + current_indent, y, current_line.strip())
                y -= line_spacing

    def draw_table(table):
        """
        Рисует таблицу в PDF с динамической шириной колонок и поддержкой переноса строк.
        """
        nonlocal y
        if y - 20 * len(table.rows) < margin:  # Если таблица не помещается, перейти на новую страницу
            pdf.showPage()
            y = height - margin

        # Вычисляем ширину каждой колонки на основе максимальной длины текста
        col_widths = [
            max(pdf.stringWidth(cell.text.strip(), "DejaVuSans", 10) + 10 for cell in column)
            for column in zip(*[row.cells for row in table.rows])
        ]
        total_width = sum(col_widths)
        if total_width > width - 2 * margin:  # Если таблица выходит за границы, масштабируем колонки
            scale = (width - 2 * margin) / total_width
            col_widths = [w * scale for w in col_widths]

        cell_height = 20  # Минимальная высота строки таблицы

        for row in table.rows:
            max_cell_height = cell_height  # Определяем высоту строки на основе контента
            x = margin
            row_texts = []  # Список текстов для каждой ячейки
            for cell, col_width in zip(row.cells, col_widths):
                cell_text = cell.text.strip()
                wrapped_text = []  # Текст с переносами строк
                words = cell_text.split(" ")
                line = ""
                for word in words:
                    if pdf.stringWidth(line + word, "DejaVuSans", 10) <= col_width - 5:
                        line += word + " "
                    else:
                        wrapped_text.append(line.strip())
                        line = word + " "
                if line:
                    wrapped_text.append(line.strip())
                row_texts.append((wrapped_text, col_width))
                max_cell_height = max(max_cell_height, len(wrapped_text) * 12 + 5)

            # Если строка превышает высоту страницы
            if y - max_cell_height < margin:
                pdf.showPage()
                y = height - margin

            # Рисуем ячейки строки
            for (wrapped_text, col_width), cell_x in zip(row_texts, col_widths):
                pdf.rect(x, y - max_cell_height, col_width, max_cell_height)  # Рисуем ячейку
                text_y = y - 12  # Начинаем рисовать текст чуть ниже верхнего края ячейки
                for line in wrapped_text:
                    pdf.drawString(x + 2, text_y, line)  # Рисуем каждую строку текста
                    text_y -= 12
                x += col_width
            y -= max_cell_height  # Переходим к следующей строке

    # Обработка текста
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            add_text_to_pdf(text)

    # Обработка таблиц
    for table in doc.tables:
        draw_table(table)

    # Сохранение PDF
    pdf.save()
    print(f"Файл успешно конвертирован в {output_file}")
