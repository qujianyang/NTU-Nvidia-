# Level 3: Error Handling and Validation for PDF Processing
# Building on Level 2 - now making code safe and robust

import fitz
from pathlib import Path
import time
import logging
import sys

# ============= SETTING UP LOGGING =============

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============= BASIC TRY-EXCEPT =============

def safe_open_pdf(pdf_path):
    """
    Open PDF with error handling
    """
    try:
        pdf = fitz.open(pdf_path)
        logger.info(f"Successfully opened: {pdf_path}")
        return pdf
    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
        return None
    except Exception as e:
        logger.error(f"Failed to open PDF: {e}")
        return None


def safe_extract_text(pdf_path):
    """
    Extract text with multiple levels of error handling
    """
    # First, validate input
    if not pdf_path:
        logger.error("No PDF path provided")
        return {"success": False, "error": "No path provided", "text": ""}

    # Try to open PDF
    try:
        pdf = fitz.open(pdf_path)
    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
        return {"success": False, "error": "File not found", "text": ""}
    except PermissionError:
        logger.error(f"Permission denied: {pdf_path}")
        return {"success": False, "error": "Permission denied", "text": ""}
    except Exception as e:
        logger.error(f"Unknown error opening PDF: {e}")
        return {"success": False, "error": str(e), "text": ""}

    # Try to extract text
    all_text = ""
    errors = []

    for page_num in range(len(pdf)):
        try:
            page = pdf[page_num]
            page_text = page.get_text()
            all_text += page_text
        except Exception as e:
            # Log error but continue with other pages
            error_msg = f"Error on page {page_num + 1}: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)

    # Close PDF
    try:
        pdf.close()
    except:
        pass  # Even if close fails, we have the text

    # Return result with status
    return {
        "success": True,
        "text": all_text,
        "errors": errors,
        "pages_with_errors": len(errors)
    }


# ============= INPUT VALIDATION =============

def validate_pdf_path(pdf_path):
    """
    Check if path is valid before processing
    """
    # Check if path is provided
    if not pdf_path:
        return False, "Path is empty"

    # Convert to Path object
    path = Path(pdf_path)

    # Check if file exists
    if not path.exists():
        return False, f"File does not exist: {pdf_path}"

    # Check if it's actually a file (not directory)
    if not path.is_file():
        return False, f"Path is not a file: {pdf_path}"

    # Check file extension
    if path.suffix.lower() != '.pdf':
        return False, f"File is not a PDF: {path.suffix}"

    # Check if file is not empty
    if path.stat().st_size == 0:
        return False, "PDF file is empty"

    # Check if file is readable
    try:
        with open(path, 'rb') as f:
            f.read(1)  # Try to read 1 byte
    except PermissionError:
        return False, "No permission to read file"
    except Exception as e:
        return False, f"Cannot read file: {e}"

    return True, "Valid PDF file"


def validate_page_number(pdf_path, page_number):
    """
    Check if page number is valid for this PDF
    """
    try:
        pdf = fitz.open(pdf_path)
        total_pages = len(pdf)
        pdf.close()

        if page_number < 0:
            return False, "Page number cannot be negative"
        if page_number >= total_pages:
            return False, f"Page {page_number} doesn't exist (PDF has {total_pages} pages)"

        return True, "Valid page number"
    except Exception as e:
        return False, f"Cannot validate: {e}"


# ============= DEFENSIVE PROGRAMMING =============

def extract_page_safe(pdf_path, page_number, default_text="[Page content unavailable]"):
    """
    Extract single page with multiple safeguards
    """
    # Validate inputs first
    is_valid, message = validate_pdf_path(pdf_path)
    if not is_valid:
        logger.error(f"Invalid PDF: {message}")
        return default_text

    # Open PDF safely
    pdf = safe_open_pdf(pdf_path)
    if not pdf:
        return default_text

    # Validate page number
    if page_number < 0 or page_number >= len(pdf):
        logger.error(f"Invalid page number: {page_number}")
        pdf.close()
        return default_text

    # Extract with fallback
    try:
        page = pdf[page_number]
        text = page.get_text()

        # Check if we got text
        if not text or len(text.strip()) == 0:
            logger.warning(f"Page {page_number} appears to be empty")
            text = "[Empty page]"

        pdf.close()
        return text

    except Exception as e:
        logger.error(f"Failed to extract page {page_number}: {e}")
        try:
            pdf.close()
        except:
            pass
        return default_text


