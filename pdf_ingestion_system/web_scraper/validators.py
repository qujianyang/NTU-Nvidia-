"""
Data validation for scraped course information
"""

from typing import Dict, Any, List
from loguru import logger


class CourseDataValidator:
    """Validate course data against expected schema"""

    REQUIRED_FIELDS = [
        'id',
        'title',
        'url',
    ]

    OPTIONAL_FIELDS = [
        'description',
        'duration',
        'duration_hours',
        'price',
        'cost_usd',
        'level',
        'format',
        'prerequisites',
        'leads_to',
        'learning_objectives',
        'target_audience',
        'technical_requirements',
        'certificate',
        'skills_taught',
        'tags',
    ]

    def validate(self, course_data: Dict[str, Any]) -> bool:
        """
        Validate course data dictionary

        Returns:
            bool: True if valid, False otherwise
        """
        if not course_data:
            logger.error("Course data is empty")
            return False

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in course_data or not course_data[field]:
                logger.error(f"Missing required field: {field}")
                return False

        # Validate data types
        if not self._validate_types(course_data):
            return False

        # Validate values
        if not self._validate_values(course_data):
            return False

        logger.debug(f"Validation passed for: {course_data.get('title', 'Unknown')}")
        return True

    def _validate_types(self, data: Dict[str, Any]) -> bool:
        """Validate data types"""

        # String fields
        string_fields = ['id', 'title', 'url', 'description', 'duration', 'price', 'level', 'format']
        for field in string_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], str):
                    logger.error(f"Field '{field}' should be string, got {type(data[field])}")
                    return False

        # Float fields
        float_fields = ['duration_hours', 'cost_usd']
        for field in float_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], (int, float)):
                    logger.error(f"Field '{field}' should be numeric, got {type(data[field])}")
                    return False

        # List fields
        list_fields = ['prerequisites', 'leads_to', 'learning_objectives', 'skills_taught', 'tags']
        for field in list_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], list):
                    logger.error(f"Field '{field}' should be list, got {type(data[field])}")
                    return False

        # Boolean fields
        if 'certificate' in data and data['certificate'] is not None:
            if not isinstance(data['certificate'], bool):
                logger.error(f"Field 'certificate' should be boolean, got {type(data['certificate'])}")
                return False

        return True

    def _validate_values(self, data: Dict[str, Any]) -> bool:
        """Validate field values"""

        # URL should contain http/https
        if 'url' in data:
            if not data['url'].startswith(('http://', 'https://')):
                logger.warning(f"URL doesn't start with http/https: {data['url']}")

        # Duration hours should be non-negative
        if 'duration_hours' in data and data['duration_hours'] is not None:
            if data['duration_hours'] < 0:
                logger.error(f"Duration hours cannot be negative: {data['duration_hours']}")
                return False

        # Cost should be non-negative
        if 'cost_usd' in data and data['cost_usd'] is not None:
            if data['cost_usd'] < 0:
                logger.error(f"Cost cannot be negative: {data['cost_usd']}")
                return False

        # Level should be in expected values (warn only)
        if 'level' in data and data['level']:
            expected_levels = ['Beginner', 'Intermediate', 'Advanced', 'General Interest', 'Unknown']
            if data['level'] not in expected_levels:
                logger.warning(f"Unexpected level value: {data['level']}")

        return True

    def sanitize(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize course data - fill in missing optional fields with defaults

        Returns:
            Sanitized course data dictionary
        """
        sanitized = course_data.copy()

        # Set defaults for missing fields
        defaults = {
            'description': '',
            'duration': 'Unknown',
            'duration_hours': 0.0,
            'price': 'Unknown',
            'cost_usd': 0.0,
            'level': 'Unknown',
            'format': 'Self-Paced Course',
            'prerequisites': [],
            'leads_to': [],
            'learning_objectives': [],
            'target_audience': 'Technical professionals',
            'technical_requirements': 'Basic programming knowledge',
            'certificate': False,
            'skills_taught': [],
            'tags': [],
        }

        for field, default_value in defaults.items():
            if field not in sanitized or sanitized[field] is None:
                sanitized[field] = default_value

        return sanitized


def validate_catalog_urls(urls: List[str]) -> List[str]:
    """
    Validate and filter course URLs from catalog

    Args:
        urls: List of URLs to validate

    Returns:
        List of valid course URLs
    """
    valid_urls = []

    for url in urls:
        # Must be string
        if not isinstance(url, str):
            continue

        # Must start with http
        if not url.startswith(('http://', 'https://')):
            continue

        # Must contain course-related keywords
        if not any(keyword in url for keyword in ['course', 'learning', 'training']):
            logger.warning(f"URL doesn't look like a course page: {url}")
            continue

        valid_urls.append(url)

    logger.info(f"Validated {len(valid_urls)}/{len(urls)} course URLs")
    return valid_urls
