# NVIDIA Learning Assistant - Implementation Plan

## Overview
Transform the existing PDF ingestion system to use LangChain's Parent Document Retriever approach, preserving course relationships and prerequisites while enabling intelligent Q&A about learning paths.

## Current System Analysis

### What We Have
- ✅ **PDF Processor**: Converts PDF to markdown using pymupdf4llm
- ✅ **Smart Chunker**: Splits content by sections with overlap
- ✅ **SQLite Storage**: Stores documents and chunks
- ✅ **Working Pipeline**: PDF → Markdown → Chunks → Database

### The Problem
- ❌ Generic chunking breaks course relationships
- ❌ Prerequisites separated from courses
- ❌ No way to query learning paths
- ❌ Hyperlinks not extracted
- ❌ No semantic understanding of course progression

## Solution: Parent-Child Document Architecture

### Core Concept
Instead of breaking content arbitrarily, we'll create:
- **Parent Documents**: Complete learning paths with all relationships preserved
- **Child Chunks**: Small, searchable pieces that point back to parents
- **Course Registry**: Structured database of all courses and prerequisites

## Implementation Phases

---

## Phase 1: Database Enhancement (Day 1-2)

### 1.1 Extend SQLite Schema

Create `enhanced_database.py`:

```python
class EnhancedSQLiteStorage(SQLiteStorage):
    """Extended storage with parent-child support"""

    def create_additional_tables(self):
        """Add new tables for parent-child architecture"""

        cursor = self.conn.cursor()

        # Parent documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parent_documents (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                parent_type TEXT NOT NULL,  -- 'learning_path', 'course_section', 'category'
                title TEXT NOT NULL,
                full_content TEXT NOT NULL,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)

        # Child chunks with parent references
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS child_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_doc_id TEXT NOT NULL,
                chunk_content TEXT NOT NULL,
                chunk_type TEXT,  -- 'prerequisite', 'description', 'objective'
                course_id TEXT,
                metadata_json TEXT,
                embedding BLOB,  -- For future vector storage
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_doc_id) REFERENCES parent_documents(id)
            )
        """)

        # Courses registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                duration TEXT,
                price TEXT,
                level TEXT,
                category TEXT,
                url TEXT,
                prerequisites_json TEXT,
                next_courses_json TEXT,
                description TEXT,
                objectives_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Course relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_course_id TEXT NOT NULL,
                to_course_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,  -- 'prerequisite', 'next', 'alternative'
                FOREIGN KEY (from_course_id) REFERENCES courses(id),
                FOREIGN KEY (to_course_id) REFERENCES courses(id)
            )
        """)

        self.conn.commit()
```

### 1.2 Migration Script

```python
# migrate_database.py
def migrate_existing_data():
    """Migrate existing chunks to new schema"""
    # Keep existing data intact
    # Add parent document layer on top
```

---

## Phase 2: Course Extraction (Day 3-4)

### 2.1 Create Course Extractor

Create `course_extractor.py`:

