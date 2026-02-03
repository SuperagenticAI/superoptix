"""
SuperOptiX Tool Factory
=======================

Factory functions for creating DSPy-compatible Tool objects from SuperOptiX tool classes.
"""

from typing import Callable, Dict, List

from dspy.adapters.types.tool import Tool

from ..categories.core import (
    CalculatorTool,
    CodeFormatterTool,
    DataProcessorTool,
    DateTimeTool,
    FileReaderTool,
    JSONProcessorTool,
    TextAnalyzerTool,
    WebSearchTool,
)
from ..categories.development import (
    APITesterTool,
    CodeReviewerTool,
    DatabaseQueryTool,
    DependencyAnalyzerTool,
    DockerHelperTool,
    GitTool,
    TestCoverageTool,
    VersionCheckerTool,
)


# Core Tools Factory Functions
def create_web_search_tool(engine: str = "duckduckgo", max_results: int = 5) -> Tool:
    """Create a web search tool."""
    tool_instance = WebSearchTool(engine=engine, max_results=max_results)

    return Tool(
        func=tool_instance.search,
        name="web_search",
        desc="Search the web for information using various search engines.",
    )


def create_calculator_tool(precision: int = 10) -> Tool:
    """Create a mathematical calculator tool."""
    tool_instance = CalculatorTool(precision=precision)

    return Tool(
        func=tool_instance.calculate,
        name="calculator",
        desc="Perform safe mathematical calculations and expressions.",
    )


def create_file_reader_tool(
    allowed_extensions: List[str] = None, max_file_size_mb: int = 10
) -> Tool:
    """Create a file reader tool."""
    tool_instance = FileReaderTool(
        allowed_extensions=allowed_extensions, max_file_size_mb=max_file_size_mb
    )

    return Tool(
        func=tool_instance.read_file,
        name="file_reader",
        desc="Read and process text files with safety restrictions.",
    )


def create_datetime_tool() -> Tool:
    """Create a date/time utility tool."""
    tool_instance = DateTimeTool()

    # Create a combined function that supports both operations
    def datetime_operations(operation: str = "current_time", **kwargs) -> str:
        if operation == "current_time":
            format_string = kwargs.get("format_string", "%Y-%m-%d %H:%M:%S")
            return tool_instance.get_current_time(format_string)
        elif operation == "format_date":
            date_string = kwargs.get("date_string", "")
            input_format = kwargs.get("input_format", "")
            output_format = kwargs.get("output_format", "")
            return tool_instance.format_date(date_string, input_format, output_format)
        else:
            return "❌ Invalid operation. Use 'current_time' or 'format_date'"

    return Tool(
        func=datetime_operations,
        name="datetime",
        desc="Get current time and format dates between different formats.",
    )


def create_text_analyzer_tool() -> Tool:
    """Create a text analysis tool."""
    tool_instance = TextAnalyzerTool()

    return Tool(
        func=tool_instance.analyze_text,
        name="text_analyzer",
        desc="Analyze text for statistics, readability, and basic metrics.",
    )


def create_json_processor_tool() -> Tool:
    """Create a JSON processing tool."""
    tool_instance = JSONProcessorTool()

    # Create a combined function that supports both operations
    def json_operations(
        operation: str = "parse", json_string: str = "", **kwargs
    ) -> str:
        if operation == "parse":
            return tool_instance.parse_json(json_string)
        elif operation == "extract":
            field_path = kwargs.get("field_path", "")
            return tool_instance.extract_json_field(json_string, field_path)
        else:
            return "❌ Invalid operation. Use 'parse' or 'extract'"

    return Tool(
        func=json_operations,
        name="json_processor",
        desc="Parse JSON and extract specific fields using dot notation.",
    )


def create_code_formatter_tool() -> Tool:
    """Create a code formatting tool."""
    tool_instance = CodeFormatterTool()

    return Tool(
        func=tool_instance.format_code,
        name="code_formatter",
        desc="Format code with basic syntax highlighting and structure.",
    )


def create_data_processor_tool() -> Tool:
    """Create a data processing tool."""
    tool_instance = DataProcessorTool()

    return Tool(
        func=tool_instance.process_csv_data,
        name="data_processor",
        desc="Process and analyze CSV data with various operations.",
    )


# Development Tools Factory Functions
def create_git_tool() -> Tool:
    """Create a Git analysis tool."""
    tool_instance = GitTool()

    return Tool(
        func=tool_instance.analyze_commit_message,
        name="git_analyzer",
        desc="Analyze Git commit messages for best practices and formatting.",
    )


