"""Tool Agent - Executes tool operations"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ToolAgent:
    """Agent responsible for tool execution"""
    
    def __init__(self):
        """Initialize tool agent"""
        self.name = "Tool"
        self.tools = {}
    
    async def execute_tool(self, tool_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool"""
        logger.info(f"[{self.name}] Executing {tool_name}.{action}")
        
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool {tool_name} not found"}
        
        tool = self.tools[tool_name]
        return await tool.run(action=action, **kwargs)
    
    def register_tool(self, tool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"[{self.name}] Registered tool: {tool.name}")
