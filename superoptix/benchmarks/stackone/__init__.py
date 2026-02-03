"""
StackOne Benchmarks
===================

Pre-built evaluation suites for StackOne integrations.
"""

from .base import StackOneBenchmark
from .hris_benchmark import HRISBenchmark
from .ats_benchmark import ATSBenchmark
from .crm_benchmark import CRMBenchmark

__all__ = ["StackOneBenchmark", "HRISBenchmark", "ATSBenchmark", "CRMBenchmark"]
