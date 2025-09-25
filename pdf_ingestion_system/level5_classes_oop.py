# Level 5: Classes and Object-Oriented Programming for PDF Processing
# Building on Level 4 - now organizing code into reusable classes

import fitz
from pathlib import Path
import time
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============= BASIC CLASS =============

class SimplePDFReader:
    """
    Most basic class - like grouping functions and data together
    """

    def __init__(self, pdf_path):
        """
        Constructor - runs when you create an object
        'self' refers to the object itself
        """
        self.pdf_path = pdf_path
        self.pdf = None
        self.is_open = False

    def open(self):
        """Method to open the PDF"""
        try:
            self.pdf = fitz.open(self.pdf_path)
            self.is_open = True
            print(f"Opened: {self.pdf_path}")
        except Exception as e:
            print(f"Failed to open: {e}")

    def get_page_count(self):
        """Method to get page count"""
        if not self.is_open:
            print("PDF not open!")
            return 0
        return len(self.pdf)

    def get_text(self):
        """Method to extract all text"""
        if not self.is_open:
            print("PDF not open!")
            return ""

        text = ""
        for page in self.pdf:
            text += page.get_text()
        return text

    def close(self):
        """Method to close the PDF"""
        if self.is_open and self.pdf:
            self.pdf.close()
            self.is_open = False
            print(f"Closed: {self.pdf_path}")


# ============= CLASS WITH PROPERTIES =============

class PDFDocument:
    """
    More advanced class with properties and private methods
    """

    def __init__(self, pdf_path):
        self._pdf_path = pdf_path  # _ means "private" by convention
        self._pdf = None
        self._metadata = None
        self._text_cache = None  # Cache extracted text

    @property
    def filename(self):
        """Property - access like attribute but runs code"""
        return Path(self._pdf_path).name

    @property
    def page_count(self):
        """Computed property - calculates when accessed"""
        if self._pdf is None:
            self._open()
        return len(self._pdf)

    @property
    def metadata(self):
        """Lazy loading - only load when needed"""
        if self._metadata is None:
            self._load_metadata()
        return self._metadata

    def _open(self):
        """Private method - internal use only"""
        if self._pdf is None:
            self._pdf = fitz.open(self._pdf_path)

    def _load_metadata(self):
        """Private method to load metadata"""
        self._open()
        self._metadata = {
            'title': self._pdf.metadata.get('title', 'Unknown'),
            'author': self._pdf.metadata.get('author', 'Unknown'),
            'pages': len(self._pdf),
            'created': self._pdf.metadata.get('creationDate', 'Unknown')
        }

    def extract_text(self, force_reload=False):
        """Public method with caching"""
        if self._text_cache is None or force_reload:
            self._open()
            self._text_cache = ""
            for page in self._pdf:
                self._text_cache += page.get_text()
        return self._text_cache

    def __str__(self):
        """String representation - what print() shows"""
        return f"PDFDocument: {self.filename} ({self.page_count} pages)"

    def __repr__(self):
        """Developer representation"""
        return f"PDFDocument('{self._pdf_path}')"

    def __enter__(self):
        """Context manager - use with 'with' statement"""
        self._open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting 'with' block"""
        if self._pdf:
            self._pdf.close()


# ============= INHERITANCE =============

class BasePDFProcessor:
    """
    Base class that other classes will inherit from
    """

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf = None
        self.processing_time = 0

    def open_pdf(self):
        """Common method all subclasses can use"""
        self.pdf = fitz.open(self.pdf_path)

    def close_pdf(self):
        """Common cleanup"""
        if self.pdf:
            self.pdf.close()

    def process(self):
        """Subclasses should override this"""
        raise NotImplementedError("Subclasses must implement process()")


class TextExtractor(BasePDFProcessor):
    """
    Inherits from BasePDFProcessor, adds text extraction
    """

    def process(self):
        """Override the parent's process method"""
        start = time.time()
        self.open_pdf()

        text = ""
        for page in self.pdf:
            text += page.get_text()

        self.close_pdf()
        self.processing_time = time.time() - start

        return text


