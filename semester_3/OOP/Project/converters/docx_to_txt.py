from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph
from docx.table import Table
import os


def convert_docx_to_txt(input_file):
    """
    Конвертирует файл DOCX в TXT, с улучшенным отображением таблиц.
    """
    output_file = os.path.splitext(input_file)[0] + ".txt"

    doc = Document(input_file)

    with open(output_file, "w", encoding="utf-8") as txt_file:
        for block in iter_block_items(doc):
            if isinstance(block, Paragraph):
                text = block.text.strip()
                if text:
                    txt_file.write(text + "\n")
            elif isinstance(block, Table):
                txt_file.write(format_table(block) + "\n")

    print(f"Файл успешно конвертирован в {output_file}")


def iter_block_items(parent):
    """
    Генератор, который перебирает параграфы и таблицы в порядке их появления в документе.
    """
    for child in parent.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def format_table(table):
    """
    Форматирует таблицу для красивого отображения в текстовом формате,
    поддерживает многострочные ячейки и добавляет горизонтальные разделители.
    """
    # Извлекаем содержимое таблицы
    rows = [[cell.text.strip().split("\n") for cell in row.cells] for row in table.rows]

    if not rows:
        return ""

    # Определяем ширину каждой колонки
    col_widths = [
        max(max(len(line) for line in cell) if cell else 0 for cell in column)
        for column in zip(*rows)
    ]

    # Функция для форматирования строки с многострочными ячейками
    def format_row(row):
        formatted_lines = []
        max_lines = max(len(cell) for cell in row)  # Находим максимальное количество строк в ряду
        for i in range(max_lines):
            line = "| "
            for j, cell in enumerate(row):
                line_content = cell[i] if i < len(cell) else ""
                line += f"{line_content:{col_widths[j]}} | "
            formatted_lines.append(line)
        return "\n".join(formatted_lines)

    # Горизонтальная линия
    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    # Формируем таблицу
    formatted_table = [separator]  # Верхняя граница
    formatted_table.append(format_row(rows[0]))  # Заголовок
    formatted_table.append(separator)  # Разделитель заголовка
    for row in rows[1:]:
        formatted_table.append(format_row(row))  # Данные
        formatted_table.append(separator)  # Горизонтальная линия после каждой строки данных

    return "\n".join(formatted_table)
