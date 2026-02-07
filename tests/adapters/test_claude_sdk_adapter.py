"""
Tests for Claude Agent SDK Adapter
==================================

Tests the ClaudeAgentSDKFrameworkAdapter and StackOneBridge Claude SDK integration.
"""

import pytest
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


# Mock StackOne classes
class MockStackOneParameters:
    """Mock StackOne tool parameters."""

    def __init__(self, schema: Dict[str, Any]):
        self._schema = schema

    def model_dump(self) -> Dict[str, Any]:
        return self._schema

    @property
    def properties(self):
        mock = MagicMock()
        mock.keys.return_value = self._schema.get("properties", {}).keys()
        return mock


class MockStackOneTool:
    """Mock StackOne tool for testing."""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = MockStackOneParameters(parameters)

    def execute(self, args: Dict[str, Any]) -> str:
        return f"Executed {self.name} with {args}"

    def to_openai_function(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description}

    def to_langchain(self) -> Any:
        return MagicMock(name=self.name)


class MockStackOneTools:
    """Mock StackOne Tools collection."""

    def __init__(self, tools: List[MockStackOneTool]):
        self._tools = tools

    def to_list(self) -> List[MockStackOneTool]:
        return self._tools


# Test fixtures
@pytest.fixture
def sample_tool_schema():
    """Sample tool parameter schema."""
    return {
        "type": "object",
        "properties": {
            "employee_id": {"type": "string", "description": "The employee ID"},
            "include_details": {"type": "boolean", "description": "Include full details"},
        },
        "required": ["employee_id"],
    }


@pytest.fixture
def sample_stackone_tool(sample_tool_schema):
    """Create a sample StackOne tool."""
    return MockStackOneTool(
        name="hris_get_employee",
        description="Get employee information from HRIS system",
        parameters=sample_tool_schema,
    )


@pytest.fixture
def sample_stackone_tools(sample_stackone_tool):
    """Create sample StackOne tools collection."""
    return [sample_stackone_tool]


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
        from superoptix.adapters.framework_registry import ClaudeAgentSDKFrameworkAdapter

        assert ClaudeAgentSDKFrameworkAdapter.framework_name == "claude-sdk"

    def test_requires_async(self):
        """Test requires_async is True."""
        from superoptix.adapters.framework_registry import ClaudeAgentSDKFrameworkAdapter

        assert ClaudeAgentSDKFrameworkAdapter.requires_async == True

    def test_get_optimizable_variable_with_instructions(self, sample_playbook):
        """Test extraction of instructions as optimizable variable."""
        from superoptix.adapters.framework_registry import ClaudeAgentSDKFrameworkAdapter

        result = ClaudeAgentSDKFrameworkAdapter.get_optimizable_variable(sample_playbook)
        assert result == "Be helpful and concise"

    def test_get_optimizable_variable_builds_from_parts(self):
        """Test building optimizable variable from role/goal/backstory."""
        from superoptix.adapters.framework_registry import ClaudeAgentSDKFrameworkAdapter

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
        from superoptix.adapters.framework_registry import ClaudeAgentSDKFrameworkAdapter

        playbook = {"spec": {"persona": {}}}

        result = ClaudeAgentSDKFrameworkAdapter.get_optimizable_variable(playbook)
        assert result == "You are a helpful AI assistant."

    def test_registered_in_framework_registry(self):
        """Test adapter is registered in FrameworkRegistry."""
        from superoptix.adapters.framework_registry import FrameworkRegistry

        assert "claude-sdk" in FrameworkRegistry.list_frameworks()
        adapter = FrameworkRegistry.get_adapter("claude-sdk")
        assert adapter.framework_name == "claude-sdk"


