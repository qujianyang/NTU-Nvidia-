import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import hashlib


class SQLiteStorage:
    def __init__(self, db_path: str = "pdf_documents.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create documents and chunks tables if they don't exist."""
        cursor = self.conn.cursor()

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                page_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document_id
            ON chunks(document_id)
        """)

        self.conn.commit()

    def store_document(self, doc_info: Dict[str, Any], chunks: List[Dict[str, Any]]) -> str:
        """Store document and its chunks in the database."""
        cursor = self.conn.cursor()

        # Generate document ID from file content hash
        doc_id = doc_info.get('doc_id', hashlib.md5(doc_info['filename'].encode()).hexdigest())

        # Insert document
        cursor.execute("""
            INSERT OR REPLACE INTO documents (id, filename, filepath, page_count, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            doc_id,
            doc_info['filename'],
            doc_info['filepath'],
            doc_info.get('page_count', 0),
            datetime.now()
        ))

        # Delete existing chunks for this document (if re-processing)
        cursor.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))

        # Insert chunks
        for chunk in chunks:
            cursor.execute("""
                INSERT INTO chunks (document_id, chunk_index, content, char_count, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                doc_id,
                chunk['chunk_index'],
                chunk['content'],
                chunk['char_count'],
                datetime.now()
            ))

        self.conn.commit()
        return doc_id

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get document metadata by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_index
        """, (doc_id,))
        return [dict(row) for row in cursor.fetchall()]

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT d.*, COUNT(c.id) as chunk_count
            FROM documents d
            LEFT JOIN chunks c ON d.id = c.document_id
            GROUP BY d.id
            ORDER BY d.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()