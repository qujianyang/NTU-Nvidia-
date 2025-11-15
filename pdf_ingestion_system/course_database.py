import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class CourseDatabase:
    """Simple SQLite database for course data with parent-child RAG structure."""

    def __init__(self, db_path: str = "nvidia_courses.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create three simple tables: courses, parent_documents, child_chunks."""
        cursor = self.conn.cursor()

        # Courses table - flat course data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT,
                duration TEXT,
                duration_hours REAL,
                price TEXT,
                cost_usd REAL,
                level TEXT,
                domain TEXT,         -- LLM or Robotics
                description TEXT,
                target_audience TEXT,
                technical_requirements TEXT,
                prerequisites TEXT,  -- JSON array of prerequisite course IDs
                leads_to TEXT,       -- JSON array of next course IDs
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Parent documents table - full context for RAG
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parent_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        # Child chunks table - searchable pieces
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS child_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES parent_documents(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        # Indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent_course ON parent_documents(course_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_child_parent ON child_chunks(parent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_child_course ON child_chunks(course_id)")

        self.conn.commit()

    def insert_course(self, course: Dict[str, Any]) -> str:
        """Insert a course into the database."""
        import json
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO courses
            (id, title, url, duration, duration_hours, price, cost_usd, level, domain,
             description, target_audience, technical_requirements,
             prerequisites, leads_to, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course['id'],
            course['title'],
            course.get('url', ''),
            course.get('duration', ''),
            course.get('duration_hours', 0),
            course.get('price', ''),
            course.get('cost_usd', 0),
            course.get('level', ''),
            course.get('domain', 'LLM'),  # Default to LLM if not specified
            course.get('description', ''),
            course.get('target_audience', ''),
            course.get('technical_requirements', ''),
            json.dumps(course.get('prerequisites', [])),  # Store as JSON array
            json.dumps(course.get('leads_to', [])),       # Store as JSON array
            datetime.now()
        ))
        self.conn.commit()
        return course['id']

    def insert_parent_document(self, course_id: str, content: str) -> int:
        """Insert a parent document and return its ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO parent_documents (course_id, content, created_at)
            VALUES (?, ?, ?)
        """, (course_id, content, datetime.now()))
        self.conn.commit()
        return cursor.lastrowid

    def insert_child_chunks(self, parent_id: int, course_id: str, chunks: List[Dict[str, Any]]):
        """Insert child chunks for a parent document."""
        cursor = self.conn.cursor()
        for chunk in chunks:
            cursor.execute("""
                INSERT INTO child_chunks
                (parent_id, course_id, chunk_index, content, char_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                parent_id,
                course_id,
                chunk['chunk_index'],
                chunk['content'],
                chunk['char_count'],
                datetime.now()
            ))
        self.conn.commit()

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Get all courses."""
        import json
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY title")
        courses = []
        for row in cursor.fetchall():
            course = dict(row)
            # Parse JSON fields back to lists
            if course.get('prerequisites'):
                course['prerequisites'] = json.loads(course['prerequisites'])
            else:
                course['prerequisites'] = []
            if course.get('leads_to'):
                course['leads_to'] = json.loads(course['leads_to'])
            else:
                course['leads_to'] = []
            courses.append(course)
        return courses

    def get_course_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM parent_documents")
        parent_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM child_chunks")
        chunk_count = cursor.fetchone()[0]

        return {
            'courses': course_count,
            'parent_documents': parent_count,
            'child_chunks': chunk_count
        }

    def close(self):
        """Close database connection."""
        self.conn.close()