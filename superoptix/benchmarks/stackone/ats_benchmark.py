"""
StackOne ATS Benchmark
======================

Benchmark suite for Applicant Tracking System (ATS) tasks.
"""

from typing import Any, Dict, List
from .base import StackOneBenchmark


class ATSBenchmark(StackOneBenchmark):
    """Benchmark for common ATS operations."""

    def __init__(self):
        super().__init__(
            name="ats_standard",
            description="Standard benchmark for ATS job, candidate, and application management.",
        )

    def get_tools(self) -> List[str]:
        return [
            "ats_list_jobs",
            "ats_get_job",
            "ats_list_candidates",
            "ats_get_candidate",
            "ats_list_applications",
        ]

    def get_dataset(self) -> List[Dict[str, Any]]:
        return [
            {
                "input": "List all open engineering jobs in London",
                "expected_tool": "ats_list_jobs",
                "expected_args": {
                    "location": "London",
                    "department": "Engineering",
                    "status": "open",
                },
            },
            {
                "input": "Get details for candidate Sarah Smith (ID: cand_456)",
                "expected_tool": "ats_get_candidate",
                "expected_args": {"id": "cand_456"},
            },
            {
                "input": "Find all applications for the Senior Developer role (job_id: 789)",
                "expected_tool": "ats_list_applications",
                "expected_args": {"job_id": "789"},
            },
            {
                "input": "Show me the job description for job ID 101",
                "expected_tool": "ats_get_job",
                "expected_args": {"id": "101"},
            },
        ]
