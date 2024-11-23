from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph
from docx.table import Table
import os

def convert_docx_to_txt(input_file):
    output_file = os.path.splitext(input_file)[0] + ".txt"

    doc = Document(input_file)

    with open(output_file, "w", encoding="utf-8") as txt_file:
        for block in iter_block_items(doc):
            if isinstance(block, Paragraph):
                text = block.text.strip()
                if text:
                    # Проверяем, является ли параграф пунктом списка
                    if is_list_item(block):
                        txt_file.write("- " + text + "\n")
                    else:
                        txt_file.write(text + "\n")
            elif isinstance(block, Table):
                txt_file.write("\nТаблица:\n")
                for row in block.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    txt_file.write("\t".join(row_data) + "\n")
                txt_file.write("\n")  # Добавляем пустую строку после таблицы

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

def is_list_item(paragraph):
    """
    Проверяет, является ли параграф элементом списка.
    """
    p = paragraph._p
    numPr = p.pPr.numPr if p.pPr is not None else None
    return numPr is not None
