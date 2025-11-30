"""
Browser automation manager with anti-detection features
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from fake_useragent import UserAgent
from loguru import logger
import random
import time
from typing import Optional, Dict, Any
from pathlib import Path

from .utils import random_delay


class BrowserManager:
    """
    Manages Playwright browser instances with anti-detection measures
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.ua = UserAgent()

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def start(self):
        """Initialize browser with anti-detection settings"""
        logger.info("Starting browser...")

        self.playwright = sync_playwright().start()

        # Browser launch options
        launch_options = {
            "headless": self.config["browser"]["headless"],
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        }

        self.browser = self.playwright.chromium.launch(**launch_options)

        # Context with anti-detection
        viewport = self.config["browser"]["viewport"]
        if self.config["anti_detection"].get("random_viewport"):
            # Add some randomness to viewport
            viewport = {
                "width": viewport["width"] + random.randint(-100, 100),
                "height": viewport["height"] + random.randint(-50, 50)
            }

        context_options = {
            "viewport": viewport,
            "user_agent": self.ua.random if self.config["anti_detection"]["rotate_user_agents"] else None,
            "java_script_enabled": True,
            "ignore_https_errors": True,
        }

        self.context = self.browser.new_context(**context_options)

        # Additional stealth settings
        if self.config["anti_detection"].get("stealth_mode", True):
            self._apply_stealth_mode()

        # Block resources if configured
        if self.config["anti_detection"].get("block_images") or self.config["anti_detection"].get("block_css"):
            self._setup_resource_blocking()

        self.page = self.context.new_page()

        # Set timeout
        self.page.set_default_timeout(self.config["browser"]["timeout"])

        logger.info("Browser started successfully")

    def _apply_stealth_mode(self):
        """Apply stealth JavaScript to hide automation"""
        self.context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Chrome runtime
            window.chrome = {
                runtime: {}
            };
        """)

    def _setup_resource_blocking(self):
        """Block unnecessary resources to speed up page loads"""
        def handle_route(route):
            resource_type = route.request.resource_type

            if self.config["anti_detection"].get("block_images") and resource_type == "image":
                route.abort()
            elif self.config["anti_detection"].get("block_css") and resource_type == "stylesheet":
                route.abort()
            else:
                route.continue_()

        self.context.route("**/*", handle_route)

    def navigate(self, url: str, wait_for: Optional[str] = None) -> bool:
        """
        Navigate to URL with error handling and waiting

        Args:
            url: URL to navigate to
            wait_for: CSS selector to wait for (optional)

        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Navigating to: {url}")

            # Navigate with network idle wait
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for specific element if provided
            if wait_for:
                logger.debug(f"Waiting for selector: {wait_for}")
                try:
                    # Wait for element to be attached to DOM (not necessarily visible)
                    self.page.wait_for_selector(wait_for, timeout=20000, state="attached")
                    # Extra wait for JavaScript rendering
                    time.sleep(3)
                    logger.info(f"✓ Found and waited for: {wait_for}")
                except Exception as e:
                    logger.warning(f"Selector not found (continuing anyway): {wait_for}")

            # Random human-like delay
            self._human_delay()

            return True

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            self._save_debug_info(f"navigation_error_{int(time.time())}")
            return False

    def get_html(self) -> str:
        """Get current page HTML"""
        return self.page.content()

    def scroll_page(self):
        """Simulate human-like scrolling to trigger lazy loading"""
        try:
            # Get page height
            page_height = self.page.evaluate("document.body.scrollHeight")

            # Scroll in chunks
            scroll_pause = 0.5
            current_position = 0
            scroll_increment = random.randint(300, 700)

            while current_position < page_height:
                # Scroll down
                self.page.evaluate(f"window.scrollTo(0, {current_position})")
                current_position += scroll_increment

                # Random pause
                time.sleep(random.uniform(0.3, scroll_pause))

                # Update page height (may change with lazy loading)
                page_height = self.page.evaluate("document.body.scrollHeight")

            # Scroll to bottom
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Wait for lazy loading
            scroll_delay = self.config["scraping"]["delay_after_scroll"]
            random_delay(scroll_delay["min"], scroll_delay["max"])

            logger.debug("Page scrolling complete")

        except Exception as e:
            logger.warning(f"Scroll simulation failed: {e}")

    def click_element(self, selector: str) -> bool:
        """
        Click an element by selector

        Args:
            selector: CSS selector

        Returns:
            bool: Success status
        """
        try:
            self.page.click(selector, timeout=5000)
            random_delay(0.5, 1.5)
            return True
        except Exception as e:
            logger.warning(f"Could not click element '{selector}': {e}")
            return False

    def type_text(self, selector: str, text: str) -> bool:
        """
        Type text into an input field with human-like delay

        Args:
            selector: CSS selector for input field
            text: Text to type

        Returns:
            bool: Success status
        """
        try:
            self.page.fill(selector, text)
            random_delay(0.3, 0.8)
            return True
        except Exception as e:
            logger.warning(f"Could not type into '{selector}': {e}")
            return False

    def _human_delay(self):
        """Add random human-like delay"""
        delay_config = self.config["scraping"]["delay_between_requests"]
        random_delay(delay_config["min"], delay_config["max"])

    def _save_debug_info(self, prefix: str):
        """Save screenshot and HTML for debugging"""
        if not self.config["monitoring"]["save_screenshots_on_error"]:
            return

        try:
            debug_dir = Path(self.config["output"]["log_dir"]) / "debug"
            debug_dir.mkdir(parents=True, exist_ok=True)

            # Screenshot
            screenshot_path = debug_dir / f"{prefix}.png"
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Screenshot saved: {screenshot_path}")

            # HTML
            if self.config["monitoring"]["save_html_on_error"]:
                html_path = debug_dir / f"{prefix}.html"
                html_path.write_text(self.page.content(), encoding="utf-8")
                logger.info(f"HTML saved: {html_path}")

        except Exception as e:
            logger.error(f"Failed to save debug info: {e}")

    def close(self):
        """Clean up browser resources"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
