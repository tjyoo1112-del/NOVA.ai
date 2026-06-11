"""Base class for all tools"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """Base class for all tool implementations"""
    
    def __init__(self, name: str, description: str):
        """Initialize tool"""
        self.name = name
        self.description = description
        self.is_available = True
        
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters"""
        pass
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run tool with validation"""
        logger.info(f"[{self.name}] Running with parameters: {kwargs}")
        
        if not self.validate_parameters(**kwargs):
            return {"success": False, "error": "Invalid parameters"}
        
        try:
            result = await self.execute(**kwargs)
            logger.info(f"[{self.name}] Execution completed successfully")
            return result
        except Exception as e:
            logger.error(f"[{self.name}] Execution failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
