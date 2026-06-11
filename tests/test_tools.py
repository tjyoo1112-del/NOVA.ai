"""Unit tests for all tools"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.tools.browser.browser_tool import BrowserTool
from src.tools.file.file_tool import FileTool
from src.tools.system.system_tool import SystemTool
from src.tools.screen.screen_tool import ScreenTool
from src.tools.voice.voice_tool import VoiceTool
from src.tools.network.network_tool import NetworkTool

class TestBrowserTool:
    """Browser Tool unit tests"""
    
    @pytest.fixture
    async def browser_tool(self):
        """Setup browser tool"""
        tool = BrowserTool()
        yield tool
        # Cleanup
        await tool.close()
    
    @pytest.mark.asyncio
    async def test_initialize(self, browser_tool):
        """Test browser initialization"""
        result = await browser_tool.initialize()
        assert result is True
        assert browser_tool.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_navigate(self, browser_tool):
        """Test web page navigation"""
        await browser_tool.initialize()
        result = await browser_tool.execute(
            action="navigate",
            url="https://www.google.com"
        )
        assert result["success"] is True
        assert "google" in browser_tool.current_url.lower()
    
    @pytest.mark.asyncio
    async def test_navigate_invalid_url(self, browser_tool):
        """Test navigation with invalid URL"""
        await browser_tool.initialize()
        result = await browser_tool.execute(
            action="navigate",
            url="https://this-domain-does-not-exist-12345.com"
        )
        assert result["success"] is False
    
    @pytest.mark.asyncio
    async def test_screenshot(self, browser_tool):
        """Test screenshot capture"""
        await browser_tool.initialize()
        await browser_tool.execute(
            action="navigate",
            url="https://www.google.com"
        )
        result = await browser_tool.execute(action="screenshot")
        assert result["success"] is True
        assert "path" in result

class TestFileTool:
    """File Tool unit tests"""
    
    @pytest.fixture
    def file_tool(self):
        """Setup file tool"""
        return FileTool()
    
    @pytest.mark.asyncio
    async def test_create_file(self, file_tool, tmp_path):
        """Test file creation"""
        test_file = tmp_path / "test.txt"
        result = await file_tool.execute(
            action="create",
            path=str(test_file)
        )
        assert result["success"] is True
        assert test_file.exists()
    
    @pytest.mark.asyncio
    async def test_write_file(self, file_tool, tmp_path):
        """Test file writing"""
        test_file = tmp_path / "test.txt"
        content = "Hello, NOVA!"
        result = await file_tool.execute(
            action="write",
            path=str(test_file),
            content=content
        )
        assert result["success"] is True
        assert test_file.read_text() == content
    
    @pytest.mark.asyncio
    async def test_read_file(self, file_tool, tmp_path):
        """Test file reading"""
        test_file = tmp_path / "test.txt"
        content = "Test content"
        test_file.write_text(content)
        
        result = await file_tool.execute(
            action="read",
            path=str(test_file)
        )
        assert result["success"] is True
        assert result["content"] == content
    
    @pytest.mark.asyncio
    async def test_search_files(self, file_tool, tmp_path):
        """Test file search"""
        # Create test files
        (tmp_path / "test1.pdf").touch()
        (tmp_path / "test2.pdf").touch()
        (tmp_path / "test3.txt").touch()
        
        result = await file_tool.execute(
            action="search",
            query="*.pdf",
            path=str(tmp_path)
        )
        assert result["success"] is True
        assert result["count"] >= 2

class TestSystemTool:
    """System Tool unit tests"""
    
    @pytest.fixture
    def system_tool(self):
        """Setup system tool"""
        return SystemTool()
    
    @pytest.mark.asyncio
    async def test_list_programs(self, system_tool):
        """Test listing running programs"""
        result = await system_tool.execute(action="list_programs")
        assert result["success"] is True
        assert "programs" in result
        assert len(result["programs"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_process_info(self, system_tool):
        """Test getting process information"""
        result = await system_tool.execute(
            action="get_process_info",
            process_name="python"
        )
        # Process may or may not be running
        assert "success" in result

class TestScreenTool:
    """Screen Tool unit tests"""
    
    @pytest.fixture
    def screen_tool(self):
        """Setup screen tool"""
        return ScreenTool()
    
    @pytest.mark.asyncio
    async def test_screenshot(self, screen_tool):
        """Test screenshot capture"""
        result = await screen_tool.execute(action="screenshot")
        assert result["success"] is True
        assert "path" in result
        assert "width" in result
        assert "height" in result
    
    @pytest.mark.asyncio
    async def test_read_text(self, screen_tool):
        """Test text reading from screen"""
        # First take screenshot
        await screen_tool.execute(action="screenshot")
        
        # Then read text
        result = await screen_tool.execute(action="read_text")
        assert result["success"] is True
        assert "text" in result

class TestNetworkTool:
    """Network Tool unit tests"""
    
    @pytest.fixture
    def network_tool(self):
        """Setup network tool"""
        return NetworkTool()
    
    @pytest.mark.asyncio
    async def test_check_connection(self, network_tool):
        """Test internet connection check"""
        result = await network_tool.execute(action="check_connection")
        assert "success" in result
        assert "connected" in result
    
    @pytest.mark.asyncio
    async def test_http_get(self, network_tool):
        """Test HTTP GET request"""
        result = await network_tool.execute(
            action="http_get",
            url="https://www.google.com"
        )
        assert result["success"] is True
        assert result["status_code"] == 200

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
