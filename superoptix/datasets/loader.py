"""
Dataset Loader for SuperOptiX

Loads external datasets from various formats and converts them to DSPy Examples.
"""

from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Load external datasets for training and evaluation."""

    def __init__(self, dataset_config: Dict[str, Any]):
        """
        Initialize dataset loader.

        Args:
                dataset_config: Dataset configuration dictionary with keys:
                        - name: Dataset name
                        - source: File path or dataset identifier
                        - format: csv, json, jsonl, parquet, or huggingface
                        - mapping: Column to field mapping
                        - split: train, test, validation, or all (default: train)
                        - limit: Max number of examples (optional)
                        - shuffle: Whether to shuffle (default: True)
        """
        self.name = dataset_config["name"]
        self.source = dataset_config["source"]
        self.format = dataset_config.get("format", "csv")
        self.mapping = dataset_config["mapping"]
        self.split = dataset_config.get("split", "train")
        self.limit = dataset_config.get("limit")
        self.shuffle = dataset_config.get("shuffle", True)

        logger.info(
            f"Initialized DatasetLoader for: {self.name} (format={self.format})"
        )

    def load(self) -> List[Dict[str, Any]]:
        """
        Load dataset and return as list of examples.

        Returns:
                List of examples with 'input' and 'output' keys
        """
        logger.info(f"Loading dataset: {self.name} from {self.source}")

        try:
            if self.format == "csv":
                return self._load_csv()
            elif self.format == "json":
                return self._load_json()
            elif self.format == "jsonl":
                return self._load_jsonl()
            elif self.format == "parquet":
                return self._load_parquet()
            elif self.format == "huggingface":
                return self._load_huggingface()
            else:
                raise ValueError(f"Unsupported format: {self.format}")
        except Exception as e:
            logger.error(f"Failed to load dataset {self.name}: {e}")
            raise

    def _load_csv(self) -> List[Dict[str, Any]]:
        """Load CSV dataset."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for CSV support. Install with: pip install pandas"
            )

        logger.debug(f"Reading CSV from: {self.source}")
        df = pd.read_csv(self.source)
        logger.info(f"Loaded {len(df)} rows from CSV")

        return self._process_dataframe(df)

    def _load_json(self) -> List[Dict[str, Any]]:
        """Load JSON dataset."""
        logger.debug(f"Reading JSON from: {self.source}")

        with open(self.source, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle both list of objects and single object with data array
        if isinstance(data, dict):
            # Try common keys for array data
            for key in ["data", "examples", "records", "items"]:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break

        if not isinstance(data, list):
            raise ValueError(
                f"JSON data must be a list or object with data array, got {type(data)}"
            )

        logger.info(f"Loaded {len(data)} records from JSON")
        return self._process_records(data)

    def _load_jsonl(self) -> List[Dict[str, Any]]:
        """Load JSONL (JSON Lines) dataset."""
        logger.debug(f"Reading JSONL from: {self.source}")

        data = []
        with open(self.source, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping invalid JSON on line {i + 1}: {e}")

        logger.info(f"Loaded {len(data)} records from JSONL")
        return self._process_records(data)

    def _load_parquet(self) -> List[Dict[str, Any]]:
        """Load Parquet dataset."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for Parquet support. Install with: pip install pandas pyarrow"
            )

        logger.debug(f"Reading Parquet from: {self.source}")

        try:
            df = pd.read_parquet(self.source)
            logger.info(f"Loaded {len(df)} rows from Parquet")
            return self._process_dataframe(df)
        except ImportError:
            raise ImportError(
                "pyarrow or fastparquet is required for Parquet support. "
                "Install with: pip install pyarrow"
            )

    def _load_huggingface(self) -> List[Dict[str, Any]]:
        """Load HuggingFace dataset."""
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError(
                "HuggingFace datasets is required. Install with: pip install datasets"
            )

        # Parse huggingface:dataset_name or huggingface:dataset_name:subset
        source = self.source.replace("huggingface:", "")
        parts = source.split(":")
        dataset_name = parts[0]
        subset = parts[1] if len(parts) > 1 else None

        logger.info(
            f"Loading HuggingFace dataset: {dataset_name}"
            + (f" (subset: {subset})" if subset else "")
        )

        try:
            dataset = load_dataset(dataset_name, subset, split=self.split)
            logger.info(f"Loaded {len(dataset)} examples from HuggingFace")
            return self._process_hf_dataset(dataset)
        except Exception as e:
            logger.error(f"Failed to load HuggingFace dataset: {e}")
            raise

    def _process_dataframe(self, df) -> List[Dict[str, Any]]:
        """Process pandas DataFrame into examples."""

        # Shuffle if requested
        if self.shuffle:
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)
            logger.debug("Shuffled dataset")

        # Limit number of examples
        if self.limit:
            df = df.head(self.limit)
            logger.debug(f"Limited to {self.limit} examples")

        examples = []
        for _, row in df.iterrows():
            try:
                example = self._map_example(row.to_dict())
                examples.append(example)
            except Exception as e:
                logger.warning(f"Skipping row due to mapping error: {e}")

        logger.info(f"Processed {len(examples)} examples from DataFrame")
        return examples

    def _process_records(self, records: List[Dict]) -> List[Dict[str, Any]]:
        """Process list of records into examples."""
        # Shuffle if requested
        if self.shuffle:
            import random

            random.seed(42)
            records = records.copy()
            random.shuffle(records)
            logger.debug("Shuffled dataset")

        # Limit number of examples
        if self.limit:
            records = records[: self.limit]
            logger.debug(f"Limited to {self.limit} examples")

        examples = []
        for record in records:
            try:
                example = self._map_example(record)
                examples.append(example)
            except Exception as e:
                logger.warning(f"Skipping record due to mapping error: {e}")

        logger.info(f"Processed {len(examples)} examples from records")
        return examples

    def _process_hf_dataset(self, dataset) -> List[Dict[str, Any]]:
        """Process HuggingFace dataset into examples."""
        # Shuffle if requested
        if self.shuffle:
            dataset = dataset.shuffle(seed=42)
            logger.debug("Shuffled dataset")

        # Limit number of examples
        if self.limit:
            max_len = min(self.limit, len(dataset))
            dataset = dataset.select(range(max_len))
            logger.debug(f"Limited to {max_len} examples")

        examples = []
        for record in dataset:
            try:
                example = self._map_example(dict(record))
                examples.append(example)
            except Exception as e:
                logger.warning(f"Skipping record due to mapping error: {e}")

        logger.info(f"Processed {len(examples)} examples from HuggingFace dataset")
        return examples

    def _map_example(self, record: Dict) -> Dict[str, Any]:
        """
        Map dataset columns to agent input/output fields.

        Args:
                record: Dictionary with dataset columns

        Returns:
                Dictionary with 'input' and 'output' keys containing mapped fields
        """
        example = {"input": {}, "output": {}}

        # Map input fields
        input_mapping = self.mapping.get("input")
        if isinstance(input_mapping, str):
            # Simple mapping: input: column_name
            # Use the mapping key or default field name
            field_name = self.mapping.get("input_field_name", input_mapping)
            example["input"][field_name] = record[input_mapping]
        elif isinstance(input_mapping, dict):
            # Complex mapping: input: {field1: col1, field2: col2}
            for field, col in input_mapping.items():
                if col not in record:
                    raise KeyError(f"Column '{col}' not found in record")
                example["input"][field] = record[col]
        else:
            raise ValueError(f"Invalid input mapping type: {type(input_mapping)}")

        # Map output fields
        output_mapping = self.mapping.get("output")
        if isinstance(output_mapping, str):
            # Simple mapping: output: column_name
            field_name = self.mapping.get("output_field_name", output_mapping)
            example["output"][field_name] = record[output_mapping]
        elif isinstance(output_mapping, dict):
            # Complex mapping: output: {field1: col1, field2: col2}
            for field, col in output_mapping.items():
                if col not in record:
                    raise KeyError(f"Column '{col}' not found in record")
                example["output"][field] = record[col]
        else:
            raise ValueError(f"Invalid output mapping type: {type(output_mapping)}")

        return example

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the dataset.

        Returns:
                Dictionary with dataset statistics
        """
        examples = self.load()

        stats = {
            "name": self.name,
            "source": self.source,
            "format": self.format,
            "total_examples": len(examples),
            "split": self.split,
            "shuffled": self.shuffle,
        }

        if self.limit:
            stats["limit_applied"] = self.limit

        # Get field names
        if examples:
            stats["input_fields"] = list(examples[0]["input"].keys())
            stats["output_fields"] = list(examples[0]["output"].keys())

        return stats
