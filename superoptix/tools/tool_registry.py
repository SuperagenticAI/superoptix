"""
SuperOptiX Tool Registry
========================

Centralized registry for all SuperOptiX tools with simplified management.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from dspy.adapters.types.tool import Tool

from .factories.tool_factory import create_tool_by_name, get_all_tool_factories

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a tool in the registry."""

    name: str
    category: str
    description: str
    factory_func: Callable
    tags: List[str] = None
    industry: str = "General"

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ToolRegistry:
    """
    Centralized registry for SuperOptiX tools.
    Manages tool discovery, creation, and metadata.
    """

    def __init__(self):
        self._registry: Dict[str, ToolMetadata] = {}
        self._categories: Dict[str, List[str]] = {}
        self._industries: Dict[str, List[str]] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        """Initialize the registry with available tools."""
        try:
            # Get factory functions from the modular structure
            factories = get_all_tool_factories()

            # Tool definitions with metadata
            tool_definitions = {
                # Core Tools
                "web_search": {
                    "category": "Core",
                    "description": "Search the web for information using various search engines",
                    "tags": ["search", "web", "research"],
                    "industry": "General",
                },
                "calculator": {
                    "category": "Core",
                    "description": "Perform safe mathematical calculations and expressions",
                    "tags": ["math", "calculation", "arithmetic"],
                    "industry": "General",
                },
                "file_reader": {
                    "category": "Core",
                    "description": "Read and process text files with safety restrictions",
                    "tags": ["file", "text", "io"],
                    "industry": "General",
                },
                "datetime": {
                    "category": "Core",
                    "description": "Get current time and format dates between different formats",
                    "tags": ["time", "date", "formatting"],
                    "industry": "General",
                },
                "text_analyzer": {
                    "category": "Core",
                    "description": "Analyze text for statistics, readability, and basic metrics",
                    "tags": ["text", "analysis", "nlp"],
                    "industry": "General",
                },
                "json_processor": {
                    "category": "Core",
                    "description": "Parse JSON and extract specific fields using dot notation",
                    "tags": ["json", "parsing", "data"],
                    "industry": "General",
                },
                "code_formatter": {
                    "category": "Development",
                    "description": "Format code with basic syntax highlighting and structure",
                    "tags": ["code", "formatting", "development"],
                    "industry": "Technology",
                },
                "data_processor": {
                    "category": "Data",
                    "description": "Process and analyze CSV data with various operations",
                    "tags": ["data", "csv", "analysis"],
                    "industry": "General",
                },
                # Development Tools
                "git_analyzer": {
                    "category": "Development",
                    "description": "Analyze Git commit messages for best practices and formatting",
                    "tags": ["git", "version-control", "commits"],
                    "industry": "Technology",
                },
                "api_tester": {
                    "category": "Development",
                    "description": "Validate and analyze API responses for structure and content",
                    "tags": ["api", "testing", "validation"],
                    "industry": "Technology",
                },
                "database_query": {
                    "category": "Development",
                    "description": "Validate SQL queries for syntax and security issues",
                    "tags": ["sql", "database", "security"],
                    "industry": "Technology",
                },
                "version_checker": {
                    "category": "Development",
                    "description": "Compare semantic versions and determine relationships",
                    "tags": ["versioning", "semver", "comparison"],
                    "industry": "Technology",
                },
                "dependency_analyzer": {
                    "category": "Development",
                    "description": "Analyze package dependencies for security and updates",
                    "tags": ["dependencies", "security", "packages"],
                    "industry": "Technology",
                },
                "code_reviewer": {
                    "category": "Development",
                    "description": "Perform automated code review and quality analysis",
                    "tags": ["code-review", "quality", "analysis"],
                    "industry": "Technology",
                },
                "test_coverage": {
                    "category": "Development",
                    "description": "Analyze test coverage reports and provide recommendations",
                    "tags": ["testing", "coverage", "quality"],
                    "industry": "Technology",
                },
                "docker_helper": {
                    "category": "Development",
                    "description": "Validate Dockerfiles for best practices and optimization",
                    "tags": ["docker", "containers", "devops"],
                    "industry": "Technology",
                },
            }

            # Register tools with metadata
            for tool_name, factory_func in factories.items():
                metadata = tool_definitions.get(
                    tool_name,
                    {
                        "category": "Miscellaneous",
                        "description": f"Tool: {tool_name}",
                        "tags": [],
                        "industry": "General",
                    },
                )

                tool_meta = ToolMetadata(
                    name=tool_name,
                    category=metadata["category"],
                    description=metadata["description"],
                    factory_func=factory_func,
                    tags=metadata["tags"],
                    industry=metadata["industry"],
                )

                self.register_tool(tool_meta)

            logger.info(f"Initialized tool registry with {len(self._registry)} tools")

        except Exception as e:
            logger.error(f"Failed to initialize tool registry: {e}")
            raise

    def register_tool(self, tool_metadata: ToolMetadata) -> None:
        """Register a tool in the registry."""
        self._registry[tool_metadata.name] = tool_metadata

        # Update category index
        if tool_metadata.category not in self._categories:
            self._categories[tool_metadata.category] = []
        self._categories[tool_metadata.category].append(tool_metadata.name)

        # Update industry index
        if tool_metadata.industry not in self._industries:
            self._industries[tool_metadata.industry] = []
        self._industries[tool_metadata.industry].append(tool_metadata.name)

    def get_tool(self, tool_name: str, **config) -> Optional[Tool]:
        """Create and return a tool instance by name."""
        if tool_name not in self._registry:
            logger.warning(f"Tool '{tool_name}' not found in registry")
            return None

        try:
            return create_tool_by_name(tool_name, **config)
        except Exception as e:
            logger.error(f"Failed to create tool '{tool_name}': {e}")
            return None

    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self._registry.keys())

    def list_categories(self) -> List[str]:
        """List all available categories."""
        return list(self._categories.keys())

    def list_industries(self) -> List[str]:
        """List all available industries."""
        return list(self._industries.keys())

    def get_tools_by_category(self, category: str) -> List[str]:
        """Get all tools in a specific category."""
        return self._categories.get(category, [])

    def get_tools_by_industry(self, industry: str) -> List[str]:
        """Get all tools for a specific industry."""
        return self._industries.get(industry, [])

    def search_tools(self, query: str) -> List[str]:
        """Search tools by name, description, or tags."""
        query = query.lower()
        results = []

        for tool_name, metadata in self._registry.items():
            # Search in name
            if query in tool_name.lower():
                results.append(tool_name)
                continue

            # Search in description
            if query in metadata.description.lower():
                results.append(tool_name)
                continue

            # Search in tags
            if any(query in tag.lower() for tag in metadata.tags):
                results.append(tool_name)
                continue

        return results

    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self._registry.get(tool_name)

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the tool registry."""
        return {
            "total_tools": len(self._registry),
            "categories": len(self._categories),
            "industries": len(self._industries),
            "tools_by_category": {
                cat: len(tools) for cat, tools in self._categories.items()
            },
            "tools_by_industry": {
                ind: len(tools) for ind, tools in self._industries.items()
            },
        }

    def create_tool_collection(
        self, tool_names: List[str], **shared_config
    ) -> List[Tool]:
        """Create multiple tools at once."""
        tools = []
        for tool_name in tool_names:
            tool = self.get_tool(tool_name, **shared_config)
            if tool:
                tools.append(tool)
        return tools


# Global registry instance
_global_registry = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


# Convenience functions
def get_tool(tool_name: str, **config) -> Optional[Tool]:
    """Get a tool from the global registry."""
    return get_tool_registry().get_tool(tool_name, **config)


def list_available_tools() -> List[str]:
    """List all available tools."""
    return get_tool_registry().list_tools()


def search_tools(query: str) -> List[str]:
    """Search for tools by query."""
    return get_tool_registry().search_tools(query)


def get_tools_by_category(category: str) -> List[str]:
    """Get tools by category."""
    return get_tool_registry().get_tools_by_category(category)


def get_default_tool_collection() -> List[Tool]:
    """Get a collection of default/essential tools."""
    registry = get_tool_registry()
    default_tools = [
        "web_search",
        "calculator",
        "file_reader",
        "datetime",
        "text_analyzer",
        "json_processor",
    ]
    return registry.create_tool_collection(default_tools)


# Export key components
__all__ = [
    "ToolRegistry",
    "ToolMetadata",
    "get_tool_registry",
    "get_tool",
    "list_available_tools",
    "search_tools",
    "get_tools_by_category",
    "get_default_tool_collection",
]
