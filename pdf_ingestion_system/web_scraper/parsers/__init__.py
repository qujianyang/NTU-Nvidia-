"""
Parsers for extracting course data from HTML
"""

from .catalog_parser import CatalogParser
from .course_parser import CourseParser

__all__ = ["CatalogParser", "CourseParser"]
