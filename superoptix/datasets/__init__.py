"""
SuperOptiX Dataset Import Module

Enables importing external datasets for training and evaluation,
freeing users from manual YAML BDD scenario creation.

Supported formats:
- CSV
- JSON/JSONL
- Parquet
- HuggingFace datasets
"""

from superoptix.datasets.loader import DatasetLoader
from superoptix.datasets.validators import DatasetValidator

__all__ = [
    "DatasetLoader",
    "DatasetValidator",
]