```python
import re
import fitz  # PyMuPDF for link extraction
from typing import List, Dict, Any
import json

class CourseExtractor:
    """Extract courses and relationships from NVIDIA PDF"""

    def __init__(self):
        self.course_patterns = {
            'duration': r'(\d+(?:\.\d+)?\s*(?:Hours?|Minutes?))',
            'price': r'\$(\d+)|Free',
            'level': r'(Beginner|Intermediate|Advanced|Technical)',
            'arrow': r'→|->|=>',
        }

    def extract_courses_from_markdown(self, markdown_content: str) -> List[Dict]:
        """Parse courses from markdown content"""
        courses = []

        # Pattern to match course entries
        # Example: "Getting Started with AI on Jetson Nano\n8 Hours | $90"
        course_pattern = r'([^\n]+)\n\s*(\d+(?:\.\d+)?\s*Hours?[^|]*\|\s*(?:\$\d+|Free))'

        matches = re.finditer(course_pattern, markdown_content)
        for match in matches:
            name = match.group(1).strip()
            details = match.group(2).strip()

            # Parse duration and price
            duration_match = re.search(r'(\d+(?:\.\d+)?\s*Hours?)', details)
            price_match = re.search(r'\$(\d+)|Free', details)

            course = {
                'name': name,
                'duration': duration_match.group(1) if duration_match else None,
                'price': price_match.group(0) if price_match else 'Unknown',
                'id': self.generate_course_id(name)
            }
            courses.append(course)

        return courses

    def extract_learning_paths(self, markdown_content: str) -> List[Dict]:
        """Extract visual learning paths with arrows"""
        paths = []

        # Find sections with arrows indicating progression
        # Example: "Course A → Course B → Course C"
        arrow_patterns = [r'→', r'->', r'=>']

        for pattern in arrow_patterns:
            # Find lines with arrows
            lines = markdown_content.split('\n')
            for line in lines:
                if pattern in line:
                    # Extract course sequence
                    courses_in_path = re.split(pattern, line)
                    if len(courses_in_path) > 1:
                        path = {
                            'type': 'sequential',
                            'courses': [c.strip() for c in courses_in_path],
                            'raw_text': line
                        }
                        paths.append(path)

        return paths

    def extract_prerequisites(self, content: str, course_name: str) -> List[str]:
        """Extract prerequisites for a specific course"""
        prerequisites = []

        # Look for prerequisite patterns
        patterns = [
            f"before.*{course_name}",
            f"prerequisite.*{course_name}",
            f"required.*{course_name}",
            f"→.*{course_name}"  # Arrow pointing to course
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Extract course names mentioned before
                context = content[max(0, match.start()-200):match.start()]
                # Parse course names from context
                potential_prereqs = self.extract_course_names(context)
                prerequisites.extend(potential_prereqs)

        return list(set(prerequisites))

    def extract_hyperlinks(self, pdf_path: str) -> Dict[str, str]:
        """Extract all hyperlinks from PDF"""
        links = {}

        with fitz.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf):
                # Get all links on the page
                link_annotations = page.get_links()

                for link in link_annotations:
                    if 'uri' in link:
                        # Try to associate link with nearby text
                        rect = link['from']
                        text = page.get_textbox(rect)
                        if text:
                            course_name = text.strip()
                            links[course_name] = link['uri']

        return links

    def generate_course_id(self, course_name: str) -> str:
        """Generate consistent ID for a course"""
        # Clean and standardize course name
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', course_name)
        cleaned = cleaned.lower().replace(' ', '_')
        return cleaned[:50]  # Limit length

    def extract_course_names(self, text: str) -> List[str]:
        """Extract potential course names from text"""
        # Look for capitalized phrases that might be course names
        pattern = r'[A-Z][A-Za-z\s]+(?:with|on|for|in)\s+[A-Z][A-Za-z\s]+'
        matches = re.findall(pattern, text)
        return matches
```

### 2.2 Test Course Extraction

```python
# test_extraction.py
def test_course_extraction():
    extractor = CourseExtractor()

    # Load sample markdown
    with open('sample_nvidia.md', 'r') as f:
        content = f.read()

    courses = extractor.extract_courses_from_markdown(content)
    paths = extractor.extract_learning_paths(content)

    print(f"Found {len(courses)} courses")
    print(f"Found {len(paths)} learning paths")
```

---

## Phase 3: Parent Document Builder (Day 5-6)

### 3.1 Create Parent Document Builder

Create `parent_builder.py`:

