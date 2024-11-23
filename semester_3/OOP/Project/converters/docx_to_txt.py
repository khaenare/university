from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.shared import Inches
import os

def save_images(doc, output_folder):
    """
    Сохраняет изображения из документа DOCX в указанную папку.
    """
    os.makedirs(output_folder, exist_ok=True)
    image_count = 0
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_count += 1
            image_data = rel.target_part.blob
            image_path = os.path.join(output_folder, f"image{image_count}.png")
            with open(image_path, "wb") as img_file:
                img_file.write(image_data)
    return image_count


def convert_docx_to_txt(input_file):
    """
    Конвертирует файл DOCX в TXT, с поддержкой таблиц, списков и изображений.
    """
    output_file = os.path.splitext(input_file)[0] + ".txt"
    output_folder = os.path.splitext(input_file)[0] + "_images"

    doc = Document(input_file)

    with open(output_file, "w", encoding="utf-8") as txt_file:
        for block in iter_block_items(doc):
            if isinstance(block, Paragraph):
                text = block.text.strip()
                if text:
                    if is_list_item(block):
                        txt_file.write(f"- {text}\n")
                    else:
                        txt_file.write(text + "\n")
            elif isinstance(block, Table):
                txt_file.write(format_table(block) + "\n")

        # Сохраняем изображения
        image_count = save_images(doc, output_folder)
        if image_count > 0:
            txt_file.write(
                f"\n[В документе найдено {image_count} изображений, они сохранены в папке '{output_folder}']\n")

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


def is_list_item(paragraph):
    """
    Проверяет, является ли параграф пунктом списка.
    """
    p = paragraph._p
    numPr = p.pPr.numPr if p.pPr is not None else None
    return numPr is not None
