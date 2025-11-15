"""
Rebuild the Chroma vector store after database changes.
This is necessary after importing new courses or updating course data.

IMPORTANT: Stop your web application before running this script!
The chroma_db files must not be locked by another process.
"""
import shutil
from pathlib import Path
import sys
import os

# Add pdf_ingestion_system to path
sys.path.insert(0, str(Path(__file__).parent / "pdf_ingestion_system"))

try:
    from rag_retriever import CourseRAGRetriever
except ImportError as e:
    print(f"\n[ERROR] Missing dependencies: {e}")
    print("\nPlease install required packages:")
    print("  pip install langchain langchain-chroma langchain-huggingface chromadb sentence-transformers")
    sys.exit(1)


def rebuild_vector_store():
    """Delete old vector store and rebuild from current database."""

    print("=" * 60)
    print("VECTOR STORE REBUILD")
    print("=" * 60)

    # Path to vector store
    chroma_path = Path(__file__).parent / "pdf_ingestion_system" / "chroma_db"

    # Delete old vector store if it exists
    if chroma_path.exists():
        print(f"\n[DELETE] Removing old vector store: {chroma_path}")
        shutil.rmtree(chroma_path)
        print("[OK] Old vector store deleted")
    else:
        print(f"\n[INFO] No existing vector store found at {chroma_path}")

    # Rebuild vector store
    print("\n[BUILD] Creating new vector store from current database...")
    print("-" * 60)

    db_path = Path(__file__).parent / "pdf_ingestion_system" / "nvidia_courses.db"

    # Initialize retriever (this will create the vector store)
    retriever = CourseRAGRetriever(str(db_path))

    print("\n" + "-" * 60)
    print("[SUCCESS] Vector store rebuilt successfully!")
    print("=" * 60)

    # Test with the user's question
    print("\n[TEST] Testing with sample question...")
    print("-" * 60)

    question = "Tell me more about Rapid Application Development Using Large Language Models"
    print(f"\nQuestion: {question}\n")

    answer = retriever.answer_question(question)
    print(f"Answer:\n{answer}")

    print("\n" + "=" * 60)
    print("[COMPLETE] Vector store is ready for use!")
    print("=" * 60)

    retriever.close()


if __name__ == "__main__":
    rebuild_vector_store()