```python
class ParentDocumentBuilder:
    """Build parent documents that preserve context"""

    def build_learning_path_parent(self,
                                  path_name: str,
                                  courses: List[Dict],
                                  relationships: Dict) -> Dict:
        """
        Create a parent document for a complete learning path
        """

        # Build narrative content
        content_parts = [
            f"# {path_name} Learning Path\n",
            f"Total Courses: {len(courses)}\n",
            f"Total Duration: {self.calculate_total_duration(courses)}\n",
            f"Total Cost: {self.calculate_total_cost(courses)}\n\n",
            "## Course Progression\n\n"
        ]

        # Add each course with context
        for i, course in enumerate(courses):
            content_parts.append(f"### Step {i+1}: {course['name']}\n")
            content_parts.append(f"- Duration: {course.get('duration', 'Unknown')}\n")
            content_parts.append(f"- Price: {course.get('price', 'Unknown')}\n")
            content_parts.append(f"- Level: {course.get('level', 'Unknown')}\n")

            # Add prerequisites
            prereqs = relationships.get(course['id'], {}).get('prerequisites', [])
            if prereqs:
                content_parts.append(f"- Prerequisites: {', '.join(prereqs)}\n")
            else:
                content_parts.append("- Prerequisites: None\n")

            # Add next courses
            next_courses = relationships.get(course['id'], {}).get('next', [])
            if next_courses:
                content_parts.append(f"- Next Courses: {', '.join(next_courses)}\n")

            # Add URL if available
            if course.get('url'):
                content_parts.append(f"- Link: {course['url']}\n")

            content_parts.append("\n")

        # Create parent document
        parent_doc = {
            'id': f"path_{self.generate_id(path_name)}",
            'type': 'learning_path',
            'title': path_name,
            'content': ''.join(content_parts),
            'metadata': {
                'course_count': len(courses),
                'course_ids': [c['id'] for c in courses],
                'total_duration': self.calculate_total_duration(courses),
                'total_cost': self.calculate_total_cost(courses)
            }
        }

        return parent_doc

    def create_child_chunks_from_parent(self, parent_doc: Dict) -> List[Dict]:
        """
        Create searchable child chunks from parent document
        """
        chunks = []
        parent_id = parent_doc['id']
        content = parent_doc['content']

        # Split by sections but keep context
        sections = content.split('###')

        for section in sections:
            if section.strip():
                # Create chunk for each course section
                chunk = {
                    'parent_doc_id': parent_id,
                    'content': section.strip(),
                    'type': self.identify_chunk_type(section),
                    'metadata': {
                        'parent_title': parent_doc['title'],
                        'parent_type': parent_doc['type']
                    }
                }
                chunks.append(chunk)

        # Add additional semantic chunks
        # Extract key phrases for better searchability
        key_phrases = self.extract_key_phrases(content)
        for phrase in key_phrases:
            chunk = {
                'parent_doc_id': parent_id,
                'content': phrase,
                'type': 'key_phrase',
                'metadata': {
                    'parent_title': parent_doc['title']
                }
            }
            chunks.append(chunk)

        return chunks

    def calculate_total_duration(self, courses: List[Dict]) -> str:
        """Calculate total duration of all courses"""
        total_hours = 0
        for course in courses:
            duration = course.get('duration', '')
            if 'Hour' in duration:
                hours = float(re.search(r'(\d+(?:\.\d+)?)', duration).group(1))
                total_hours += hours
        return f"{total_hours} Hours"

    def calculate_total_cost(self, courses: List[Dict]) -> str:
        """Calculate total cost of all courses"""
        total_cost = 0
        free_count = 0

        for course in courses:
            price = course.get('price', '')
            if price == 'Free':
                free_count += 1
            elif '$' in price:
                cost = int(re.search(r'\$(\d+)', price).group(1))
                total_cost += cost

        if total_cost == 0 and free_count == len(courses):
            return "Free"
        elif free_count > 0:
            return f"${total_cost} ({free_count} free courses)"
        else:
            return f"${total_cost}"

    def identify_chunk_type(self, content: str) -> str:
        """Identify the type of content in a chunk"""
        if 'prerequisite' in content.lower():
            return 'prerequisite'
        elif 'duration' in content.lower():
            return 'metadata'
        elif 'step' in content.lower():
            return 'course_step'
        else:
            return 'general'

    def extract_key_phrases(self, content: str) -> List[str]:
        """Extract important phrases for searchability"""
        phrases = []

        # Extract prerequisite statements
        prereq_pattern = r'Prerequisites?: ([^\n]+)'
        for match in re.finditer(prereq_pattern, content):
            phrases.append(f"Prerequisites: {match.group(1)}")

        # Extract progression statements
        if '→' in content or 'Next:' in content:
            progression_pattern = r'([^→\n]+)\s*→\s*([^→\n]+)'
            for match in re.finditer(progression_pattern, content):
                phrases.append(f"{match.group(1)} leads to {match.group(2)}")

        return phrases

    def generate_id(self, name: str) -> str:
        """Generate unique ID"""
        import hashlib
        return hashlib.md5(name.encode()).hexdigest()[:16]
```

