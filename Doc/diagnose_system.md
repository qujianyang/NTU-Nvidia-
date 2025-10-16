"""
Diagnostic script to test all components of the NVIDIA Course Advisor system
Run this to identify what's causing the error
"""

import sys
import os
import sqlite3
import requests
import json
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_ollama():
    """Test Ollama connectivity and model availability"""
    print_section("1. TESTING OLLAMA CONNECTION")

    try:
        # Test basic connectivity
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running on port 11434")
            models = response.json().get('models', [])
            print(f"   Found {len(models)} models installed:")
            for model in models:
                print(f"   - {model.get('name', 'unknown')}")

            # Check for required model
            model_names = [m.get('name', '') for m in models]
            if 'qwen2:7b-instruct-q4_0' in model_names:
                print("✅ Required model 'qwen2:7b-instruct-q4_0' is installed")
            else:
                print("❌ Required model 'qwen2:7b-instruct-q4_0' NOT found")
                print("   Run: ollama pull qwen2:7b-instruct-q4_0")
                return False

            # Test generation
            print("\n   Testing model generation...")
            test_prompt = "Say 'hello' in one word"
            payload = {
                "model": "qwen2:7b-instruct-q4_0",
                "prompt": test_prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            }
            gen_response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            if gen_response.status_code == 200:
                result = gen_response.json().get('response', '').strip()
                print(f"✅ Model generation works. Response: {result[:50]}")
                return True
            else:
                print(f"❌ Model generation failed: {gen_response.status_code}")
                return False
        else:
            print(f"❌ Ollama not responding properly. Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama on localhost:11434")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def test_database():
    """Test database connectivity and content"""
    print_section("2. TESTING DATABASE")

    db_path = Path(__file__).parent / "nvidia_courses.db"

    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("   Run the data ingestion script first")
        return False

    print(f"✅ Database found at: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        print(f"   Tables found: {', '.join(table_names)}")

        required_tables = ['courses', 'parent_documents', 'child_chunks']
        for table in required_tables:
            if table in table_names:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ Table '{table}' has {count} records")

                if count == 0:
                    print(f"⚠️  Table '{table}' is empty - run data ingestion")
            else:
                print(f"❌ Required table '{table}' not found")
                return False

        # Check for URLs in courses
        cursor.execute("SELECT COUNT(*) FROM courses WHERE url IS NOT NULL AND url != ''")
        url_count = cursor.fetchone()[0]
        print(f"   Courses with URLs: {url_count}")

        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_embeddings():
    """Test if embeddings model can be loaded"""
    print_section("3. TESTING EMBEDDINGS MODEL")

    try:
        print("   Loading HuggingFace embeddings model...")
        print("   (This may take a minute on first run)")

        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # Test embedding generation
        test_text = "test embedding"
        embedding = embeddings.embed_query(test_text)

        if len(embedding) > 0:
            print(f"✅ Embeddings model loaded successfully")
            print(f"   Embedding dimension: {len(embedding)}")
            return True
        else:
            print("❌ Embeddings generated but empty")
            return False

    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Install with: pip install langchain-huggingface sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Error loading embeddings: {e}")
        return False

def test_rag_retriever():
    """Test the full RAG retriever"""
    print_section("4. TESTING RAG RETRIEVER")

    try:
        # Add parent directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        from rag_retriever import CourseRAGRetriever

        print("   Initializing RAG retriever...")
        retriever = CourseRAGRetriever()

        # Test a simple query
        test_question = "What is Isaac Sim?"
        print(f"   Testing query: '{test_question}'")

        answer = retriever.answer_question(test_question)

        if answer and not answer.startswith("Error"):
            print(f"✅ RAG retriever working!")
            print(f"   Sample response: {answer[:100]}...")

            # Check if URLs are in response
            if "http" in answer:
                print("✅ URLs are being included in responses")
            else:
                print("⚠️  No URLs found in response - check prompt settings")

            retriever.close()
            return True
        else:
            print(f"❌ RAG retriever returned error: {answer}")
            retriever.close()
            return False

    except Exception as e:
        print(f"❌ Error testing RAG retriever: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Check if all required packages are installed"""
    print_section("5. CHECKING PYTHON DEPENDENCIES")

    required_packages = [
        'flask',
        'requests',
        'langchain_chroma',
        'langchain_core',
        'sqlite3'  # Built-in
    ]

    missing = []
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            missing.append(package)

    # Check for either langchain_huggingface or langchain_community
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        print("✅ langchain_huggingface installed")
    except ImportError:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            print("✅ langchain_community installed (fallback)")
        except ImportError:
            print("❌ Neither langchain_huggingface nor langchain_community found")
            missing.append("langchain_huggingface")

    if missing:
        print(f"\n⚠️  Install missing packages with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True

def main():
    """Run all diagnostic tests"""
    print("\n" + "🔍 NVIDIA COURSE ADVISOR - SYSTEM DIAGNOSTICS 🔍".center(60))
    print("This will test all components to identify issues")

    results = {
        "Dependencies": test_dependencies(),
        "Ollama": test_ollama(),
        "Database": test_database(),
        "Embeddings": test_embeddings(),
        "RAG Retriever": test_rag_retriever()
    }

    print_section("DIAGNOSTIC SUMMARY")

    all_passed = True
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {component:15} : {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)

    if all_passed:
        print("🎉 All systems operational! Your chatbot should work.")
        print("If you still see errors, check the Flask console output.")
    else:
        print("⚠️  Some components failed. Fix the issues above and try again.")
        print("\nCommon fixes:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull the model: ollama pull qwen2:7b-instruct-q4_0")
        print("3. Install packages: pip install -r requirements.txt")
        print("4. Run data ingestion to populate the database")

    print("\n")

if __name__ == "__main__":
    main()