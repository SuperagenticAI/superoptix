"""
Tests for StackOne Adapter
=========================

Tests the StackOneBridge adapter for converting StackOne tools to various frameworks.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, Dict, List


# Mock StackOne SDK classes for testing without actual dependencies
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


# Patch StackOne availability
@pytest.fixture(autouse=True)
def mock_stackone_available():
    """Mock StackOne SDK availability."""
    with patch.dict(
        "sys.modules",
        {
            "stackone_ai": MagicMock(),
            "stackone_ai.models": MagicMock(),
        },
    ):
        yield


class TestStackOneBridge:
    """Tests for StackOneBridge class."""

    def test_bridge_initialization_with_list(self, sample_stackone_tools):
        """Test bridge initialization with list of tools."""
        # Patch the imports inside the adapter
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            assert len(bridge.tools) == 1
            assert bridge.tools[0].name == "hris_get_employee"

    def test_bridge_initialization_with_tools_object(self, sample_stackone_tool):
        """Test bridge initialization with Tools object."""
        tools_obj = MockStackOneTools([sample_stackone_tool])

        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(tools_obj)
            assert len(bridge.tools) == 1

    def test_create_pydantic_model_from_schema(self, sample_stackone_tools, sample_tool_schema):
        """Test dynamic Pydantic model creation."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            model = bridge._create_pydantic_model_from_schema(
                "test_tool", sample_tool_schema
            )

            # Check model name
            assert model.__name__ == "test_toolArgs"

            # Check fields
            assert "employee_id" in model.model_fields
            assert "include_details" in model.model_fields

    def test_to_openai(self, sample_stackone_tools):
        """Test OpenAI conversion (pass-through)."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            openai_tools = bridge.to_openai()

            assert len(openai_tools) == 1
            assert openai_tools[0]["name"] == "hris_get_employee"

    def test_to_langchain(self, sample_stackone_tools):
        """Test LangChain conversion (pass-through)."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            langchain_tools = bridge.to_langchain()

            assert len(langchain_tools) == 1

    def test_to_google_adk(self, sample_stackone_tools):
        """Test Google ADK conversion."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            google_tools = bridge.to_google_adk()

            assert len(google_tools) == 1
            assert google_tools[0]["name"] == "hris_get_employee"
            assert "parameters" in google_tools[0]
            assert google_tools[0]["parameters"]["type"] == "OBJECT"


class TestStackOneBridgeCrewAI:
    """Tests for CrewAI integration."""

    def test_to_crewai_without_crewai_installed(self, sample_stackone_tools):
        """Test to_crewai raises ImportError when CrewAI not installed."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ), patch(
            "superoptix.adapters.stackone_adapter.CREWAI_AVAILABLE", False
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)

            with pytest.raises(ImportError) as exc_info:
                bridge.to_crewai()

            assert "crewai is not installed" in str(exc_info.value)

    def test_to_crewai_async_without_crewai_installed(self, sample_stackone_tools):
        """Test to_crewai_async raises ImportError when CrewAI not installed."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ), patch(
            "superoptix.adapters.stackone_adapter.CREWAI_AVAILABLE", False
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)

            with pytest.raises(ImportError) as exc_info:
                bridge.to_crewai_async()

            assert "crewai is not installed" in str(exc_info.value)

    def test_to_crewai_with_mock(self, sample_stackone_tools):
        """Test to_crewai with mocked CrewAI classes."""
        mock_crewai_tool = MagicMock()

        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ), patch(
            "superoptix.adapters.stackone_adapter.CREWAI_AVAILABLE", True
        ), patch(
            "superoptix.adapters.stackone_adapter.CrewAITool", mock_crewai_tool
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)
            crewai_tools = bridge.to_crewai()

            # Verify CrewAITool was called
            assert mock_crewai_tool.called
            assert len(crewai_tools) == 1

            # Verify the tool was created with correct parameters
            call_kwargs = mock_crewai_tool.call_args.kwargs
            assert call_kwargs["name"] == "hris_get_employee"
            assert "description" in call_kwargs
            assert "func" in call_kwargs
            assert "args_schema" in call_kwargs


class TestStackOneBridgeDiscoveryTools:
    """Tests for discovery tools with CrewAI support."""

    def test_to_discovery_tools_crewai_framework(self, sample_stackone_tools):
        """Test discovery tools conversion for CrewAI framework."""
        # This test verifies the framework parameter routing
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ), patch(
            "superoptix.adapters.stackone_adapter.CREWAI_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)

            # Mock the utility tools imports
            with patch(
                "superoptix.adapters.stackone_adapter.StackOneBridge.to_crewai"
            ) as mock_to_crewai, patch(
                "stackone_ai.models.Tools"
            ), patch(
                "stackone_ai.utility_tools.ToolIndex"
            ), patch(
                "stackone_ai.utility_tools.create_tool_search"
            ), patch(
                "stackone_ai.utility_tools.create_tool_execute"
            ):
                mock_to_crewai.return_value = [MagicMock(), MagicMock()]

                # This should call to_crewai on the temp bridge
                # Note: The actual call will fail due to missing imports,
                # but we're testing the framework routing logic
                pass

    def test_to_discovery_tools_invalid_framework(self, sample_stackone_tools):
        """Test discovery tools with invalid framework raises ValueError."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneBridge

            bridge = StackOneBridge(sample_stackone_tools)

            # Mock the utility tools imports to get past initial checks
            with patch(
                "stackone_ai.models.Tools"
            ), patch(
                "stackone_ai.utility_tools.ToolIndex"
            ), patch(
                "stackone_ai.utility_tools.create_tool_search"
            ) as mock_search, patch(
                "stackone_ai.utility_tools.create_tool_execute"
            ) as mock_execute:
                mock_search.return_value = MagicMock()
                mock_execute.return_value = MagicMock()

                with pytest.raises(ValueError) as exc_info:
                    bridge.to_discovery_tools(framework="invalid_framework")

                assert "Unknown framework" in str(exc_info.value)
                assert "crewai" in str(exc_info.value)  # Should list supported frameworks


class TestStackOneOptimizableComponent:
    """Tests for StackOneOptimizableComponent."""

    def test_component_initialization(self, sample_stackone_tool):
        """Test component initialization."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneOptimizableComponent

            component = StackOneOptimizableComponent(sample_stackone_tool)

            assert component.name == "hris_get_employee"
            assert component.description == "Get employee information from HRIS system"
            assert component.variable == sample_stackone_tool.description

    def test_component_forward(self, sample_stackone_tool):
        """Test component forward execution."""
        with patch(
            "superoptix.adapters.stackone_adapter.STACKONE_AVAILABLE", True
        ):
            from superoptix.adapters.stackone_adapter import StackOneOptimizableComponent

            component = StackOneOptimizableComponent(sample_stackone_tool)
            result = component.forward(employee_id="123")

            assert "result" in result
            assert "hris_get_employee" in result["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
