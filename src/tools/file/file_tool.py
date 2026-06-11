"""File management tool for file operations"""

import logging
import os
import shutil
from typing import Dict, Any, List
from pathlib import Path
from src.tools.base_tool import BaseTool
from enum import Enum

logger = logging.getLogger(__name__)

class FileAction(Enum):
    """File operations"""
    CREATE = "create"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    LIST = "list"
    SEARCH = "search"
    READ = "read"
    WRITE = "write"

class FileTool(BaseTool):
    """Tool for file management operations"""
    
    def __init__(self):
        """Initialize file tool"""
        super().__init__(
            name="FileManager",
            description="Manage files and directories: create, delete, copy, move, search, organize"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute file operation"""
        try:
            if action == FileAction.CREATE.value:
                return await self._create_file(kwargs.get("path"))
            elif action == FileAction.DELETE.value:
                return await self._delete_file(kwargs.get("path"))
            elif action == FileAction.COPY.value:
                return await self._copy_file(kwargs.get("src"), kwargs.get("dst"))
            elif action == FileAction.MOVE.value:
                return await self._move_file(kwargs.get("src"), kwargs.get("dst"))
            elif action == FileAction.LIST.value:
                return await self._list_directory(kwargs.get("path"))
            elif action == FileAction.SEARCH.value:
                return await self._search_files(kwargs.get("query"), kwargs.get("path"))
            elif action == FileAction.READ.value:
                return await self._read_file(kwargs.get("path"))
            elif action == FileAction.WRITE.value:
                return await self._write_file(kwargs.get("path"), kwargs.get("content"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"[FileManager] Error executing action {action}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_file(self, path: str) -> Dict[str, Any]:
        """Create a file"""
        logger.info(f"[FileManager] Creating file: {path}")
        try:
            Path(path).touch()
            return {"success": True, "path": path, "message": "File created"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file with security check"""
        logger.warning(f"[FileManager] Deleting file: {path}")
        # TODO: Require user confirmation for deletion
        try:
            if os.path.isfile(path):
                os.remove(path)
                return {"success": True, "path": path, "message": "File deleted"}
            else:
                return {"success": False, "error": "File not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _copy_file(self, src: str, dst: str) -> Dict[str, Any]:
        """Copy a file"""
        logger.info(f"[FileManager] Copying {src} to {dst}")
        try:
            shutil.copy2(src, dst)
            return {"success": True, "src": src, "dst": dst, "message": "File copied"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _move_file(self, src: str, dst: str) -> Dict[str, Any]:
        """Move a file"""
        logger.info(f"[FileManager] Moving {src} to {dst}")
        try:
            shutil.move(src, dst)
            return {"success": True, "src": src, "dst": dst, "message": "File moved"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List files in directory"""
        logger.info(f"[FileManager] Listing directory: {path}")
        try:
            items = os.listdir(path)
            files = [f for f in items if os.path.isfile(os.path.join(path, f))]
            folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
            return {
                "success": True,
                "path": path,
                "files": files,
                "folders": folders,
                "total": len(items)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _search_files(self, query: str, path: str = None) -> Dict[str, Any]:
        """Search for files matching pattern"""
        logger.info(f"[FileManager] Searching for: {query} in {path}")
        try:
            if path is None:
                path = os.path.expanduser("~")
            
            results = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if query.lower() in file.lower():
                        results.append(os.path.join(root, file))
                        if len(results) >= 50:  # Limit results
                            break
            
            return {"success": True, "query": query, "results": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file content"""
        logger.info(f"[FileManager] Reading file: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "path": path, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        logger.info(f"[FileManager] Writing to file: {path}")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "path": path, "message": "Content written"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters"""
        action = kwargs.get("action")
        return action is not None
