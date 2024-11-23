from docx import Document
import os

def convert_docx_to_txt(input_file):
    """
    Конвертирует файл DOCX в TXT.
    
    :param input_file: Путь к входному файлу .docx
    """
    output_file = os.path.splitext(input_file)[0] + ".txt"
    
    # Открываем документ Word
    doc = Document(input_file)
    
    # Извлекаем весь текст из документа
    with open(output_file, "w", encoding="utf-8") as txt_file:
        for paragraph in doc.paragraphs:
            txt_file.write(paragraph.text + "\n")
    
    print(f"Файл успешно конвертирован в {output_file}")