class PageAnalyzer(BasePDFProcessor):
    """
    Another child class with different behavior
    """

    def process(self):
        """Different implementation of process"""
        start = time.time()
        self.open_pdf()

        analysis = []
        for i, page in enumerate(self.pdf):
            text = page.get_text()
            analysis.append({
                'page': i + 1,
                'chars': len(text),
                'words': len(text.split()),
                'lines': len(text.split('\n'))
            })

        self.close_pdf()
        self.processing_time = time.time() - start

        return analysis


# ============= COMPOSITION VS INHERITANCE =============

class PDFStatistics:
    """
    Helper class - used by composition
    """

    def calculate_stats(self, text):
        return {
            'total_chars': len(text),
            'total_words': len(text.split()),
            'total_lines': len(text.split('\n')),
            'avg_word_length': sum(len(w) for w in text.split()) / len(text.split()) if text.split() else 0
        }


class AdvancedPDFProcessor:
    """
    Uses composition - HAS a statistics calculator
    """

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.stats_calculator = PDFStatistics()  # Composition - HAS-A relationship
        self.text_extractor = TextExtractor(pdf_path)  # Another composition

    def process_with_stats(self):
        # Use composed objects
        text = self.text_extractor.process()
        stats = self.stats_calculator.calculate_stats(text)

        return {
            'text': text,
            'statistics': stats,
            'extraction_time': self.text_extractor.processing_time
        }


# ============= ABSTRACT BASE CLASS =============

class PDFPlugin(ABC):
    """
    Abstract base class - defines interface for plugins
    """

    @abstractmethod
    def can_handle(self, pdf_path) -> bool:
        """Check if plugin can handle this PDF"""
        pass

    @abstractmethod
    def process(self, pdf_path) -> Any:
        """Process the PDF"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name"""
        pass


class OCRPlugin(PDFPlugin):
    """
    Concrete implementation of abstract class
    """

    def can_handle(self, pdf_path) -> bool:
        # Check if PDF has images/scanned pages
        return True  # Simplified

    def process(self, pdf_path) -> Any:
        return "OCR processing (simulated)"

    def get_name(self) -> str:
        return "OCR Processor"


class EncryptedPDFPlugin(PDFPlugin):
    """
    Another plugin implementation
    """

    def can_handle(self, pdf_path) -> bool:
        try:
            pdf = fitz.open(pdf_path)
            is_encrypted = pdf.is_encrypted
            pdf.close()
            return is_encrypted
        except:
            return False

    def process(self, pdf_path) -> Any:
        return "Handling encrypted PDF"

    def get_name(self) -> str:
        return "Encrypted PDF Handler"


# ============= DATACLASS (SIMPLER CLASS SYNTAX) =============

@dataclass
class PDFInfo:
    """
    Dataclass - automatic __init__, __repr__, __eq__
    Perfect for data containers
    """
    filename: str
    path: str
    pages: int
    size_bytes: int
    created_at: datetime
    metadata: Dict[str, Any]
    is_valid: bool = True  # Default value

    def get_size_mb(self):
        """Can still add custom methods"""
        return self.size_bytes / (1024 * 1024)


# ============= CLASS METHODS AND STATIC METHODS =============

class PDFFactory:
    """
    Factory pattern using class methods
    """

    processors = {}  # Class variable - shared by all instances

    @classmethod
    def register_processor(cls, name, processor_class):
        """Class method - works on the class, not instance"""
        cls.processors[name] = processor_class

    @classmethod
    def create_processor(cls, name, pdf_path):
        """Factory method to create processors"""
        if name not in cls.processors:
            raise ValueError(f"Unknown processor: {name}")
        return cls.processors[name](pdf_path)

    @staticmethod
    def validate_pdf_path(pdf_path):
        """Static method - doesn't need class or instance"""
        return Path(pdf_path).exists() and pdf_path.endswith('.pdf')


