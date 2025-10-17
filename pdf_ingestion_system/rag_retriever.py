"""
RAG Retriever with Parent Document Retriever Pattern
Integrates with Ollama LLM for answering questions about NVIDIA courses
"""

from typing import List, Dict, Any
from pathlib import Path
import requests
import time

from langchain_chroma import Chroma
from langchain_core.documents import Document
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from course_database import CourseDatabase

# ============================================================================
# CONFIGURATION - Edit these settings
# ============================================================================

# Ollama settings
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2:7b-instruct-q4_0"

# Embedding settings (local, no API key needed)
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Retrieval settings
TOP_K_CHUNKS = 4  # Number of child chunks to retrieve
CHUNK_OVERLAP = 2  # Number of parent docs to return

# LLM generation settings
LLM_TEMPERATURE = 0.2
LLM_TIMEOUT = 120

# ============================================================================


class CourseRAGRetriever:
    """
    RAG system using Parent Document Retriever pattern.

    - Searches child chunks for relevance
    - Returns full parent documents for context
    - Generates answers using Ollama
    """

    def __init__(self, db_path: str = "nvidia_courses.db"):
        self.db_path = db_path
        self.db = CourseDatabase(db_path)

        print("Initializing RAG retriever...")
        self.embeddings = self._load_embeddings()
        self.vectorstore, self.parent_map = self._setup_vectorstore()
        print("RAG retriever ready!")

    def _load_embeddings(self):
        """Load local embedding model."""
        print(f"Loading embeddings model: {EMBEDDING_MODEL}")
        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def _setup_vectorstore(self):
        """Set up vector store with child chunks and parent document mapping."""
        print("Loading parent documents and child chunks from database...")

        # Get all parent documents
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, course_id, content
            FROM parent_documents
            ORDER BY id
        """)
        parent_rows = cursor.fetchall()

        # Get all child chunks
        cursor.execute("""
            SELECT id, parent_id, content, chunk_index
            FROM child_chunks
            ORDER BY parent_id, chunk_index
        """)
        child_rows = cursor.fetchall()

        print(f"Loaded {len(parent_rows)} parent docs, {len(child_rows)} child chunks")

        # Create parent document map (parent_id -> parent content)
        parent_map = {}
        for row in parent_rows:
            parent_map[row[0]] = {
                'content': row[2],
                'course_id': row[1]
            }

        # Create child documents with parent_id in metadata
        child_docs = []
        for row in child_rows:
            doc = Document(
                page_content=row[2],  # content
                metadata={
                    "parent_id": row[1],  # parent_id
                    "chunk_index": row[3]  # chunk_index
                }
            )
            child_docs.append(doc)

        # Create vector store for child chunks
        print("Creating vector store...")
        vectorstore = Chroma.from_documents(
            documents=child_docs,
            embedding=self.embeddings,
            collection_name="course_chunks"
        )

        return vectorstore, parent_map

    def query(self, question: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant parent documents for a question.

        Args:
            question: User's question

        Returns:
            List of parent documents (dicts with content and course_id)
        """
        print(f"\nSearching for: {question}")

        # Search child chunks
        child_docs = self.vectorstore.similarity_search(question, k=TOP_K_CHUNKS)
        print(f"Found {len(child_docs)} matching child chunks")

        # Get unique parent IDs from matching chunks
        parent_ids = set()
        for doc in child_docs:
            parent_id = doc.metadata.get('parent_id')
            if parent_id:
                parent_ids.add(parent_id)

        # Retrieve parent documents
        parent_docs = []
        for parent_id in list(parent_ids)[:CHUNK_OVERLAP]:  # Limit to CHUNK_OVERLAP parents
            if parent_id in self.parent_map:
                parent_docs.append(self.parent_map[parent_id])

        print(f"Retrieved {len(parent_docs)} parent documents")
        return parent_docs

    def answer_question(self, question: str) -> str:
        """
        Answer a question using RAG.

        Args:
            question: User's question

        Returns:
            Generated answer from Ollama
        """
        # Retrieve relevant documents
        parent_docs = self.query(question)

        if not parent_docs:
            return "I couldn't find relevant information about that in the NVIDIA course catalog."

        # Build context from parent documents
        context_parts = []
        for i, doc in enumerate(parent_docs, 1):
            course_id = doc.get('course_id', 'unknown')
            content = doc.get('content', '')
            context_parts.append(f"[Course {i} - {course_id}]\n{content}\n")

        context = "\n---\n".join(context_parts)

        # Build prompt
        prompt = self._build_prompt(question, context)

        # Generate answer with Ollama
        answer = self._call_ollama(prompt)

        return answer

    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for LLM."""
        return f"""You are a helpful assistant that answers questions about NVIDIA's robotics and AI courses.

Based on the course information below, answer the user's question clearly and concisely.

COURSE INFORMATION:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer based only on the provided course information
- Be specific about course names, prerequisites, and learning paths
- If the information doesn't fully answer the question, say so
- Keep your answer focused and practical

ANSWER:"""

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate answer."""
        url = f"{OLLAMA_API_URL}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": LLM_TEMPERATURE,
                "top_p": 0.8,
                "top_k": 20,
                "num_ctx": 4096,
            }
        }

        print("Generating answer with Ollama...")
        start = time.time()

        try:
            response = requests.post(url, json=payload, timeout=LLM_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            answer = data.get("response", "")

            elapsed = time.time() - start
            print(f"Answer generated in {elapsed:.2f}s")

            return answer.strip()

        except requests.RequestException as e:
            print(f"Error calling Ollama: {e}")
            return f"Error generating answer: {e}"

    def close(self):
        """Close database connection."""
        self.db.close()


def test_retriever():
    """Simple test function."""
    retriever = CourseRAGRetriever()

    # Test query
    question = "What prerequisites do I need for Isaac Sim?"
    answer = retriever.answer_question(question)

    print("\n" + "="*60)
    print("TEST QUERY")
    print("="*60)
    print(f"Question: {question}")
    print(f"\nAnswer:\n{answer}")
    print("="*60)

    retriever.close()


if __name__ == "__main__":
    test_retriever()