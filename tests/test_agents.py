"""Integration tests for agents"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.core.agent.coordinator_agent import CoordinatorAgent
from src.core.agent.planner_agent import PlannerAgent
from src.core.agent.memory_agent import MemoryAgent
from src.core.agent.tool_agent import ToolAgent
from src.core.agent.verifier_agent import VerifierAgent

class TestCoordinatorAgent:
    """Coordinator agent integration tests"""
    
    @pytest.fixture
    async def coordinator(self):
        """Setup coordinator agent"""
        agent = CoordinatorAgent()
        yield agent
    
    @pytest.mark.asyncio
    async def test_coordinator_initialization(self, coordinator):
        """Test coordinator initialization"""
        result = await coordinator.initialize()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_coordinator_process_input(self, coordinator):
        """Test processing user input"""
        await coordinator.initialize()
        result = await coordinator.process_user_input(
            "시스템 상태를 확인해줘"
        )
        assert "status" in result
        assert result["status"] in ["success", "failed"]

class TestPlannerAgent:
    """Planner agent integration tests"""
    
    @pytest.fixture
    async def planner(self):
        """Setup planner agent"""
        agent = PlannerAgent()
        yield agent
    
    @pytest.mark.asyncio
    async def test_plan_simple_task(self, planner):
        """Test planning simple task"""
        tasks = await planner.plan_tasks(
            intent="program_launch",
            parameters={"program_name": "notepad"}
        )
        assert len(tasks) > 0
        assert tasks[0]["tool"] == "system"
    
    @pytest.mark.asyncio
    async def test_plan_complex_task(self, planner):
        """Test planning complex task with dependencies"""
        tasks = await planner.plan_tasks(
            intent="file_download_and_organize",
            parameters={
                "url": "https://example.com/file.pdf",
                "destination": "C:/Downloads"
            }
        )
        assert len(tasks) >= 2
        # Check for dependencies
        assert any(t["depends_on"] for t in tasks if "depends_on" in t)

class TestMemoryAgent:
    """Memory agent integration tests"""
    
    @pytest.fixture
    async def memory(self):
        """Setup memory agent"""
        agent = MemoryAgent()
        yield agent
    
    @pytest.mark.asyncio
    async def test_store_and_recall(self, memory):
        """Test storing and recalling memory"""
        # Store memory
        await memory.store_memory(
            key="favorite_program",
            value="VS Code",
            category="habit"
        )
        
        # Recall memory
        results = await memory.recall_memory(
            query="좋아하는 프로그램",
            top_k=1
        )
        assert len(results) > 0
        assert "VS Code" in str(results[0])
    
    @pytest.mark.asyncio
    async def test_memory_update(self, memory):
        """Test updating memory"""
        # Store initial value
        await memory.store_memory(
            key="work_start_time",
            value="9:00 AM",
            category="habit"
        )
        
        # Update value
        result = await memory.update_memory(
            key="work_start_time",
            value="8:30 AM"
        )
        assert result is True

class TestToolAgent:
    """Tool agent integration tests"""
    
    @pytest.fixture
    async def tool_agent(self):
        """Setup tool agent"""
        agent = ToolAgent()
        yield agent
    
    @pytest.mark.asyncio
    async def test_tool_registration(self, tool_agent):
        """Test tool registration"""
        mock_tool = AsyncMock()
        mock_tool.name = "MockTool"
        
        tool_agent.register_tool(mock_tool)
        assert "MockTool" in tool_agent.tools
    
    @pytest.mark.asyncio
    async def test_tool_execution(self, tool_agent):
        """Test tool execution"""
        mock_tool = AsyncMock()
        mock_tool.name = "TestTool"
        mock_tool.run = AsyncMock(return_value={
            "success": True,
            "result": "test_result"
        })
        
        tool_agent.register_tool(mock_tool)
        result = await tool_agent.execute_tool(
            tool_name="TestTool",
            action="test_action",
            param1="value1"
        )
        assert result["success"] is True

class TestVerifierAgent:
    """Verifier agent integration tests"""
    
    @pytest.fixture
    async def verifier(self):
        """Setup verifier agent"""
        agent = VerifierAgent()
        yield agent
    
    @pytest.mark.asyncio
    async def test_verify_successful_task(self, verifier):
        """Test verifying successful task"""
        result = {
            "success": True,
            "result": "프로그램 실행 완료",
            "duration": 2.5
        }
        success, message = await verifier.verify_task(
            "launch_program",
            result
        )
        assert success is True
    
    @pytest.mark.asyncio
    async def test_verify_failed_task(self, verifier):
        """Test verifying failed task"""
        result = {
            "success": False,
            "error": "프로그램을 찾을 수 없음",
            "duration": 1.2
        }
        success, message = await verifier.verify_task(
            "launch_program",
            result
        )
        assert success is False

class TestAgentCommunication:
    """Test communication between agents"""
    
    @pytest.mark.asyncio
    async def test_coordinator_planner_communication(self):
        """Test communication between coordinator and planner"""
        coordinator = CoordinatorAgent()
        planner = PlannerAgent()
        
        await coordinator.initialize()
        
        # Simulate coordinator requesting plan from planner
        tasks = await planner.plan_tasks(
            intent="program_launch",
            parameters={"program_name": "notepad"}
        )
        
        assert len(tasks) > 0
        assert tasks[0]["tool"] is not None

class TestErrorHandling:
    """Test error handling in agents"""
    
    @pytest.mark.asyncio
    async def test_coordinator_error_recovery(self):
        """Test coordinator error recovery"""
        coordinator = CoordinatorAgent()
        await coordinator.initialize()
        
        # Test with invalid input
        result = await coordinator.process_user_input("")
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_tool_agent_invalid_tool(self):
        """Test tool agent with invalid tool"""
        tool_agent = ToolAgent()
        
        result = await tool_agent.execute_tool(
            tool_name="NonExistentTool",
            action="test"
        )
        assert result["success"] is False

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
