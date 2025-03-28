from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph
from docx.table import Table
import os
import textwrap

# Регистрация шрифта с поддержкой кириллицы
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

def convert_docx_to_pdf(input_file):
    """
    Конвертирует файл DOCX в PDF с поддержкой таблиц и форматирования текста.
    """
    try:
        output_file = os.path.splitext(input_file)[0] + ".pdf"

        doc = Document(input_file)
        pdf = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        margin = 50
        y = height - margin

        def iter_block_items(parent):
            """
            Генератор для итерации по блокам (параграфам и таблицам) в порядке их появления.
            """
            for child in parent.element.body.iterchildren():
                if isinstance(child, CT_P):
                    yield Paragraph(child, parent)
                elif isinstance(child, CT_Tbl):
                    yield Table(child, parent)

        def add_text_to_pdf(paragraph, font="DejaVuSans", font_size=12, line_spacing=14, indent=20):
            """
            Добавляет текст из абзаца в PDF с контролем ширины строки.
            """
            nonlocal y
            pdf.setFont(font, font_size)

            text = paragraph.text.strip()
            if not text:
                return  # Пропускаем пустые абзацы

            words = text.split(" ")
            current_line = ""
            current_indent = indent

            for word in words:
                # Проверяем ширину строки
                if pdf.stringWidth(current_line + word, font, font_size) > width - 2 * margin - current_indent:
                    # Если строка выходит за границы, переносим
                    if y < margin + line_spacing:
                        pdf.showPage()
                        pdf.setFont(font, font_size)
                        y = height - margin
                    pdf.drawString(margin + current_indent, y, current_line.strip())
                    y -= line_spacing
                    current_line = word + " "
                    current_indent = 0  # Отступ только для первой строки абзаца
                else:
                    current_line += word + " "

            # Печатаем остаток строки
            if current_line.strip():
                if y < margin + line_spacing:
                    pdf.showPage()
                    pdf.setFont(font, font_size)
                    y = height - margin
                pdf.drawString(margin + current_indent, y, current_line.strip())
                y -= line_spacing

        def draw_table(table):
            """
            Рисует таблицу с масштабированием столбцов под ширину страницы.
            """
            nonlocal y
            pdf.setFont("DejaVuSans", 10)

            # Вычисляем ширину столбцов
            col_widths = []
            for col_index in range(len(table.rows[0].cells)):
                max_width = 0
                for row in table.rows:
                    cell_text = row.cells[col_index].text.strip()
                    cell_width = pdf.stringWidth(cell_text, "DejaVuSans", 10) + 10
                    max_width = max(max_width, cell_width)
                col_widths.append(max_width)

            # Масштабируем столбцы, если суммарная ширина больше доступной
            total_width = sum(col_widths)
            if total_width > width - 2 * margin:
                scale_factor = (width - 2 * margin) / total_width
                col_widths = [w * scale_factor for w in col_widths]

            # Рисуем таблицу
            cell_height = 20
            for row in table.rows:
                max_cell_height = cell_height
                row_texts = []

                for cell, col_width in zip(row.cells, col_widths):
                    cell_text = cell.text.strip()
                    wrapped_text = []
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

                if y - max_cell_height < margin:
                    pdf.showPage()
                    pdf.setFont("DejaVuSans", 10)
                    y = height - margin

                x = margin
                for (wrapped_text, col_width) in row_texts:
                    pdf.rect(x, y - max_cell_height, col_width, max_cell_height)
                    text_y = y - 12
                    for line in wrapped_text:
                        pdf.drawString(x + 2, text_y, line)
                        text_y -= 12
                    x += col_width
                y -= max_cell_height

            y -= 20

        for block in iter_block_items(doc):
            if isinstance(block, Paragraph):
                add_text_to_pdf(block, indent=30)  # Передаем объект Paragraph
            elif isinstance(block, Table):
                draw_table(block)

        pdf.save()
        print(f"Файл успешно конвертирован в {output_file}")

    except Exception as e:
        print(f"Ошибка при конвертации: {e}")
