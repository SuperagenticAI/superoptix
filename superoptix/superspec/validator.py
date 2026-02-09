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

        # Validate RLM (optional, DSPy-specific)
        if "rlm" in spec:
            self._validate_rlm_config(spec["rlm"])

        # Validate DSPy automation block (optional, preferred)
        if "dspy" in spec:
            self._validate_dspy_config(spec["dspy"], spec)

        # Validate Pydantic AI framework block (optional)
        if "pydantic_ai" in spec:
            self._validate_pydantic_ai_config(spec["pydantic_ai"])

        # Validate OpenAI Agents framework block (optional)
        if "openai_agent" in spec:
            self._validate_openai_agent_config(spec["openai_agent"])

        # Validate Google ADK framework block (optional)
        if "google_adk" in spec:
            self._validate_google_adk_config(spec["google_adk"])

        # Validate DeepAgents framework block (optional)
        if "deepagents" in spec:
            self._validate_deepagents_config(spec["deepagents"])

        # Validate CrewAI framework block (optional)
        if "crewai" in spec:
            self._validate_crewai_config(spec["crewai"])

        # Validate optimization config (optional)
        if "optimization" in spec:
            self._validate_optimization_config(spec["optimization"])

    def _validate_language_model(self, lm_config: Dict[str, Any]):
        """Validate language model configuration."""
        required_fields = ["provider", "model"]
        for field in required_fields:
            if field not in lm_config:
                self.errors.append(f"Missing required language_model field: {field}")

        # Validate provider
        if "provider" in lm_config:
            valid_providers = [
                "ollama",
                "vllm",
                "sglang",
                "mlx",
                "lm_studio",
                "gateway",
                "openai",
                "anthropic",
                "google",
                "azure",
                "mistral",
                "cohere",
                "groq",
                "deepseek",
            ]
            provider = str(lm_config.get("provider", "")).strip()
            if provider and provider not in valid_providers:
                self.errors.append(
                    f"Invalid provider '{provider}'. Valid options: {', '.join(valid_providers)}"
                )

        # Validate runtime mode
        runtime_mode = str(lm_config.get("runtime_mode", "")).strip().lower()
        if runtime_mode and runtime_mode not in {"direct", "gateway"}:
            self.errors.append(
                f"Invalid language_model.runtime_mode '{runtime_mode}'. Valid options: direct, gateway"
            )

        # Validate gateway config
        gateway_cfg = lm_config.get("gateway")
        if gateway_cfg is not None and not isinstance(gateway_cfg, dict):
            self.errors.append("language_model.gateway must be an object")
        elif isinstance(gateway_cfg, dict):
            if "enabled" in gateway_cfg and not isinstance(
                gateway_cfg.get("enabled"), bool
            ):
                self.errors.append("language_model.gateway.enabled must be a boolean")
            if "base_url" in gateway_cfg and not isinstance(
                gateway_cfg.get("base_url"), str
            ):
                self.errors.append("language_model.gateway.base_url must be a string")
            if "api_key_env" in gateway_cfg and not isinstance(
                gateway_cfg.get("api_key_env"), str
            ):
                self.errors.append(
                    "language_model.gateway.api_key_env must be a string"
                )

            timeout_sec = gateway_cfg.get("timeout_sec")
            if timeout_sec is not None and (
                not isinstance(timeout_sec, int) or timeout_sec < 1 or timeout_sec > 600
            ):
                self.errors.append(
                    "language_model.gateway.timeout_sec must be an integer between 1 and 600"
                )

            model_map = gateway_cfg.get("model_map")
            if model_map is not None:
                if not isinstance(model_map, dict) or not all(
                    isinstance(k, str) and isinstance(v, str)
                    for k, v in model_map.items()
                ):
                    self.errors.append(
                        "language_model.gateway.model_map must be an object with string keys/values"
                    )

        if runtime_mode == "gateway":
            if not isinstance(gateway_cfg, dict):
                self.errors.append(
                    "language_model.runtime_mode='gateway' requires language_model.gateway object"
                )
            else:
                base_url = str(gateway_cfg.get("base_url", "")).strip()
                if not base_url:
                    self.errors.append(
                        "language_model.runtime_mode='gateway' requires language_model.gateway.base_url"
                    )
                api_key_env = str(gateway_cfg.get("api_key_env", "")).strip()
                if not api_key_env:
                    self.errors.append(
                        "language_model.runtime_mode='gateway' requires language_model.gateway.api_key_env"
                    )

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

            # No tier-specific blocking in unified OSS mode.

    def _validate_tier_features(self, playbook_data: Dict[str, Any]):
        """Validate tier-specific features."""
        metadata = playbook_data.get("metadata", {})
        spec = playbook_data.get("spec", {})
        tier = metadata.get("level", "oracles")

        # No tier-gated spec features in unified OSS mode.
        genies_only_features = []

        if tier == "oracles":
            for feature in genies_only_features:
                if feature in spec:
                    self.errors.append(f"Feature '{feature}' requires Genies tier")

        # Validate specific feature configurations
        if "memory" in spec:
            self._validate_memory_config(spec["memory"])

        if "tool_calling" in spec:
            self._validate_tool_calling_config(spec["tool_calling"])

        if "retrieval" in spec:
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
            retriever = str(retrieval_config["retriever_type"]).strip()
            valid_retrievers = {
                "chroma",
                "chromadb",
                "weaviate",
                "lancedb",
                "lance",
                "faiss",
                "qdrant",
                "milvus",
                "pinecone",
                "colbertv2",
                "custom",
            }
            if retriever.lower() not in valid_retrievers:
                self.errors.append(
                    f"Invalid retriever_type: {retrieval_config['retriever_type']}"
                )

    def _validate_rlm_config(self, rlm_config: Dict[str, Any]):
        """Validate DSPy RLM configuration."""
        if not isinstance(rlm_config, dict):
            self.errors.append("rlm configuration must be an object")
            return

        if "enabled" in rlm_config and not isinstance(rlm_config["enabled"], bool):
            self.errors.append("rlm.enabled must be a boolean")

        if "max_iters" in rlm_config:
            max_iters = rlm_config["max_iters"]
            if not isinstance(max_iters, int) or max_iters < 1 or max_iters > 50:
                self.errors.append("rlm.max_iters must be an integer between 1 and 50")

        if "max_llm_calls" in rlm_config:
            max_llm_calls = rlm_config["max_llm_calls"]
            if (
                not isinstance(max_llm_calls, int)
                or max_llm_calls < 1
                or max_llm_calls > 100
            ):
                self.errors.append(
                    "rlm.max_llm_calls must be an integer between 1 and 100"
                )

    def _validate_dspy_config(self, dspy_config: Dict[str, Any], spec: Dict[str, Any]):
        """Validate SuperSpec DSPy automation block (GEPA + RLM focus)."""
        if not isinstance(dspy_config, dict):
            self.errors.append("dspy configuration must be an object")
            return

        def _validate_adapter_block(
            adapter_cfg: Dict[str, Any], prefix: str = "dspy.adapter"
        ) -> None:
            mode = adapter_cfg.get("mode")
            valid_adapter_modes = ["manual", "auto"]
            if mode is not None and mode not in valid_adapter_modes:
                self.errors.append(
                    f"{prefix}.mode must be one of {', '.join(valid_adapter_modes)}"
                )

            adapter_type = adapter_cfg.get("type")
            valid_adapter_types = ["chat", "json", "xml", "twostep"]
            if adapter_type is not None and adapter_type not in valid_adapter_types:
                self.errors.append(
                    f"{prefix}.type must be one of {', '.join(valid_adapter_types)}"
                )
            fallback_adapter = adapter_cfg.get("fallback_adapter")
            if (
                fallback_adapter is not None
                and fallback_adapter not in valid_adapter_types
            ):
                self.errors.append(
                    f"{prefix}.fallback_adapter must be one of {', '.join(valid_adapter_types)}"
                )
            if "native_function_calling" in adapter_cfg and not isinstance(
                adapter_cfg.get("native_function_calling"), bool
            ):
                self.errors.append(
                    f"{prefix}.native_function_calling must be a boolean"
                )
            if "strict" in adapter_cfg and not isinstance(
                adapter_cfg.get("strict"), bool
            ):
                self.errors.append(f"{prefix}.strict must be a boolean")
            if "retry_on_parse_error" in adapter_cfg:
                retry = adapter_cfg.get("retry_on_parse_error")
                if not isinstance(retry, int) or retry < 0 or retry > 10:
                    self.errors.append(
                        f"{prefix}.retry_on_parse_error must be an integer between 0 and 10"
                    )

        module = dspy_config.get("module")
        valid_modules = [
            "predict",
            "chain_of_thought",
            "react",
            "rlm",
            "program_of_thought",
            "parallel",
        ]
        if module is not None and module not in valid_modules:
            self.errors.append(
                f"Invalid dspy.module '{module}'. Valid options: {', '.join(valid_modules)}"
            )

        module_params = dspy_config.get("module_params")
        if module_params is not None:
            if not isinstance(module_params, dict):
                self.errors.append("dspy.module_params must be an object")
            else:
                if "max_iterations" in module_params:
                    v = module_params["max_iterations"]
                    if not isinstance(v, int) or v < 1 or v > 100:
                        self.errors.append(
                            "dspy.module_params.max_iterations must be an integer between 1 and 100"
                        )
                if "parallel_workers" in module_params:
                    v = module_params["parallel_workers"]
                    if not isinstance(v, int) or v < 1 or v > 32:
                        self.errors.append(
                            "dspy.module_params.parallel_workers must be an integer between 1 and 32"
                        )
                if "temperature" in module_params:
                    v = module_params["temperature"]
                    if not isinstance(v, (int, float)) or v < 0 or v > 2:
                        self.errors.append(
                            "dspy.module_params.temperature must be a number between 0 and 2"
                        )
                if "max_tokens" in module_params:
                    v = module_params["max_tokens"]
                    if not isinstance(v, int) or v < 1 or v > 200000:
                        self.errors.append(
                            "dspy.module_params.max_tokens must be an integer between 1 and 200000"
                        )

        adapter_cfg = dspy_config.get("adapter")
        if adapter_cfg is not None:
            if not isinstance(adapter_cfg, dict):
                self.errors.append("dspy.adapter must be an object")
            else:
                _validate_adapter_block(adapter_cfg, prefix="dspy.adapter")

        signature_cfg = dspy_config.get("signature")
        if signature_cfg is not None:
            if not isinstance(signature_cfg, dict):
                self.errors.append("dspy.signature must be an object")
            else:
                output_mode = signature_cfg.get("output_mode")
                valid_output_modes = ["simple", "structured"]
                if output_mode is not None and output_mode not in valid_output_modes:
                    self.errors.append(
                        f"dspy.signature.output_mode must be one of {', '.join(valid_output_modes)}"
                    )

        assertions_cfg = dspy_config.get("assertions")
        if assertions_cfg is not None:
            if not isinstance(assertions_cfg, dict):
                self.errors.append("dspy.assertions must be an object")
            else:
                if "enabled" in assertions_cfg and not isinstance(
                    assertions_cfg.get("enabled"), bool
                ):
                    self.errors.append("dspy.assertions.enabled must be a boolean")

                mode = assertions_cfg.get("mode")
                valid_modes = ["fail_fast", "warn_only"]
                if mode is not None and mode not in valid_modes:
                    self.errors.append(
                        f"dspy.assertions.mode must be one of {', '.join(valid_modes)}"
                    )
                if "metric_weight" in assertions_cfg:
                    metric_weight = assertions_cfg.get("metric_weight")
                    if not isinstance(metric_weight, (int, float)) or not (
                        0.0 <= float(metric_weight) <= 1.0
                    ):
                        self.errors.append(
                            "dspy.assertions.metric_weight must be a number between 0 and 1"
                        )

                for list_key in ["required_fields", "non_empty"]:
                    value = assertions_cfg.get(list_key)
                    if value is not None:
                        if not isinstance(value, list) or not all(
                            isinstance(v, str) for v in value
                        ):
                            self.errors.append(
                                f"dspy.assertions.{list_key} must be a list of strings"
                            )

                enum_cfg = assertions_cfg.get("enum")
                if enum_cfg is not None:
                    if not isinstance(enum_cfg, dict):
                        self.errors.append("dspy.assertions.enum must be an object")
                    else:
                        for key, values in enum_cfg.items():
                            if not isinstance(key, str):
                                self.errors.append(
                                    "dspy.assertions.enum keys must be strings"
                                )
                                continue
                            if not isinstance(values, list) or not all(
                                isinstance(v, str) for v in values
                            ):
                                self.errors.append(
                                    f"dspy.assertions.enum.{key} must be a list of strings"
                                )

                max_length_cfg = assertions_cfg.get("max_length")
                if max_length_cfg is not None:
                    if not isinstance(max_length_cfg, dict):
                        self.errors.append(
                            "dspy.assertions.max_length must be an object"
                        )
                    else:
                        for key, value in max_length_cfg.items():
                            if not isinstance(key, str):
                                self.errors.append(
                                    "dspy.assertions.max_length keys must be strings"
                                )
                                continue
                            if not isinstance(value, int) or value < 0:
                                self.errors.append(
                                    f"dspy.assertions.max_length.{key} must be a non-negative integer"
                                )

                regex_cfg = assertions_cfg.get("custom_regex")
                if regex_cfg is not None:
                    if not isinstance(regex_cfg, dict):
                        self.errors.append(
                            "dspy.assertions.custom_regex must be an object"
                        )
                    else:
                        for key, pattern in regex_cfg.items():
                            if not isinstance(key, str) or not isinstance(pattern, str):
                                self.errors.append(
                                    "dspy.assertions.custom_regex entries must be string:string"
                                )

        modules_cfg = dspy_config.get("modules")
        if modules_cfg is not None:
            if not isinstance(modules_cfg, list):
                self.errors.append("dspy.modules must be a list")
            else:
                for idx, module_cfg in enumerate(modules_cfg):
                    prefix = f"dspy.modules[{idx}]"
                    if not isinstance(module_cfg, dict):
                        self.errors.append(f"{prefix} must be an object")
                        continue
                    name = module_cfg.get("name")
                    if not isinstance(name, str) or name not in valid_modules:
                        self.errors.append(
                            f"{prefix}.name must be one of {', '.join(valid_modules)}"
                        )
                    module_adapter_cfg = module_cfg.get("adapter")
                    if module_adapter_cfg is not None:
                        if not isinstance(module_adapter_cfg, dict):
                            self.errors.append(f"{prefix}.adapter must be an object")
                        else:
                            _validate_adapter_block(
                                module_adapter_cfg, prefix=f"{prefix}.adapter"
                            )

        tools_cfg = dspy_config.get("tools")
        if tools_cfg is not None:
            if not isinstance(tools_cfg, dict):
                self.errors.append("dspy.tools must be an object")
            else:
                mode = tools_cfg.get("mode")
                valid_modes = [
                    "none",
                    "builtin",
                    "mcp",
                    "stackone",
                    "stackone_discovery",
                ]
                if mode is not None and mode not in valid_modes:
                    self.errors.append(
                        f"dspy.tools.mode must be one of {', '.join(valid_modes)}"
                    )
                if "builtin_tools" in tools_cfg and not isinstance(
                    tools_cfg.get("builtin_tools"), list
                ):
                    self.errors.append("dspy.tools.builtin_tools must be a list")
                if "mcp_servers" in tools_cfg and not isinstance(
                    tools_cfg.get("mcp_servers"), list
                ):
                    self.errors.append("dspy.tools.mcp_servers must be a list")
                stackone_cfg = tools_cfg.get("stackone")
                if stackone_cfg is not None:
                    if not isinstance(stackone_cfg, dict):
                        self.errors.append("dspy.tools.stackone must be an object")
                    else:
                        for list_key in ["account_ids", "providers", "actions"]:
                            if list_key in stackone_cfg and not isinstance(
                                stackone_cfg.get(list_key), list
                            ):
                                self.errors.append(
                                    f"dspy.tools.stackone.{list_key} must be a list"
                                )
                        if "enabled" in stackone_cfg and not isinstance(
                            stackone_cfg.get("enabled"), bool
                        ):
                            self.errors.append(
                                "dspy.tools.stackone.enabled must be a boolean"
                            )
                        if "discovery_mode" in stackone_cfg and not isinstance(
                            stackone_cfg.get("discovery_mode"), bool
                        ):
                            self.errors.append(
                                "dspy.tools.stackone.discovery_mode must be a boolean"
                            )
                        if "fallback_unfiltered" in stackone_cfg and not isinstance(
                            stackone_cfg.get("fallback_unfiltered"), bool
                        ):
                            self.errors.append(
                                "dspy.tools.stackone.fallback_unfiltered must be a boolean"
                            )

        # Validate DSPy RLM section
        rlm_cfg = dspy_config.get("rlm")
        if rlm_cfg is not None:
            if not isinstance(rlm_cfg, dict):
                self.errors.append("dspy.rlm must be an object")
            else:
                # Reuse existing RLM validator by mapping keys.
                normalized_rlm = {
                    "enabled": rlm_cfg.get("enabled", False),
                    "max_iters": rlm_cfg.get(
                        "max_iters", rlm_cfg.get("max_iterations")
                    ),
                    "max_llm_calls": rlm_cfg.get("max_llm_calls"),
                }
                self._validate_rlm_config(normalized_rlm)

        # Validate GEPA-only optimizer section
        gepa_cfg = dspy_config.get("gepa")
        if gepa_cfg is not None:
            if not isinstance(gepa_cfg, dict):
                self.errors.append("dspy.gepa must be an object")
            else:
                if "enabled" in gepa_cfg and not isinstance(gepa_cfg["enabled"], bool):
                    self.errors.append("dspy.gepa.enabled must be a boolean")

                auto = gepa_cfg.get("auto")
                valid_auto = ["light", "medium", "heavy"]
                if auto is not None and auto not in valid_auto:
                    self.errors.append(
                        f"dspy.gepa.auto must be one of {', '.join(valid_auto)}"
                    )

                if (
                    gepa_cfg.get("auto") is not None
                    and gepa_cfg.get("max_full_evals") is not None
                ):
                    self.errors.append(
                        "dspy.gepa: use either 'auto' or 'max_full_evals', not both."
                    )
                if (
                    gepa_cfg.get("auto") is not None
                    and gepa_cfg.get("max_metric_calls") is not None
                ):
                    self.errors.append(
                        "dspy.gepa: use either 'auto' or 'max_metric_calls', not both."
                    )

                int_ranges = {
                    "max_full_evals": (1, 10000),
                    "max_metric_calls": (1, 100000),
                    "reflection_minibatch_size": (1, 1000),
                    "max_merge_invocations": (0, 1000),
                    "seed": (0, 2_147_483_647),
                }
                for key, (low, high) in int_ranges.items():
                    if key in gepa_cfg and gepa_cfg[key] is not None:
                        val = gepa_cfg[key]
                        if not isinstance(val, int) or val < low or val > high:
                            self.errors.append(
                                f"dspy.gepa.{key} must be an integer between {low} and {high}"
                            )

                bool_fields = ["skip_perfect_score", "use_merge", "track_stats"]
                for key in bool_fields:
                    if key in gepa_cfg and not isinstance(gepa_cfg[key], bool):
                        self.errors.append(f"dspy.gepa.{key} must be a boolean")

        # Guard against conflicting parallel config style.
        if "optimization" in spec and isinstance(spec.get("optimization"), dict):
            opt = spec["optimization"]
            optimizer_name = (
                (opt.get("optimizer") or {}).get("name")
                if isinstance(opt.get("optimizer"), dict)
                else None
            )
            if optimizer_name and optimizer_name != "GEPA" and gepa_cfg:
                self.warnings.append(
                    "Both spec.optimization and dspy.gepa are set. dspy.gepa will be treated as the source of truth for DSPy compile."
                )

    def _validate_optimization_config(self, optimization_config: Dict[str, Any]):
        """Validate generic optimization config with GEPA-focused params."""
        if not isinstance(optimization_config, dict):
            self.errors.append("optimization must be an object")
            return

        optimizer = optimization_config.get("optimizer")
        if optimizer is None:
            return
        if not isinstance(optimizer, dict):
            self.errors.append("optimization.optimizer must be an object")
            return

        params = optimizer.get("params")
        if params is None:
            return
        if not isinstance(params, dict):
            self.errors.append("optimization.optimizer.params must be an object")
            return

        backend = params.get("backend")
        if backend is not None:
            valid_backends = {"universal", "pydantic_native"}
            if str(backend).strip().lower() not in valid_backends:
                self.errors.append(
                    "optimization.optimizer.params.backend must be one of: universal, pydantic_native"
                )

    def _validate_pydantic_ai_config(self, pydantic_cfg: Dict[str, Any]):
        """Validate spec.pydantic_ai configuration block."""
        if not isinstance(pydantic_cfg, dict):
            self.errors.append("pydantic_ai must be an object")
            return

        rlm_cfg = pydantic_cfg.get("rlm")
        if rlm_cfg is None:
            return
        if not isinstance(rlm_cfg, dict):
            self.errors.append("pydantic_ai.rlm must be an object")
            return

        if "enabled" in rlm_cfg and not isinstance(rlm_cfg["enabled"], bool):
            self.errors.append("pydantic_ai.rlm.enabled must be a boolean")

        mode = rlm_cfg.get("mode")
        if mode is not None and mode not in {"assist", "replace"}:
            self.errors.append("pydantic_ai.rlm.mode must be one of: assist, replace")

        backend = rlm_cfg.get("backend")
        if backend is not None and not isinstance(backend, str):
            self.errors.append("pydantic_ai.rlm.backend must be a string")

        environment = rlm_cfg.get("environment")
        if environment is not None and not isinstance(environment, str):
            self.errors.append("pydantic_ai.rlm.environment must be a string")

        max_iterations = rlm_cfg.get("max_iterations")
        if max_iterations is not None and (
            not isinstance(max_iterations, int)
            or max_iterations < 1
            or max_iterations > 50
        ):
            self.errors.append(
                "pydantic_ai.rlm.max_iterations must be an integer between 1 and 50"
            )

        max_depth = rlm_cfg.get("max_depth")
        if max_depth is not None and (
            not isinstance(max_depth, int) or max_depth < 1 or max_depth > 4
        ):
            self.errors.append(
                "pydantic_ai.rlm.max_depth must be an integer between 1 and 4"
            )

        for bool_key in ("verbose", "persistent"):
            if bool_key in rlm_cfg and not isinstance(rlm_cfg.get(bool_key), bool):
                self.errors.append(f"pydantic_ai.rlm.{bool_key} must be a boolean")

        for str_key in ("task_model", "api_key_env", "api_base"):
            if (
                str_key in rlm_cfg
                and rlm_cfg.get(str_key) is not None
                and not isinstance(rlm_cfg.get(str_key), str)
            ):
                self.errors.append(f"pydantic_ai.rlm.{str_key} must be a string")

        logger_cfg = rlm_cfg.get("logger")
        if logger_cfg is not None:
            if not isinstance(logger_cfg, dict):
                self.errors.append("pydantic_ai.rlm.logger must be an object")
            else:
                if "enabled" in logger_cfg and not isinstance(
                    logger_cfg.get("enabled"), bool
                ):
                    self.errors.append(
                        "pydantic_ai.rlm.logger.enabled must be a boolean"
                    )
                for key in ("log_dir", "file_name"):
                    if (
                        key in logger_cfg
                        and logger_cfg.get(key) is not None
                        and not isinstance(logger_cfg.get(key), str)
                    ):
                        self.errors.append(
                            f"pydantic_ai.rlm.logger.{key} must be a string"
                        )

    def _validate_openai_agent_config(self, openai_cfg: Dict[str, Any]):
        """Validate spec.openai_agent configuration block."""
        if not isinstance(openai_cfg, dict):
            self.errors.append("openai_agent must be an object")
            return

        rlm_cfg = openai_cfg.get("rlm")
        if rlm_cfg is None:
            return
        if not isinstance(rlm_cfg, dict):
            self.errors.append("openai_agent.rlm must be an object")
            return

        if "enabled" in rlm_cfg and not isinstance(rlm_cfg["enabled"], bool):
            self.errors.append("openai_agent.rlm.enabled must be a boolean")

        mode = rlm_cfg.get("mode")
        if mode is not None and mode not in {"assist", "replace"}:
            self.errors.append("openai_agent.rlm.mode must be one of: assist, replace")

        backend = rlm_cfg.get("backend")
        if backend is not None and not isinstance(backend, str):
            self.errors.append("openai_agent.rlm.backend must be a string")

        environment = rlm_cfg.get("environment")
        if environment is not None and not isinstance(environment, str):
            self.errors.append("openai_agent.rlm.environment must be a string")

        max_iterations = rlm_cfg.get("max_iterations")
        if max_iterations is not None and (
            not isinstance(max_iterations, int)
            or max_iterations < 1
            or max_iterations > 50
        ):
            self.errors.append(
                "openai_agent.rlm.max_iterations must be an integer between 1 and 50"
            )

        max_depth = rlm_cfg.get("max_depth")
        if max_depth is not None and (
            not isinstance(max_depth, int) or max_depth < 1 or max_depth > 4
        ):
            self.errors.append(
                "openai_agent.rlm.max_depth must be an integer between 1 and 4"
            )

        for bool_key in ("verbose", "persistent"):
            if bool_key in rlm_cfg and not isinstance(rlm_cfg.get(bool_key), bool):
                self.errors.append(f"openai_agent.rlm.{bool_key} must be a boolean")

        for str_key in ("task_model", "api_key_env", "api_base"):
            if (
                str_key in rlm_cfg
                and rlm_cfg.get(str_key) is not None
                and not isinstance(rlm_cfg.get(str_key), str)
            ):
                self.errors.append(f"openai_agent.rlm.{str_key} must be a string")

        logger_cfg = rlm_cfg.get("logger")
        if logger_cfg is not None:
            if not isinstance(logger_cfg, dict):
                self.errors.append("openai_agent.rlm.logger must be an object")
            else:
                if "enabled" in logger_cfg and not isinstance(
                    logger_cfg.get("enabled"), bool
                ):
                    self.errors.append(
                        "openai_agent.rlm.logger.enabled must be a boolean"
                    )
                for key in ("log_dir", "file_name"):
                    if (
                        key in logger_cfg
                        and logger_cfg.get(key) is not None
                        and not isinstance(logger_cfg.get(key), str)
                    ):
                        self.errors.append(
                            f"openai_agent.rlm.logger.{key} must be a string"
                        )

    def _validate_google_adk_config(self, adk_cfg: Dict[str, Any]):
        """Validate spec.google_adk configuration block."""
        if not isinstance(adk_cfg, dict):
            self.errors.append("google_adk must be an object")
            return

        rlm_cfg = adk_cfg.get("rlm")
        if rlm_cfg is None:
            return
        if not isinstance(rlm_cfg, dict):
            self.errors.append("google_adk.rlm must be an object")
            return

        if "enabled" in rlm_cfg and not isinstance(rlm_cfg["enabled"], bool):
            self.errors.append("google_adk.rlm.enabled must be a boolean")

        mode = rlm_cfg.get("mode")
        if mode is not None and mode not in {"assist", "replace"}:
            self.errors.append("google_adk.rlm.mode must be one of: assist, replace")

        backend = rlm_cfg.get("backend")
        if backend is not None and not isinstance(backend, str):
            self.errors.append("google_adk.rlm.backend must be a string")

        environment = rlm_cfg.get("environment")
        if environment is not None and not isinstance(environment, str):
            self.errors.append("google_adk.rlm.environment must be a string")

        max_iterations = rlm_cfg.get("max_iterations")
        if max_iterations is not None and (
            not isinstance(max_iterations, int)
            or max_iterations < 1
            or max_iterations > 50
        ):
            self.errors.append(
                "google_adk.rlm.max_iterations must be an integer between 1 and 50"
            )

        max_depth = rlm_cfg.get("max_depth")
        if max_depth is not None and (
            not isinstance(max_depth, int) or max_depth < 1 or max_depth > 4
        ):
            self.errors.append(
                "google_adk.rlm.max_depth must be an integer between 1 and 4"
            )

        for bool_key in ("verbose", "persistent"):
            if bool_key in rlm_cfg and not isinstance(rlm_cfg.get(bool_key), bool):
                self.errors.append(f"google_adk.rlm.{bool_key} must be a boolean")

        for str_key in ("task_model", "api_key_env", "api_base"):
            if (
                str_key in rlm_cfg
                and rlm_cfg.get(str_key) is not None
                and not isinstance(rlm_cfg.get(str_key), str)
            ):
                self.errors.append(f"google_adk.rlm.{str_key} must be a string")

        logger_cfg = rlm_cfg.get("logger")
        if logger_cfg is not None:
            if not isinstance(logger_cfg, dict):
                self.errors.append("google_adk.rlm.logger must be an object")
            else:
                if "enabled" in logger_cfg and not isinstance(
                    logger_cfg.get("enabled"), bool
                ):
                    self.errors.append(
                        "google_adk.rlm.logger.enabled must be a boolean"
                    )
                for key in ("log_dir", "file_name"):
                    if (
                        key in logger_cfg
                        and logger_cfg.get(key) is not None
                        and not isinstance(logger_cfg.get(key), str)
                    ):
                        self.errors.append(
                            f"google_adk.rlm.logger.{key} must be a string"
                        )

    def _validate_deepagents_config(self, deep_cfg: Dict[str, Any]):
        """Validate spec.deepagents configuration block."""
        if not isinstance(deep_cfg, dict):
            self.errors.append("deepagents must be an object")
            return

        rlm_cfg = deep_cfg.get("rlm")
        if rlm_cfg is None:
            return
        if not isinstance(rlm_cfg, dict):
            self.errors.append("deepagents.rlm must be an object")
            return

        if "enabled" in rlm_cfg and not isinstance(rlm_cfg["enabled"], bool):
            self.errors.append("deepagents.rlm.enabled must be a boolean")

        mode = rlm_cfg.get("mode")
        if mode is not None and mode not in {"assist", "replace"}:
            self.errors.append("deepagents.rlm.mode must be one of: assist, replace")

        backend = rlm_cfg.get("backend")
        if backend is not None and not isinstance(backend, str):
            self.errors.append("deepagents.rlm.backend must be a string")

        environment = rlm_cfg.get("environment")
        if environment is not None and not isinstance(environment, str):
            self.errors.append("deepagents.rlm.environment must be a string")

        max_iterations = rlm_cfg.get("max_iterations")
        if max_iterations is not None and (
            not isinstance(max_iterations, int)
            or max_iterations < 1
            or max_iterations > 50
        ):
            self.errors.append(
                "deepagents.rlm.max_iterations must be an integer between 1 and 50"
            )

        max_depth = rlm_cfg.get("max_depth")
        if max_depth is not None and (
            not isinstance(max_depth, int) or max_depth < 1 or max_depth > 4
        ):
            self.errors.append(
                "deepagents.rlm.max_depth must be an integer between 1 and 4"
            )

        for bool_key in ("verbose", "persistent"):
            if bool_key in rlm_cfg and not isinstance(rlm_cfg.get(bool_key), bool):
                self.errors.append(f"deepagents.rlm.{bool_key} must be a boolean")

        for str_key in ("task_model", "api_key_env", "api_base"):
            if (
                str_key in rlm_cfg
                and rlm_cfg.get(str_key) is not None
                and not isinstance(rlm_cfg.get(str_key), str)
            ):
                self.errors.append(f"deepagents.rlm.{str_key} must be a string")

        logger_cfg = rlm_cfg.get("logger")
        if logger_cfg is not None:
            if not isinstance(logger_cfg, dict):
                self.errors.append("deepagents.rlm.logger must be an object")
            else:
                if "enabled" in logger_cfg and not isinstance(
                    logger_cfg.get("enabled"), bool
                ):
                    self.errors.append(
                        "deepagents.rlm.logger.enabled must be a boolean"
                    )
                for key in ("log_dir", "file_name"):
                    if (
                        key in logger_cfg
                        and logger_cfg.get(key) is not None
                        and not isinstance(logger_cfg.get(key), str)
                    ):
                        self.errors.append(
                            f"deepagents.rlm.logger.{key} must be a string"
                        )

    def _validate_crewai_config(self, crew_cfg: Dict[str, Any]):
        """Validate spec.crewai configuration block."""
        if not isinstance(crew_cfg, dict):
            self.errors.append("crewai must be an object")
            return

        rlm_cfg = crew_cfg.get("rlm")
        if rlm_cfg is None:
            return
        if not isinstance(rlm_cfg, dict):
            self.errors.append("crewai.rlm must be an object")
            return

        if "enabled" in rlm_cfg and not isinstance(rlm_cfg["enabled"], bool):
            self.errors.append("crewai.rlm.enabled must be a boolean")

        mode = rlm_cfg.get("mode")
        if mode is not None and mode not in {"assist", "replace"}:
            self.errors.append("crewai.rlm.mode must be one of: assist, replace")

        backend = rlm_cfg.get("backend")
        if backend is not None and not isinstance(backend, str):
            self.errors.append("crewai.rlm.backend must be a string")

        environment = rlm_cfg.get("environment")
        if environment is not None and not isinstance(environment, str):
            self.errors.append("crewai.rlm.environment must be a string")

        max_iterations = rlm_cfg.get("max_iterations")
        if max_iterations is not None and (
            not isinstance(max_iterations, int)
            or max_iterations < 1
            or max_iterations > 50
        ):
            self.errors.append(
                "crewai.rlm.max_iterations must be an integer between 1 and 50"
            )

        max_depth = rlm_cfg.get("max_depth")
        if max_depth is not None and (
            not isinstance(max_depth, int) or max_depth < 1 or max_depth > 4
        ):
            self.errors.append(
                "crewai.rlm.max_depth must be an integer between 1 and 4"
            )

        for bool_key in ("verbose", "persistent"):
            if bool_key in rlm_cfg and not isinstance(rlm_cfg.get(bool_key), bool):
                self.errors.append(f"crewai.rlm.{bool_key} must be a boolean")

        for str_key in ("task_model", "api_key_env", "api_base"):
            if (
                str_key in rlm_cfg
                and rlm_cfg.get(str_key) is not None
                and not isinstance(rlm_cfg.get(str_key), str)
            ):
                self.errors.append(f"crewai.rlm.{str_key} must be a string")

        logger_cfg = rlm_cfg.get("logger")
        if logger_cfg is not None:
            if not isinstance(logger_cfg, dict):
                self.errors.append("crewai.rlm.logger must be an object")
            else:
                if "enabled" in logger_cfg and not isinstance(
                    logger_cfg.get("enabled"), bool
                ):
                    self.errors.append("crewai.rlm.logger.enabled must be a boolean")
                for key in ("log_dir", "file_name"):
                    if (
                        key in logger_cfg
                        and logger_cfg.get(key) is not None
                        and not isinstance(logger_cfg.get(key), str)
                    ):
                        self.errors.append(f"crewai.rlm.logger.{key} must be a string")

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
