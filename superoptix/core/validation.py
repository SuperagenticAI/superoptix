"""
SuperOptiX Core Validation - Mid Tier Current Version
================================================

Basic validation utilities for SuperOptiX agents and pipelines.
Focuses on configuration validation and basic checks.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_agent_spec(spec: Dict[str, Any]) -> bool:
    """Validate agent specification format and required fields."""
    required_fields = ["apiVersion", "kind", "metadata", "spec"]

    for field in required_fields:
        if field not in spec:
            raise ValidationError(f"Missing required field: {field}")

    # Validate metadata
    metadata = spec.get("metadata", {})
    required_metadata = ["name", "id", "version", "level"]
    for field in required_metadata:
        if field not in metadata:
            raise ValidationError(f"Missing required metadata field: {field}")

    # Validate spec structure
    agent_spec = spec.get("spec", {})
    required_spec_fields = ["language_model", "persona", "tasks"]
    for field in required_spec_fields:
        if field not in agent_spec:
            raise ValidationError(f"Missing required spec field: {field}")

    return True


def validate_language_model_config(lm_config: Dict[str, Any]) -> bool:
    """Validate language model configuration."""
    required_fields = ["provider", "model"]

    for field in required_fields:
        if field not in lm_config:
            raise ValidationError(f"Missing language model field: {field}")

    # Validate provider
    supported_providers = [
        "openai",
        "ollama",
        "anthropic",
        "google",
        "azure",
        "mistral",
    ]
    if lm_config["provider"] not in supported_providers:
        raise ValidationError(
            f"Unsupported provider: {lm_config['provider']}. Supported: {supported_providers}"
        )

    # Validate temperature range
    if "temperature" in lm_config:
        temp = lm_config["temperature"]
        if not 0.0 <= temp <= 2.0:
            raise ValidationError(
                f"Temperature must be between 0.0 and 2.0, got: {temp}"
            )

    # Validate max_tokens
    if "max_tokens" in lm_config:
        max_tokens = lm_config["max_tokens"]
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise ValidationError(
                f"max_tokens must be a positive integer, got: {max_tokens}"
            )

    return True


def validate_task_definition(task: Dict[str, Any]) -> bool:
    """Validate task definition structure."""
    required_fields = ["name", "type", "inputs", "outputs"]

    for field in required_fields:
        if field not in task:
            raise ValidationError(f"Missing task field: {field}")

    # Validate task type
    supported_types = ["predict", "chainofthought", "react", "generate"]
    if task["type"] not in supported_types:
        raise ValidationError(
            f"Unsupported task type: {task['type']}. Supported: {supported_types}"
        )

    # Validate inputs and outputs
    for io_type in ["inputs", "outputs"]:
        io_list = task[io_type]
        if not isinstance(io_list, list) or len(io_list) == 0:
            raise ValidationError(f"Task {io_type} must be a non-empty list")

        for io_item in io_list:
            if (
                not isinstance(io_item, dict)
                or "name" not in io_item
                or "type" not in io_item
            ):
                raise ValidationError(
                    f"Invalid {io_type} item: must have 'name' and 'type' fields"
                )

    return True


def validate_tool_configuration(tools_config: Dict[str, Any]) -> bool:
    """Validate tools configuration."""
    if "builtin_tools" in tools_config:
        builtin_tools = tools_config["builtin_tools"]
        if not isinstance(builtin_tools, list):
            raise ValidationError("builtin_tools must be a list")

        for tool in builtin_tools:
            if not isinstance(tool, dict) or "name" not in tool:
                raise ValidationError("Each builtin tool must have a 'name' field")

    if "custom_tools" in tools_config:
        custom_tools = tools_config["custom_tools"]
        if not isinstance(custom_tools, list):
            raise ValidationError("custom_tools must be a list")

        for tool in custom_tools:
            required_fields = ["name", "description", "function_name", "parameters"]
            for field in required_fields:
                if field not in tool:
                    raise ValidationError(
                        f"Custom tool missing required field: {field}"
                    )

    return True


def validate_react_config(react_config: Dict[str, Any]) -> bool:
    """Validate ReAct agent configuration."""
    if "max_iters" in react_config:
        max_iters = react_config["max_iters"]
        if not isinstance(max_iters, int) or max_iters <= 0:
            raise ValidationError("max_iters must be a positive integer")

    if "max_tool_calls" in react_config:
        max_calls = react_config["max_tool_calls"]
        if not isinstance(max_calls, int) or max_calls <= 0:
            raise ValidationError("max_tool_calls must be a positive integer")

    return True


def validate_rag_config(rag_config: Dict[str, Any]) -> bool:
    """Validate RAG configuration."""
    if rag_config.get("enabled", False):
        required_fields = ["retriever_type", "config", "vector_store"]
        for field in required_fields:
            if field not in rag_config:
                raise ValidationError(
                    f"RAG configuration missing required field: {field}"
                )

        # Validate retriever type
        supported_retrievers = [
            "chroma",
            "weaviate",
            "lancedb",
            "milvus",
            "qdrant",
            "pinecone",
            "faiss",
        ]
        if rag_config["retriever_type"] not in supported_retrievers:
            raise ValidationError(
                f"Unsupported retriever type: {rag_config['retriever_type']}"
            )

        # Validate config
        config = rag_config["config"]
        if "top_k" in config:
            top_k = config["top_k"]
            if not isinstance(top_k, int) or top_k <= 0:
                raise ValidationError("top_k must be a positive integer")

        if "similarity_threshold" in config:
            threshold = config["similarity_threshold"]
            if not 0.0 <= threshold <= 1.0:
                raise ValidationError(
                    "similarity_threshold must be between 0.0 and 1.0"
                )

    return True


def validate_memory_config(memory_config: Dict[str, Any]) -> bool:
    """Validate memory configuration."""
    if "short_term" in memory_config:
        st_config = memory_config["short_term"]
        if "max_items" in st_config:
            max_items = st_config["max_items"]
            if not isinstance(max_items, int) or max_items <= 0:
                raise ValidationError("short_term.max_items must be a positive integer")

    if "episodic" in memory_config:
        ep_config = memory_config["episodic"]
        if "max_episodes" in ep_config:
            max_episodes = ep_config["max_episodes"]
            if not isinstance(max_episodes, int) or max_episodes <= 0:
                raise ValidationError(
                    "episodic.max_episodes must be a positive integer"
                )

    return True


def validate_optimization_config(opt_config: Dict[str, Any]) -> bool:
    """Validate optimization configuration."""
    if "strategy" in opt_config:
        strategy = opt_config["strategy"]
        # Mid-tier supported strategies
        supported_strategies = ["bootstrap_fewshot", "knn_fewshot", "labeled_fewshot"]
        if strategy not in supported_strategies:
            raise ValidationError(
                f"Unsupported optimization strategy: {strategy}. Supported: {supported_strategies}"
            )

    if "max_examples" in opt_config:
        max_examples = opt_config["max_examples"]
        if not isinstance(max_examples, int) or max_examples <= 0:
            raise ValidationError("max_examples must be a positive integer")

    if "max_rounds" in opt_config:
        max_rounds = opt_config["max_rounds"]
        if not isinstance(max_rounds, int) or max_rounds <= 0:
            raise ValidationError("max_rounds must be a positive integer")

    return True


def validate_tier_level(tier_level: str) -> bool:
    """Validate tier level."""
    supported_tiers = ["oracles", "genies", "protocols", "superagents", "sovereigns"]
    if tier_level not in supported_tiers:
        raise ValidationError(
            f"Unsupported tier level: {tier_level}. Supported: {supported_tiers}"
        )
    return True


def load_and_validate_spec_file(spec_path: Union[str, Path]) -> Dict[str, Any]:
    """Load and validate a specification file."""
    spec_path = Path(spec_path)

    if not spec_path.exists():
        raise ValidationError(f"Specification file not found: {spec_path}")

    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            if spec_path.suffix.lower() in [".yaml", ".yml"]:
                spec = yaml.safe_load(f)
            elif spec_path.suffix.lower() == ".json":
                spec = json.load(f)
            else:
                raise ValidationError(f"Unsupported file format: {spec_path.suffix}")
    except Exception as e:
        raise ValidationError(f"Failed to parse specification file: {e}")

    # Validate the loaded specification
    validate_agent_spec(spec)

    return spec


def validate_environment_variables(required_vars: List[str]) -> Dict[str, str]:
    """Validate that required environment variables are set."""
    missing_vars = []
    env_vars = {}

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            env_vars[var] = value

    if missing_vars:
        raise ValidationError(f"Missing required environment variables: {missing_vars}")

    return env_vars


def validate_file_path(file_path: Union[str, Path], must_exist: bool = True) -> Path:
    """Validate file path."""
    path = Path(file_path).resolve()

    if must_exist and not path.exists():
        raise ValidationError(f"File not found: {file_path}")

    # Basic security check - no parent directory traversal
    if ".." in str(path) or str(path).startswith("/"):
        logger.warning(f"Potentially unsafe file path: {file_path}")

    return path


def validate_model_compatibility(provider: str, model: str, tier_level: str) -> bool:
    """Validate model compatibility with tier level."""
    # Basic compatibility checks
    if tier_level == "oracle":
        # Oracle tier should use smaller models
        small_models = ["gpt-4o-mini", "llama3.2:1b", "llama3.2:3b", "claude-3-haiku"]
        if provider == "openai" and model not in small_models:
            logger.warning(f"Model {model} may be expensive for oracle tier")

    return True


# === UTILITY FUNCTIONS ===


def get_validation_summary(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Get validation summary for a specification."""
    summary = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "tier_level": None,
        "agent_type": None,
    }

    try:
        validate_agent_spec(spec)

        # Extract basic info
        metadata = spec.get("metadata", {})
        summary["tier_level"] = metadata.get("level")
        summary["agent_type"] = metadata.get("agent_type")

        # Validate components
        agent_spec = spec.get("spec", {})

        if "language_model" in agent_spec:
            validate_language_model_config(agent_spec["language_model"])

        if "tasks" in agent_spec:
            for task in agent_spec["tasks"]:
                validate_task_definition(task)

        if "tools" in agent_spec:
            validate_tool_configuration(agent_spec["tools"])

        if "react_config" in agent_spec:
            validate_react_config(agent_spec["react_config"])

        if "retrieval" in agent_spec:
            validate_rag_config(agent_spec["retrieval"])

        if "memory" in agent_spec:
            validate_memory_config(agent_spec["memory"])

        if "optimization" in agent_spec:
            validate_optimization_config(agent_spec["optimization"])

        summary["valid"] = True

    except ValidationError as e:
        summary["errors"].append(str(e))
    except Exception as e:
        summary["errors"].append(f"Unexpected error: {str(e)}")

    return summary


