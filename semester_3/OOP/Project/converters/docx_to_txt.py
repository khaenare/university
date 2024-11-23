from docx import Document
import os

def convert_docx_to_txt(input_file):
    """
    Конвертирует файл DOCX в TXT, включая обработку таблиц и пунктов.
    
    :param input_file: Путь к входному файлу .docx
    """
    output_file = os.path.splitext(input_file)[0] + ".txt"
    
    # Открываем документ Word
    doc = Document(input_file)
    
    with open(output_file, "w", encoding="utf-8") as txt_file:
        for paragraph in doc.paragraphs:
            # Обрабатываем пункты (списки)
            if paragraph.style.name.startswith("List"):
                txt_file.write(f"- {paragraph.text}\n")
            else:
                txt_file.write(paragraph.text + "\n")
        
        # Обрабатываем таблицы
        for table in doc.tables:
            txt_file.write("\nТаблица:\n")
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                txt_file.write("\t".join(row_data) + "\n")
    
    print(f"Файл успешно конвертирован в {output_file}")
