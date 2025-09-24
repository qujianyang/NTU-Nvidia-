# Level 2: Data Structures & Loops for PDF Processing
# Building on basic functions - now using lists, dictionaries, and loops

import fitz
from pathlib import Path
import time

# ============= WORKING WITH LISTS =============

def get_all_pages_as_list(pdf_path):
    """
    Store each page in a list instead of one big string
    """
    pdf = fitz.open(pdf_path)

    # Create empty list to store pages
    pages_list = []

    # Loop through pages and add to list
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        page_text = page.get_text()
        pages_list.append(page_text)  # Add to list

    pdf.close()
    return pages_list


def find_pages_with_keyword(pdf_path, keyword):
    """
    Find which pages contain a specific word
    Returns list of page numbers
    """
    pdf = fitz.open(pdf_path)

    # List to store page numbers that have the keyword
    matching_pages = []

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        page_text = page.get_text()

        # Check if keyword is in this page
        if keyword.lower() in page_text.lower():
            matching_pages.append(page_num + 1)  # Add 1 for human-readable numbering

    pdf.close()
    return matching_pages


# ============= WORKING WITH DICTIONARIES =============

def get_page_info_as_dict(pdf_path, page_number):
    """
    Get detailed info about one page as a dictionary
    """
    pdf = fitz.open(pdf_path)
    page = pdf[page_number]

    # Create dictionary with page information
    page_info = {
        "page_number": page_number + 1,
        "text": page.get_text(),
        "char_count": len(page.get_text()),
        "word_count": len(page.get_text().split()),
        "has_content": len(page.get_text().strip()) > 0
    }

    pdf.close()
    return page_info


def process_pdf_to_structured_data(pdf_path):
    """
    Process entire PDF into structured dictionary
    """
    pdf = fitz.open(pdf_path)

    # Main dictionary to hold all data
    pdf_data = {
        "filename": Path(pdf_path).name,
        "total_pages": len(pdf),
        "metadata": pdf.metadata,
        "pages": [],  # List of page dictionaries
        "statistics": {}  # Overall stats
    }

    total_chars = 0
    total_words = 0

    # Process each page
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text = page.get_text()

        # Create dictionary for this page
        page_dict = {
            "number": page_num + 1,
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split())
        }

        # Add page to pages list
        pdf_data["pages"].append(page_dict)

        # Update totals
        total_chars += len(text)
        total_words += len(text.split())

    # Add statistics
    pdf_data["statistics"] = {
        "total_characters": total_chars,
        "total_words": total_words,
        "avg_chars_per_page": total_chars // len(pdf) if len(pdf) > 0 else 0,
        "avg_words_per_page": total_words // len(pdf) if len(pdf) > 0 else 0
    }

    pdf.close()
    return pdf_data


# ============= LOOPS WITH CONDITIONS =============

def extract_non_empty_pages(pdf_path):
    """
    Get only pages that have actual content
    """
    pdf = fitz.open(pdf_path)

    content_pages = []

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text = page.get_text().strip()

        # Only add if page has content
        if text:  # This is True if text is not empty
            page_data = {
                "page_number": page_num + 1,
                "content": text,
                "preview": text[:100] + "..." if len(text) > 100 else text
            }
            content_pages.append(page_data)

    pdf.close()
    return content_pages


def analyze_page_lengths(pdf_path):
    """
    Categorize pages by their text length
    """
    pdf = fitz.open(pdf_path)

    # Dictionary to categorize pages
    page_categories = {
        "empty": [],      # 0 characters
        "short": [],      # 1-500 characters
        "medium": [],     # 501-2000 characters
        "long": []        # 2000+ characters
    }

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text_length = len(page.get_text().strip())

        # Categorize based on length
        if text_length == 0:
            page_categories["empty"].append(page_num + 1)
        elif text_length <= 500:
            page_categories["short"].append(page_num + 1)
        elif text_length <= 2000:
            page_categories["medium"].append(page_num + 1)
        else:
            page_categories["long"].append(page_num + 1)

    pdf.close()
    return page_categories


# ============= LIST COMPREHENSIONS (More Advanced) =============

def get_page_previews(pdf_path, preview_length=50):
    """
    Get preview of each page using list comprehension
    """
    pdf = fitz.open(pdf_path)

    # List comprehension - creates list in one line
    previews = [
        {
            "page": i + 1,
            "preview": pdf[i].get_text()[:preview_length] + "..."
        }
        for i in range(len(pdf))
        if len(pdf[i].get_text().strip()) > 0  # Only non-empty pages
    ]

    pdf.close()
    return previews


# ============= NESTED DATA STRUCTURES =============

def create_document_index(pdf_path, keywords):
    """
    Create an index showing which keywords appear on which pages
    """
    pdf = fitz.open(pdf_path)

    # Dictionary of lists
    index = {keyword: [] for keyword in keywords}

    # Also track which pages have which keywords
    page_keywords = {}

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text = page.get_text().lower()

        # List to store keywords found on this page
        found_keywords = []

        # Check each keyword
        for keyword in keywords:
            if keyword.lower() in text:
                # Add page to keyword's list
                index[keyword].append(page_num + 1)
                found_keywords.append(keyword)

        # Store keywords for this page
        if found_keywords:
            page_keywords[page_num + 1] = found_keywords

    pdf.close()

    # Return both indexes
    result = {
        "keyword_to_pages": index,
        "page_to_keywords": page_keywords
    }

    return result


