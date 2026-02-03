"""
Dataset configuration validators for SuperOptiX
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatasetValidator:
    """Validate dataset configurations."""

    @staticmethod
    def validate_config(dataset_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate dataset configuration.

        Args:
                dataset_config: Dataset configuration dictionary

        Returns:
                Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = ["name", "source", "mapping"]
        for field in required_fields:
            if field not in dataset_config:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        # Validate format
        valid_formats = ["csv", "json", "jsonl", "parquet", "huggingface"]
        format_type = dataset_config.get("format", "csv")
        if format_type not in valid_formats:
            errors.append(
                f"Invalid format: {format_type}. Must be one of {valid_formats}"
            )

        # Validate source
        source = dataset_config["source"]
        if format_type != "huggingface":
            # Check if file exists
            source_path = Path(source)
            if not source_path.exists():
                errors.append(f"Source file not found: {source}")
        else:
            # Check HuggingFace format
            if not source.startswith("huggingface:"):
                errors.append("HuggingFace source must start with 'huggingface:'")

        # Validate mapping
        mapping = dataset_config.get("mapping", {})
        if not isinstance(mapping, dict):
            errors.append("Mapping must be a dictionary")
        else:
            if "input" not in mapping:
                errors.append("Mapping must include 'input' field")
            if "output" not in mapping:
                errors.append("Mapping must include 'output' field")

        # Validate split
        valid_splits = ["train", "test", "validation", "all"]
        split = dataset_config.get("split", "train")
        if split not in valid_splits:
            errors.append(f"Invalid split: {split}. Must be one of {valid_splits}")

        # Validate limit
        limit = dataset_config.get("limit")
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                errors.append("Limit must be a positive integer")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dataset_list(
        datasets_config: List[Dict[str, Any]],
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate a list of dataset configurations.

        Args:
                datasets_config: List of dataset configurations

        Returns:
                Tuple of (all_valid, dict_of_errors_by_dataset_name)
        """
        all_errors = {}
        all_valid = True

        for dataset in datasets_config:
            name = dataset.get("name", "unnamed")
            is_valid, errors = DatasetValidator.validate_config(dataset)

            if not is_valid:
                all_valid = False
                all_errors[name] = errors

        return all_valid, all_errors