# ============= HANDLING SPECIFIC ERRORS =============

def process_pdf_with_recovery(pdf_path):
    """
    Process PDF with ability to recover from errors
    """
    results = {
        "success": False,
        "filename": "",
        "pages_processed": 0,
        "pages_failed": 0,
        "content": [],
        "errors": []
    }

    # Validate first
    is_valid, validation_msg = validate_pdf_path(pdf_path)
    if not is_valid:
        results["errors"].append(validation_msg)
        return results

    results["filename"] = Path(pdf_path).name

    # Try primary processing method
    try:
        pdf = fitz.open(pdf_path)
        total_pages = len(pdf)
        logger.info(f"Processing {total_pages} pages")

        for page_num in range(total_pages):
            try:
                # Try to get page
                page = pdf[page_num]
                text = page.get_text()

                # Store successful extraction
                results["content"].append({
                    "page": page_num + 1,
                    "text": text,
                    "status": "success"
                })
                results["pages_processed"] += 1

            except Exception as page_error:
                # Page failed but continue with others
                logger.warning(f"Page {page_num + 1} failed: {page_error}")
                results["content"].append({
                    "page": page_num + 1,
                    "text": "",
                    "status": "failed",
                    "error": str(page_error)
                })
                results["pages_failed"] += 1

        pdf.close()
        results["success"] = results["pages_processed"] > 0

    except Exception as pdf_error:
        logger.error(f"PDF processing failed completely: {pdf_error}")
        results["errors"].append(str(pdf_error))

        # Try alternative method
        logger.info("Attempting alternative extraction method...")
        try:
            # Simpler extraction as fallback
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    try:
                        text = page.get_text("text")  # Simpler text extraction
                        results["content"].append({
                            "page": page.number + 1,
                            "text": text,
                            "status": "recovered"
                        })
                        results["pages_processed"] += 1
                    except:
                        results["pages_failed"] += 1

            results["success"] = results["pages_processed"] > 0

        except Exception as fallback_error:
            results["errors"].append(f"Fallback also failed: {fallback_error}")

    return results


# ============= TIMEOUT HANDLING =============

def extract_with_timeout(pdf_path, max_seconds=30):
    """
    Extract text but stop if taking too long
    """
    import signal

    class TimeoutException(Exception):
        pass

    def timeout_handler(signum, frame):
        raise TimeoutException("Processing took too long")

    # This works on Unix/Linux/Mac (not Windows)
    if sys.platform != "win32":
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(max_seconds)

    try:
        # Do the extraction
        result = safe_extract_text(pdf_path)

        if sys.platform != "win32":
            signal.alarm(0)  # Cancel timeout

        return result

    except TimeoutException:
        logger.error(f"Timeout: Processing took longer than {max_seconds} seconds")
        return {"success": False, "error": "Timeout", "text": ""}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {"success": False, "error": str(e), "text": ""}


# ============= RESOURCE CLEANUP =============

def process_with_cleanup(pdf_path):
    """
    Ensure resources are always cleaned up
    """
    pdf = None
    results = None

    try:
        # Allocate resources
        pdf = fitz.open(pdf_path)
        results = []

        # Process
        for page in pdf:
            results.append(page.get_text())

        return {"success": True, "pages": results}

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return {"success": False, "error": str(e)}

    finally:
        # This ALWAYS runs, even if there's an error
        if pdf:
            try:
                pdf.close()
                logger.info("PDF closed successfully")
            except:
                logger.warning("Failed to close PDF")

        # Could also clean up temp files, close connections, etc.
        logger.info("Cleanup completed")


# ============= USER-FRIENDLY ERROR MESSAGES =============

