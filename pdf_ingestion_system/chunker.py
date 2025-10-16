"""
Simple text chunker for breaking documents into smaller pieces
Following KISS principle - just splits text into manageable chunks
"""

from typing import List, Dict, Any


class SmartChunker:
    """Simple chunker that splits text into manageable pieces."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_markdown(self, text: str) -> List[Dict[str, Any]]:
        """
        Split markdown text into chunks with overlap.

        Args:
            text: The markdown text to chunk

        Returns:
            List of chunk dictionaries with content and metadata
        """
        chunks = []
        words = text.split()

        # If text is short enough, return as single chunk
        if len(text) <= self.chunk_size:
            return [{
                'chunk_index': 0,
                'content': text,
                'char_count': len(text)
            }]

        # Split into chunks by character count
        start = 0
        chunk_index = 0

        while start < len(text):
            # Find end position for this chunk
            end = start + self.chunk_size

            # Try to break at word boundary if possible
            if end < len(text):
                # Look for last space before chunk_size
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space

            # Create chunk
            chunk_content = text[start:end].strip()
            if chunk_content:  # Only add non-empty chunks
                chunks.append({
                    'chunk_index': chunk_index,
                    'content': chunk_content,
                    'char_count': len(chunk_content)
                })
                chunk_index += 1

            # Move start position with overlap
            start = end - self.chunk_overlap if end < len(text) else end

        return chunks