from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import acroform
import os

def convert_txt_to_pdf(input_file):
    output_file = os.path.splitext(input_file)[0] + ".pdf"

    # Регистрация шрифта с поддержкой кириллицы
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    with open(input_file, "r", encoding="utf-8") as txt_file:
        content = txt_file.readlines()  # Читаем строки файла

    pdf = canvas.Canvas(output_file)
    pdf.setFont("DejaVuSans", 12)  # Устанавливаем шрифт
    x, y = 50, 750  # Начальные координаты текста

    for line in content:
        if y < 50:  # Если текст выходит за пределы страницы
            pdf.showPage()
            pdf.setFont("DejaVuSans", 12)
            y = 750
        pdf.drawString(x, y, line.strip())  # Добавляем текст строки
        y -= 15  # Смещаем координату Y для новой строки

    pdf.save()