# ============= POLYMORPHISM =============

class PDFHandler:
    """
    Base handler class
    """

    def handle(self, pdf_path):
        return f"Base handling: {pdf_path}"


class TextPDFHandler(PDFHandler):
    def handle(self, pdf_path):
        return f"Text extraction from: {pdf_path}"


class ImagePDFHandler(PDFHandler):
    def handle(self, pdf_path):
        return f"Image extraction from: {pdf_path}"


def process_any_handler(handler: PDFHandler, pdf_path):
    """
    Polymorphism - same method call, different behavior
    """
    return handler.handle(pdf_path)


# ============= COMPLETE EXAMPLE CLASS =============

class CompletePDFManager:
    """
    Full-featured class combining everything
    """

    # Class variables
    _instances = []
    default_timeout = 30

    def __init__(self, pdf_path, config=None):
        # Instance variables
        self.pdf_path = pdf_path
        self.config = config or {}
        self._pdf = None
        self._cache = {}
        self.created_at = datetime.now()

        # Register instance
        CompletePDFManager._instances.append(self)

        # Initialize components
        self._init_components()

    def _init_components(self):
        """Initialize internal components"""
        self.text_extractor = TextExtractor(self.pdf_path)
        self.analyzer = PageAnalyzer(self.pdf_path)
        self.stats = PDFStatistics()

    @property
    def is_open(self):
        return self._pdf is not None

    @property
    def info(self):
        """Lazy-loaded info"""
        if 'info' not in self._cache:
            self._cache['info'] = self._load_info()
        return self._cache['info']

    def _load_info(self):
        """Load PDF information"""
        path = Path(self.pdf_path)
        return PDFInfo(
            filename=path.name,
            path=str(path.absolute()),
            pages=self._get_page_count(),
            size_bytes=path.stat().st_size,
            created_at=datetime.now(),
            metadata=self._get_metadata(),
            is_valid=True
        )

    def _get_page_count(self):
        """Get page count"""
        if not self.is_open:
            self.open()
        return len(self._pdf)

    def _get_metadata(self):
        """Get metadata"""
        if not self.is_open:
            self.open()
        return self._pdf.metadata

    def open(self):
        """Open PDF"""
        if not self.is_open:
            self._pdf = fitz.open(self.pdf_path)
        return self

    def close(self):
        """Close PDF"""
        if self.is_open:
            self._pdf.close()
            self._pdf = None

    def extract_text(self, use_cache=True):
        """Extract text with caching"""
        if use_cache and 'text' in self._cache:
            return self._cache['text']

        text = self.text_extractor.process()
        if use_cache:
            self._cache['text'] = text
        return text

    def analyze(self):
        """Analyze pages"""
        return self.analyzer.process()

    def get_statistics(self):
        """Get text statistics"""
        text = self.extract_text()
        return self.stats.calculate_stats(text)

    def process_all(self):
        """Process everything"""
        return {
            'info': self.info,
            'text': self.extract_text(),
            'analysis': self.analyze(),
            'statistics': self.get_statistics()
        }

    @classmethod
    def from_directory(cls, directory):
        """Alternative constructor - create from directory"""
        pdfs = []
        for pdf_file in Path(directory).glob("*.pdf"):
            pdfs.append(cls(str(pdf_file)))
        return pdfs

    @classmethod
    def get_all_instances(cls):
        """Get all created instances"""
        return cls._instances

    def __enter__(self):
        """Context manager support"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on exit"""
        self.close()

    def __str__(self):
        return f"PDFManager: {self.info.filename}"

    def __repr__(self):
        return f"CompletePDFManager('{self.pdf_path}')"


# ============= TESTING ALL CONCEPTS =============

