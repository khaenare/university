from reportlab.pdfgen import canvas
import os

def convert_txt_to_pdf(input_file):
    output_file = os.path.splitext(input_file)[0] + ".pdf"
    with open(input_file, "r", encoding="utf-8") as txt_file:
        content = txt_file.read()

    pdf = canvas.Canvas(output_file)
    pdf.drawString(100, 750, "Содержимое файла:")
    pdf.drawString(100, 730, content[:2000])
    pdf.save()
