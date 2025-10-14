# Intelligent Learning Path Extraction from PDFs: Solutions Overview

## Problem Statement
Traditional RAG systems using semantic chunking lose critical relationships between courses in learning path PDFs. When courses are connected by arrows (→) indicating prerequisites and sequences, splitting them into separate chunks destroys this vital information.

## Research Findings & Solutions

### 1. GraphRAG with Neo4j + LangChain
**Approach**: Build a knowledge graph that preserves all course relationships

**Implementation**:
- Extract courses as nodes, arrows as edges (prerequisites)
- Use **LLMGraphTransformer** from LangChain to build knowledge graph
- Combine vector search for course content + graph traversal for relationships
- Store in Neo4j graph database

**Example Query Flow**:
```
Query: "Path to CUDA C++?"
→ Graph traverses prerequisites
→ Returns: "An Even Easier Introduction to CUDA" → "Getting Started with Accelerated Computing" → "CUDA C++"
```

**Pros**: Maintains complete relationship structure, enables complex path queries
**Cons**: Requires graph database infrastructure

---

### 2. Multi-Modal PDF Parser + Spatial Layout Analysis
**Approach**: Use computer vision to detect visual elements and their relationships

**Technologies**:
- **Arrow R-CNN**: Detects boxes and arrows with 78.6% accuracy
- **GenFlowchart**: Uses Segment Anything Model (SAM) for component detection
- **Flowmind2Digital**: Handles complex flowchart structures

**Implementation**:
```python
# Pseudo-code
1. Extract PDF as image
2. Detect boxes (courses) using object detection
3. Detect arrows using Arrow R-CNN
4. Build spatial relationship graph
5. Store: courses table + prerequisites table
```

**Pros**: Handles complex visual layouts, works with hand-drawn diagrams
**Cons**: Computationally intensive, requires training data

---

### 3. Dual Knowledge Structure Approach
**Approach**: Create two complementary graphs to prevent learning bottlenecks

**Structure**:
1. **Prerequisite Graph**: Direct course dependencies (A → B → C)
2. **Similarity Graph**: Related courses by topic/content

**Benefits**:
- Prevents "blocked phenomena" where learners get stuck
- Offers alternative paths when prerequisites are too challenging
- Uses Graph Neural Networks (GNN) for intelligent path recommendation

**Implementation**:
```sql
-- Database schema
CREATE TABLE prerequisite_edges (
    from_course_id TEXT,
    to_course_id TEXT,
    strength FLOAT
);

CREATE TABLE similarity_edges (
    course1_id TEXT,
    course2_id TEXT,
    similarity_score FLOAT
);
```

**Pros**: Flexible learning paths, handles edge cases
**Cons**: More complex to implement and maintain

---

### 4. Doc2Graph Framework
**Approach**: Treat document as a graph from the start

**Key Features**:
- Each text box = graph node
- Edges based on:
  - Visual proximity (same row/column)
  - Arrow connections
  - Section hierarchy
  - Semantic similarity

**Architecture**:
```
PDF → Text Box Detection → Graph Construction → GNN Processing → Query Interface
```

**Pros**: Task-agnostic, handles various document types
**Cons**: May require fine-tuning for specific layouts

---

### 5. Hybrid Extraction + Rules Engine (Recommended)
**Approach**: Combine pattern recognition with structured storage

**Implementation Steps**:

```python
# Step 1: Extract markdown with pymupdf4llm
markdown = pymupdf4llm.to_markdown(pdf_path)

# Step 2: Parse relationship patterns
patterns = {
    'arrows': [r'→', r'->', r'⟶'],
    'prerequisites': [r'after', r'following', r'requires'],
    'alternatives': [r'or', r'alternatively']
}

# Step 3: Build dependency graph
def extract_relationships(text):
    relationships = []
    for line in text.split('\n'):
        if any(arrow in line for arrow in patterns['arrows']):
            # Parse: "Course A → Course B"
            parts = re.split(r'[→\->⟶]', line)
            if len(parts) == 2:
                relationships.append({
                    'from': clean_course_name(parts[0]),
                    'to': clean_course_name(parts[1]),
                    'type': 'prerequisite'
                })
    return relationships

# Step 4: Store in SQLite with structured schema
```

