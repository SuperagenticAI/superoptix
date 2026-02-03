"""
StackOne Benchmark Base Module
==============================

Base classes for StackOne-specific benchmarks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class StackOneBenchmark(ABC):
    """Base class for StackOne benchmarks."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def get_tools(self) -> List[str]:
        """Return list of StackOne tool names required for this benchmark."""
        pass

    @abstractmethod
    def get_dataset(self) -> List[Dict[str, Any]]:
        """
        Return the evaluation dataset.
        
        Format:
        [
            {
                "input": "User query...",
                "expected_tool": "tool_name",
                "expected_args": {"arg1": "value"}
            },
            ...
        ]
        """
        pass

    def evaluate_tool_call(self, tool_name: str, tool_args: Dict[str, Any], expected: Dict[str, Any]) -> float:
        """
        Evaluate if a tool call matches expectations.
        
        Returns score 0.0 to 1.0.
        """
        if tool_name != expected["expected_tool"]:
            return 0.0
        
        # Check arguments (simple exact match for now, can be extended)
        expected_args = expected.get("expected_args", {})
        for k, v in expected_args.items():
            if tool_args.get(k) != v:
                return 0.5 # Correct tool, wrong args
        
        return 1.0
