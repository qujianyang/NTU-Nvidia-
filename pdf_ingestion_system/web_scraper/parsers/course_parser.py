"""
Parse NVIDIA course detail pages to extract comprehensive course information
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from loguru import logger
import re

from ..utils import (
    extract_course_id,
    parse_duration_to_hours,
    parse_price_to_usd,
    normalize_level,
    clean_text,
    generate_slug
)


class CourseParser:
    """
    Parses individual NVIDIA course detail pages
    """

    def __init__(self, selectors: Dict[str, str]):
        self.selectors = selectors

    def parse(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Parse course detail page HTML into structured data

        Args:
            html: HTML content of course page
            url: Original URL (for course ID extraction)

        Returns:
            Dict with course data matching your JSON schema, or None if parsing fails
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract all fields
            course_data = {
                "id": extract_course_id(url) or generate_slug(self._extract_title(soup)),
                "url": url,
                "title": self._extract_title(soup),
                "short_code": "",  # Will generate from title if needed
                "description": self._extract_description(soup),
                "learning_objectives": self._extract_learning_objectives(soup),
                "duration": self._extract_duration(soup),
                "duration_hours": 0.0,  # Computed below
                "price": self._extract_price(soup),
                "cost_usd": 0.0,  # Computed below
                "level": self._extract_level(soup),
                "format": self._extract_format(soup),
                "category": "",  # Will be inferred
                "track": "",  # Will be assigned during import
                "prerequisites": self._extract_prerequisites(soup),
                "leads_to": [],  # Will be computed from relationships
                "target_audience": self._extract_target_audience(soup),
                "technical_requirements": self._extract_technical_requirements(soup),
                "certificate": self._has_certificate(soup),
                "skills_taught": self._extract_skills(soup),
                "related_courses": [],
                "tags": [],  # Generated from metadata
                "notes": ""
            }

            # Compute derived fields
            course_data["duration_hours"] = parse_duration_to_hours(course_data["duration"])
            course_data["cost_usd"] = parse_price_to_usd(course_data["price"])
            course_data["level"] = normalize_level(course_data["level"])
            course_data["tags"] = self._generate_tags(course_data)
            course_data["short_code"] = self._generate_short_code(course_data["title"])

            # Validation
            if not course_data["title"]:
                logger.warning(f"Could not extract title from: {url}")
                return None

            logger.info(f"Successfully parsed: {course_data['title']}")
            return course_data

        except Exception as e:
            logger.error(f"Failed to parse course page {url}: {e}")
            logger.exception(e)
            return None

    def _extract_with_selectors(self, soup: BeautifulSoup, selector_key: str) -> str:
        """Helper to try multiple selectors"""
        selectors = self.selectors.get(selector_key, "")
        if not selectors:
            return ""

        for selector in selectors.split(','):
            selector = selector.strip()
            if not selector:
                continue

            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text(separator=' '))

        return ""

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract course title"""
        return self._extract_with_selectors(soup, "title")

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract course description"""
        desc = self._extract_with_selectors(soup, "description")

        # If empty, try to find description in meta tags
        if not desc:
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                desc = meta_desc.get('content', '')

        return clean_text(desc)

    def _extract_learning_objectives(self, soup: BeautifulSoup) -> List[str]:
        """Extract learning objectives as list"""
        objectives = []

        # Try selector-based extraction
        selectors = self.selectors.get("learning_objectives", "")
        for selector in selectors.split(','):
            selector = selector.strip()
            if not selector:
                continue

            elements = soup.select(selector)
            if elements:
                objectives = [clean_text(el.get_text()) for el in elements if el.get_text(strip=True)]
                if objectives:
                    break

        # Fallback: search for sections with relevant headings
        if not objectives:
            objectives = self._extract_list_from_section(soup, [
                "what you'll learn",
                "learning objectives",
                "objectives",
                "what you will learn",
                "you will learn",
                "key learnings",
                "outcomes"
            ])

        # Limit to 15 objectives
        return objectives[:15]

    def _extract_duration(self, soup: BeautifulSoup) -> str:
        """Extract course duration"""
        duration = self._extract_with_selectors(soup, "duration")

        # Normalize format
        if duration:
            duration = re.sub(r'(\d+)\s*hour', r'\1 Hour', duration, flags=re.I)
            duration = re.sub(r'(\d+)\s*h\b', r'\1 Hours', duration, flags=re.I)
            duration = re.sub(r'(\d+)\s*min', r'\1 Minutes', duration, flags=re.I)

        return duration or "Unknown"

    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract course price"""
        price = self._extract_with_selectors(soup, "price")

        # Check for free indicators
        if price and re.search(r'\bfree\b', price, re.I):
            return "Free"

        # Extract dollar amount
        if price:
            match = re.search(r'\$\s*(\d+)', price)
            if match:
                return f"${match.group(1)}"

        return price or "Unknown"

    def _extract_level(self, soup: BeautifulSoup) -> str:
        """Extract difficulty level"""
        return self._extract_with_selectors(soup, "level") or "Unknown"

    def _extract_format(self, soup: BeautifulSoup) -> str:
        """Extract or infer course format"""
        format_text = self._extract_with_selectors(soup, "format")

        if format_text:
            return format_text

        # Infer from page content
        page_text = soup.get_text().lower()

        if 'self-paced' in page_text or 'self paced' in page_text:
            return "Self-Paced Course"
        elif 'instructor' in page_text and ('led' in page_text or 'live' in page_text):
            return "Instructor-Led Workshop"
        elif 'workshop' in page_text:
            return "Workshop"

        return "Self-Paced Course"  # Default

    def _extract_prerequisites(self, soup: BeautifulSoup) -> List[str]:
        """Extract prerequisite course IDs"""
        prereq_ids = []

        # Try to find prerequisite links
        selectors = self.selectors.get("prerequisites", "")
        for selector in selectors.split(','):
            selector = selector.strip()
            if not selector:
                continue

            links = soup.select(selector)
            if links:
                for link in links:
                    href = link.get('href', '')
                    if 'course' in href:
                        course_id = extract_course_id(href)
                        if course_id and course_id not in prereq_ids:
                            prereq_ids.append(course_id)
                break

        return prereq_ids

    def _extract_target_audience(self, soup: BeautifulSoup) -> str:
        """Extract target audience"""
        audience = self._extract_with_selectors(soup, "target_audience")

        # Fallback: search sections
        if not audience:
            audience = self._extract_text_from_section(soup, [
                "who should attend",
                "target audience",
                "audience",
                "who is this for",
                "intended audience",
                "ideal participant"
            ])

        return audience or "Technical professionals and developers"

    def _extract_technical_requirements(self, soup: BeautifulSoup) -> str:
        """Extract technical requirements"""
        reqs = self._extract_with_selectors(soup, "technical_requirements")

        # Fallback
        if not reqs:
            reqs = self._extract_text_from_section(soup, [
                "technical requirements",
                "requirements",
                "prerequisites",
                "what you need",
                "system requirements",
                "before you start"
            ])

        return reqs or "Basic programming knowledge recommended"

    def _has_certificate(self, soup: BeautifulSoup) -> bool:
        """Check if course offers certificate"""
        # Check selector
        cert_elem = self._extract_with_selectors(soup, "certificate")
        if cert_elem and 'certificate' in cert_elem.lower():
            return True

        # Check page text
        page_text = soup.get_text().lower()
        certificate_keywords = [
            'certificate of completion',
            'certificate available',
            'earn a certificate',
            'receive a certificate',
            'certification upon completion'
        ]
        return any(keyword in page_text for keyword in certificate_keywords)

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract skills taught"""
        skills = []

        # Try selectors
        selectors = self.selectors.get("skills", "")
        for selector in selectors.split(','):
            selector = selector.strip()
            if not selector:
                continue

            elements = soup.select(selector)
            if elements:
                skills = [clean_text(el.get_text()) for el in elements if el.get_text(strip=True)]
                if skills:
                    break

        # Fallback: extract from sections
        if not skills:
            skills = self._extract_list_from_section(soup, [
                "skills",
                "technologies",
                "tools",
                "what you'll learn",
                "topics covered"
            ])

        return skills[:20]  # Limit to 20 skills

    # Helper methods

    def _extract_list_from_section(self, soup: BeautifulSoup, headings: List[str]) -> List[str]:
        """Extract bullet points from section with matching heading"""
        for heading_text in headings:
            # Find heading
            all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b'])
            for heading in all_headings:
                if heading_text.lower() in heading.get_text().lower():
                    # Find next ul/ol
                    next_list = heading.find_next(['ul', 'ol'])
                    if next_list:
                        items = next_list.find_all('li', recursive=False)
                        return [clean_text(item.get_text()) for item in items if item.get_text(strip=True)]

        return []

    def _extract_text_from_section(self, soup: BeautifulSoup, headings: List[str]) -> str:
        """Extract paragraph text from section with matching heading"""
        for heading_text in headings:
            all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong'])
            for heading in all_headings:
                if heading_text.lower() in heading.get_text().lower():
                    # Find next paragraph or div
                    next_elem = heading.find_next(['p', 'div'])
                    if next_elem:
                        return clean_text(next_elem.get_text())

        return ""

    def _generate_tags(self, course_data: Dict[str, Any]) -> List[str]:
        """Generate tags from course data"""
        tags = []

        # Add level tag
        level = course_data.get("level", "").lower()
        if level and level != "unknown":
            tags.append(level)

        # Add format tag
        format_text = course_data.get("format", "").lower()
        if "self-paced" in format_text:
            tags.append("self-paced")
        elif "instructor" in format_text:
            tags.append("instructor-led")
        elif "workshop" in format_text:
            tags.append("workshop")

        # Add price tag
        if course_data.get("cost_usd", 0) == 0:
            tags.append("free")
        else:
            tags.append("paid")

        # Add certificate tag
        if course_data.get("certificate"):
            tags.append("certificate")

        # Add duration tag
        duration_hours = course_data.get("duration_hours", 0)
        if 0 < duration_hours <= 2:
            tags.append("quick")
        elif duration_hours > 8:
            tags.append("comprehensive")

        return tags

    def _generate_short_code(self, title: str) -> str:
        """Generate short code from title"""
        if not title:
            return ""

        # Convert to uppercase, remove special chars
        code = re.sub(r'[^A-Z0-9\s]', '', title.upper())
        # Take first letter of each word
        words = code.split()
        short_code = ''.join([w[0] for w in words if w])

        # If too short, use first 3 letters of first 2 words
        if len(short_code) < 3 and len(words) >= 1:
            short_code = words[0][:4] if words else "COURSE"

        return short_code[:15]  # Limit length