def extract_with_user_messages(pdf_path):
    """
    Provide helpful error messages for users
    """
    # Check file existence with user-friendly message
    if not Path(pdf_path).exists():
        return {
            "success": False,
            "user_message": f"Cannot find the file '{pdf_path}'. Please check the file path.",
            "suggestion": "Make sure the file exists and the path is correct."
        }

    # Check file type
    if not pdf_path.lower().endswith('.pdf'):
        return {
            "success": False,
            "user_message": "This doesn't appear to be a PDF file.",
            "suggestion": "Please provide a file with .pdf extension."
        }

    # Try to process
    try:
        pdf = fitz.open(pdf_path)
        text = ""
        for page in pdf:
            text += page.get_text()
        pdf.close()

        if not text.strip():
            return {
                "success": True,
                "text": text,
                "user_message": "PDF processed but appears to be empty.",
                "suggestion": "This might be a scanned PDF. Consider using OCR."
            }

        return {
            "success": True,
            "text": text,
            "user_message": "PDF processed successfully!",
            "pages": len(pdf)
        }

    except PermissionError:
        return {
            "success": False,
            "user_message": "Cannot access the PDF file.",
            "suggestion": "Make sure the file is not open in another program."
        }
    except Exception as e:
        return {
            "success": False,
            "user_message": "Something went wrong while processing the PDF.",
            "suggestion": "Try with a different PDF file or contact support.",
            "technical_error": str(e)
        }


# ============= BATCH PROCESSING WITH ERROR RECOVERY =============

def process_multiple_pdfs(pdf_paths):
    """
    Process multiple PDFs, continuing even if some fail
    """
    results = {
        "total": len(pdf_paths),
        "successful": 0,
        "failed": 0,
        "details": []
    }

    for pdf_path in pdf_paths:
        logger.info(f"Processing: {pdf_path}")

        try:
            # Validate first
            is_valid, msg = validate_pdf_path(pdf_path)
            if not is_valid:
                raise ValueError(msg)

            # Process
            text = safe_extract_text(pdf_path)
            if text["success"]:
                results["successful"] += 1
                results["details"].append({
                    "file": pdf_path,
                    "status": "success",
                    "pages": len(text["text"].split("\n")) // 50  # Rough page estimate
                })
            else:
                raise Exception(text.get("error", "Unknown error"))

        except Exception as e:
            # Log but continue with next file
            logger.error(f"Failed to process {pdf_path}: {e}")
            results["failed"] += 1
            results["details"].append({
                "file": pdf_path,
                "status": "failed",
                "error": str(e)
            })

    # Summary
    logger.info(f"Batch complete: {results['successful']}/{results['total']} successful")
    return results


# ============= MAIN TESTING FUNCTION =============

if __name__ == "__main__":
    # Test file
    pdf_file = "../nvidia.pdf"

    # Bad file for testing errors
    bad_file = "nonexistent.pdf"
    not_pdf = "test.txt"

    print("=== Level 3: Error Handling Demo ===\n")

    # Test 1: Validation
    print("1. Testing validation...")
    is_valid, msg = validate_pdf_path(pdf_file)
    print(f"   Valid PDF: {is_valid} - {msg}")
    is_valid, msg = validate_pdf_path(bad_file)
    print(f"   Bad file: {is_valid} - {msg}\n")

    # Test 2: Safe extraction
    print("2. Testing safe extraction...")
    result = safe_extract_text(pdf_file)
    if result["success"]:
        print(f"   Success! Extracted {len(result['text'])} characters")
        if result.get("errors"):
            print(f"   Had {len(result['errors'])} page errors")
    else:
        print(f"   Failed: {result['error']}\n")

    # Test 3: Error recovery
    print("3. Testing error recovery...")
    result = process_pdf_with_recovery(pdf_file)
    print(f"   Processed: {result['pages_processed']} pages")
    print(f"   Failed: {result['pages_failed']} pages\n")

    # Test 4: User-friendly messages
    print("4. Testing user-friendly errors...")
    result = extract_with_user_messages(bad_file)
    if not result["success"]:
        print(f"   Message: {result['user_message']}")
        print(f"   Suggestion: {result['suggestion']}\n")

    # Test 5: Cleanup
    print("5. Testing resource cleanup...")
    result = process_with_cleanup(pdf_file)
    print(f"   Cleanup test completed: {result['success']}\n")

    # Test 6: Batch processing
    print("6. Testing batch processing...")
    test_files = [pdf_file, bad_file, pdf_file]  # Mix of good and bad
    batch_result = process_multiple_pdfs(test_files)
    print(f"   Results: {batch_result['successful']}/{batch_result['total']} successful")
    for detail in batch_result["details"]:
        print(f"   - {Path(detail['file']).name}: {detail['status']}")

    print("\n=== Error handling complete! ===")
    print("Your code is now much more robust and user-friendly!")