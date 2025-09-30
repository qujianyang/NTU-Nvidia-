from course_database import CourseDatabase


def test_import():
    """Simple test to verify course import worked correctly."""
    db = CourseDatabase("nvidia_courses.db")

    print("="*60)
    print("NVIDIA Course Database Test")
    print("="*60)

    # Get stats
    stats = db.get_course_stats()
    print(f"\n[*] Database Statistics:")
    print(f"  Courses: {stats['courses']}")
    print(f"  Parent Documents: {stats['parent_documents']}")
    print(f"  Child Chunks: {stats['child_chunks']}")

    # List all courses
    print(f"\n[*] All Courses:")
    courses = db.get_all_courses()
    for i, course in enumerate(courses, 1):
        print(f"  {i}. [{course['id']}] {course['title']}")
        print(f"     Level: {course['level']} | Duration: {course['duration']}")

    # Sample a course with parent/child
    if courses:
        sample = courses[0]
        print(f"\n[*] Sample Course Details: {sample['title']}")
        print(f"  Description: {sample['description'][:200]}...")

        # Get parent document
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT id, content FROM parent_documents
            WHERE course_id = ?
        """, (sample['id'],))
        parent = cursor.fetchone()

        if parent:
            print(f"\n[*] Parent Document Preview:")
            print(f"  Length: {len(parent['content'])} characters")
            print(f"  Preview: {parent['content'][:300]}...")

            # Get child chunks
            cursor.execute("""
                SELECT COUNT(*) FROM child_chunks
                WHERE parent_id = ?
            """, (parent['id'],))
            chunk_count = cursor.fetchone()[0]
            print(f"\n[*] Child Chunks: {chunk_count} chunks")

            # Show first 3 chunks
            cursor.execute("""
                SELECT chunk_index, content, char_count FROM child_chunks
                WHERE parent_id = ?
                ORDER BY chunk_index
                LIMIT 3
            """, (parent['id'],))
            chunks = cursor.fetchall()

            for chunk in chunks:
                print(f"\n  Chunk {chunk[0]} ({chunk[2]} chars):")
                print(f"    {chunk[1][:150]}...")

    print("\n" + "="*60)
    print("[OK] Test complete!")
    print("="*60)

    db.close()


if __name__ == "__main__":
    test_import()