---

## Phase 4: Integration Pipeline (Day 7-8)

### 4.1 Update Main Processing Pipeline

Create `enhanced_main.py`:

```python
from pdf_processor import PDFProcessor
from course_extractor import CourseExtractor
from parent_builder import ParentDocumentBuilder
from enhanced_database import EnhancedSQLiteStorage

def process_nvidia_pdf_with_relationships(pdf_path: str):
    """
    Enhanced pipeline with parent-child architecture
    """

    print("=== NVIDIA PDF Processing with Relationship Preservation ===\n")

    # Initialize components
    processor = PDFProcessor()
    extractor = CourseExtractor()
    builder = ParentDocumentBuilder()
    store = EnhancedSQLiteStorage()

    # Step 1: Extract PDF to markdown
    print("Step 1: Extracting PDF content...")
    doc_info = processor.process_pdf(pdf_path)
    markdown_content = doc_info['content']
    print(f"  ✓ Extracted {len(markdown_content)} characters")

    # Step 2: Extract courses and relationships
    print("\nStep 2: Identifying courses and relationships...")
    courses = extractor.extract_courses_from_markdown(markdown_content)
    learning_paths = extractor.extract_learning_paths(markdown_content)
    hyperlinks = extractor.extract_hyperlinks(pdf_path)
    print(f"  ✓ Found {len(courses)} courses")
    print(f"  ✓ Found {len(learning_paths)} learning paths")
    print(f"  ✓ Extracted {len(hyperlinks)} hyperlinks")

    # Step 3: Build prerequisite map
    print("\nStep 3: Mapping prerequisites...")
    relationships = {}
    for course in courses:
        course_id = course['id']
        prerequisites = extractor.extract_prerequisites(markdown_content, course['name'])
        relationships[course_id] = {
            'prerequisites': prerequisites,
            'next': []  # Will be filled from learning paths
        }
    print(f"  ✓ Mapped prerequisites for {len(relationships)} courses")

    # Step 4: Build parent documents
    print("\nStep 4: Building parent documents...")
    parent_docs = []
    all_child_chunks = []

    # Create parent for each learning path
    for path in learning_paths:
        # Get courses in this path
        path_courses = [c for c in courses if c['name'] in path['courses']]

        # Build parent document
        parent_doc = builder.build_learning_path_parent(
            f"Learning Path {len(parent_docs) + 1}",
            path_courses,
            relationships
        )

        # Create child chunks
        child_chunks = builder.create_child_chunks_from_parent(parent_doc)

        parent_docs.append(parent_doc)
        all_child_chunks.extend(child_chunks)

    print(f"  ✓ Created {len(parent_docs)} parent documents")
    print(f"  ✓ Generated {len(all_child_chunks)} child chunks")

    # Step 5: Store everything
    print("\nStep 5: Storing to database...")

    # Store courses
    for course in courses:
        # Add hyperlink if available
        course['url'] = hyperlinks.get(course['name'], '')
        store.store_course(course)

    # Store parent documents
    for parent in parent_docs:
        store.store_parent_document(parent)

    # Store child chunks
    for chunk in all_child_chunks:
        store.store_child_chunk(chunk)

    # Store relationships
    for course_id, rels in relationships.items():
        for prereq in rels['prerequisites']:
            store.store_relationship(prereq, course_id, 'prerequisite')

    print(f"  ✓ Data stored successfully")

    # Step 6: Display summary
    print("\n=== Processing Complete ===")
    print(f"Database: {store.db_path}")
    print(f"Courses: {len(courses)}")
    print(f"Parent Documents: {len(parent_docs)}")
    print(f"Child Chunks: {len(all_child_chunks)}")
    print(f"Relationships: {sum(len(r['prerequisites']) for r in relationships.values())}")

    store.close()
    return doc_info['doc_id']
```

