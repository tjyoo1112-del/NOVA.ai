"""Memory management system"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages short-term and long-term user memory"""
    
    def __init__(self):
        """Initialize memory manager"""
        self.short_term: List[Dict[str, Any]] = []
        self.long_term: Dict[str, Any] = {}
        
    def store_short_term(self, key: str, value: Any) -> None:
        """Store information in short-term memory"""
        self.short_term.append({"key": key, "value": value})
        logger.debug(f"Stored in short-term memory: {key}")
    
    def store_long_term(self, key: str, value: Any) -> None:
        """Store information in long-term memory"""
        self.long_term[key] = value
        logger.debug(f"Stored in long-term memory: {key}")
    
    def recall_short_term(self, key: str) -> Optional[Any]:
        """Recall information from short-term memory"""
        for item in self.short_term:
            if item["key"] == key:
                return item["value"]
        return None
    
    def recall_long_term(self, key: str) -> Optional[Any]:
        """Recall information from long-term memory"""
        return self.long_term.get(key)
    
    def clear_short_term(self) -> None:
        """Clear short-term memory"""
        self.short_term.clear()
        logger.debug("Cleared short-term memory")
