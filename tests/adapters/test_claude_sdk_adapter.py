"""
Tests for Claude Agent SDK Adapter
==================================

Tests the ClaudeAgentSDKFrameworkAdapter.
"""

import pytest
import types
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Any, Dict, List


# Mock Claude Agent SDK classes for testing without actual dependencies
class MockSdkMcpTool:
    """Mock SdkMcpTool."""

    def __init__(self, name: str, description: str, input_schema: Dict, handler: Any):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


class MockMcpServerConfig:
    """Mock MCP server config."""

    def __init__(self, name: str, version: str, tools: List):
        self.name = name
        self.version = version
        self.tools = tools




# Test fixtures
@pytest.fixture
def sample_tool_schema():
    """Sample tool parameter schema."""
    return {
        "type": "object",
        "properties": {
            "employee_id": {"type": "string", "description": "The employee ID"},
            "include_details": {
                "type": "boolean",
                "description": "Include full details",
            },
        },
        "required": ["employee_id"],
    }


@pytest.fixture
def sample_playbook():
    """Sample SuperSpec playbook for testing."""
    return {
        "metadata": {
            "name": "test_agent",
            "version": "1.0.0",
            "description": "Test Claude SDK agent",
        },
        "spec": {
            "persona": {
                "role": "You are a helpful assistant",
                "goal": "Help users with queries",
                "backstory": "You are an AI assistant",
                "instructions": "Be helpful and concise",
            },
            "language_model": {
                "model": "claude-sonnet-4-5",
                "provider": "anthropic",
            },
            "input_fields": [
                {"name": "query", "type": "string"},
            ],
            "output_fields": [
                {"name": "response", "type": "string"},
            ],
        },
    }


class TestClaudeAgentSDKFrameworkAdapter:
    """Tests for ClaudeAgentSDKFrameworkAdapter."""

    def test_framework_name(self):
        """Test framework name is correct."""
        from superoptix.adapters.framework_registry import (
            ClaudeAgentSDKFrameworkAdapter,
        )

        assert ClaudeAgentSDKFrameworkAdapter.framework_name == "claude-sdk"

    def test_requires_async(self):
        """Test requires_async is True."""
        from superoptix.adapters.framework_registry import (
            ClaudeAgentSDKFrameworkAdapter,
        )

        assert ClaudeAgentSDKFrameworkAdapter.requires_async == True

    def test_get_optimizable_variable_with_instructions(self, sample_playbook):
        """Test extraction of instructions as optimizable variable."""
        from superoptix.adapters.framework_registry import (
            ClaudeAgentSDKFrameworkAdapter,
        )

        result = ClaudeAgentSDKFrameworkAdapter.get_optimizable_variable(
            sample_playbook
        )
        assert result == "Be helpful and concise"

    def test_get_optimizable_variable_builds_from_parts(self):
        """Test building optimizable variable from role/goal/backstory."""
        from superoptix.adapters.framework_registry import (
            ClaudeAgentSDKFrameworkAdapter,
        )

        playbook = {
            "spec": {
                "persona": {
                    "role": "You are a helper",
                    "goal": "Assist users",
                    # No instructions field
                }
            }
        }

        result = ClaudeAgentSDKFrameworkAdapter.get_optimizable_variable(playbook)
        assert "You are a helper" in result
        assert "Assist users" in result

    def test_get_optimizable_variable_default(self):
        """Test default when no persona info."""
        from superoptix.adapters.framework_registry import (
            ClaudeAgentSDKFrameworkAdapter,
        )

        playbook = {"spec": {"persona": {}}}

        result = ClaudeAgentSDKFrameworkAdapter.get_optimizable_variable(playbook)
        assert result == "You are a helpful AI assistant."

    def test_registered_in_framework_registry(self):
        """Test adapter is registered in FrameworkRegistry."""
        from superoptix.adapters.framework_registry import FrameworkRegistry

        assert "claude-sdk" in FrameworkRegistry.list_frameworks()
        adapter = FrameworkRegistry.get_adapter("claude-sdk")
        assert adapter.framework_name == "claude-sdk"


class TestClaudeSDKTemplate:
    """Tests for Claude SDK template compilation."""

    def test_template_exists(self):
        """Test that the Claude SDK template file exists."""
        from pathlib import Path

        template_path = (
            Path(__file__).parent.parent.parent
            / "superoptix"
            / "templates"
            / "pipeline"
            / "claude_sdk_pipeline.py.jinja2"
        )
        assert template_path.exists(), f"Template not found at {template_path}"

    def test_compile_from_playbook(self, sample_playbook, tmp_path):
        """Test template compilation from playbook."""
        from superoptix.adapters.framework_registry import (
            ClaudeAgentSDKFrameworkAdapter,
        )

        output_path = tmp_path / "test_agent_claude_sdk_pipeline.py"
        result = ClaudeAgentSDKFrameworkAdapter.compile_from_playbook(
            sample_playbook, str(output_path)
        )

        # Verify file was created
        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert "TestAgentComponent" in content
        assert "BaseComponent" in content
        assert "claude_agent_sdk" in content
        assert "async def forward" in content


class TestFrameworkRegistryIntegration:
    """Integration tests for FrameworkRegistry with Claude SDK."""

    def test_compile_agent(self, sample_playbook, tmp_path):
        """Test compiling agent through FrameworkRegistry."""
        from superoptix.adapters.framework_registry import FrameworkRegistry

        output_path = tmp_path / "agent_pipeline.py"
        result = FrameworkRegistry.compile_agent(
            "claude-sdk", sample_playbook, str(output_path)
        )

        assert output_path.exists()

    def test_get_framework_info(self):
        """Test getting framework info for Claude SDK."""
        from superoptix.adapters.framework_registry import FrameworkRegistry

        info = FrameworkRegistry.get_framework_info("claude-sdk")

        assert info["name"] == "claude-sdk"
        assert info["requires_async"] == True
        assert info["implemented"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
