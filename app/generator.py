from docx import Document
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import textwrap


def create_docx_from_text(text: str, out_path: str):
    doc = Document()
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        doc.add_paragraph(para)
    doc.save(out_path)


def create_pdf_from_text(text: str, out_path: str):
    c = canvas.Canvas(out_path, pagesize=LETTER)
    width, height = LETTER
    margin = 72
    max_width = width - 2 * margin
    y = height - margin
    for paragraph in text.split("\n\n"):
        if not paragraph.strip():
            y -= 12
            continue
        lines = textwrap.wrap(paragraph, 100)
        for line in lines:
            y -= 14
            if y < margin:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line)
        y -= 6
    c.save()