---

## Phase 5: LangChain RAG Integration (Day 9-10)

### 5.1 Create RAG Retriever

Create `rag_retriever.py`:

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore import InMemoryDocstore
from enhanced_database import EnhancedSQLiteStorage

class CourseRAGRetriever:
    """
    RAG retriever using Parent Document approach
    """

    def __init__(self, db_path: str = "pdf_documents.db"):
        self.store = EnhancedSQLiteStorage(db_path)
        self.embeddings = OpenAIEmbeddings()  # Or use local embeddings
        self.setup_retriever()

    def setup_retriever(self):
        """Initialize the Parent Document Retriever"""

        # Load parent documents from SQLite
        parent_docs = self.store.get_all_parent_documents()

        # Load child chunks
        child_chunks = self.store.get_all_child_chunks()

        # Create vector store for child chunks
        texts = [chunk['content'] for chunk in child_chunks]
        metadatas = [chunk['metadata'] for chunk in child_chunks]

        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )

        # Create docstore for parent documents
        self.docstore = InMemoryDocstore(
            {doc['id']: doc for doc in parent_docs}
        )

        # Create the retriever
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.docstore,
            verbose=True
        )

    def query(self, question: str, k: int = 4) -> List[str]:
        """
        Query the system with a question
        """
        # Retrieve relevant parent documents
        docs = self.retriever.get_relevant_documents(question, k=k)

        return [doc.page_content for doc in docs]

    def answer_question(self, question: str) -> str:
        """
        Answer a question using retrieved context
        """
        # Get relevant parent documents
        relevant_docs = self.query(question)

        # Format context
        context = "\n\n".join(relevant_docs)

        # Generate answer (simplified - you'd use an LLM here)
        answer = self.generate_answer(question, context)

        return answer

    def generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer from context (placeholder for LLM integration)
        """
        # This is where you'd integrate with OpenAI/Claude/etc.
        # For now, return formatted context

        return f"""
Based on the NVIDIA course catalog, here's what I found:

{context}

