"""
Import merged catalog while preserving user data.
Clears course tables but keeps user tables intact.
"""

import sqlite3
import sys
from pathlib import Path

# Add pdf_ingestion_system to path for imports
sys.path.insert(0, str(Path(__file__).parent / "pdf_ingestion_system"))

from json_importer import CourseImporter

DB_PATH = "pdf_ingestion_system/nvidia_courses.db"
MERGED_JSON = "nvidia_courses_merged.json"


def clear_course_data_only(db_path: str):
    """Clear course-related tables while preserving user data."""
    print("=" * 60)
    print("CLEARING COURSE DATA (PRESERVING USER DATA)")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current stats
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user_progress")
    progress_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user_sessions")
    session_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user_chat_history")
    chat_count = cursor.fetchone()[0]

    print(f"\nPreserving user data:")
    print(f"  Users: {user_count}")
    print(f"  User Progress: {progress_count}")
    print(f"  User Sessions: {session_count}")
    print(f"  Chat History: {chat_count}")

    # Clear only course-related tables
    print("\nClearing course tables...")
    cursor.execute("DELETE FROM child_chunks")
    cursor.execute("DELETE FROM parent_documents")
    cursor.execute("DELETE FROM courses")

    conn.commit()
    conn.close()

    print("[OK] Course data cleared")
    print("=" * 60 + "\n")


def main():
    # Step 1: Clear course data only
    clear_course_data_only(DB_PATH)

    # Step 2: Import merged catalog
    print("=" * 60)
    print("IMPORTING MERGED CATALOG")
    print("=" * 60)
    print(f"Source: {MERGED_JSON}\n")

    importer = CourseImporter(DB_PATH)
    try:
        importer.import_from_json(MERGED_JSON)
    finally:
        importer.close()

    # Step 3: Verify final state
    print("\n" + "=" * 60)
    print("VERIFYING DATABASE")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM courses")
    course_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM parent_documents")
    parent_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM child_chunks")
    chunk_count = cursor.fetchone()[0]

    cursor.execute("SELECT domain, COUNT(*) FROM courses GROUP BY domain")
    domain_counts = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    print("\nCourse Data:")
    print(f"  Total Courses: {course_count}")
    for domain, count in domain_counts:
        print(f"    {domain}: {count}")
    print(f"  Parent Documents: {parent_count}")
    print(f"  Child Chunks: {chunk_count}")

    print("\nUser Data (Preserved):")
    print(f"  Users: {user_count}")

    conn.close()

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