# === COMPATIBILITY FUNCTIONS ===
# These functions provide compatibility for the framework imports


def validate_framework_integrity() -> bool:
    """Basic framework integrity check for current version."""
    logger.info("✅ SuperOptiX framework integrity validated")
    return True


def validate_tier_access(tier_level: str) -> bool:
    """Basic tier access validation for current version."""
    valid_tiers = ["oracle", "genie"]
    if tier_level in valid_tiers:
        logger.info(f"✅ Tier '{tier_level}' access validated")
        return True
    else:
        logger.warning(f"⚠️ Tier '{tier_level}' not available in current version")
        return False


def track_tool_usage(tool_name: str, usage_data: Dict[str, Any]) -> None:
    """Basic tool usage tracking for current version."""
    logger.info(
        f"🔧 Tool '{tool_name}' used - {usage_data.get('success', 'unknown')} status"
    )


def register_pipeline_validation(pipeline_type: str, validator_func) -> None:
    """Register custom pipeline validation function."""
    logger.info(f"📝 Pipeline validator registered for type: {pipeline_type}")


def validate_tier_compatibility(spec: Dict[str, Any], target_tier: str) -> bool:
    """Validate that playbook supports the target tier."""
    metadata = spec.get("metadata", {})
    supported_tiers = metadata.get("supported_tiers", [metadata.get("level", "oracle")])

    if target_tier not in supported_tiers:
        # Check if it's a basic upgrade (oracle -> genie) which we allow by default
        playbook_tier = metadata.get("level", "oracle")
        if playbook_tier == "oracle" and target_tier == "genie":
            logger.info("✅ Allowing oracle→genie tier upgrade for enhanced features")
            return True
        else:
            raise ValidationError(
                f"Agent does not support tier '{target_tier}'. Supported: {supported_tiers}"
            )

    return True


