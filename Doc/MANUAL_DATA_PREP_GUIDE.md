
  The Complete Flow: JSON → SQLite → Parent-Child RAG

  Here's how your manually collected JSON data becomes a
  powerful RAG system:

  Architecture Overview

  [1. Manual Collection]     [2. Import & Transform]     [3.
  RAG Ready]
       JSON File          →    SQLite Database       →
  Parent-Child Docs
     (Course Data)            (Structured Storage)
  (LangChain RAG)

  Step-by-Step Implementation

  Phase 1: Your JSON Structure (What You'll Create Manually)

  // nvidia_courses.json
  {
    "courses": [
      {
        "id": "mobilityGen-001",
        "title": "Generating High-Quality Motion Data for
  Robotics With MobilityGen",
        "url": "https://learn.nvidia.com/...",
        "duration": "1.5 Hours",
        "price": "Free",
        "level": "Technical - Intermediate",
        "description": "This tutorial introduces
  MobilityGen...",
        "learning_objectives": [
          "Understand importance of high-quality motion data",
          "Learn key components of MobilityGen"
        ],
        "prerequisites": ["isaac-sim-001", "python-basics"],
        "leads_to": ["advanced-robotics-001"],
        "category": "Robotics",
        "track": "robotics-developer"
      }
      // ... 99 more courses
    ],

    "learning_paths": [
      {
        "id": "path-robotics-dev",
        "name": "Robotics Developer Track",
        "courses": ["python-basics", "isaac-sim-001",
  "mobilityGen-001"],
        "total_duration": "6 Hours",
        "description": "Complete path for robotics development"
      }
      // ... other paths
    ]
  }

  Phase 2: Import Script - JSON to SQLite with Parent-Child 
  Structure

  Create json_to_sqlite_importer.py:

  import json
  import sqlite3
  from datetime import datetime
  from typing import Dict, List
  import hashlib

  class CourseDataImporter:
      """
      Transform flat JSON course data into Parent-Child SQLite
  structure
      """

      def __init__(self, json_path: str, db_path: str =
  "nvidia_courses.db"):
          self.json_path = json_path
          self.db_path = db_path
          self.conn = sqlite3.connect(db_path)
          self.setup_database()

      def setup_database(self):
          """Create all necessary tables"""
          cursor = self.conn.cursor()

          # 1. Courses table (from your JSON)
          cursor.execute("""
              CREATE TABLE IF NOT EXISTS courses (
                  id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  url TEXT,
                  duration TEXT,
                  price TEXT,
                  level TEXT,
                  category TEXT,
                  track TEXT,
                  description TEXT,
                  learning_objectives_json TEXT,
                  prerequisites_json TEXT,
                  leads_to_json TEXT,
                  created_at TIMESTAMP DEFAULT
  CURRENT_TIMESTAMP
              )
          """)

          # 2. Parent Documents (learning contexts)
          cursor.execute("""
              CREATE TABLE IF NOT EXISTS parent_documents (
                  id TEXT PRIMARY KEY,
                  doc_type TEXT, -- 'learning_path',
  'course_detail', 'prerequisite_chain'
                  title TEXT,
                  full_content TEXT, -- Complete context with
  relationships
                  metadata_json TEXT,
                  created_at TIMESTAMP DEFAULT
  CURRENT_TIMESTAMP
              )
          """)

          # 3. Child Chunks (searchable pieces)
          cursor.execute("""
              CREATE TABLE IF NOT EXISTS child_chunks (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  parent_id TEXT NOT NULL,
                  chunk_text TEXT NOT NULL,
                  chunk_type TEXT, -- 'objective',
  'prerequisite', 'description'
                  course_id TEXT,
                  embedding BLOB, -- For vector search later
                  metadata_json TEXT,
                  FOREIGN KEY (parent_id) REFERENCES
  parent_documents(id),
                  FOREIGN KEY (course_id) REFERENCES
  courses(id)
              )
          """)

          # 4. Course Relationships
          cursor.execute("""
              CREATE TABLE IF NOT EXISTS course_relationships (
                  from_course_id TEXT,
                  to_course_id TEXT,
                  relationship_type TEXT, -- 'prerequisite',
  'leads_to'
                  PRIMARY KEY (from_course_id, to_course_id,
  relationship_type)
              )
          """)

          self.conn.commit()

      def import_courses(self, courses_data: List[Dict]):
          """Import course data from JSON"""
          cursor = self.conn.cursor()

          for course in courses_data:
              # Insert course
              cursor.execute("""
                  INSERT OR REPLACE INTO courses
                  (id, title, url, duration, price, level,
  category, track,
                   description, learning_objectives_json,
  prerequisites_json, leads_to_json)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              """, (
                  course['id'],
                  course['title'],
                  course.get('url', ''),
                  course.get('duration', ''),
                  course.get('price', ''),
                  course.get('level', ''),
                  course.get('category', ''),
                  course.get('track', ''),
                  course.get('description', ''),
                  json.dumps(course.get('learning_objectives',
  [])),
                  json.dumps(course.get('prerequisites', [])),
                  json.dumps(course.get('leads_to', []))
              ))

              # Store relationships
              for prereq_id in course.get('prerequisites', []):
                  cursor.execute("""
                      INSERT OR IGNORE INTO
  course_relationships
                      VALUES (?, ?, 'prerequisite')
                  """, (prereq_id, course['id']))

              for next_id in course.get('leads_to', []):
                  cursor.execute("""
                      INSERT OR IGNORE INTO
  course_relationships
                      VALUES (?, ?, 'leads_to')
                  """, (course['id'], next_id))

          self.conn.commit()
          print(f"✓ Imported {len(courses_data)} courses")

      def create_parent_documents(self, courses_data:
  List[Dict], paths_data: List[Dict]):
          """
          Create parent documents that preserve context
          This is the KEY transformation for RAG
          """
          cursor = self.conn.cursor()
          parent_docs_created = 0
          child_chunks_created = 0

          # 1. Create parent doc for each learning path
          for path in paths_data:
              parent_id = f"path_{path['id']}"

              # Build rich context document
              content = self._build_learning_path_content(path,
   courses_data)

              # Store parent document
              cursor.execute("""
                  INSERT OR REPLACE INTO parent_documents
                  (id, doc_type, title, full_content,
  metadata_json)
                  VALUES (?, ?, ?, ?, ?)
              """, (
                  parent_id,
                  'learning_path',
                  path['name'],
                  content,
                  json.dumps({
                      'course_count': len(path['courses']),
                      'total_duration':
  path.get('total_duration', ''),
                      'course_ids': path['courses']
                  })
              ))
              parent_docs_created += 1

              # Create child chunks from this parent
              chunks =
  self._create_child_chunks_from_content(content, parent_id)
              for chunk in chunks:
                  cursor.execute("""
                      INSERT INTO child_chunks
                      (parent_id, chunk_text, chunk_type,
  metadata_json)
                      VALUES (?, ?, ?, ?)
                  """, (
                      chunk['parent_id'],
                      chunk['text'],
                      chunk['type'],
                      json.dumps(chunk.get('metadata', {}))
                  ))
                  child_chunks_created += 1

          # 2. Create parent doc for each course with its
  prerequisites
          for course in courses_data:
              parent_id = f"course_context_{course['id']}"

              # Build prerequisite chain context
              content = self._build_course_context(course,
  courses_data)

              cursor.execute("""
                  INSERT OR REPLACE INTO parent_documents
                  (id, doc_type, title, full_content,
  metadata_json)
                  VALUES (?, ?, ?, ?, ?)
              """, (
                  parent_id,
                  'course_detail',
                  f"Context for {course['title']}",
                  content,
                  json.dumps({
                      'course_id': course['id'],
                      'has_prerequisites':
  len(course.get('prerequisites', [])) > 0
                  })
              ))
              parent_docs_created += 1

              # Create searchable chunks
              chunks = self._create_course_chunks(course,
  parent_id)
              for chunk in chunks:
                  cursor.execute("""
                      INSERT INTO child_chunks
                      (parent_id, chunk_text, chunk_type,
  course_id, metadata_json)
                      VALUES (?, ?, ?, ?, ?)
                  """, (
                      parent_id,
                      chunk['text'],
                      chunk['type'],
                      course['id'],
                      json.dumps(chunk.get('metadata', {}))
                  ))
                  child_chunks_created += 1

          self.conn.commit()
          print(f"✓ Created {parent_docs_created} parent
  documents")
          print(f"✓ Created {child_chunks_created} child
  chunks")

      def _build_learning_path_content(self, path: Dict,
  all_courses: List[Dict]) -> str:
          """Build comprehensive learning path document"""

          # Get course details for this path
          course_map = {c['id']: c for c in all_courses}
          path_courses = [course_map[cid] for cid in
  path['courses'] if cid in course_map]

          content = [
              f"# {path['name']}",
              f"Total Duration: {path.get('total_duration',
  'Unknown')}",
              f"Number of Courses: {len(path_courses)}",
              "",
              "## Learning Progression:",
              ""
          ]

          for i, course in enumerate(path_courses, 1):
              content.append(f"### Step {i}:
  {course['title']}")
              content.append(f"- Duration:
  {course.get('duration', 'Unknown')}")
              content.append(f"- Level: {course.get('level',
  'Unknown')}")
              content.append(f"- Price: {course.get('price',
  'Unknown')}")

              # Add prerequisites
              if course.get('prerequisites'):
                  prereq_names = [course_map[pid]['title']
                                 for pid in
  course['prerequisites']
                                 if pid in course_map]
                  content.append(f"- Prerequisites: {',
  '.join(prereq_names)}")
              else:
                  content.append("- Prerequisites: None")

              # Add what it leads to
              if course.get('leads_to'):
                  next_names = [course_map[nid]['title']
                               for nid in course['leads_to']
                               if nid in course_map]
                  content.append(f"- Leads to: {',
  '.join(next_names)}")

              content.append("")

          return "\n".join(content)

      def _build_course_context(self, course: Dict,
  all_courses: List[Dict]) -> str:
          """Build course with full prerequisite context"""

          course_map = {c['id']: c for c in all_courses}

          content = [
              f"# {course['title']}",
              f"Level: {course.get('level', 'Unknown')}",
              f"Duration: {course.get('duration', 'Unknown')}",
              f"Price: {course.get('price', 'Unknown')}",
              "",
              "## Description:",
              course.get('description', 'No description
  available'),
              ""
          ]

          # Add learning objectives
          if course.get('learning_objectives'):
              content.append("## Learning Objectives:")
              for obj in course['learning_objectives']:
                  content.append(f"- {obj}")
              content.append("")

          # Add prerequisite context
          if course.get('prerequisites'):
              content.append("## Prerequisites Required:")
              for prereq_id in course['prerequisites']:
                  if prereq_id in course_map:
                      prereq = course_map[prereq_id]
                      content.append(f"- {prereq['title']}
  ({prereq.get('duration', 'Unknown')})")
              content.append("")

          # Add next courses
          if course.get('leads_to'):
              content.append("## Next Courses You Can Take:")
              for next_id in course['leads_to']:
                  if next_id in course_map:
                      next_course = course_map[next_id]
                      content.append(f"-
  {next_course['title']}")
              content.append("")

          return "\n".join(content)

      def _create_child_chunks_from_content(self, content: str,
   parent_id: str) -> List[Dict]:
          """Split content into searchable chunks"""
          chunks = []

          # Split by sections
          sections = content.split('\n\n')
          for section in sections:
              if section.strip():
                  chunk_type = 'general'
                  if 'Step' in section:
                      chunk_type = 'progression'
                  elif 'Prerequisite' in section:
                      chunk_type = 'prerequisite'
                  elif 'Duration' in section:
                      chunk_type = 'metadata'

                  chunks.append({
                      'parent_id': parent_id,
                      'text': section.strip(),
                      'type': chunk_type,
                      'metadata': {'section': True}
                  })

          return chunks

      def _create_course_chunks(self, course: Dict, parent_id:
  str) -> List[Dict]:
          """Create searchable chunks from course data"""
          chunks = []

          # Chunk 1: Basic info
          basic_info = f"{course['title']} is a
  {course.get('level', '')} course that takes
  {course.get('duration', '')}."
          chunks.append({
              'text': basic_info,
              'type': 'basic_info',
              'parent_id': parent_id
          })

          # Chunk 2: Prerequisites
          if course.get('prerequisites'):
              prereq_text = f"Before taking {course['title']},
  you need to complete: {', '.join(course['prerequisites'])}"
              chunks.append({
                  'text': prereq_text,
                  'type': 'prerequisite',
                  'parent_id': parent_id
              })

          # Chunk 3: Learning objectives
          for obj in course.get('learning_objectives', []):
              chunks.append({
                  'text': f"In {course['title']} you will
  learn: {obj}",
                  'type': 'objective',
                  'parent_id': parent_id
              })

          return chunks

      def run_import(self):
          """Main import process"""
          print("=== Starting JSON to SQLite Import ===")

          # Load JSON
          with open(self.json_path, 'r') as f:
              data = json.load(f)

          courses = data.get('courses', [])
          paths = data.get('learning_paths', [])

          print(f"Found {len(courses)} courses and {len(paths)}
   learning paths")

          # Import courses
          self.import_courses(courses)

          # Create parent-child documents
          self.create_parent_documents(courses, paths)

          print("=== Import Complete ===")

          # Show statistics
          cursor = self.conn.cursor()
          cursor.execute("SELECT COUNT(*) FROM courses")
          course_count = cursor.fetchone()[0]

          cursor.execute("SELECT COUNT(*) FROM
  parent_documents")
          parent_count = cursor.fetchone()[0]

          cursor.execute("SELECT COUNT(*) FROM child_chunks")
          chunk_count = cursor.fetchone()[0]

          print(f"\nDatabase Statistics:")
          print(f"  Courses: {course_count}")
          print(f"  Parent Documents: {parent_count}")
          print(f"  Child Chunks: {chunk_count}")

          self.conn.close()

  # Usage
  if __name__ == "__main__":
      importer = CourseDataImporter(
          json_path="nvidia_courses.json",
          db_path="nvidia_rag.db"
      )
      importer.run_import()

  Phase 3: Query with LangChain RAG

  Create query_system.py:

  from langchain.retrievers import ParentDocumentRetriever
  from langchain.vectorstores import Chroma
  from langchain.embeddings import OpenAIEmbeddings
  import sqlite3

  class NvidiaCoursesRAG:
      """Query system using Parent-Child architecture"""

      def __init__(self, db_path="nvidia_rag.db"):
          self.db_path = db_path
          self.setup_retriever()

      def setup_retriever(self):
          """Initialize Parent Document Retriever from
  SQLite"""

          conn = sqlite3.connect(self.db_path)
          cursor = conn.cursor()

          # Load parent documents
          cursor.execute("SELECT id, full_content FROM
  parent_documents")
          parent_docs = {row[0]: row[1] for row in
  cursor.fetchall()}

          # Load child chunks
          cursor.execute("""
              SELECT chunk_text, parent_id, metadata_json
              FROM child_chunks
          """)
          child_chunks = cursor.fetchall()

          # Create vector store from child chunks
          texts = [chunk[0] for chunk in child_chunks]
          metadatas = [{'parent_id': chunk[1]} for chunk in
  child_chunks]

          # Setup retriever
          self.vectorstore = Chroma.from_texts(
              texts=texts,
              metadatas=metadatas,
              embedding=OpenAIEmbeddings()
          )

          # This is the magic - child chunks find, parent docs
  return!
          self.retriever = ParentDocumentRetriever(
              vectorstore=self.vectorstore,
              docstore={},  # We'll fetch from SQLite
              parent_id_key="parent_id"
          )

          conn.close()

      def query(self, question: str):
          """Answer questions using parent-child retrieval"""

          # 1. Search child chunks
          relevant_chunks =
  self.vectorstore.similarity_search(question, k=4)

          # 2. Get parent IDs
          parent_ids = set(chunk.metadata['parent_id'] for
  chunk in relevant_chunks)

          # 3. Fetch full parent documents from SQLite
          conn = sqlite3.connect(self.db_path)
          cursor = conn.cursor()

          parents = []
          for pid in parent_ids:
              cursor.execute(
                  "SELECT full_content FROM parent_documents
  WHERE id = ?",
                  (pid,)
              )
              result = cursor.fetchone()
              if result:
                  parents.append(result[0])

          conn.close()

          # 4. Return complete context
          return "\n\n---\n\n".join(parents)

  # Example usage
  rag = NvidiaCoursesRAG()

  # User asks about prerequisites
  answer = rag.query("What do I need to know before taking
  MobilityGen?")
  print(answer)
  # Returns: Complete learning path with all prerequisites, not
   just fragments!

  The Complete Flow Visualized

  Step 1: Manual Data Collection (3-4 hours)
  ├── Open course web pages
  ├── Copy details to JSON
  └── Save nvidia_courses.json

  Step 2: Import & Transform (5 minutes)
  ├── Run: python json_to_sqlite_importer.py
  ├── Creates nvidia_rag.db with:
  │   ├── courses table (flat data)
  │   ├── parent_documents (full context)
  │   └── child_chunks (searchable pieces)
  └── Relationships preserved!

  Step 3: Query with RAG (instant)
  ├── User asks: "Prerequisites for MobilityGen?"
  ├── System searches child chunks
  ├── Finds relevant parent documents
  └── Returns complete learning path!

  Why This Architecture Works

  Your JSON = Clean, structured data source
  SQLite = Persistent storage with relationships
  Parent Docs = Complete context preservation
  Child Chunks = Semantic search capability
  Result = Best of both worlds!

  When someone asks about MobilityGen, they get:
  - The complete learning path
  - All prerequisites in context
  - What comes next
  - Total time investment

  Not just a fragment saying "MobilityGen requires Isaac Sim"
  but the ENTIRE journey!

  Ready to start with the manual data collection?