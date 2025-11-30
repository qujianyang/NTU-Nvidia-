#!/usr/bin/env python3
"""
NVIDIA Course Scraper - CLI Entry Point

Automatically scrapes NVIDIA Learn course catalog and generates JSON template.

Usage:
    python run_scraper.py                           # Full scrape with default config
    python run_scraper.py --config custom.yaml      # Use custom configuration
    python run_scraper.py --dry-run                 # Test run without saving
    python run_scraper.py --validate                # Validate existing output
    python run_scraper.py --help                    # Show help

Examples:
    # Standard scrape
    python run_scraper.py

    # Test with visible browser (for debugging)
    python run_scraper.py --visible

    # Scrape and immediately import to database
    python run_scraper.py --import

Author: NTU NVIDIA Learning Assistant Team
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path
from loguru import logger
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from web_scraper.scraper import NVIDIACourseScraper


def main():
    parser = argparse.ArgumentParser(
        description="NVIDIA Course Web Scraper - Automatically extract course data from learn.nvidia.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py                    # Full scrape
  python run_scraper.py --dry-run          # Test without saving
  python run_scraper.py --visible          # Show browser window
  python run_scraper.py --import           # Scrape and import to database

For more information: https://github.com/your-repo/nvidia-learning-assistant
        """
    )

    parser.add_argument(
        "--config",
        default="nvidia_scraper_config.yaml",
        help="Path to configuration YAML file (default: nvidia_scraper_config.yaml)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run scraper without saving results (for testing)"
    )

    parser.add_argument(
        "--visible",
        action="store_true",
        help="Run browser in visible mode (not headless) for debugging"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing output JSON without scraping"
    )

    parser.add_argument(
        "--import",
        action="store_true",
        dest="do_import",
        help="Automatically import scraped data to database after scraping"
    )

    parser.add_argument(
        "--max-courses",
        type=int,
        help="Maximum number of courses to scrape (for testing)"
    )

    args = parser.parse_args()

    # Display banner
    print_banner()

    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        logger.info("Please create nvidia_scraper_config.yaml or specify --config")
        sys.exit(1)

    # Handle validation mode
    if args.validate:
        validate_output(config_path)
        return

    # Modify config for visible mode
    if args.visible:
        logger.info("Running in VISIBLE mode (browser window will be shown)")
        # Load config and modify
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        config_data['browser']['headless'] = False
        # Save temporary config
        temp_config_path = config_path.parent / "nvidia_scraper_config_visible.yaml"
        with open(temp_config_path, 'w') as f:
            yaml.dump(config_data, f)
        config_path = temp_config_path
        logger.info(f"Using temporary config: {temp_config_path}")

    # Initialize scraper
    try:
        scraper = NVIDIACourseScraper(str(config_path))
    except Exception as e:
        logger.error(f"Failed to initialize scraper: {e}")
        sys.exit(1)

    # Override max courses if specified
    if args.max_courses:
        scraper.config.data['scraping']['max_courses'] = args.max_courses
        logger.info(f"Limited to {args.max_courses} courses (--max-courses)")

    # Run scraper
    try:
        logger.info("Starting scraping process...")
        logger.info(f"Config: {config_path}")
        logger.info(f"Dry run: {args.dry_run}")
        logger.info("")

        courses = scraper.scrape_all_courses()

        if not courses:
            logger.error("No courses scraped!")
            sys.exit(1)

        # Save results (unless dry run)
        if not args.dry_run:
            scraper.save_results(courses)

            # Import to database if requested
            if args.do_import:
                import_to_database(scraper.config["output"]["json_file"])

            # Show success message
            print_success_message(len(courses), scraper.config["output"]["json_file"])
        else:
            logger.info(f"\n[DRY RUN] Would have saved {len(courses)} courses")
            logger.info("Run without --dry-run to save results")

    except KeyboardInterrupt:
        logger.warning("\n\nScraping interrupted by user (Ctrl+C)")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Fatal error during scraping: {e}")
        sys.exit(1)


def print_banner():
    """Print ASCII art banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          NVIDIA COURSE WEB SCRAPER v1.0.0                ║
║     Automated Course Data Extraction from learn.nvidia.com    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_success_message(course_count: int, output_file: str):
    """Print success message with next steps"""
    message = f"""
╔═══════════════════════════════════════════════════════════╗
║                    SCRAPING SUCCESS!                      ║
╚═══════════════════════════════════════════════════════════╝

✓ Successfully scraped {course_count} courses
✓ Data saved to: {output_file}

NEXT STEPS:

1. Review the scraped data:
   → Open {output_file}

2. Import to database:
   → python json_importer.py {output_file}

3. Verify import:
   → Check pdf_ingestion_system/nvidia_courses.db

4. Start the web application:
   → cd web_app
   → python app.py

═══════════════════════════════════════════════════════════════
"""
    print(message)


def validate_output(config_path: Path):
    """Validate existing output JSON"""
    import yaml
    from web_scraper.validators import CourseDataValidator

    logger.info("Validation mode: checking existing output")

    # Load config to get output path
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    output_file = Path(config["output"]["json_file"])

    if not output_file.exists():
        logger.error(f"Output file not found: {output_file}")
        sys.exit(1)

    # Load JSON
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        sys.exit(1)

    # Validate
    validator = CourseDataValidator()
    courses = data.get("courses", [])

    logger.info(f"Validating {len(courses)} courses...")

    valid_count = 0
    invalid_count = 0

    for i, course in enumerate(courses, 1):
        if validator.validate(course):
            valid_count += 1
        else:
            invalid_count += 1
            logger.warning(f"Course {i} invalid: {course.get('title', 'Unknown')}")

    # Results
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION RESULTS")
    logger.info("=" * 60)
    logger.info(f"Total courses: {len(courses)}")
    logger.info(f"Valid: {valid_count}")
    logger.info(f"Invalid: {invalid_count}")
    logger.info("=" * 60)

    if invalid_count == 0:
        logger.success("✓ All courses are valid!")
    else:
        logger.warning(f"✗ {invalid_count} courses have validation issues")


def import_to_database(json_file: str):
    """Import scraped data to database"""
    logger.info("\n" + "=" * 60)
    logger.info("IMPORTING TO DATABASE")
    logger.info("=" * 60)

    try:
        # Import the json_importer module
        import json_importer

        logger.info(f"Running: python json_importer.py {json_file}")

        # Call the main function from json_importer
        # (Assuming json_importer has a main function or similar)
        # You may need to adjust this based on actual json_importer.py structure
        import subprocess
        result = subprocess.run(
            [sys.executable, "json_importer.py", json_file],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.success("✓ Successfully imported to database")
        else:
            logger.error(f"Import failed: {result.stderr}")

    except Exception as e:
        logger.error(f"Failed to import: {e}")
        logger.info("You can manually import with: python json_importer.py <json_file>")


if __name__ == "__main__":
    main()
