import fitz  # PyMuPDF library
import time
import hashlib
from pathlib import Path

def open_pdf(pdf_path):
    pdf=fitz.open(pdf_path)
    return pdf

def get_page_count(pdf):

    return len(pdf)


def get_text_from_page(pdf, page_number):
    
    page = pdf[page_number]
    text = page.get_text()
    return text

def close_pdf(pdf):
    pdf.close()

if __name__ == "__main__":
    print("testing")
    pdf_path = r"C:\Users\qujia\QuantumKeyDistribution\NTU-Nvidia-\nvidia.pdf"
    pdf = open_pdf(pdf_path) 
    page_count=get_page_count(pdf)
    print(f"totoal page count:{page_count}")
    text = get_text_from_page(pdf, 0)
    if page_count > 0:
        first_page_text = get_text_from_page(pdf, 0)
        print(f"\nFirst page text preview [first 500 chars]:\n{first_page_text[:500]}")
    close_pdf(pdf)
    
    

