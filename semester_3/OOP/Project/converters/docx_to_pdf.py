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

# Регистрация шрифта с поддержкой кириллицы
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

def convert_docx_to_pdf(input_file):
    """
    Конвертирует файл DOCX в PDF с поддержкой таблиц в правильном порядке.
    """
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

    def add_text_to_pdf(text, font="DejaVuSans", font_size=12, line_spacing=14, indent=20):
        """
        Добавляет текст в PDF с автоматическим переносом строк и поддержкой табуляции (отступа в начале абзаца).
        """
        nonlocal y
        pdf.setFont(font, font_size)

        for line_index, line in enumerate(text.split("\n")):
            # Определяем отступ для первой строки абзаца
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
                    current_indent = 0  # Отступ применяется только к первой строке абзаца
                else:
                    current_line += word + " "
            # Печатаем последнюю строку
            if current_line.strip():
                if y < margin + line_spacing:
                    pdf.showPage()
                    pdf.setFont(font, font_size)
                    y = height - margin
                pdf.drawString(margin + current_indent, y, current_line.strip())
                y -= line_spacing

    def draw_table(table):
        """
        Рисует таблицу построчно, с увеличенным расстоянием между таблицей и следующим текстом.
        """
        nonlocal y
        col_widths = [width / len(table.rows[0].cells) for _ in table.rows[0].cells]
        cell_height = 20  # Минимальная высота строки таблицы
        table_spacing = 20  # Увеличенный отступ между таблицей и следующим текстом

        for row in table.rows:
            # Подсчитываем высоту текущей строки с учетом содержимого
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

            # Проверяем место для строки. Если строка не помещается, переносим на новую страницу.
            if y - max_cell_height < margin + table_spacing:
                pdf.showPage()
                y = height - margin

            # Рисуем строку
            x = margin
            for (wrapped_text, col_width) in row_texts:
                pdf.rect(x, y - max_cell_height, col_width, max_cell_height)  # Рисуем ячейку
                text_y = y - 12
                for line in wrapped_text:
                    pdf.drawString(x + 2, text_y, line)
                    text_y -= 12
                x += col_width
            y -= max_cell_height  # Сдвигаемся на следующую строку

        # Увеличиваем отступ после таблицы
        y -= table_spacing

    # Обработка документа по блокам
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                add_text_to_pdf(text, indent=30)  # Добавление табуляции в 30 пунктов
        elif isinstance(block, Table):
            draw_table(block)

    pdf.save()
    print(f"Файл успешно конвертирован в {output_file}")
