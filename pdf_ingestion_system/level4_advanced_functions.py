# Level 4: Advanced Function Features for PDF Processing
# Building on Level 3 - now with powerful function techniques

import fitz
from pathlib import Path
import time
import logging
from functools import wraps
from typing import Optional, List, Dict, Any, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============= DEFAULT PARAMETERS =============

def extract_pdf_text(pdf_path,
                     start_page=0,           # Default: start from first page
                     end_page=None,           # Default: go to last page
                     clean_text=True,         # Default: clean the text
                     include_metadata=False): # Default: don't include metadata
    """
    Extract text with configurable options

    You can call this many ways:
    - extract_pdf_text(path)                    # Use all defaults
    - extract_pdf_text(path, start_page=5)      # Start from page 5
    - extract_pdf_text(path, clean_text=False)  # Don't clean text
    """
    try:
        pdf = fitz.open(pdf_path)

        # If end_page not specified, use last page
        if end_page is None:
            end_page = len(pdf)

        # Extract text from specified range
        text = ""
        for page_num in range(start_page, min(end_page, len(pdf))):
            page_text = pdf[page_num].get_text()
            text += page_text

        # Clean text if requested
        if clean_text:
            text = text.strip()
            # Remove multiple spaces
            text = ' '.join(text.split())

        # Add metadata if requested
        result = {"text": text}
        if include_metadata:
            result["metadata"] = pdf.metadata
            result["pages_extracted"] = min(end_page, len(pdf)) - start_page

        pdf.close()
        return result

    except Exception as e:
        logger.error(f"Failed to extract: {e}")
        return None


# ============= *ARGS (VARIABLE ARGUMENTS) =============

def combine_pdf_texts(*pdf_paths):
    """
    Combine text from multiple PDFs

    Can accept any number of PDF paths:
    - combine_pdf_texts(pdf1)
    - combine_pdf_texts(pdf1, pdf2)
    - combine_pdf_texts(pdf1, pdf2, pdf3, pdf4, ...)
    """
    combined_text = ""
    successful = []
    failed = []

    # *pdf_paths becomes a tuple of all arguments
    for pdf_path in pdf_paths:
        try:
            pdf = fitz.open(pdf_path)
            for page in pdf:
                combined_text += page.get_text()
            pdf.close()
            successful.append(pdf_path)
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
            failed.append(pdf_path)

    return {
        "text": combined_text,
        "successful_pdfs": successful,
        "failed_pdfs": failed,
        "total_processed": len(successful)
    }


# ============= **KWARGS (KEYWORD ARGUMENTS) =============

def process_pdf_flexible(pdf_path, **options):
    """
    Process PDF with any combination of options

    Examples:
    - process_pdf_flexible(path, extract_text=True)
    - process_pdf_flexible(path, extract_text=True, get_images=True)
    - process_pdf_flexible(path, custom_option="anything", another=123)
    """
    results = {
        "file": pdf_path,
        "operations_performed": []
    }

    try:
        pdf = fitz.open(pdf_path)

        # Check what operations were requested
        if options.get('extract_text', False):
            text = ""
            for page in pdf:
                text += page.get_text()
            results['text'] = text
            results['operations_performed'].append('text_extraction')

        if options.get('count_pages', False):
            results['page_count'] = len(pdf)
            results['operations_performed'].append('page_counting')

        if options.get('get_metadata', False):
            results['metadata'] = pdf.metadata
            results['operations_performed'].append('metadata_extraction')

        if options.get('page_sizes', False):
            sizes = []
            for page in pdf:
                rect = page.rect
                sizes.append({
                    "width": rect.width,
                    "height": rect.height
                })
            results['page_sizes'] = sizes
            results['operations_performed'].append('size_measurement')

        # Store any custom options
        results['custom_options'] = {k: v for k, v in options.items()
                                    if k not in ['extract_text', 'count_pages',
                                                'get_metadata', 'page_sizes']}

        pdf.close()
        return results

    except Exception as e:
        logger.error(f"Error: {e}")
        return None


# ============= FUNCTION DECORATORS =============

def timer_decorator(func):
    """
    Decorator to measure function execution time
    """
    @wraps(func)  # Preserves function name and docstring
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper


