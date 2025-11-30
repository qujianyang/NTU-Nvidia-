"""
Utility functions for web scraping
"""

import time
import random
import re
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger


def random_delay(min_seconds: float, max_seconds: float):
    """Sleep for a random duration between min and max seconds"""
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Waiting {delay:.2f}s...")
    time.sleep(delay)


def parse_duration_to_hours(duration_str: str) -> float:
    """
    Convert duration string to hours (float)

    Examples:
        "2 Hours" -> 2.0
        "30 Minutes" -> 0.5
        "1 Hour 30 Minutes" -> 1.5
        "90 min" -> 1.5
    """
    if not duration_str or duration_str.lower() in ['unknown', 'n/a', '']:
        return 0.0

    duration_str = duration_str.lower()
    total_hours = 0.0

    # Extract hours
    hours_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hour|hr|h\b)', duration_str)
    if hours_match:
        total_hours += float(hours_match.group(1))

    # Extract minutes
    minutes_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:minute|min|m\b)', duration_str)
    if minutes_match:
        total_hours += float(minutes_match.group(1)) / 60.0

    # Extract days (convert to hours)
    days_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:day|d\b)', duration_str)
    if days_match:
        total_hours += float(days_match.group(1)) * 24.0

    return round(total_hours, 2)


def parse_price_to_usd(price_str: str) -> float:
    """
    Convert price string to USD (float)

    Examples:
        "Free" -> 0.0
        "$90" -> 90.0
        "$1,500" -> 1500.0
        "500 USD" -> 500.0
    """
    if not price_str or price_str.lower() in ['free', 'unknown', 'n/a', '']:
        return 0.0

    # Check for free indicators
    if re.search(r'\bfree\b', price_str, re.I):
        return 0.0

    # Extract dollar amount
    match = re.search(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', price_str)
    if match:
        amount_str = match.group(1).replace(',', '')
        return float(amount_str)

    return 0.0


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def extract_course_id(url: str) -> Optional[str]:
    """
    Extract course ID from URL

    Examples:
        "...?course_id=course-v1:DLI+T-DS-03+V1" -> "course-v1:DLI+T-DS-03+V1"
        "...?course_id=GENAI-EXPLAINED" -> "GENAI-EXPLAINED"
    """
    # Try to extract from query parameter
    match = re.search(r'course_id=([^&]+)', url)
    if match:
        return match.group(1)

    # Fallback: use last part of URL path
    parts = url.rstrip('/').split('/')
    if parts:
        return parts[-1]

    return None


def normalize_level(level_str: str) -> str:
    """
    Normalize difficulty level to standard values

    Returns: "Beginner", "Intermediate", "Advanced", or original string
    """
    if not level_str:
        return "Unknown"

    level_str = level_str.lower().strip()

    # Beginner synonyms
    if any(term in level_str for term in ['beginner', 'introductory', 'intro', 'basic', 'fundamental']):
        return "Beginner"

    # Intermediate synonyms
    if any(term in level_str for term in ['intermediate', 'moderate']):
        return "Intermediate"

    # Advanced synonyms
    if any(term in level_str for term in ['advanced', 'expert', 'professional']):
        return "Advanced"

    # General interest / non-technical
    if any(term in level_str for term in ['general', 'overview', 'awareness']):
        return "General Interest"

    # Return original if no match
    return level_str.title()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def retry_on_failure(func, *args, **kwargs):
    """Retry a function up to 3 times with exponential backoff"""
    return func(*args, **kwargs)


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text

    Example: "Building a Brain in 10 Minutes" -> "building-brain-10-minutes"
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug
