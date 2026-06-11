"""Network tool for API calls and web requests"""

import logging
import requests
from typing import Dict, Any, Optional, List
from src.tools.base_tool import BaseTool
from enum import Enum

logger = logging.getLogger(__name__)

class NetworkAction(Enum):
    """Network actions"""
    HTTP_GET = "http_get"
    HTTP_POST = "http_post"
    HTTP_PUT = "http_put"
    HTTP_DELETE = "http_delete"
    DOWNLOAD_FILE = "download_file"
    CHECK_CONNECTION = "check_connection"

class NetworkTool(BaseTool):
    """Tool for network operations"""
    
    def __init__(self):
        """Initialize network tool"""
        super().__init__(
            name="Network",
            description="Handle network operations: API calls, downloads, connectivity checks"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute network action"""
        try:
            if action == NetworkAction.HTTP_GET.value:
                return await self._http_get(kwargs.get("url"), kwargs.get("headers"))
            elif action == NetworkAction.HTTP_POST.value:
                return await self._http_post(kwargs.get("url"), kwargs.get("data"), kwargs.get("headers"))
            elif action == NetworkAction.DOWNLOAD_FILE.value:
                return await self._download_file(kwargs.get("url"), kwargs.get("path"))
            elif action == NetworkAction.CHECK_CONNECTION.value:
                return await self._check_connection()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"[Network] Error executing action {action}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _http_get(self, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP GET request"""
        logger.info(f"[Network] GET request to {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "content": response.text[:1000]  # First 1000 chars
            }
        except Exception as e:
            logger.error(f"[Network] GET request failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _http_post(self, url: str, data: Dict = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP POST request"""
        logger.info(f"[Network] POST request to {url}")
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text
            }
        except Exception as e:
            logger.error(f"[Network] POST request failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _download_file(self, url: str, path: str) -> Dict[str, Any]:
        """Download file from URL"""
        logger.info(f"[Network] Downloading {url} to {path}")
        try:
            response = requests.get(url, timeout=30)
            with open(path, 'wb') as f:
                f.write(response.content)
            return {
                "success": True,
                "url": url,
                "path": path,
                "size": len(response.content),
                "message": "File downloaded"
            }
        except Exception as e:
            logger.error(f"[Network] Download failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_connection(self) -> Dict[str, Any]:
        """Check internet connectivity"""
        logger.info("[Network] Checking internet connection")
        try:
            response = requests.get('https://www.google.com', timeout=5)
            return {
                "success": True,
                "connected": response.status_code == 200,
                "message": "Connected to internet" if response.status_code == 200 else "No connection"
            }
        except Exception as e:
            logger.warning(f"[Network] No internet connection: {e}")
            return {"success": False, "connected": False, "error": "No internet connection"}
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters"""
        action = kwargs.get("action")
        return action is not None