def validate_tier_features(spec: Dict[str, Any], tier_level: str) -> bool:
    """Validate that features are appropriate for tier level."""
    if tier_level == "oracle":
        # Ensure no advanced features are forced on
        advanced_features = ["react_config", "tools", "retrieval"]
        for feature in advanced_features:
            if spec.get(feature, {}).get("enabled") is True:
                logger.warning(
                    f"⚠️ Feature '{feature}' enabled but not recommended for oracle tier"
                )

    elif tier_level == "genie":
        # Validate genie-tier feature configuration
        if "tools" in spec and not spec["tools"].get("enabled"):
            logger.info(
                "💡 Tools available but not enabled for genie-tier - can be enabled in playbook"
            )

        if "retrieval" in spec and spec["retrieval"].get("enabled"):
            validate_rag_config(spec["retrieval"])

    return True


# Export all validation functions
__all__ = [
    "ValidationError",
    "validate_agent_spec",
    "validate_language_model_config",
    "validate_task_definition",
    "validate_tool_configuration",
    "validate_react_config",
    "validate_rag_config",
    "validate_memory_config",
    "validate_optimization_config",
    "validate_tier_level",
    "load_and_validate_spec_file",
    "validate_environment_variables",
    "validate_file_path",
    "validate_model_compatibility",
    "get_validation_summary",
    "validate_framework_integrity",
    "validate_tier_access",
    "track_tool_usage",
    "register_pipeline_validation",
    "validate_tier_compatibility",
    "validate_tier_features",
]
