"""Tests for coordinator agent"""

import pytest
from src.core.agent.coordinator import CoordinatorAgent

@pytest.fixture
async def coordinator():
    """Fixture for coordinator agent"""
    agent = CoordinatorAgent()
    await agent.initialize()
    yield agent
    await agent.shutdown()

@pytest.mark.asyncio
async def test_coordinator_initialization(coordinator):
    """Test coordinator initialization"""
    assert coordinator.name == "Coordinator"
    assert coordinator.is_running == False

@pytest.mark.asyncio
async def test_coordinator_startup(coordinator):
    """Test coordinator startup"""
    # Note: This is a simplified test
    pass
