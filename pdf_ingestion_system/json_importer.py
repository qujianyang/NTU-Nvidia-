import json
from pathlib import Path
from typing import Dict, Any, List
from course_database import CourseDatabase
from chunker import SmartChunker


class CourseImporter:
    """Simple importer to load courses from JSON into parent-child database."""

    def __init__(self, db_path: str = "nvidia_courses.db"):
        self.db = CourseDatabase(db_path)
        self.chunker = SmartChunker(chunk_size=512, chunk_overlap=64)

    def import_from_json(self, json_path: str):
        """Import all courses from JSON file."""
        print(f"Loading courses from {json_path}...")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        courses = data.get('courses', [])
        print(f"Found {len(courses)} courses")

        for i, course in enumerate(courses, 1):
            print(f"\n[{i}/{len(courses)}] Processing: {course['title']}")
            self._import_course(course)

        print("\n" + "="*50)
        print("Import complete!")
        stats = self.db.get_course_stats()
        print(f"Courses: {stats['courses']}")
        print(f"Parent Documents: {stats['parent_documents']}")
        print(f"Child Chunks: {stats['child_chunks']}")

    def _import_course(self, course: Dict[str, Any]):
        """Import a single course with parent-child structure."""

        # 1. Insert flat course data
        course_id = self.db.insert_course(course)

        # 2. Build parent document (full context)
        parent_content = self._build_parent_document(course)
        parent_id = self.db.insert_parent_document(course_id, parent_content)

        # 3. Chunk parent into children
        chunks = self.chunker.chunk_markdown(parent_content)
        self.db.insert_child_chunks(parent_id, course_id, chunks)

        print(f"  -> Created parent doc with {len(chunks)} child chunks")

    def _build_parent_document(self, course: Dict[str, Any]) -> str:
        """Build comprehensive parent document from course data."""
        sections = []

        # Title and basic info
        sections.append(f"# {course['title']}\n")
        sections.append(f"**Level:** {course.get('level', 'N/A')}")
        sections.append(f"**Duration:** {course.get('duration', 'N/A')}")
        sections.append(f"**Price:** {course.get('price', 'N/A')}\n")

        # Description
        if course.get('description'):
            sections.append(f"## About This Course\n{course['description']}\n")

        # Learning objectives
        if course.get('learning_objectives'):
            sections.append("## Learning Objectives")
            for obj in course['learning_objectives']:
                sections.append(f"- {obj}")
            sections.append("")

        # Target audience
        if course.get('target_audience'):
            sections.append(f"## Target Audience\n{course['target_audience']}\n")

        # Technical requirements
        if course.get('technical_requirements'):
            sections.append(f"## Prerequisites\n{course['technical_requirements']}\n")

        # Skills taught
        if course.get('skills_taught'):
            sections.append(f"## Skills You'll Learn\n{', '.join(course['skills_taught'])}\n")

        # Course relationships
        if course.get('prerequisites'):
            sections.append(f"## Required Prerequisites\nYou should complete: {', '.join(course['prerequisites'])}\n")

        if course.get('leads_to'):
            sections.append(f"## Next Steps\nAfter this course, consider: {', '.join(course['leads_to'])}\n")

        # Additional metadata
        sections.append(f"## Course Details")
        sections.append(f"Course ID: {course['id']}")
        sections.append(f"URL: {course.get('url', 'N/A')}")
        sections.append(f"Category: {course.get('category', 'N/A')}")

        return "\n".join(sections)

    def close(self):
        """Close database connection."""
        self.db.close()


def main():
    """Main entry point for importing courses."""
    import sys

    # Default JSON path
    default_json = r"C:\Users\user\Documents\GitHub\NTU-Nvidia-\nvidia_courses_template.json"

    # Check command line argument
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = default_json

    if not Path(json_path).exists():
        print(f"Error: JSON file not found: {json_path}")
        print("\nUsage: python json_importer.py <path_to_json>")
        return

    # Import courses
    importer = CourseImporter()
    try:
        importer.import_from_json(json_path)
    finally:
        importer.close()


if __name__ == "__main__":
    main()