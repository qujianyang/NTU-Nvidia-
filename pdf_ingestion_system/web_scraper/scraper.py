"""
Main orchestrator for scraping NVIDIA Learn courses
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from loguru import logger
from datetime import datetime
import sys

from .browser_manager import BrowserManager
from .parsers.catalog_parser import CatalogParser
from .parsers.course_parser import CourseParser
from .validators import CourseDataValidator, validate_catalog_urls
from .config import Config


class NVIDIACourseScraper:
    """
    Main orchestrator for scraping NVIDIA Learn courses
    """

    def __init__(self, config_path: str):
        # Load configuration
        self.config = Config(config_path)

        # Setup logging
        self._setup_logging()

        # Initialize parsers
        self.catalog_parser = CatalogParser(self.config["parsing"]["catalog"])
        self.course_parser = CourseParser(self.config["parsing"]["course_detail"])
        self.validator = CourseDataValidator()

        # Statistics
        self.stats = {
            "total_urls": 0,
            "successful": 0,
            "failed": 0,
            "invalid": 0,
            "start_time": None,
            "end_time": None
        }

        logger.info("=" * 60)
        logger.info("NVIDIA Course Scraper initialized")
        logger.info("=" * 60)

    def scrape_all_courses(self) -> List[Dict[str, Any]]:
        """
        Main entry point: Scrape all courses from catalog

        Returns:
            List of course dictionaries
        """
        self.stats["start_time"] = datetime.now()
        logger.info(f"Starting full course catalog scrape at {self.stats['start_time']}")

        all_courses = []

        try:
            with BrowserManager(self.config.data) as browser:
                # Step 1: Get course URLs from catalog
                logger.info("\n" + "=" * 60)
                logger.info("STEP 1: Scraping Course Catalog")
                logger.info("=" * 60)

                course_urls = self._scrape_catalog(browser)
                self.stats["total_urls"] = len(course_urls)

                logger.info(f"Found {len(course_urls)} courses in catalog")

                if not course_urls:
                    logger.error("No courses found in catalog! Check selectors.")
                    return []

                # Step 2: Scrape each course detail page
                logger.info("\n" + "=" * 60)
                logger.info("STEP 2: Scraping Individual Course Pages")
                logger.info("=" * 60)

                max_courses = self.config.get("scraping.max_courses", 100)
                if len(course_urls) > max_courses:
                    logger.warning(f"Limiting to {max_courses} courses (safety limit)")
                    course_urls = course_urls[:max_courses]

                progress_interval = self.config.get("monitoring.progress_interval", 5)

                for i, url in enumerate(course_urls, 1):
                    # Progress logging
                    if i % progress_interval == 0 or i == 1 or i == len(course_urls):
                        logger.info(f"\n--- Progress: {i}/{len(course_urls)} ({i/len(course_urls)*100:.1f}%) ---")

                    logger.info(f"[{i}/{len(course_urls)}] Scraping: {url}")

                    # Scrape course
                    course_data = self._scrape_course_detail(browser, url)

                    if course_data:
                        # Validate data
                        if self.validator.validate(course_data):
                            # Sanitize (fill missing fields)
                            course_data = self.validator.sanitize(course_data)
                            all_courses.append(course_data)
                            self.stats["successful"] += 1
                            logger.success(f"✓ Scraped: {course_data['title']}")
                        else:
                            self.stats["invalid"] += 1
                            logger.warning(f"✗ Invalid data for: {url}")
                    else:
                        self.stats["failed"] += 1
                        logger.warning(f"✗ Failed to scrape: {url}")

                    # Save progress backup periodically
                    if i % 10 == 0:
                        self._save_backup(all_courses, f"progress_{i}")

            self.stats["end_time"] = datetime.now()
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

            # Final summary
            logger.info("\n" + "=" * 60)
            logger.info("SCRAPING COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Total URLs found: {self.stats['total_urls']}")
            logger.info(f"Successfully scraped: {self.stats['successful']}")
            logger.info(f"Failed: {self.stats['failed']}")
            logger.info(f"Invalid: {self.stats['invalid']}")
            logger.info(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            logger.info("=" * 60)

            return all_courses

        except KeyboardInterrupt:
            logger.warning("\n\nScraping interrupted by user!")
            logger.info(f"Partial results: {len(all_courses)} courses scraped")
            return all_courses

        except Exception as e:
            logger.exception(f"Scraping failed with error: {e}")
            logger.info(f"Partial results: {len(all_courses)} courses scraped")
            return all_courses

    def _scrape_catalog(self, browser: BrowserManager) -> List[str]:
        """
        Scrape catalog page to get list of course URLs
        """
        catalog_url = self.config["urls"]["catalog"]

        # Navigate to catalog
        logger.info("Navigating to catalog page...")
        if not browser.navigate(catalog_url):
            logger.error("Failed to load catalog page")
            return []

        # Handle cookie popup (if present)
        logger.info("Checking for cookie popup...")
        try:
            # Try to click "Accept All" or "Reject Optional"
            if browser.click_element("button:has-text('Accept All')"):
                logger.info("✓ Dismissed cookie popup")
            elif browser.click_element("button:has-text('Reject Optional')"):
                logger.info("✓ Dismissed cookie popup")
        except:
            logger.debug("No cookie popup found (or already dismissed)")

        # CRITICAL: Trigger course display by selecting sort option
        logger.info("Selecting sort option to trigger course display...")
        import time
        try:
            # Select "new" option to show courses
            browser.page.select_option("select#sort-by-select", "new")
            logger.info("✓ Selected 'new' from sort dropdown")

            # Wait for courses to load after sort selection
            time.sleep(3)

        except Exception as e:
            logger.warning(f"Could not interact with sort dropdown: {e}")

        # Wait for course cards to appear
        logger.info("Waiting for course cards to load...")
        time.sleep(5)

        # Scroll to load all courses (if lazy loading)
        logger.info("Scrolling page to load all courses...")
        browser.scroll_page()

        # Get HTML and parse
        html = browser.get_html()
        course_urls = self.catalog_parser.parse(html, catalog_url)

        # Validate URLs
        course_urls = validate_catalog_urls(course_urls)

        return course_urls

    def _scrape_course_detail(self, browser: BrowserManager, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual course detail page
        """
        timeout = self.config.get("scraping.timeout_per_course", 60)

        # Navigate to course page
        if not browser.navigate(url):
            logger.error(f"Failed to navigate to: {url}")
            return None

        # Scroll to load all content
        browser.scroll_page()

        # Get HTML and parse
        html = browser.get_html()
        course_data = self.course_parser.parse(html, url)

        return course_data

    def save_results(self, courses: List[Dict[str, Any]]):
        """
        Save scraped courses to JSON file matching your template format
        """
        output_path = Path(self.config["output"]["json_file"])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build output matching your template structure
        output_data = {
            "metadata": {
                "source": "nvidia_learn_website_scraper",
                "catalog_name": "NVIDIA Deep Learning Institute Courses",
                "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                "extraction_time": datetime.now().strftime("%H:%M:%S"),
                "total_courses": len(courses),
                "scraper_version": "1.0.0",
                "statistics": {
                    "total_urls_found": self.stats["total_urls"],
                    "successfully_scraped": self.stats["successful"],
                    "failed": self.stats["failed"],
                    "invalid": self.stats["invalid"],
                    "duration_seconds": (self.stats["end_time"] - self.stats["start_time"]).total_seconds() if self.stats["end_time"] else 0
                }
            },
            "courses": courses
        }

        # Save JSON with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.success(f"\n✓ Results saved to: {output_path}")
        logger.info(f"  Total courses: {len(courses)}")
        logger.info(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

        # Also save backup
        self._save_backup(courses, "final")

    def _save_backup(self, courses: List[Dict[str, Any]], suffix: str):
        """Save backup copy"""
        backup_dir = Path(self.config["output"]["backup_dir"])
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"nvidia_courses_{suffix}_{timestamp}.json"

        backup_data = {
            "metadata": {
                "backup_type": suffix,
                "timestamp": timestamp,
                "course_count": len(courses)
            },
            "courses": courses
        }

        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        logger.debug(f"Backup saved: {backup_path}")

    def _setup_logging(self):
        """Configure logging"""
        log_dir = Path(self.config["output"]["log_dir"])
        log_dir.mkdir(parents=True, exist_ok=True)

        log_level = self.config["monitoring"]["log_level"]

        # Remove default handler
        logger.remove()

        # Console handler (colored)
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>",
            colorize=True
        )

        # File handler (detailed)
        logger.add(
            log_dir / f"scraper_{datetime.now().strftime('%Y%m%d')}.log",
            level="DEBUG",  # Always log everything to file
            rotation="10 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {name}:{function}:{line} | {message}"
        )

        logger.info(f"Logging configured: {log_level}")


from typing import Optional  # Add this import at top if not present
