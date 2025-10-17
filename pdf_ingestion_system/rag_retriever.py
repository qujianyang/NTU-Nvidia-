"""
RAG Retriever with Parent Document Retriever Pattern
Integrates with Ollama LLM for answering questions about NVIDIA courses
"""

from typing import List, Dict, Any
from pathlib import Path
import requests
import time
import sqlite3
import torch

from langchain_chroma import Chroma
from langchain_core.documents import Document

# Fix 1: Use the updated import to avoid deprecation warning
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        from langchain.embeddings import HuggingFaceEmbeddings

from course_database import CourseDatabase

# ============================================================================
# CONFIGURATION - Edit these settings
# ============================================================================

# Ollama settings
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:7b-instruct-v0.3-q4_K_M"

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
        # Fix 2: Don't keep a persistent database connection (threading issue)
        # Create connections as needed instead

        print("Initializing RAG retriever...")
        self.embeddings = self._load_embeddings()
        self.vectorstore, self.parent_map = self._setup_vectorstore()
        print("RAG retriever ready!")

    def _load_embeddings(self):
        """Load local embedding model."""
        print(f"Loading embeddings model: {EMBEDDING_MODEL}")

        # Fix 3: Handle device properly to avoid meta tensor error
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Ensure model loads to the correct device
        model_kwargs = {
            'device': device,
            'trust_remote_code': True  # Allow model to load properly
        }

        # If CPU, ensure no CUDA tensors are created
        if device == 'cpu':
            torch.set_default_tensor_type(torch.FloatTensor)

        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs=model_kwargs,
            encode_kwargs={'normalize_embeddings': True, 'device': device}
        )

    def get_course_details(self, course_id: str) -> Dict[str, str]:
        """Get course title and URL by course ID."""
        # Fix 4: Create a new connection for thread safety
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, url
            FROM courses
            WHERE id = ?
        """, (course_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"title": row[0], "url": row[1] or ""}
        return {"title": course_id, "url": ""}

    def _setup_vectorstore(self):
        """Set up vector store with child chunks and parent document mapping."""
        print("Loading parent documents and child chunks from database...")

        # Fix 5: Create a new connection for thread safety
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all parent documents
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

        conn.close()

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

        # Retrieve parent documents with course details
        parent_docs = []
        for parent_id in list(parent_ids)[:CHUNK_OVERLAP]:  # Limit to CHUNK_OVERLAP parents
            if parent_id in self.parent_map:
                parent_doc = self.parent_map[parent_id].copy()
                # Get course details including URL
                course_id = parent_doc.get('course_id', '')
                if course_id:
                    course_details = self.get_course_details(course_id)
                    parent_doc['course_title'] = course_details['title']
                    parent_doc['course_url'] = course_details['url']
                parent_docs.append(parent_doc)

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

        # Build context from parent documents with URLs
        context_parts = []
        course_info_list = []  # Store course info for fallback

        for i, doc in enumerate(parent_docs, 1):
            course_id = doc.get('course_id', 'unknown')
            course_title = doc.get('course_title', course_id)
            course_url = doc.get('course_url', '')
            content = doc.get('content', '')

            # Add course info for context
            context_parts.append(f"[Course {i}: {course_title} ({course_id})]\n{content}\n")

            # Store course info as tuple for fallback mechanism
            if course_url:
                course_info_list.append((course_title, course_url))

        context = "\n---\n".join(context_parts)

        # Add course URLs section to help LLM include them
        if course_info_list:
            course_urls_section = "\nAVAILABLE COURSE LINKS:\n" + "\n".join([f"{title}: {url}" for title, url in course_info_list])
            context = context + "\n\n" + course_urls_section

        # Build prompt
        prompt = self._build_prompt(question, context)

        # Generate answer with Ollama
        answer = self._call_ollama(prompt)

        # KISS Fix: Post-process to ensure URLs are included if missing
        # Check if any course URLs are in the response
        has_urls = any(url in answer for _, url in course_info_list)

        # If no URLs found in answer, append them at the end
        if not has_urls and course_info_list:
            answer += "\n\n**Learn more:**\n"
            for title, url in course_info_list:
                answer += f"- {title}: {url}\n"

        return answer

    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for LLM."""
        return f"""You are a helpful assistant for NVIDIA courses.

COURSE INFORMATION:
{context}

USER QUESTION: {question}

IMPORTANT: Always include course URLs when mentioning courses.

Example format:
"I recommend Taking Isaac Sim (https://learn.nvidia.com/...) which teaches..."

Answer the question using the course information above. Include URLs for all mentioned courses.

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
        # No persistent connection to close anymore (thread-safe)


def test_retriever():
    """Enhanced test function to verify URL inclusion."""
    retriever = CourseRAGRetriever()

    # Test queries
    test_questions = [
        "What prerequisites do I need for Isaac Sim?",
        "Which courses should I take to learn about robotics?",
        "What are the beginner-friendly NVIDIA courses?"
    ]

    for question in test_questions:
        print("\n" + "="*60)
        print("TEST QUERY")
        print("="*60)
        print(f"Question: {question}")

        # Get answer
        answer = retriever.answer_question(question)
        print(f"\nAnswer:\n{answer}")

        # Check if URLs are present in the answer
        if "https://" in answer or "http://" in answer:
            print("\n✓ URLs detected in response")
        else:
            print("\n⚠ No URLs found in response - LLM may need different prompting")

        print("="*60)

    retriever.close()


if __name__ == "__main__":
    test_retriever()