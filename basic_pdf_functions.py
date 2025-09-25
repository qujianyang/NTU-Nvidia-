# Super Simple PDF Processing - No Classes, Just Functions
# Each function does ONE thing

import fitz  # PyMuPDF library
import time
import hashlib
from pathlib import Path

# ============= LEVEL 1: Most Basic Functions =============

def open_pdf(pdf_path):
    """
    Just open a PDF file
    """
    pdf_path="C:\Users\qujia\QuantumKeyDistribution\NTU-Nvidia-\nvidia.pdf"
    pdf = fitz.open(pdf_path)
    return pdf


def get_page_count(pdf):
    """
    Count how many pages in PDF
    """
    return len(pdf)


def get_text_from_page(pdf, page_number):
    """
    Get text from one specific page
    """
    page = pdf[page_number]
    text = page.get_text()
    return text


def close_pdf(pdf):
    """
    Close the PDF when done
    """
    pdf.close()


# ============= LEVEL 2: Combine Basic Functions =============

def extract_all_text(pdf_path):
    """
    Get all text from entire PDF
    """
    # Step 1: Open PDF
    pdf = open_pdf(pdf_path)

    # Step 2: Get page count
    total_pages = get_page_count(pdf)

    # Step 3: Loop through pages and collect text
    all_text = ""
    for page_num in range(total_pages):
        page_text = get_text_from_page(pdf, page_num)
        all_text = all_text + page_text

    # Step 4: Close PDF
    close_pdf(pdf)

    return all_text


def check_if_file_exists(pdf_path):
    """
    Check if PDF file exists before trying to open
    """
    path = Path(pdf_path)
    if path.exists():
        return True
    else:
        return False


def get_pdf_metadata(pdf_path):
    """
    Get info about the PDF (title, author, etc)
    """
    pdf = open_pdf(pdf_path)

    # Get the metadata dictionary
    metadata = pdf.metadata

    # Extract specific fields
    title = metadata.get('title', 'No title')
    author = metadata.get('author', 'No author')
    pages = get_page_count(pdf)

    close_pdf(pdf)

    # Return as simple dictionary
    info = {
        'title': title,
        'author': author,
        'pages': pages
    }

    return info


# ============= LEVEL 3: Add More Features =============

def extract_text_with_page_numbers(pdf_path):
    """
    Get text but mark which page it came from
    """
    pdf = open_pdf(pdf_path)
    total_pages = get_page_count(pdf)

    text_with_pages = ""

    for page_num in range(total_pages):
        # Add page marker
        text_with_pages = text_with_pages + f"\n=== PAGE {page_num + 1} ===\n"

        # Add page text
        page_text = get_text_from_page(pdf, page_num)
        text_with_pages = text_with_pages + page_text

    close_pdf(pdf)

    return text_with_pages


def measure_processing_time(pdf_path):
    """
    See how long it takes to process PDF
    """
    start = time.time()

    # Do the processing
    text = extract_all_text(pdf_path)

    end = time.time()
    time_taken = end - start

    return time_taken


def create_document_id(pdf_path):
    """
    Create unique ID for a PDF file
    """
    # Read file as bytes
    path = Path(pdf_path)
    file_bytes = path.read_bytes()

    # Create hash (unique fingerprint)
    doc_id = hashlib.md5(file_bytes).hexdigest()

    return doc_id


# ============= LEVEL 4: Markdown Conversion =============

def convert_text_to_markdown(text, title="Document"):
    """
    Make text look nicer with markdown formatting
    """
    markdown = f"# {title}\n\n"
    markdown = markdown + "---\n\n"
    markdown = markdown + text

    return markdown


def clean_text(text):
    """
    Remove extra blank lines and spaces
    """
    # Split into lines
    lines = text.split('\n')

    # Keep only non-empty lines
    clean_lines = []
    for line in lines:
        if line.strip():  # If line has actual content
            clean_lines.append(line)

    # Join back together
    cleaned = '\n'.join(clean_lines)

    return cleaned


# ============= LEVEL 5: Error Handling =============

def safe_extract_text(pdf_path):
    """
    Extract text but handle errors gracefully
    """
    # Check if file exists first
    if not check_if_file_exists(pdf_path):
        return "Error: File does not exist"

    try:
        text = extract_all_text(pdf_path)
        return text
    except Exception as e:
        return f"Error: Could not process PDF - {e}"


# ============= MAIN PROCESSING FUNCTION (Combines Everything) =============

def process_pdf_complete(pdf_path):
    """
    This is like the main process_pdf from the original code
    But broken down into simple function calls
    """
    # 1. Check file exists
    if not check_if_file_exists(pdf_path):
        return {"error": "File not found"}

    # 2. Create document ID
    doc_id = create_document_id(pdf_path)

    # 3. Get filename
    filename = Path(pdf_path).name

    # 4. Start timer
    start_time = time.time()

    # 5. Extract text with page numbers
    content = extract_text_with_page_numbers(pdf_path)

    # 6. Clean the text
    content = clean_text(content)

    # 7. Get metadata
    metadata = get_pdf_metadata(pdf_path)

    # 8. Convert to markdown
    markdown_content = convert_text_to_markdown(
        content,
        title=metadata['title']
    )

    # 9. Calculate time
    processing_time = time.time() - start_time

    # 10. Build result dictionary
    result = {
        'doc_id': doc_id,
        'filename': filename,
        'content': markdown_content,
        'page_count': metadata['pages'],
        'title': metadata['title'],
        'author': metadata['author'],
        'processing_time': processing_time
    }

    return result


# ============= HOW TO USE THESE FUNCTIONS =============

if __name__ == "__main__":
    pdf_file = r"C:\Users\qujia\QuantumKeyDistribution\NTU-Nvidia-\nvidia.pdf"

    print("=== Testing Basic Functions ===\n")

    # Test 1: Check if file exists
    exists = check_if_file_exists(pdf_file)
    print(f"1. File exists: {exists}")

    # Test 2: Get metadata
    info = get_pdf_metadata(pdf_file)
    print(f"2. PDF has {info['pages']} pages")
    print(f"   Title: {info['title']}")

    # Test 3: Extract first page only
    pdf = open_pdf(pdf_file)
    first_page_text = get_text_from_page(pdf, 0)
    close_pdf(pdf)
    print(f"3. First page has {len(first_page_text)} characters")

    # Test 4: Create document ID
    doc_id = create_document_id(pdf_file)
    print(f"4. Document ID: {doc_id[:10]}...")  # Show first 10 chars

    # Test 5: Measure time
    time_taken = measure_processing_time(pdf_file)
    print(f"5. Processing took {time_taken:.2f} seconds")

    print("\n=== Testing Complete Processing ===\n")

    # Test the complete function
    result = process_pdf_complete(pdf_file)

    print(f"Document ID: {result['doc_id'][:10]}...")
    print(f"Filename: {result['filename']}")
    print(f"Pages: {result['page_count']}")
    print(f"Processing time: {result['processing_time']:.2f} seconds")
    print(f"\nFirst 500 characters of content:")
    print(result['content'][:500])
    
