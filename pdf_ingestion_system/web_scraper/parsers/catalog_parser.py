"""
Parse NVIDIA course catalog pages to extract course URLs
"""

from bs4 import BeautifulSoup
from typing import List, Dict
from loguru import logger
import re

from ..utils import extract_course_id


class CatalogParser:
    """
    Parses the NVIDIA course catalog to extract course URLs
    """

    def __init__(self, selectors: Dict[str, str]):
        self.selectors = selectors

    def parse(self, html: str, catalog_url: str) -> List[str]:
        """
        Parse catalog HTML to extract course URLs

        Args:
            html: HTML content of catalog page
            catalog_url: Base catalog URL for resolving relative links

        Returns:
            List of course detail URLs
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            course_urls = []

            # Find all course cards
            course_cards = self._find_course_cards(soup)
            logger.info(f"Found {len(course_cards)} course cards in catalog")

            # Debug: Show what selectors we're trying
            if len(course_cards) == 0:
                logger.warning(f"Tried selectors: {self.selectors['course_card']}")
                # Check if there are any <a> tags at all
                all_links = soup.find_all('a', limit=10)
                logger.debug(f"Sample links found: {[a.get('class') for a in all_links]}")

            if not course_cards:
                logger.warning("No course cards found - selectors may need updating")
                self._try_fallback_extraction(soup, course_urls, catalog_url)
            else:
                # Extract URLs from each card
                for card in course_cards:
                    url = self._extract_course_url(card, catalog_url)
                    if url and url not in course_urls:
                        course_urls.append(url)

            logger.info(f"Extracted {len(course_urls)} unique course URLs")
            return course_urls

        except Exception as e:
            logger.error(f"Failed to parse catalog: {e}")
            return []

    def _find_course_cards(self, soup: BeautifulSoup) -> List:
        """Find course card elements in the catalog"""
        cards = []

        # Try multiple selectors
        for selector in self.selectors["course_card"].split(','):
            selector = selector.strip()
            found_cards = soup.select(selector)
            if found_cards:
                logger.debug(f"Found {len(found_cards)} cards with selector: {selector}")
                cards.extend(found_cards)
                break  # Use first successful selector

        # Remove duplicates
        return list(set(cards))

    def _extract_course_url(self, card_element, base_url: str) -> str:
        """Extract course URL from a card element"""
        # First check if the card element itself is a link (most common case)
        if card_element.name == 'a' and card_element.get('href'):
            href = card_element.get('href')
            logger.debug(f"Found href on card itself: {href}")

            # Convert relative URL to absolute
            if href.startswith('/'):
                # Extract base domain from catalog URL
                base_domain = re.match(r'(https?://[^/]+)', base_url)
                if base_domain:
                    href = base_domain.group(1) + href
            elif not href.startswith('http'):
                # Relative path
                href = base_url.rstrip('/') + '/' + href.lstrip('/')

            return href

        # Otherwise, try to find link inside the card
        for selector in self.selectors["course_url"].split(','):
            selector = selector.strip()
            link = card_element.select_one(selector)
            if link and link.get('href'):
                href = link.get('href')

                # Convert relative URL to absolute
                if href.startswith('/'):
                    # Extract base domain from catalog URL
                    base_domain = re.match(r'(https?://[^/]+)', base_url)
                    if base_domain:
                        href = base_domain.group(1) + href
                elif not href.startswith('http'):
                    # Relative path
                    href = base_url.rstrip('/') + '/' + href.lstrip('/')

                return href

        return ""

    def _try_fallback_extraction(self, soup: BeautifulSoup, course_urls: List[str], base_url: str):
        """
        Fallback: try to find any links that look like course pages
        """
        logger.info("Trying fallback extraction...")

        # Find all links
        all_links = soup.find_all('a', href=True)
        logger.info(f"Found {len(all_links)} total links")

        # Filter for course-like URLs
        course_pattern = re.compile(r'course[_-]?(detail|id|view)', re.I)

        for link in all_links:
            href = link.get('href', '')

            # Must match course pattern
            if course_pattern.search(href):
                # Convert to absolute URL
                if href.startswith('/'):
                    base_domain = re.match(r'(https?://[^/]+)', base_url)
                    if base_domain:
                        href = base_domain.group(1) + href

                if href and href not in course_urls:
                    course_urls.append(href)
                    logger.debug(f"Fallback found: {href}")

    def extract_course_metadata_from_card(self, card_element) -> Dict[str, str]:
        """
        Extract metadata visible in catalog cards (optional - for efficiency)

        Returns:
            Dict with title, level, duration, price if available
        """
        metadata = {}

        # Extract title
        for selector in self.selectors.get("course_title", "").split(','):
            if not selector:
                continue
            title_elem = card_element.select_one(selector.strip())
            if title_elem:
                metadata["title"] = title_elem.get_text(strip=True)
                break

        # Extract level
        for selector in self.selectors.get("course_level", "").split(','):
            if not selector:
                continue
            level_elem = card_element.select_one(selector.strip())
            if level_elem:
                metadata["level"] = level_elem.get_text(strip=True)
                break

        # Extract duration
        for selector in self.selectors.get("course_duration", "").split(','):
            if not selector:
                continue
            duration_elem = card_element.select_one(selector.strip())
            if duration_elem:
                metadata["duration"] = duration_elem.get_text(strip=True)
                break

        # Extract price
        for selector in self.selectors.get("course_price", "").split(','):
            if not selector:
                continue
            price_elem = card_element.select_one(selector.strip())
            if price_elem:
                metadata["price"] = price_elem.get_text(strip=True)
                break

        return metadata
