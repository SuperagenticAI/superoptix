"""
SuperSpec Validator

Validates agent playbooks against the SuperSpec DSL specification.
Ensures tier-specific feature compliance and current version limitations.
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class SuperSpecXValidator:
    """Validates agent playbooks against SuperSpec DSL specification."""

    def __init__(self, dsl_path: Optional[str] = None):
        """Initialize validator with DSL specification."""
        self.errors = []
        self.warnings = []
        self.dsl_spec = self._load_dsl_spec(dsl_path)

    def _load_dsl_spec(self, dsl_path: Optional[str]) -> Dict[str, Any]:
        """Load DSL specification from file."""
        if dsl_path is None:
            # Use default DSL specification path
            dsl_path = Path(__file__).parent / "superspec_dsl.yaml"

        try:
            with open(dsl_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return minimal spec if file not found
            return self._get_minimal_spec()

    def _get_minimal_spec(self) -> Dict[str, Any]:
        """Return minimal DSL specification for validation."""
        return {
            "schema": {
                "root": {
                    "apiVersion": {"required": True, "enum": ["agent/v1"]},
                    "kind": {"required": True, "enum": ["AgentSpec"]},
                    "metadata": {"required": True},
                    "spec": {"required": True},
                }
            }
        }

    def validate(self, playbook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a playbook against SuperSpec DSL specification.

        Note: Optimization configuration is optional and won't cause validation failures.

        Args:
            playbook_data: Parsed playbook data

        Returns:
            Validation result with errors, warnings, and validity
        """
        self.errors = []
        self.warnings = []

        # Validate basic structure
        self._validate_root_structure(playbook_data)

        # Validate metadata
        self._validate_metadata(playbook_data)

        # Validate spec
        self._validate_spec(playbook_data)

        # Validate tier-specific features
        self._validate_tier_features(playbook_data)

        # Validate current version limitations
        self._validate_current_version_limitations(playbook_data)

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "tier": playbook_data.get("metadata", {}).get("level", "oracles"),
        }

    def _validate_root_structure(self, playbook_data: Dict[str, Any]):
        """Validate root structure requirements."""
        required_fields = ["apiVersion", "kind", "metadata", "spec"]

        for field in required_fields:
            if field not in playbook_data:
                self.errors.append(f"Missing required root field: {field}")

        # Validate apiVersion
        if "apiVersion" in playbook_data:
            if playbook_data["apiVersion"] != "agent/v1":
                self.errors.append(
                    f"Invalid apiVersion: {playbook_data['apiVersion']}. Must be 'agent/v1'"
                )

        # Validate kind
        if "kind" in playbook_data:
            if playbook_data["kind"] != "AgentSpec":
                self.errors.append(
                    f"Invalid kind: {playbook_data['kind']}. Must be 'AgentSpec'"
                )

    def _validate_metadata(self, playbook_data: Dict[str, Any]):
        """Validate metadata section."""
        metadata = playbook_data.get("metadata", {})

        # Required metadata fields
        required_fields = ["name", "id", "version"]
        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"Missing required metadata field: {field}")

        # Validate tier
        tier = metadata.get("level", "oracles")
        valid_tiers = ["oracles", "genies"]
        if tier not in valid_tiers:
            self.errors.append(
                f"Invalid tier '{tier}'. Valid options: {', '.join(valid_tiers)}"
            )

        # Validate namespace
        if "namespace" in metadata:
            valid_namespaces = [
                "software",
                "education",
                "healthcare",
                "finance",
                "marketing",
                "legal",
                "consulting",
                "retail",
                "manufacturing",
                "transportation",
                "agriculture_food",
                "energy_utilities",
                "gaming_sports",
                "government_public",
                "hospitality_tourism",
                "human_resources",
                "media_entertainment",
                "real_estate",
                "testing",
            ]
            if metadata["namespace"] not in valid_namespaces:
                self.warnings.append(
                    f"Namespace '{metadata['namespace']}' not in standard list"
                )

        # Validate agent_type
        if "agent_type" in metadata:
            valid_types = [
                "Autonomous",
                "Supervised",
                "Interactive",
                "Reactive",
                "Deliberative",
                "Hybrid",
            ]
            if metadata["agent_type"] not in valid_types:
                self.errors.append(
                    f"Invalid agent_type '{metadata['agent_type']}'. Valid options: {', '.join(valid_types)}"
                )

        # Validate stage
        if "stage" in metadata:
            valid_stages = ["alpha", "beta", "stable"]
            if metadata["stage"] not in valid_stages:
                self.errors.append(
                    f"Invalid stage '{metadata['stage']}'. Valid options: {', '.join(valid_stages)}"
                )

        # Validate version format
        if "version" in metadata:
            import re

            version_pattern = r"^\d+\.\d+\.\d+$"
            if not re.match(version_pattern, metadata["version"]):
                self.errors.append(
                    f"Invalid version format '{metadata['version']}'. Must be semantic versioning (e.g., '1.0.0')"
                )

    def _validate_spec(self, playbook_data: Dict[str, Any]):
        """Validate spec section."""
        spec = playbook_data.get("spec", {})

        # Validate language_model (required)
        if "language_model" not in spec:
            self.errors.append("Missing required spec field: language_model")
        else:
            self._validate_language_model(spec["language_model"])

        # Validate persona (optional but recommended)
        if "persona" not in spec:
            self.warnings.append(
                "No persona defined - recommended for better agent behavior"
            )
        else:
            self._validate_persona(spec["persona"])

        # Validate tasks (required)
        if "tasks" not in spec:
            self.errors.append("Missing required spec field: tasks")
        elif not spec["tasks"]:
            self.errors.append("Tasks list cannot be empty")
        else:
            self._validate_tasks(spec["tasks"])

        # Validate agentflow (optional)
        if "agentflow" in spec:
            self._validate_agentflow(
                spec["agentflow"],
                playbook_data.get("metadata", {}).get("level", "oracles"),
            )

    def _validate_language_model(self, lm_config: Dict[str, Any]):
        """Validate language model configuration."""
        required_fields = ["provider", "model"]
        for field in required_fields:
            if field not in lm_config:
                self.errors.append(f"Missing required language_model field: {field}")

        # Validate location
        if "location" in lm_config:
            valid_locations = ["local", "self-hosted", "cloud"]
            if lm_config["location"] not in valid_locations:
                self.errors.append(
                    f"Invalid location '{lm_config['location']}'. Valid options: {', '.join(valid_locations)}"
                )

        # Validate temperature range
        if "temperature" in lm_config:
            temp = lm_config["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                self.errors.append(f"Temperature must be between 0 and 2, got: {temp}")

        # Validate max_tokens
        if "max_tokens" in lm_config:
            max_tokens = lm_config["max_tokens"]
            if not isinstance(max_tokens, int) or max_tokens < 1:
                self.errors.append(
                    f"max_tokens must be a positive integer, got: {max_tokens}"
                )

        # Validate modalities
        if "modalities" in lm_config:
            valid_modalities = ["text", "image", "audio", "video"]
            for modality in lm_config["modalities"]:
                if modality not in valid_modalities:
                    self.errors.append(
                        f"Invalid modality '{modality}'. Valid options: {', '.join(valid_modalities)}"
                    )

    def _validate_persona(self, persona: Dict[str, Any]):
        """Validate persona configuration."""
        if "role" not in persona:
            self.warnings.append(
                "Persona missing 'role' field - recommended for clarity"
            )

        # Validate communication preferences
        if "communication_preferences" in persona:
            comm_prefs = persona["communication_preferences"]
            if "style" in comm_prefs:
                valid_styles = ["formal", "casual", "technical", "conversational"]
                if comm_prefs["style"] not in valid_styles:
                    self.warnings.append(
                        f"Invalid communication style '{comm_prefs['style']}'"
                    )

            if "tone" in comm_prefs:
                valid_tones = [
                    "professional",
                    "friendly",
                    "authoritative",
                    "supportive",
                ]
                if comm_prefs["tone"] not in valid_tones:
                    self.warnings.append(
                        f"Invalid communication tone '{comm_prefs['tone']}'"
                    )

    def _validate_tasks(self, tasks: List[Dict[str, Any]]):
        """Validate tasks configuration."""
        if not tasks:
            self.errors.append("Tasks list cannot be empty")
            return

        task_names = set()
        for i, task in enumerate(tasks):
            # Validate required fields
            required_fields = ["name", "instruction"]
            for field in required_fields:
                if field not in task:
                    self.errors.append(f"Task {i + 1} missing required field: {field}")

            # Check for duplicate task names
            if "name" in task:
                if task["name"] in task_names:
                    self.errors.append(f"Duplicate task name: {task['name']}")
                task_names.add(task["name"])

            # Validate inputs
            if "inputs" in task:
                self._validate_task_inputs(task["inputs"], i + 1)

            # Validate outputs
            if "outputs" in task:
                self._validate_task_outputs(task["outputs"], i + 1)

    def _validate_task_inputs(self, inputs: List[Dict[str, Any]], task_num: int):
        """Validate task inputs."""
        if not inputs:
            self.warnings.append(f"Task {task_num} has no inputs defined")
            return

        valid_types = ["str", "int", "bool", "float", "list[str]", "dict[str,Any]"]
        for i, input_field in enumerate(inputs):
            required_fields = ["name", "type", "description", "required"]
            for field in required_fields:
                if field not in input_field:
                    self.errors.append(
                        f"Task {task_num} input {i + 1} missing required field: {field}"
                    )

            if "type" in input_field and input_field["type"] not in valid_types:
                self.errors.append(
                    f"Task {task_num} input {i + 1} invalid type: {input_field['type']}"
                )

    def _validate_task_outputs(self, outputs: List[Dict[str, Any]], task_num: int):
        """Validate task outputs."""
        if not outputs:
            self.warnings.append(f"Task {task_num} has no outputs defined")
            return

        valid_types = ["str", "int", "bool", "float", "list[str]", "dict[str,Any]"]
        for i, output_field in enumerate(outputs):
            required_fields = ["name", "type", "description"]
            for field in required_fields:
                if field not in output_field:
                    self.errors.append(
                        f"Task {task_num} output {i + 1} missing required field: {field}"
                    )

            if "type" in output_field and output_field["type"] not in valid_types:
                self.errors.append(
                    f"Task {task_num} output {i + 1} invalid type: {output_field['type']}"
                )

    def _validate_agentflow(self, agentflow: List[Dict[str, Any]], tier: str):
        """Validate agent flow configuration."""
        if not agentflow:
            self.warnings.append("Empty agentflow - agent will use default execution")
            return

        # Define allowed step types per tier
        oracles_types = ["Generate", "Think", "Compare", "Route"]
        genies_types = [
            "Generate",
            "Think",
            "ActWithTools",
            "Search",
            "Compare",
            "Route",
        ]

        allowed_types = oracles_types if tier == "oracles" else genies_types

        step_names = set()
        for i, step in enumerate(agentflow):
            # Validate required fields
            required_fields = ["name", "type", "task"]
            for field in required_fields:
                if field not in step:
                    self.errors.append(
                        f"Agentflow step {i + 1} missing required field: {field}"
                    )

            # Check for duplicate step names
            if "name" in step:
                if step["name"] in step_names:
                    self.errors.append(f"Duplicate agentflow step name: {step['name']}")
                step_names.add(step["name"])

            # Validate step type
            if "type" in step:
                if step["type"] not in allowed_types:
                    self.errors.append(
                        f"Step type '{step['type']}' not allowed for {tier} tier"
                    )

            # Validate tier-specific step configurations
            if "type" in step and step["type"] == "ActWithTools" and tier == "oracles":
                self.errors.append("ActWithTools step type requires Genies tier")

            if "type" in step and step["type"] == "Search" and tier == "oracles":
                self.errors.append("Search step type requires Genies tier")

    def _validate_tier_features(self, playbook_data: Dict[str, Any]):
        """Validate tier-specific features."""
        metadata = playbook_data.get("metadata", {})
        spec = playbook_data.get("spec", {})
        tier = metadata.get("level", "oracles")

        # Features that require Genies tier
        genies_only_features = [
            "retrieval",
            "memory",
            "tool_calling",
            "react_config",
            "rag_config",
            "streaming",
        ]

        if tier == "oracles":
            for feature in genies_only_features:
                if feature in spec:
                    self.errors.append(f"Feature '{feature}' requires Genies tier")

        # Validate specific feature configurations
        if "memory" in spec and tier == "genies":
            self._validate_memory_config(spec["memory"])

        if "tool_calling" in spec and tier == "genies":
            self._validate_tool_calling_config(spec["tool_calling"])

        if "retrieval" in spec and tier == "genies":
            self._validate_retrieval_config(spec["retrieval"])

    def _validate_memory_config(self, memory_config: Dict[str, Any]):
        """Validate memory configuration."""
        if "backend" in memory_config:
            backend = memory_config["backend"]
            if isinstance(backend, dict) and "type" in backend:
                valid_backends = ["file", "sqlite", "redis"]
                if backend["type"] not in valid_backends:
                    self.errors.append(
                        f"Invalid memory backend type: {backend['type']}"
                    )

        # Validate memory types
        if "short_term" in memory_config:
            short_term = memory_config["short_term"]
            if "capacity" in short_term:
                capacity = short_term["capacity"]
                if not isinstance(capacity, int) or capacity < 10 or capacity > 1000:
                    self.warnings.append(
                        f"Short-term memory capacity should be between 10 and 1000, got: {capacity}"
                    )

    def _validate_tool_calling_config(self, tool_config: Dict[str, Any]):
        """Validate tool calling configuration."""
        if "enabled" not in tool_config:
            self.errors.append("Tool calling configuration missing 'enabled' field")

        if "max_tool_calls" in tool_config:
            max_calls = tool_config["max_tool_calls"]
            if not isinstance(max_calls, int) or max_calls < 1 or max_calls > 20:
                self.warnings.append(
                    f"max_tool_calls should be between 1 and 20, got: {max_calls}"
                )

    def _validate_retrieval_config(self, retrieval_config: Dict[str, Any]):
        """Validate retrieval (RAG) configuration."""
        if "enabled" not in retrieval_config:
            self.errors.append("Retrieval configuration missing 'enabled' field")

        if "retriever_type" in retrieval_config:
            valid_retrievers = [
                "ColBERTv2",
                "Weaviate",
                "ChromaDB",
                "Pinecone",
                "FAISS",
                "Custom",
            ]
            if retrieval_config["retriever_type"] not in valid_retrievers:
                self.errors.append(
                    f"Invalid retriever_type: {retrieval_config['retriever_type']}"
                )

    def _validate_current_version_limitations(self, playbook_data: Dict[str, Any]):
        """Validate that no commercial features are used."""
        spec = playbook_data.get("spec", {})

        # Check for advanced optimizers
        if "optimization" in spec:
            opt_config = spec["optimization"]
            if "strategy" in opt_config:
                strategy = opt_config["strategy"]
                if strategy not in ["few_shot_bootstrapping"]:
                    self.errors.append(
                        f"Advanced optimization strategy '{strategy}' not available in current version"
                    )

        # Check for advanced orchestration
        if "orchestration" in spec:
            orch_config = spec["orchestration"]
            if "strategy" in orch_config:
                strategy = orch_config["strategy"]
                if strategy not in ["sequential"]:
                    self.errors.append(
                        f"Advanced orchestration strategy '{strategy}' not available in current version"
                    )

        # Check for enterprise features
        enterprise_features = [
            "white_label",
            "custom_branding",
            "enterprise_security",
            "professional_services",
            "custom_teleprompt",
        ]

        for feature in enterprise_features:
            if feature in spec:
                self.errors.append(
                    f"Enterprise feature '{feature}' not available in current version"
                )

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a playbook file."""
        try:
            with open(file_path, "r") as f:
                playbook_data = yaml.safe_load(f)

            result = self.validate(playbook_data)
            result["file_path"] = file_path
            return result

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse file: {str(e)}"],
                "warnings": [],
                "file_path": file_path,
            }

    def get_validation_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of validation results.

        Args:
            results: List of validation results

        Returns:
            Summary statistics
        """
        total_files = len(results)
        valid_files = sum(1 for r in results if r["valid"])
        invalid_files = total_files - valid_files

        total_errors = sum(len(r["errors"]) for r in results)
        total_warnings = sum(len(r["warnings"]) for r in results)

        tier_counts = {}
        for result in results:
            tier = result.get("tier", "unknown")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        return {
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "tier_distribution": tier_counts,
            "validation_rate": valid_files / total_files if total_files > 0 else 0,
        }
