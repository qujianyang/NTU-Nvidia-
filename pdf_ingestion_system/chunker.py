from typing import List, Dict, Any
import re


class SmartChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        """
        Initialize the chunker with configurable chunk size and overlap.

        Args:
            chunk_size: Maximum characters per chunk (default 512)
            chunk_overlap: Number of characters to overlap between chunks (default 64)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_markdown(self, content: str) -> List[Dict[str, Any]]:
        """
        Intelligently chunk markdown content preserving structure.

        This method attempts to:
        1. Preserve markdown headers (##, ###, etc.)
        2. Keep paragraphs intact when possible
        3. Maintain context between chunks with overlap

        Args:
            content: The markdown content to chunk

        Returns:
            List of chunk dictionaries with content and metadata
        """
        chunks = []

        if not content:
            return chunks

        # Split by major sections (## headers)
        sections = re.split(r'\n(?=##\s)', content)

        current_chunk = ""
        chunk_index = 0

        for section in sections:
            # If section fits in current chunk, add it
            if len(current_chunk) + len(section) <= self.chunk_size:
                current_chunk += section + "\n"
            else:
                # Save current chunk if not empty
                if current_chunk.strip():
                    chunks.append({
                        'chunk_index': chunk_index,
                        'content': current_chunk.strip(),
                        'char_count': len(current_chunk.strip())
                    })
                    chunk_index += 1

                    # Add overlap from end of previous chunk to start of new one
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        overlap_text = current_chunk[-self.chunk_overlap:]
                        current_chunk = overlap_text

                # Handle large sections that exceed chunk size
                if len(section) > self.chunk_size:
                    sub_chunks = self._split_large_section(section)
                    for i, sub_chunk in enumerate(sub_chunks):
                        if i == 0 and current_chunk:
                            # Combine with overlap if exists
                            combined = current_chunk + sub_chunk
                            if len(combined) <= self.chunk_size:
                                chunks.append({
                                    'chunk_index': chunk_index,
                                    'content': combined.strip(),
                                    'char_count': len(combined.strip())
                                })
                            else:
                                # Save overlap as separate chunk
                                if current_chunk.strip():
                                    chunks.append({
                                        'chunk_index': chunk_index,
                                        'content': current_chunk.strip(),
                                        'char_count': len(current_chunk.strip())
                                    })
                                    chunk_index += 1
                                chunks.append({
                                    'chunk_index': chunk_index,
                                    'content': sub_chunk.strip(),
                                    'char_count': len(sub_chunk.strip())
                                })
                        else:
                            chunks.append({
                                'chunk_index': chunk_index,
                                'content': sub_chunk.strip(),
                                'char_count': len(sub_chunk.strip())
                            })
                        chunk_index += 1
                    current_chunk = ""
                else:
                    current_chunk = section + "\n"

        # Don't forget last chunk
        if current_chunk.strip():
            chunks.append({
                'chunk_index': chunk_index,
                'content': current_chunk.strip(),
                'char_count': len(current_chunk.strip())
            })

        return chunks

    def _split_large_section(self, text: str) -> List[str]:
        """
        Split large sections by paragraphs or sentences.

        Args:
            text: Large text section to split

        Returns:
            List of smaller text chunks
        """
        chunks = []

        # Try to split by paragraphs first
        paragraphs = text.split('\n\n')

        current = ""
        for para in paragraphs:
            # If paragraph itself is too large, split by sentences
            if len(para) > self.chunk_size:
                # Split by sentences (periods followed by space or newline)
                sentences = re.split(r'(?<=[.!?])\s+', para)

                for sentence in sentences:
                    if len(current) + len(sentence) <= self.chunk_size:
                        current += sentence + " "
                    else:
                        if current.strip():
                            chunks.append(current.strip())

                        # If single sentence is too long, force split
                        if len(sentence) > self.chunk_size:
                            # Split long sentence into smaller pieces
                            for i in range(0, len(sentence), self.chunk_size - self.chunk_overlap):
                                chunk = sentence[i:i + self.chunk_size]
                                chunks.append(chunk.strip())
                            current = ""
                        else:
                            current = sentence + " "
            else:
                # Paragraph fits
                if len(current) + len(para) <= self.chunk_size:
                    current += para + "\n\n"
                else:
                    if current.strip():
                        chunks.append(current.strip())
                    current = para + "\n\n"

        if current.strip():
            chunks.append(current.strip())

        return chunks

    def get_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics for the chunks.

        Args:
            chunks: List of chunks

        Returns:
            Dictionary with chunking statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'avg_chunk_size': 0,
                'min_chunk_size': 0,
                'max_chunk_size': 0,
                'total_chars': 0
            }

        char_counts = [chunk['char_count'] for chunk in chunks]

        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(char_counts) // len(char_counts),
            'min_chunk_size': min(char_counts),
            'max_chunk_size': max(char_counts),
            'total_chars': sum(char_counts)
        }