if __name__ == "__main__":
    pdf_file = "../nvidia.pdf"

    print("=== Level 5: Classes and OOP Demo ===\n")

    # Test 1: Basic class
    print("1. Testing basic class...")
    reader = SimplePDFReader(pdf_file)
    reader.open()
    print(f"   Pages: {reader.get_page_count()}")
    text = reader.get_text()
    print(f"   Text length: {len(text)} chars")
    reader.close()
    print()

    # Test 2: Properties
    print("2. Testing properties...")
    doc = PDFDocument(pdf_file)
    print(f"   Filename: {doc.filename}")  # Property access
    print(f"   Pages: {doc.page_count}")    # Computed property
    print(f"   {doc}")  # Uses __str__
    print()

    # Test 3: Context manager
    print("3. Testing context manager...")
    with PDFDocument(pdf_file) as doc:
        text = doc.extract_text()
        print(f"   Extracted {len(text)} chars inside 'with' block")
    print("   PDF automatically closed after 'with' block\n")

    # Test 4: Inheritance
    print("4. Testing inheritance...")
    text_proc = TextExtractor(pdf_file)
    text = text_proc.process()
    print(f"   TextExtractor: {len(text)} chars in {text_proc.processing_time:.2f}s")

    page_proc = PageAnalyzer(pdf_file)
    analysis = page_proc.process()
    print(f"   PageAnalyzer: {len(analysis)} pages analyzed in {page_proc.processing_time:.2f}s\n")

    # Test 5: Composition
    print("5. Testing composition...")
    advanced = AdvancedPDFProcessor(pdf_file)
    result = advanced.process_with_stats()
    print(f"   Words: {result['statistics']['total_words']}")
    print(f"   Extraction time: {result['extraction_time']:.2f}s\n")

    # Test 6: Abstract classes / Plugins
    print("6. Testing plugin system...")
    plugins = [OCRPlugin(), EncryptedPDFPlugin()]
    for plugin in plugins:
        if plugin.can_handle(pdf_file):
            print(f"   {plugin.get_name()}: {plugin.process(pdf_file)}")
    print()

    # Test 7: Dataclass
    print("7. Testing dataclass...")
    info = PDFInfo(
        filename="test.pdf",
        path="/path/to/test.pdf",
        pages=100,
        size_bytes=1024000,
        created_at=datetime.now(),
        metadata={'title': 'Test'}
    )
    print(f"   {info.filename}: {info.get_size_mb():.2f} MB")
    print()

    # Test 8: Class/Static methods
    print("8. Testing factory pattern...")
    PDFFactory.register_processor('text', TextExtractor)
    PDFFactory.register_processor('analyze', PageAnalyzer)
    processor = PDFFactory.create_processor('text', pdf_file)
    print(f"   Factory created: {type(processor).__name__}")
    print(f"   Path valid: {PDFFactory.validate_pdf_path(pdf_file)}\n")

    # Test 9: Polymorphism
    print("9. Testing polymorphism...")
    handlers = [PDFHandler(), TextPDFHandler(), ImagePDFHandler()]
    for handler in handlers:
        result = process_any_handler(handler, pdf_file)
        print(f"   {result}")
    print()

    # Test 10: Complete manager
    print("10. Testing complete manager...")
    with CompletePDFManager(pdf_file) as manager:
        info = manager.info
        print(f"   File: {info.filename}")
        print(f"   Size: {info.get_size_mb():.2f} MB")
        print(f"   Pages: {info.pages}")

        stats = manager.get_statistics()
        print(f"   Words: {stats['total_words']}")

    # Show all instances
    all_managers = CompletePDFManager.get_all_instances()
    print(f"\n   Total managers created: {len(all_managers)}")

    print("\n=== OOP concepts mastered! ===")
    print("You now understand:")
    print("- Classes and objects")
    print("- Properties and methods")
    print("- Inheritance and composition")
    print("- Abstract classes and interfaces")
    print("- Polymorphism and encapsulation")
    print("- Context managers and factory patterns")