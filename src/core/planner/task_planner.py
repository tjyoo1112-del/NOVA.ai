"""Task planning engine"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a single task"""
    id: str
    name: str
    description: str
    tool: str
    parameters: Dict[str, Any]
    priority: int = 0
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class TaskPlanner:
    """Plans and decomposes complex user requests into executable tasks"""
    
    def __init__(self):
        """Initialize task planner"""
        self.tasks: List[Task] = []
        self.executed_tasks: List[str] = []
        
    def plan(self, user_request: str, intent: str) -> List[Task]:
        """Plan tasks from user request"""
        logger.info(f"Planning tasks for request: {user_request}")
        # TODO: Decompose user request into tasks using LLM
        # TODO: Identify dependencies between tasks
        # TODO: Prioritize tasks
        return self.tasks
    
    def add_task(self, task: Task) -> None:
        """Add a task to the plan"""
        self.tasks.append(task)
        logger.debug(f"Added task: {task.name}")
    
    def get_next_task(self) -> Task:
        """Get the next executable task"""
        for task in self.tasks:
            # Check if all dependencies are satisfied
            if all(dep in self.executed_tasks for dep in task.dependencies):
                return task
        return None
    
    def mark_task_executed(self, task_id: str) -> None:
        """Mark a task as executed"""
        self.executed_tasks.append(task_id)
        logger.debug(f"Task executed: {task_id}")
