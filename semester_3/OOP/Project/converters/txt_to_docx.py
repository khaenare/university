from docx import Document
import os

def convert_txt_to_docx(input_file):
    """
    Конвертирует файл TXT в DOCX.
    
    :param input_file: Путь к входному файлу .txt
    """
    output_file = os.path.splitext(input_file)[0] + ".docx"
    
    # Создаем новый документ Word
    doc = Document()
    
    # Читаем содержимое TXT файла
    with open(input_file, "r", encoding="utf-8") as txt_file:
        content = txt_file.readlines()
    
    # Добавляем строки в документ
    for line in content:
        doc.add_paragraph(line.strip())
    
    # Сохраняем документ
    doc.save(output_file)
    print(f"Файл успешно конвертирован в {output_file}")
