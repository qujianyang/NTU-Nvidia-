import sys
from pathlib import Path
from pdf_processor import PDFProcessor
from chunker import SmartChunker
from database import SQLiteStorage


def process_pdf(pdf_path: str, chunk_size: int = 512, chunk_overlap: int = 64):
    """
    Main function to process a PDF document and store it in SQLite database.

    Args:
        pdf_path: Path to the PDF file
        chunk_size: Maximum characters per chunk (default 512)
        chunk_overlap: Number of characters to overlap between chunks (default 64)

    Returns:
        Document ID of the processed document
    """
    print(f"\n=== PDF Ingestion System ===")
    print(f"Processing: {pdf_path}")
    print(f"Chunk size: {chunk_size} chars")
    print(f"Chunk overlap: {chunk_overlap} chars\n")

    # Initialize components
    processor = PDFProcessor()
    chunker = SmartChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    store = SQLiteStorage()

    try:
        # Step 1: Process PDF
        print("Step 1: Extracting content from PDF...")
        doc_info = processor.process_pdf(pdf_path)
        content = doc_info.pop('content')  # Remove content from doc_info for storage

        print(f"  - Extracted {len(content)} characters")
        print(f"  - Page count: {doc_info['page_count']}")

        # Step 2: Chunk content
        print("\nStep 2: Creating chunks...")
        chunks = chunker.chunk_markdown(content)

        # Get chunking statistics
        stats = chunker.get_stats(chunks)
        print(f"  - Created {stats['total_chunks']} chunks")
        print(f"  - Average chunk size: {stats['avg_chunk_size']} chars")
        print(f"  - Min/Max chunk size: {stats['min_chunk_size']}/{stats['max_chunk_size']} chars")

        # Step 3: Store in SQLite
        print("\nStep 3: Storing to SQLite database...")
        doc_id = store.store_document(doc_info, chunks)
        print(f"  - Document ID: {doc_id}")
        print(f"  - Database: {store.db_path}")

        # Display sample chunks
        print("\n=== Sample Chunks (First 3) ===")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i}:")
            preview = chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content']
            print(f"  {preview}")
            print(f"  [Length: {chunk['char_count']} chars]")

        print(f"\n[SUCCESS] Processing complete! Document stored with ID: {doc_id}")
        print(f"  Open {store.db_path} in DB Browser for SQLite to view the data.")

        store.close()
        return doc_id

    except Exception as e:
        print(f"\n[ERROR] Error processing PDF: {e}")
        store.close()
        raise


def list_documents():
    """List all documents in the database."""
    store = SQLiteStorage()
    documents = store.list_documents()

    if not documents:
        print("No documents found in database.")
        store.close()
        return

    print("\n=== Documents in Database ===")
    for doc in documents:
        print(f"\nDocument ID: {doc['id']}")
        print(f"  Filename: {doc['filename']}")
        print(f"  Pages: {doc['page_count']}")
        print(f"  Chunks: {doc['chunk_count']}")
        print(f"  Created: {doc['created_at']}")

    store.close()


def view_chunks(doc_id: str, max_chunks: int = 5):
    """View chunks for a specific document."""
    store = SQLiteStorage()

    # Get document info
    doc = store.get_document(doc_id)
    if not doc:
        print(f"Document not found: {doc_id}")
        store.close()
        return

    # Get chunks
    chunks = store.get_chunks(doc_id)

    print(f"\n=== Chunks for Document: {doc['filename']} ===")
    print(f"Total chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks[:max_chunks]):
        print(f"\n--- Chunk {chunk['chunk_index']} ---")
        preview = chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content']
        print(preview)
        print(f"[Length: {chunk['char_count']} chars]")

    if len(chunks) > max_chunks:
        print(f"\n... and {len(chunks) - max_chunks} more chunks")

    store.close()


if __name__ == "__main__":
    # Default PDF path from the project
    default_pdf = r"C:\Users\qujia\QuantumKeyDistribution\NTU-Nvidia-\nvt-learning-learning-path-developers-it-administrators.pdf"

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_documents()
        elif sys.argv[1] == "view" and len(sys.argv) > 2:
            view_chunks(sys.argv[2])
        else:
            pdf_path = sys.argv[1]
            if Path(pdf_path).exists():
                process_pdf(pdf_path)
            else:
                print(f"Error: PDF file not found: {pdf_path}")
    else:
        # Process default PDF if it exists
        if Path(default_pdf).exists():
            process_pdf(default_pdf)
        else:
            print("Usage:")
            print("  python main.py <pdf_path>       # Process a PDF file")
            print("  python main.py list              # List all documents")
            print("  python main.py view <doc_id>     # View chunks for a document")
            print(f"\nDefault PDF not found: {default_pdf}")