"""
StackOne HRIS Benchmark
=======================

Benchmark suite for Human Resource Information System (HRIS) tasks.
"""

from typing import Any, Dict, List
from .base import StackOneBenchmark

class HRISBenchmark(StackOneBenchmark):
    """Benchmark for common HRIS operations."""

    def __init__(self):
        super().__init__(
            name="hris_standard",
            description="Standard benchmark for HRIS employee retrieval and management tasks."
        )

    def get_tools(self) -> List[str]:
        return [
            "hris_get_employee",
            "hris_list_employees",
            "hris_get_employment", 
            "hris_list_employments"
        ]

    def get_dataset(self) -> List[Dict[str, Any]]:
        return [
            {
                "input": "Who is the employee with ID 12345?",
                "expected_tool": "hris_get_employee",
                "expected_args": {"id": "12345"}
            },
            {
                "input": "Get employment details for John Doe (ID: emp_999)",
                "expected_tool": "hris_get_employment",
                "expected_args": {"id": "emp_999"}
            },
            {
                "input": "List all active employees created after 2023-01-01",
                "expected_tool": "hris_list_employees",
                "expected_args": {"created_after": "2023-01-01"}
            }
        ]
