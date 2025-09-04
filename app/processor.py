import pdfplumber
from docx import Document
from typing import Optional

def extract_text_from_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ''
            text_parts.append(page_text)
    return '\n'.join(text_parts)

def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text and not p.text.isspace()]
    return '\n'.join(paragraphs)

def extract_text_from_file(path: str) -> str:
    path = path.lower()
    if path.endswith('.pdf'):
        return extract_text_from_pdf(path)
    elif path.endswith('.docx'):
        return extract_text_from_docx(path)
    else:
        raise ValueError('Unsupported file type')