def retry_decorator(max_attempts=3):
    """
    Decorator to retry function if it fails
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(1)  # Wait before retry
        return wrapper
    return decorator


@timer_decorator
@retry_decorator(max_attempts=2)
def extract_with_decorators(pdf_path):
    """
    Extract text with automatic timing and retry
    """
    pdf = fitz.open(pdf_path)
    text = ""
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text


# ============= LAMBDA FUNCTIONS =============

def process_pages_with_filter(pdf_path, page_filter=None):
    """
    Process pages with custom filter function

    Examples:
    - process_pages_with_filter(path, lambda p: p > 5)  # Pages after 5
    - process_pages_with_filter(path, lambda p: p % 2 == 0)  # Even pages
    """
    if page_filter is None:
        # Default: include all pages
        page_filter = lambda x: True

    pdf = fitz.open(pdf_path)
    selected_pages = []

    for page_num in range(len(pdf)):
        if page_filter(page_num):
            page = pdf[page_num]
            selected_pages.append({
                "page_number": page_num + 1,
                "text": page.get_text()
            })

    pdf.close()
    return selected_pages


# Sort pages by text length using lambda
def sort_pages_by_length(pdf_path):
    """
    Sort pages by their text length
    """
    pages = process_pages_with_filter(pdf_path)

    # Lambda function as key for sorting
    sorted_pages = sorted(pages,
                         key=lambda p: len(p['text']),
                         reverse=True)

    return sorted_pages


# ============= GENERATOR FUNCTIONS (YIELD) =============

def pdf_page_generator(pdf_path):
    """
    Generator that yields one page at a time
    Memory efficient for large PDFs
    """
    pdf = fitz.open(pdf_path)

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        # Yield returns one page and pauses
        yield {
            "page_number": page_num + 1,
            "text": page.get_text()
        }

    pdf.close()


def process_large_pdf_efficiently(pdf_path, process_func):
    """
    Process large PDF one page at a time using generator
    """
    results = []

    # Generator only loads one page at a time
    for page_data in pdf_page_generator(pdf_path):
        # Process each page
        processed = process_func(page_data)
        if processed:
            results.append(processed)

    return results


# ============= TYPE HINTS =============

def extract_page_range(
    pdf_path: str,
    start: int = 0,
    end: Optional[int] = None,
    as_list: bool = False
) -> Union[str, List[str]]:
    """
    Extract pages with type hints for clarity

    Args:
        pdf_path: Path to PDF file
        start: Starting page (0-indexed)
        end: Ending page (None = last page)
        as_list: Return list of pages or single string

    Returns:
        Either string or list of strings depending on as_list
    """
    pdf = fitz.open(pdf_path)

    if end is None:
        end = len(pdf)

    if as_list:
        pages: List[str] = []
        for i in range(start, min(end, len(pdf))):
            pages.append(pdf[i].get_text())
        pdf.close()
        return pages
    else:
        text: str = ""
        for i in range(start, min(end, len(pdf))):
            text += pdf[i].get_text()
        pdf.close()
        return text


# ============= CLOSURES =============

def create_pdf_processor(default_options):
    """
    Create a customized processor with preset options
    """
    def process(pdf_path, **override_options):
        # Combine default options with overrides
        options = {**default_options, **override_options}

        pdf = fitz.open(pdf_path)
        result = {"pages": []}

        for i in range(len(pdf)):
            if i >= options.get('start_page', 0) and \
               i < options.get('end_page', len(pdf)):
                page = pdf[i]
                page_data = {"page": i + 1}

                if options.get('extract_text', True):
                    page_data['text'] = page.get_text()

                if options.get('count_words', False):
                    page_data['words'] = len(page.get_text().split())

                result['pages'].append(page_data)

        pdf.close()
        return result

    return process


# ============= FUNCTION COMPOSITION =============

def compose(*functions):
    """
    Compose multiple functions into one
    """
    def composed(x):
        for func in reversed(functions):
            x = func(x)
        return x
    return composed


# Example functions to compose
def extract_text_simple(pdf_path):
    pdf = fitz.open(pdf_path)
    text = ""
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text

def clean_text_func(text):
    return ' '.join(text.split())

def uppercase_text(text):
    return text.upper()

# Composed function
extract_clean_upper = compose(uppercase_text, clean_text_func, extract_text_simple)


# ============= RECURSIVE FUNCTIONS =============

def process_pdf_directory(directory_path, results=None):
    """
    Recursively process all PDFs in directory and subdirectories
    """
    if results is None:
        results = []

    path = Path(directory_path)

    for item in path.iterdir():
        if item.is_file() and item.suffix.lower() == '.pdf':
            # Process PDF
            try:
                pdf = fitz.open(str(item))
                results.append({
                    "file": str(item),
                    "pages": len(pdf)
                })
                pdf.close()
            except:
                results.append({
                    "file": str(item),
                    "error": "Failed to process"
                })
        elif item.is_dir():
            # Recursive call for subdirectory
            process_pdf_directory(item, results)

    return results


# ============= MAIN TESTING FUNCTION =============

if __name__ == "__main__":
    pdf_file = "../nvidia.pdf"

    print("=== Level 4: Advanced Functions Demo ===\n")

    # Test 1: Default parameters
    print("1. Testing default parameters...")
    result = extract_pdf_text(pdf_file)  # All defaults
    print(f"   With defaults: {len(result['text'])} chars")
    result = extract_pdf_text(pdf_file, start_page=5, end_page=10)
    print(f"   Pages 5-10: {len(result['text'])} chars")
    result = extract_pdf_text(pdf_file, include_metadata=True)
    print(f"   With metadata: {result['pages_extracted']} pages\n")

    # Test 2: Variable arguments
    print("2. Testing *args...")
    result = combine_pdf_texts(pdf_file, pdf_file)  # Same file twice
    print(f"   Combined 2 PDFs: {len(result['text'])} chars")
    print(f"   Successful: {result['total_processed']}\n")

    # Test 3: Keyword arguments
    print("3. Testing **kwargs...")
    result = process_pdf_flexible(
        pdf_file,
        extract_text=True,
        count_pages=True,
        custom_setting="test"
    )
    print(f"   Operations: {result['operations_performed']}")
    print(f"   Custom options: {result['custom_options']}\n")

    # Test 4: Decorators
    print("4. Testing decorators...")
    text = extract_with_decorators(pdf_file)  # Will show timing
    print(f"   Extracted with retry: {len(text)} chars\n")

    # Test 5: Lambda functions
    print("5. Testing lambda functions...")
    # Get only first 5 pages
    pages = process_pages_with_filter(
        pdf_file,
        lambda p: p < 5
    )
    print(f"   First 5 pages: {len(pages)} pages")
    # Get even pages
    even_pages = process_pages_with_filter(
        pdf_file,
        lambda p: p % 2 == 0
    )
    print(f"   Even pages: {len(even_pages)} pages\n")

    # Test 6: Generators
    print("6. Testing generators...")
    gen = pdf_page_generator(pdf_file)
    first_page = next(gen)  # Get just first page
    print(f"   First page (generator): {len(first_page['text'])} chars")
    second_page = next(gen)  # Get second page
    print(f"   Second page (generator): {len(second_page['text'])} chars")
    # Generator doesn't load all pages at once!\n")

    # Test 7: Type hints
    print("7. Testing with type hints...")
    text_result: str = extract_page_range(pdf_file, 0, 3, as_list=False)
    list_result: List[str] = extract_page_range(pdf_file, 0, 3, as_list=True)
    print(f"   As string: {len(text_result)} chars")
    print(f"   As list: {len(list_result)} pages\n")

    # Test 8: Closures
    print("8. Testing closures...")
    # Create custom processor
    quick_processor = create_pdf_processor({
        'start_page': 0,
        'end_page': 3,
        'extract_text': True,
        'count_words': True
    })
    result = quick_processor(pdf_file)
    print(f"   Custom processor: {len(result['pages'])} pages")
    if result['pages']:
        print(f"   First page words: {result['pages'][0].get('words', 0)}\n")

    # Test 9: Function composition
    print("9. Testing function composition...")
    result = extract_clean_upper(pdf_file)
    print(f"   Composed result: {result[:50]}...")  # Show first 50 chars

    print("\n=== Advanced functions mastered! ===")
    print("You now understand:")
    print("- Default parameters & *args/**kwargs")
    print("- Decorators for reusable functionality")
    print("- Generators for memory efficiency")
    print("- Lambda functions for quick filters")
    print("- Type hints for clarity")
    print("- And much more!")