# ============= WORKING WITH BATCHES =============

def process_in_batches(pdf_path, batch_size=10):
    """
    Process PDF in batches instead of all at once
    Useful for large PDFs
    """
    pdf = fitz.open(pdf_path)
    total_pages = len(pdf)

    batches = []

    # Process in batches
    for start_page in range(0, total_pages, batch_size):
        end_page = min(start_page + batch_size, total_pages)

        batch = {
            "batch_number": (start_page // batch_size) + 1,
            "start_page": start_page + 1,
            "end_page": end_page,
            "pages": []
        }

        # Process pages in this batch
        for page_num in range(start_page, end_page):
            page = pdf[page_num]
            batch["pages"].append({
                "number": page_num + 1,
                "text_length": len(page.get_text())
            })

        batches.append(batch)

    pdf.close()
    return batches


# ============= MAIN FUNCTION USING ALL CONCEPTS =============

def advanced_pdf_analysis(pdf_path):
    """
    Complete analysis using lists, dicts, and loops
    """
    results = {
        "basic_info": {},
        "page_analysis": [],
        "keyword_search": {},
        "statistics": {}
    }

    # 1. Get basic info
    pdf = fitz.open(pdf_path)
    results["basic_info"] = {
        "filename": Path(pdf_path).name,
        "pages": len(pdf),
        "title": pdf.metadata.get('title', 'Unknown')
    }

    # 2. Analyze each page
    char_counts = []  # List to track character counts
    word_counts = []  # List to track word counts

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text = page.get_text()

        # Create page analysis dict
        page_analysis = {
            "page": page_num + 1,
            "chars": len(text),
            "words": len(text.split()),
            "lines": len(text.split('\n')),
            "is_empty": len(text.strip()) == 0
        }

        results["page_analysis"].append(page_analysis)

        # Add to counting lists
        if not page_analysis["is_empty"]:
            char_counts.append(page_analysis["chars"])
            word_counts.append(page_analysis["words"])

    # 3. Calculate statistics
    if char_counts:  # If we have non-empty pages
        results["statistics"] = {
            "total_chars": sum(char_counts),
            "total_words": sum(word_counts),
            "avg_chars": sum(char_counts) // len(char_counts),
            "avg_words": sum(word_counts) // len(word_counts),
            "max_chars": max(char_counts),
            "min_chars": min(char_counts),
            "non_empty_pages": len(char_counts),
            "empty_pages": len(pdf) - len(char_counts)
        }

    pdf.close()
    return results


# ============= TESTING THE FUNCTIONS =============

if __name__ == "__main__":
    pdf_file = r"C:\Users\qujia\QuantumKeyDistribution\NTU-Nvidia-\nvt-learning-learning-path-developers-it-administrators.pdf"

    print("=== Level 2: Data Structures Demo ===\n")

    # Test 1: Get pages as list
    print("1. Getting pages as list...")
    pages = get_all_pages_as_list(pdf_file)
    print(f"   Got {len(pages)} pages")
    print(f"   First page has {len(pages[0])} characters\n")

    # Test 2: Find pages with keyword
    print("2. Finding pages with 'CUDA'...")
    cuda_pages = find_pages_with_keyword(pdf_file, "CUDA")
    print(f"   Found on pages: {cuda_pages[:5]}...\n")  # Show first 5

    # Test 3: Get structured data
    print("3. Processing to structured data...")
    pdf_data = process_pdf_to_structured_data(pdf_file)
    print(f"   Total pages: {pdf_data['total_pages']}")
    print(f"   Total words: {pdf_data['statistics']['total_words']}")
    print(f"   Avg words/page: {pdf_data['statistics']['avg_words_per_page']}\n")

    # Test 4: Get non-empty pages
    print("4. Extracting non-empty pages...")
    content_pages = extract_non_empty_pages(pdf_file)
    print(f"   Found {len(content_pages)} pages with content\n")

    # Test 5: Analyze page lengths
    print("5. Categorizing pages by length...")
    categories = analyze_page_lengths(pdf_file)
    for category, pages in categories.items():
        print(f"   {category}: {len(pages)} pages")

    # Test 6: Create keyword index
    print("\n6. Creating keyword index...")
    keywords = ["CUDA", "GPU", "Python", "AI"]
    index = create_document_index(pdf_file, keywords)
    for keyword, pages in index["keyword_to_pages"].items():
        print(f"   '{keyword}' found on {len(pages)} pages")

    # Test 7: Process in batches
    print("\n7. Processing in batches...")
    batches = process_in_batches(pdf_file, batch_size=5)
    print(f"   Created {len(batches)} batches")
    print(f"   First batch: pages {batches[0]['start_page']}-{batches[0]['end_page']}")

    # Test 8: Complete analysis
    print("\n8. Running complete analysis...")
    analysis = advanced_pdf_analysis(pdf_file)
    print(f"   Analyzed {analysis['basic_info']['pages']} pages")
    print(f"   Non-empty: {analysis['statistics']['non_empty_pages']}")
    print(f"   Empty: {analysis['statistics']['empty_pages']}")
    print(f"   Total words: {analysis['statistics']['total_words']:,}")