"""Main UI window for NOVA AI"""

import logging

logger = logging.getLogger(__name__)

class MainWindow:
    """Main application window"""
    
    def __init__(self):
        """Initialize main window"""
        self.title = "NOVA AI - Personal Agent OS"
        self.theme = "dark"  # or 'light'
        self.width = 1200
        self.height = 800
        
        logger.info(f"[UI] Initializing {self.title}")
    
    async def initialize(self) -> bool:
        """Initialize UI components"""
        logger.info("[UI] Loading UI components")
        # TODO: Initialize Electron window with React
        # TODO: Setup chat panel
        # TODO: Setup execution plan panel
        # TODO: Setup voice button
        # TODO: Setup agent status display
        return True
    
    async def show_message(self, message: str, role: str = "assistant") -> None:
        """Display message in chat"""
        logger.debug(f"[UI] Showing message: {message}")
        # TODO: Update chat UI
    
    async def show_task_plan(self, tasks: list) -> None:
        """Display task execution plan"""
        logger.debug(f"[UI] Showing task plan with {len(tasks)} tasks")
        # TODO: Update execution plan panel
    
    async def update_status(self, status: str) -> None:
        """Update agent status"""
        logger.debug(f"[UI] Status: {status}")
        # TODO: Update status indicator
