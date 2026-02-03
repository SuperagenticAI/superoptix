"""
SuperOptiX Tools Base Module
============================

Base classes and common functionality for all SuperOptiX tools.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all SuperOptiX tools."""

    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category
        self.version = "1.0.0"

    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        """Execute the tool's main functionality."""
        pass

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        return True

    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
        }


class ToolError(Exception):
    """Base exception for tool-related errors."""

    pass


class ToolValidationError(ToolError):
    """Exception raised when tool input validation fails."""

    pass


class ToolExecutionError(ToolError):
    """Exception raised when tool execution fails."""

    pass


def safe_execute(func):
    """Decorator for safe tool execution with error handling."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return f"❌ Error: {str(e)}"

    return wrapper


def validate_required_params(required_params: List[str]):
    """Decorator to validate required parameters."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for param in required_params:
                if param not in kwargs or kwargs[param] is None:
                    raise ToolValidationError(
                        f"Required parameter '{param}' is missing"
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator
