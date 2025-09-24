import fitz  # PyMuPDF library
import time
import hashlib
from pathlib import Path

def open_pdf(pdf_path):
    pdf=fitz.open(pdf_path)
    return pdf