**Database Schema**:
```sql
-- Core tables
CREATE TABLE courses (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    duration TEXT,
    price TEXT,
    course_type TEXT,  -- 'self-paced' or 'instructor-led'
    category TEXT       -- 'accelerated-computing', 'deep-learning', etc.
);

CREATE TABLE learning_paths (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT,          -- 'developer' or 'administrator'
    topic TEXT
);

CREATE TABLE prerequisites (
    from_course_id TEXT,
    to_course_id TEXT,
    path_id TEXT,
    sequence_order INTEGER,
    FOREIGN KEY (from_course_id) REFERENCES courses(id),
    FOREIGN KEY (to_course_id) REFERENCES courses(id),
    FOREIGN KEY (path_id) REFERENCES learning_paths(id)
);

CREATE TABLE alternatives (
    course_id TEXT,
    alternative_id TEXT,
    reason TEXT,        -- 'same-topic', 'different-format', etc.
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (alternative_id) REFERENCES courses(id)
);

-- For semantic search
CREATE TABLE course_embeddings (
    course_id TEXT PRIMARY KEY,
    embedding BLOB,     -- Store vector as binary
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

**Query Examples**:
```python
# Query 1: Find learning path
def get_learning_path(topic, role):
    query = """
    WITH RECURSIVE path AS (
        -- Find starting courses (no prerequisites)
        SELECT c.*, 0 as level
        FROM courses c
        JOIN learning_paths lp ON ...
        WHERE NOT EXISTS (
            SELECT 1 FROM prerequisites p
            WHERE p.to_course_id = c.id
        )

        UNION ALL

        -- Recursively find next courses
        SELECT c.*, path.level + 1
        FROM courses c
        JOIN prerequisites p ON c.id = p.to_course_id
        JOIN path ON p.from_course_id = path.id
    )
    SELECT * FROM path ORDER BY level;
    """

# Query 2: Find alternatives
def get_alternatives(course_id):
    # Combine SQL for explicit alternatives
    # + vector similarity for content-based alternatives
    pass
```

**Pros**:
- Flexible and extensible
- Combines structured and unstructured search
- No heavy ML infrastructure needed
- Works with existing SQLite + embeddings

**Cons**:
- Requires careful pattern design
- May miss complex visual relationships

---

## Recommended Solution for NVIDIA Learning Paths

Given your specific PDF structure with:
- Clear boxes containing courses
- Arrows showing prerequisites
- Alternative paths (dotted boxes)
- Role-based tracks (Developer vs Administrator)

**Best Approach**: **Hybrid Extraction + Rules Engine** with these enhancements:

1. **Initial Processing**:
   - Use pymupdf4llm for text extraction
   - Use computer vision (optional) for arrow detection
   - Parse visual patterns (boxes, arrows)

2. **Knowledge Graph Construction**:
   ```python
   graph = {
       "courses": {...},
       "prerequisites": [(from_id, to_id), ...],
       "alternatives": [(id1, id2), ...],
       "paths": {
           "accelerated_computing_developer": [...],
           "ai_infrastructure_admin": [...]
       }
   }
   ```

3. **Storage**: SQLite with the schema above

4. **RAG Enhancement**:
   - Use course embeddings for content search
   - Use graph traversal for pathway queries
   - Combine both for comprehensive answers

5. **Query Interface**:
   ```python
   class LearningPathRAG:
       def answer(self, question):
           # Parse intent
           if "path" in question or "courses" in question:
               # Use graph traversal
               return self.get_pathway_answer(question)
           elif "similar" in question or "about" in question:
               # Use vector search
               return self.get_semantic_answer(question)
           else:
               # Hybrid approach
               return self.get_hybrid_answer(question)
   ```

## Implementation Priority

1. **Phase 1**: Basic extraction and storage
   - Extract courses with metadata
   - Parse simple arrow relationships
   - Store in SQLite

2. **Phase 2**: Enhanced relationships
   - Add alternative detection
   - Implement path traversal
   - Add role-based filtering

3. **Phase 3**: RAG integration
   - Generate embeddings
   - Implement hybrid search
   - Add LLM for answer generation

## Key Insights

1. **Don't rely solely on semantic search** - it loses structural relationships
2. **Preserve document structure** as a graph, not just text chunks
3. **Combine multiple approaches**:
   - SQL for structured queries
   - Embeddings for semantic search
   - Graph traversal for pathways
4. **Consider visual layout** as meaningful information
5. **Build incrementally** - start simple, enhance gradually

## Next Steps

1. Choose approach based on your requirements
2. Start with Phase 1 implementation
3. Test with sample queries
4. Iterate based on results
5. Scale up to full document processing