This information directly addresses your question about: "{question}"
        """
```

### 5.2 Query Interface

Create `query_interface.py`:

```python
class QueryInterface:
    """User-friendly query interface"""

    def __init__(self):
        self.retriever = CourseRAGRetriever()

    def interactive_session(self):
        """Run interactive Q&A session"""

        print("=== NVIDIA Learning Assistant ===")
        print("Ask questions about courses, prerequisites, and learning paths!")
        print("Type 'exit' to quit\n")

        while True:
            question = input("Your question: ")

            if question.lower() == 'exit':
                break

            # Process question
            answer = self.retriever.answer_question(question)
            print(f"\nAnswer: {answer}\n")
            print("-" * 50)

    def example_queries(self):
        """Test with example queries"""

        queries = [
            "What are the prerequisites for MobilityGen?",
            "How long does the robotics learning path take?",
            "What courses should I take to learn Isaac Sim?",
            "Show me free courses for beginners",
            "What comes after Python fundamentals?"
        ]

        for query in queries:
            print(f"\nQ: {query}")
            answer = self.retriever.answer_question(query)
            print(f"A: {answer}\n")
```

---

## Phase 6: Testing & Validation (Day 11-12)

### 6.1 Test Suite

Create `test_system.py`:

```python
def test_relationship_preservation():
    """Ensure relationships are preserved"""

    # Process test PDF
    doc_id = process_nvidia_pdf_with_relationships("nvidia-18.pdf")

    # Query for prerequisites
    retriever = CourseRAGRetriever()

    # Test queries
    test_cases = [
        {
            'question': "What are the prerequisites for MobilityGen?",
            'expected_keywords': ['Isaac Sim', 'prerequisite']
        },
        {
            'question': "What's the complete robotics learning path?",
            'expected_keywords': ['Step 1', 'Step 2', 'Step 3']
        }
    ]

    for test in test_cases:
        answer = retriever.answer_question(test['question'])

        # Check if expected keywords are in answer
        for keyword in test['expected_keywords']:
            assert keyword in answer, f"Missing {keyword} in answer"

        print(f"✓ Test passed: {test['question']}")
```

### 6.2 Performance Metrics

```python
def measure_performance():
    """Measure query performance"""

    import time
    retriever = CourseRAGRetriever()

    queries = [
        "What courses require Python?",
        "How much does the AI certification path cost?",
        "Show me courses under 2 hours"
    ]

    for query in queries:
        start = time.time()
        answer = retriever.answer_question(query)
        elapsed = time.time() - start

        print(f"Query: {query[:50]}...")
        print(f"Time: {elapsed:.2f}s")
        print(f"Answer length: {len(answer)} chars\n")
```

---

## Deployment Checklist

### Prerequisites
- [ ] Python 3.8+
- [ ] SQLite installed
- [ ] Required packages: `pip install langchain pymupdf4llm fitz chromadb`
- [ ] OpenAI API key (for embeddings) or local embedding model

### Setup Steps
1. [ ] Run database migration to add new tables
2. [ ] Process NVIDIA PDF with new pipeline
3. [ ] Verify parent documents created correctly
4. [ ] Test query interface with sample questions
5. [ ] Optimize chunk sizes based on results

### Configuration
```python
# config.py
CHUNK_SIZE = 512  # Optimal for child chunks
OVERLAP = 64
EMBEDDING_MODEL = "text-embedding-ada-002"  # Or local alternative
MAX_PARENT_SIZE = 4000  # Maximum parent document size
```

---

## Troubleshooting Guide

### Common Issues

#### 1. Relationships Not Detected
- Check regex patterns in `CourseExtractor`
- Verify arrow symbols in PDF (→, ->, =>)
- Manually review markdown output

#### 2. Parent Documents Too Large
- Adjust `MAX_PARENT_SIZE` in config
- Split learning paths into smaller segments
- Consider category-based parents instead

#### 3. Poor Query Results
- Verify embeddings are generated correctly
- Check if child chunks are too small/large
- Ensure metadata is properly stored

#### 4. Slow Performance
- Add indexes to SQLite tables
- Cache embeddings
- Use batch processing for large PDFs

---

## Next Steps & Enhancements

### Immediate Improvements
1. **Web Scraping**: Add course detail fetching from URLs
2. **Embedding Optimization**: Use sentence-transformers for local embeddings
3. **Query Enhancement**: Add query rewriting for better results

### Future Features
1. **Visual Path Display**: Generate graphical learning paths
2. **Progress Tracking**: Track user's completed courses
3. **Personalization**: Recommend based on user background
4. **Multi-PDF Support**: Handle multiple course catalogs

### Advanced Capabilities
1. **Graph Visualization**: D3.js visualization of course relationships
2. **Time Estimation**: Calculate realistic completion times
3. **Cost Optimization**: Find cheapest path to goal
4. **Prerequisite Validation**: Check if user meets requirements

---

## Resources & References

### Documentation
- [LangChain Parent Document Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/parent_document_retriever)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [SQLite JSON Functions](https://www.sqlite.org/json1.html)

### Example Code
- [Parent Document Retriever Example](https://github.com/langchain-ai/langchain/tree/master/templates/rag-parent-document-retrieval)
- [PDF Processing with PyMuPDF](https://github.com/pymupdf/PyMuPDF-Utilities)

### Community Resources
- LangChain Discord for RAG questions
- Stack Overflow tag: `langchain-retriever`

---

## Summary

This implementation plan transforms your existing PDF ingestion system into an intelligent learning assistant that:

1. **Preserves Relationships**: Never loses course prerequisites or progressions
2. **Enables Complex Queries**: Answers questions about learning paths naturally
3. **Maintains Simplicity**: Uses SQLite and Python without complex infrastructure
4. **Scales Well**: Handles hundreds of courses efficiently
5. **Provides Context**: Returns complete learning paths, not fragments

The Parent Document Retriever approach ensures that when someone asks "What do I need before MobilityGen?", they get the complete learning path with all prerequisites, not just a fragment mentioning the course name.

Ready to implement? Start with Phase 1 (Database Enhancement) and work through each phase systematically!