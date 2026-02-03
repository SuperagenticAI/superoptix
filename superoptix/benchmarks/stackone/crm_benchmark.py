"""
StackOne CRM Benchmark
======================

Benchmark suite for Customer Relationship Management (CRM) tasks.
"""

from typing import Any, Dict, List
from .base import StackOneBenchmark

class CRMBenchmark(StackOneBenchmark):
    """Benchmark for common CRM operations."""

    def __init__(self):
        super().__init__(
            name="crm_standard",
            description="Standard benchmark for CRM account, contact, and opportunity management."
        )

    def get_tools(self) -> List[str]:
        return [
            "crm_list_accounts",
            "crm_get_account",
            "crm_list_contacts",
            "crm_get_contact",
            "crm_list_opportunities"
        ]

    def get_dataset(self) -> List[Dict[str, Any]]:
        return [
            {
                "input": "Find the account details for 'Acme Corp' (ID: acc_123)",
                "expected_tool": "crm_get_account",
                "expected_args": {"id": "acc_123"}
            },
            {
                "input": "List all contacts associated with account acc_123",
                "expected_tool": "crm_list_contacts",
                "expected_args": {"account_id": "acc_123"}
            },
            {
                "input": "Show me open opportunities worth more than $50k",
                "expected_tool": "crm_list_opportunities",
                "expected_args": {"status": "open", "min_amount": 50000}
            },
            {
                "input": "Get contact information for Jane Doe (ID: c_987)",
                "expected_tool": "crm_get_contact",
                "expected_args": {"id": "c_987"}
            }
        ]
