"""Browser automation with Playwright"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from src.tools.base_tool import BaseTool
from enum import Enum

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError:
    async_playwright = None
    Browser = None
    Page = None
    BrowserContext = None

logger = logging.getLogger(__name__)

class BrowserAction(Enum):
    """Browser actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    SEARCH = "search"
    EXTRACT_TEXT = "extract_text"
    WAIT_FOR_SELECTOR = "wait_for_selector"
    FILL_FORM = "fill_form"

class BrowserTool(BaseTool):
    """Tool for browser automation using Playwright"""
    
    def __init__(self):
        """Initialize browser tool"""
        super().__init__(
            name="Browser",
            description="Automate web browser operations like navigation, clicking, searching"
        )
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None
        self.current_url: Optional[str] = None
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize browser with Playwright"""
        if not async_playwright:
            logger.error("[Browser] Playwright not installed")
            return False
        
        try:
            logger.info("[Browser] Initializing Playwright...")
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            self.is_initialized = True
            logger.info("[Browser] Browser initialized successfully")
            return True
        except Exception as e:
            logger.error(f"[Browser] Failed to initialize: {e}")
            return False
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute browser action"""
        if not self.is_initialized or not self.page:
            logger.error("[Browser] Browser not initialized")
            return {"success": False, "error": "Browser not initialized"}
        
        try:
            if action == BrowserAction.NAVIGATE.value:
                return await self._navigate(kwargs.get("url"))
            elif action == BrowserAction.CLICK.value:
                return await self._click(kwargs.get("selector"))
            elif action == BrowserAction.TYPE.value:
                return await self._type(kwargs.get("selector"), kwargs.get("text"))
            elif action == BrowserAction.SEARCH.value:
                return await self._search(kwargs.get("query"))
            elif action == BrowserAction.SCREENSHOT.value:
                return await self._screenshot(kwargs.get("path"))
            elif action == BrowserAction.EXTRACT_TEXT.value:
                return await self._extract_text()
            elif action == BrowserAction.WAIT_FOR_SELECTOR.value:
                return await self._wait_for_selector(kwargs.get("selector"), kwargs.get("timeout", 5000))
            elif action == BrowserAction.FILL_FORM.value:
                return await self._fill_form(kwargs.get("fields"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"[Browser] Error executing action {action}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL"""
        logger.info(f"[Browser] Navigating to: {url}")
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            
            await self.page.goto(url, wait_until="networkidle")
            self.current_url = url
            logger.info(f"[Browser] Successfully navigated to {url}")
            return {"success": True, "url": url}
        except Exception as e:
            logger.error(f"[Browser] Navigation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _click(self, selector: str) -> Dict[str, Any]:
        """Click on element"""
        logger.info(f"[Browser] Clicking on: {selector}")
        try:
            await self.page.click(selector)
            logger.info(f"[Browser] Successfully clicked {selector}")
            return {"success": True, "selector": selector}
        except Exception as e:
            logger.error(f"[Browser] Click failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _type(self, selector: str, text: str) -> Dict[str, Any]:
        """Type text into element"""
        logger.info(f"[Browser] Typing into {selector}: {text}")
        try:
            await self.page.fill(selector, text)
            logger.info(f"[Browser] Successfully typed text")
            return {"success": True, "selector": selector, "text": text}
        except Exception as e:
            logger.error(f"[Browser] Type failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _search(self, query: str) -> Dict[str, Any]:
        """Search on Google"""
        logger.info(f"[Browser] Searching: {query}")
        try:
            await self._navigate("https://www.google.com")
            await self.page.fill("input[name=q]", query)
            await self.page.press("input[name=q]", "Enter")
            await self.page.wait_for_load_state("networkidle")
            
            # Extract search results
            results = await self.page.query_selector_all("div.g")
            logger.info(f"[Browser] Found {len(results)} search results")
            
            return {"success": True, "query": query, "results_count": len(results)}
        except Exception as e:
            logger.error(f"[Browser] Search failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _screenshot(self, path: str = "screenshot.png") -> Dict[str, Any]:
        """Take screenshot"""
        logger.info(f"[Browser] Taking screenshot to {path}")
        try:
            await self.page.screenshot(path=path)
            logger.info(f"[Browser] Screenshot saved to {path}")
            return {"success": True, "path": path}
        except Exception as e:
            logger.error(f"[Browser] Screenshot failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_text(self) -> Dict[str, Any]:
        """Extract all text from current page"""
        logger.info("[Browser] Extracting text from page")
        try:
            text = await self.page.content()
            return {"success": True, "text": text[:2000]}  # First 2000 chars
        except Exception as e:
            logger.error(f"[Browser] Text extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _wait_for_selector(self, selector: str, timeout: int = 5000) -> Dict[str, Any]:
        """Wait for element to appear"""
        logger.info(f"[Browser] Waiting for selector: {selector}")
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            logger.info(f"[Browser] Selector found: {selector}")
            return {"success": True, "selector": selector}
        except Exception as e:
            logger.error(f"[Browser] Wait failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _fill_form(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Fill form with multiple fields"""
        logger.info(f"[Browser] Filling form with {len(fields)} fields")
        try:
            for selector, value in fields.items():
                await self.page.fill(selector, value)
            
            logger.info(f"[Browser] Form filled successfully")
            return {"success": True, "fields_count": len(fields)}
        except Exception as e:
            logger.error(f"[Browser] Form fill failed: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters"""
        action = kwargs.get("action")
        return action is not None
    
    async def close(self) -> None:
        """Close browser"""
        logger.info("[Browser] Closing browser")
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            self.is_initialized = False
        except Exception as e:
            logger.error(f"[Browser] Error closing: {e}")
