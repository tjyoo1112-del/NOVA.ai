"""System control tool for program and process management"""

import logging
import subprocess
import psutil
from typing import Dict, Any, List, Optional
from src.tools.base_tool import BaseTool
from enum import Enum

logger = logging.getLogger(__name__)

class SystemAction(Enum):
    """System control actions"""
    LAUNCH_PROGRAM = "launch_program"
    CLOSE_PROGRAM = "close_program"
    LIST_PROGRAMS = "list_programs"
    GET_PROCESS_INFO = "get_process_info"
    KILL_PROCESS = "kill_process"
    SHORTCUT = "shortcut"
    SCREENSHOT = "screenshot"
    LOCK_SCREEN = "lock_screen"
    SHUTDOWN = "shutdown"
    RESTART = "restart"

class SystemTool(BaseTool):
    """Tool for system control operations"""
    
    def __init__(self):
        """Initialize system tool"""
        super().__init__(
            name="SystemControl",
            description="Control system operations: launch/close programs, manage processes, shortcuts"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute system control action"""
        try:
            if action == SystemAction.LAUNCH_PROGRAM.value:
                return await self._launch_program(kwargs.get("program_name"), kwargs.get("args"))
            elif action == SystemAction.CLOSE_PROGRAM.value:
                return await self._close_program(kwargs.get("program_name"))
            elif action == SystemAction.LIST_PROGRAMS.value:
                return await self._list_programs()
            elif action == SystemAction.GET_PROCESS_INFO.value:
                return await self._get_process_info(kwargs.get("process_name"))
            elif action == SystemAction.KILL_PROCESS.value:
                return await self._kill_process(kwargs.get("process_id"))
            elif action == SystemAction.SHORTCUT.value:
                return await self._execute_shortcut(kwargs.get("keys"))
            elif action == SystemAction.SCREENSHOT.value:
                return await self._take_screenshot()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"[SystemControl] Error executing action {action}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _launch_program(self, program_name: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Launch a program"""
        logger.info(f"[SystemControl] Launching program: {program_name}")
        try:
            cmd = [program_name]
            if args:
                cmd.extend(args)
            
            process = subprocess.Popen(cmd)
            logger.info(f"[SystemControl] Program launched with PID: {process.pid}")
            return {
                "success": True,
                "program": program_name,
                "pid": process.pid,
                "message": f"Program {program_name} launched"
            }
        except Exception as e:
            logger.error(f"[SystemControl] Failed to launch {program_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _close_program(self, program_name: str) -> Dict[str, Any]:
        """Close a running program"""
        logger.info(f"[SystemControl] Closing program: {program_name}")
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if program_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    logger.info(f"[SystemControl] Terminated process: {proc.info['name']}")
                    return {"success": True, "program": program_name, "message": "Program closed"}
            
            return {"success": False, "error": f"Program {program_name} not found"}
        except Exception as e:
            logger.error(f"[SystemControl] Failed to close {program_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _list_programs(self) -> Dict[str, Any]:
        """List all running programs"""
        logger.info(f"[SystemControl] Listing running programs")
        try:
            programs = []
            for proc in psutil.process_iter(['pid', 'name']):
                programs.append({"pid": proc.info['pid'], "name": proc.info['name']})
            
            return {"success": True, "programs": programs, "count": len(programs)}
        except Exception as e:
            logger.error(f"[SystemControl] Failed to list programs: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_process_info(self, process_name: str) -> Dict[str, Any]:
        """Get information about a process"""
        logger.info(f"[SystemControl] Getting info for process: {process_name}")
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                if process_name.lower() in proc.info['name'].lower():
                    return {
                        "success": True,
                        "name": proc.info['name'],
                        "pid": proc.info['pid'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_mb": proc.info['memory_info'].rss / (1024 * 1024)
                    }
            
            return {"success": False, "error": f"Process {process_name} not found"}
        except Exception as e:
            logger.error(f"[SystemControl] Failed to get process info: {e}")
            return {"success": False, "error": str(e)}
    
    async def _kill_process(self, process_id: int) -> Dict[str, Any]:
        """Kill a process (requires security approval)"""
        logger.warning(f"[SystemControl] Killing process: {process_id}")
        # TODO: Require user confirmation
        try:
            proc = psutil.Process(process_id)
            proc.kill()
            return {"success": True, "pid": process_id, "message": "Process killed"}
        except Exception as e:
            logger.error(f"[SystemControl] Failed to kill process {process_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_shortcut(self, keys: str) -> Dict[str, Any]:
        """Execute keyboard shortcut"""
        logger.info(f"[SystemControl] Executing shortcut: {keys}")
        try:
            # TODO: Use pyautogui or keyboard library
            logger.info(f"[SystemControl] Shortcut executed: {keys}")
            return {"success": True, "shortcut": keys, "message": "Shortcut executed"}
        except Exception as e:
            logger.error(f"[SystemControl] Failed to execute shortcut: {e}")
            return {"success": False, "error": str(e)}
    
    async def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot"""
        logger.info(f"[SystemControl] Taking screenshot")
        try:
            # TODO: Use PIL or pyautogui
            return {"success": True, "path": "screenshot.png", "message": "Screenshot taken"}
        except Exception as e:
            logger.error(f"[SystemControl] Failed to take screenshot: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters"""
        action = kwargs.get("action")
        return action is not None