class TestStackOneBridgeClaudeSDK:
    """Tests for StackOneBridge Claude SDK conversion."""

    def test_to_claude_sdk_not_installed(self, sample_stackone_tools):
        """Test to_claude_sdk raises ImportError when SDK not installed."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)

            with pytest.raises(ImportError) as exc_info:
                bridge.to_claude_sdk()

            assert "claude-agent-sdk" in str(exc_info.value)

    def test_to_claude_sdk_creates_mcp_server(self, sample_stackone_tools):
        """Test to_claude_sdk creates MCP server and returns tool names."""
        mock_mcp_server = MagicMock()

        def mock_create_server(name, version, tools):
            return MockMcpServerConfig(name, version, tools)

        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ), patch.dict(
            "sys.modules",
            {
                "claude_agent_sdk": MagicMock(
                    SdkMcpTool=MockSdkMcpTool,
                    create_sdk_mcp_server=mock_create_server,
                ),
            },
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            mcp_server, tool_names = bridge.to_claude_sdk()

            # Verify tool names follow convention
            assert len(tool_names) == 1
            assert tool_names[0] == "mcp__stackone__hris_get_employee"

            # Verify MCP server was created
            assert mcp_server.name == "stackone"
            assert mcp_server.version == "1.0.0"
            assert len(mcp_server.tools) == 1

    def test_convert_to_claude_sdk_schema(self, sample_stackone_tools, sample_tool_schema):
        """Test schema conversion for Claude SDK."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            schema = bridge._convert_to_claude_sdk_schema(sample_tool_schema)

            # Check types are converted correctly
            assert schema["employee_id"] == str
            assert schema["include_details"] == bool

    def test_to_discovery_tools_claude_sdk_framework(self, sample_stackone_tools):
        """Test to_discovery_tools supports claude_sdk framework."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)

            # Mock the utility tools imports
            with patch(
                "stackone_ai.models.Tools"
            ), patch(
                "stackone_ai.utility_tools.ToolIndex"
            ), patch(
                "stackone_ai.utility_tools.create_tool_search"
            ) as mock_search, patch(
                "stackone_ai.utility_tools.create_tool_execute"
            ) as mock_execute, patch.object(
                StackOneBridge, "to_claude_sdk"
            ) as mock_to_claude:
                mock_search.return_value = MagicMock()
                mock_execute.return_value = MagicMock()
                mock_to_claude.return_value = (MagicMock(), ["tool1", "tool2"])

                result = bridge.to_discovery_tools(framework="claude_sdk")

                # Verify to_claude_sdk was called
                mock_to_claude.assert_called_once()


class TestClaudeSDKToolHandler:
    """Tests for Claude SDK tool handler generation."""

    @pytest.mark.asyncio
    async def test_handler_returns_correct_format(self, sample_stackone_tools):
        """Test that generated handlers return correct Claude SDK format."""
        mock_mcp_server = MagicMock()
        captured_tools = []

        def mock_create_server(name, version, tools):
            captured_tools.extend(tools)
            return MockMcpServerConfig(name, version, tools)

        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ), patch.dict(
            "sys.modules",
            {
                "claude_agent_sdk": MagicMock(
                    SdkMcpTool=MockSdkMcpTool,
                    create_sdk_mcp_server=mock_create_server,
                ),
            },
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            bridge.to_claude_sdk()

            # Get the created tool's handler
            assert len(captured_tools) == 1
            tool = captured_tools[0]

            # Execute the handler
            result = await tool.handler({"employee_id": "123"})

            # Verify response format
            assert "content" in result
            assert isinstance(result["content"], list)
            assert result["content"][0]["type"] == "text"
            assert "hris_get_employee" in result["content"][0]["text"]


class TestClaudeSDKTemplate:
    """Tests for Claude SDK template compilation."""

    def test_template_exists(self):
        """Test that the Claude SDK template file exists."""
        from pathlib import Path

        template_path = Path(__file__).parent.parent.parent / "superoptix" / "templates" / "pipeline" / "claude_sdk_pipeline.py.jinja2"
        assert template_path.exists(), f"Template not found at {template_path}"

    def test_compile_from_playbook(self, sample_playbook, tmp_path):
        """Test template compilation from playbook."""
        from superoptix.adapters.framework_registry import ClaudeAgentSDKFrameworkAdapter

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