def create_api_tester_tool() -> Tool:
    """Create an API testing tool."""
    tool_instance = APITesterTool()

    return Tool(
        func=tool_instance.validate_api_response,
        name="api_tester",
        desc="Validate and analyze API responses for structure and content.",
    )


def create_database_query_tool() -> Tool:
    """Create a database query validation tool."""
    tool_instance = DatabaseQueryTool()

    return Tool(
        func=tool_instance.validate_sql_query,
        name="database_query",
        desc="Validate SQL queries for syntax and security issues.",
    )


def create_version_checker_tool() -> Tool:
    """Create a version comparison tool."""
    tool_instance = VersionCheckerTool()

    return Tool(
        func=tool_instance.compare_versions,
        name="version_checker",
        desc="Compare semantic versions and determine relationships.",
    )


def create_dependency_analyzer_tool() -> Tool:
    """Create a dependency analysis tool."""
    tool_instance = DependencyAnalyzerTool()

    return Tool(
        func=tool_instance.analyze_dependencies,
        name="dependency_analyzer",
        desc="Analyze package dependencies for security and updates.",
    )


def create_code_reviewer_tool() -> Tool:
    """Create a code review tool."""
    tool_instance = CodeReviewerTool()

    return Tool(
        func=tool_instance.review_code,
        name="code_reviewer",
        desc="Perform automated code review and quality analysis.",
    )


def create_test_coverage_tool() -> Tool:
    """Create a test coverage analysis tool."""
    tool_instance = TestCoverageTool()

    return Tool(
        func=tool_instance.analyze_coverage,
        name="test_coverage",
        desc="Analyze test coverage reports and provide recommendations.",
    )


def create_docker_helper_tool() -> Tool:
    """Create a Docker helper tool."""
    tool_instance = DockerHelperTool()

    return Tool(
        func=tool_instance.validate_dockerfile,
        name="docker_helper",
        desc="Validate Dockerfiles for best practices and optimization.",
    )


# Registry of all factory functions
TOOL_FACTORIES = {
    # Core tools
    "web_search": create_web_search_tool,
    "calculator": create_calculator_tool,
    "file_reader": create_file_reader_tool,
    "datetime": create_datetime_tool,
    "text_analyzer": create_text_analyzer_tool,
    "json_processor": create_json_processor_tool,
    "code_formatter": create_code_formatter_tool,
    "data_processor": create_data_processor_tool,
    # Development tools
    "git_analyzer": create_git_tool,
    "api_tester": create_api_tester_tool,
    "database_query": create_database_query_tool,
    "version_checker": create_version_checker_tool,
    "dependency_analyzer": create_dependency_analyzer_tool,
    "code_reviewer": create_code_reviewer_tool,
    "test_coverage": create_test_coverage_tool,
    "docker_helper": create_docker_helper_tool,
}


def get_all_tool_factories() -> Dict[str, Callable]:
    """Get all available tool factory functions."""
    return TOOL_FACTORIES.copy()


def create_tool_by_name(tool_name: str, **config) -> Tool:
    """Create a tool by name with optional configuration."""
    if tool_name not in TOOL_FACTORIES:
        available_tools = list(TOOL_FACTORIES.keys())
        raise ValueError(
            f"Unknown tool '{tool_name}'. Available tools: {available_tools}"
        )

    factory_func = TOOL_FACTORIES[tool_name]

    try:
        return factory_func(**config)
    except TypeError:
        # If configuration parameters don't match, try without config
        try:
            return factory_func()
        except Exception as inner_e:
            raise ValueError(f"Failed to create tool '{tool_name}': {str(inner_e)}")


def get_default_tools() -> List[Tool]:
    """Get a list of default essential tools."""
    default_tool_names = [
        "web_search",
        "calculator",
        "file_reader",
        "datetime",
        "text_analyzer",
        "json_processor",
    ]

    return [create_tool_by_name(name) for name in default_tool_names]


def get_available_tools() -> List[str]:
    """Get list of all available tool names."""
    return list(TOOL_FACTORIES.keys())


# Export main functions
__all__ = [
    "create_web_search_tool",
    "create_calculator_tool",
    "create_file_reader_tool",
    "create_datetime_tool",
    "create_text_analyzer_tool",
    "create_json_processor_tool",
    "create_code_formatter_tool",
    "create_data_processor_tool",
    "create_git_tool",
    "create_api_tester_tool",
    "create_database_query_tool",
    "create_version_checker_tool",
    "create_dependency_analyzer_tool",
    "create_code_reviewer_tool",
    "create_test_coverage_tool",
    "create_docker_helper_tool",
    "get_all_tool_factories",
    "create_tool_by_name",
    "get_default_tools",
    "get_available_tools",
]
