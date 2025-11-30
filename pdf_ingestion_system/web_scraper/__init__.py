"""
NVIDIA Course Web Scraper Module

Automatically extracts course information from learn.nvidia.com
"""

from .scraper import NVIDIACourseScraper
from .browser_manager import BrowserManager

__version__ = "1.0.0"
__all__ = ["NVIDIACourseScraper", "BrowserManager"]
