"""
SuperSpec Schema - Core validation schemas and tier-specific rules

Provides structured schema definitions for the SuperSpec DSL.
Used for validation, code completion, and documentation generation.
"""

from typing import Dict, List, Any
from enum import Enum


class AgentTier(Enum):
    """Supported agent tiers."""

    ORACLES = "oracles"
    GENIES = "genies"


class SuperSpecXSchema:
    """Schema definitions for SuperSpec DSL."""

    # Valid enumerations
    VALID_API_VERSIONS = ["agent/v1"]
    VALID_KINDS = ["AgentSpec"]
    VALID_TIERS = ["oracles", "genies", "protocols", "superagents", "sovereigns"]
    VALID_STAGES = ["alpha", "beta", "stable"]
    VALID_AGENT_TYPES = [
        "Autonomous",
        "Supervised",
        "Interactive",
        "Reactive",
        "Deliberative",
        "Hybrid",
    ]

    VALID_NAMESPACES = [
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

    VALID_LM_LOCATIONS = ["local", "self-hosted", "cloud"]
    VALID_LM_PROVIDERS = [
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
    VALID_MODEL_TYPES = ["chat", "text", "completion"]
    VALID_MODALITIES = ["text", "image", "audio", "video"]

    VALID_COMMUNICATION_STYLES = ["formal", "casual", "technical", "conversational"]
    VALID_COMMUNICATION_TONES = [
        "professional",
        "friendly",
        "authoritative",
        "supportive",
    ]
    VALID_VERBOSITY_LEVELS = ["concise", "detailed", "adaptive"]

    VALID_TASK_STYLES = ["chain_of_thought", "direct", "structured"]
    VALID_INPUT_TYPES = ["str", "int", "bool", "float", "list[str]", "dict[str,Any]"]
    VALID_OUTPUT_TYPES = ["str", "int", "bool", "float", "list[str]", "dict[str,Any]"]

    # Agent flow step types by tier
    VALID_AGENTFLOW_TYPES = {
        "oracles": ["Generate", "Think", "Compare", "Route"],
        "genies": ["Generate", "Think", "ActWithTools", "Search", "Compare", "Route"],
    }

    VALID_RETRY_STRATEGIES = ["exponential", "linear", "fixed"]

    # Genies-specific features
    VALID_MEMORY_BACKENDS = ["file", "sqlite", "redis"]
    VALID_MEMORY_RETENTION_POLICIES = ["lru", "fifo", "priority"]
    VALID_MEMORY_EPISODE_BOUNDARIES = ["time", "task", "manual", "interaction"]
    VALID_MEMORY_COMPRESSION_STRATEGIES = ["summarization", "key_extraction", "both"]
    VALID_MEMORY_SCOPES = ["global", "session", "task", "local"]

    VALID_RETRIEVER_TYPES = [
        "ColBERTv2",
        "Weaviate",
        "ChromaDB",
        "Pinecone",
        "FAISS",
        "Custom",
    ]
    VALID_TOOL_SELECTION_STRATEGIES = ["automatic", "manual", "hybrid"]

    VALID_BUILTIN_TOOLS = [
        "calculator",
        "web_search",
        "file_operations",
        "code_executor",
        "api_caller",
        "data_processor",
        "email_sender",
        "calendar",
        "database_query",
    ]

    # Evaluation and optimization
    VALID_BUILTIN_METRICS = [
        "answer_exact_match",
        "answer_passage_match",
        "semantic_f1",
        "rouge_l",
        "bleu",
        "meteor",
        "answer_correctness",
        "faithfulness",
        "context_relevance",
    ]

    VALID_VALIDATION_TYPES = [
        "syntax",
        "semantic",
        "functional",
        "style",
        "requirements",
        "rule_based",
        "llm_judge",
        "statistical",
    ]

    # DSPy Optimizers - All supported optimizers
    VALID_DSPY_OPTIMIZERS = [
        "GEPA",
        "SIMBA",
        "MIPROv2",
        "BootstrapFewShot",
        "BetterTogether",
        "COPRO",
        "KNNFewShot",
        "LabeledFewShot",
    ]

    # SuperSpec DSPy automation surface (current focus)
    VALID_DSPY_MODULES = [
        "predict",
        "chain_of_thought",
        "react",
        "rlm",
        "program_of_thought",
        "parallel",
    ]
    VALID_DSPY_AUTOMATION_OPTIMIZERS = ["GEPA"]

    # GEPA-specific configuration options
    VALID_GEPA_BUDGETS = ["minimal", "light", "medium", "heavy"]
    VALID_GEPA_METRICS = [
        "answer_exact_match",
        "advanced_math_feedback",
        "multi_component_enterprise_feedback",
        "vulnerability_detection_feedback",
        "privacy_preservation_feedback",
        "medical_accuracy_feedback",
        "legal_analysis_feedback",
    ]

    # Optimizer compatibility by tier - Allow all optimizers for all tiers for now
    # Tier validation can be applied later as needed
    OPTIMIZER_TIER_COMPATIBILITY = {
        "oracles": [
            "GEPA",
            "SIMBA",
            "MIPROv2",
            "BootstrapFewShot",
            "BetterTogether",
            "COPRO",
            "KNNFewShot",
            "LabeledFewShot",
        ],
        "genies": [
            "GEPA",
            "SIMBA",
            "MIPROv2",
            "BootstrapFewShot",
            "BetterTogether",
            "COPRO",
            "KNNFewShot",
            "LabeledFewShot",
        ],
        "protocols": [
            "GEPA",
            "SIMBA",
            "MIPROv2",
            "BootstrapFewShot",
            "BetterTogether",
            "COPRO",
            "KNNFewShot",
            "LabeledFewShot",
        ],
        "superagents": [
            "GEPA",
            "SIMBA",
            "MIPROv2",
            "BootstrapFewShot",
            "BetterTogether",
            "COPRO",
            "KNNFewShot",
            "LabeledFewShot",
        ],
        "sovereigns": [
            "GEPA",
            "SIMBA",
            "MIPROv2",
            "BootstrapFewShot",
            "BetterTogether",
            "COPRO",
            "KNNFewShot",
            "LabeledFewShot",
        ],
    }

    VALID_OPTIMIZATION_STRATEGIES = ["few_shot_bootstrapping"]  # Legacy - deprecated
    VALID_DATA_SOURCES = ["file", "database", "api", "synthetic", "streaming"]
    VALID_DATA_FORMATS = ["json", "csv", "jsonl", "parquet", "hf_dataset"]

    # Runtime and deployment
    VALID_CACHE_BACKENDS = ["memory", "disk", "redis"]
    VALID_CACHE_KEY_STRATEGIES = ["content", "signature", "custom"]
    VALID_LOG_LEVELS = ["debug", "info", "warn", "error"]
    VALID_BACKOFF_STRATEGIES = ["exponential", "linear", "fixed"]

    # Security and compliance
    VALID_COMPLIANCE_FRAMEWORKS = ["GDPR", "HIPAA", "SOC2", "PCI_DSS"]

    GENIES_ONLY_FEATURES = [
        "memory",
        "tool_calling",
        "retrieval",
        "streaming",
        "react_config",
    ]

    @classmethod
    def get_tier_features(cls, tier: str) -> Dict[str, Any]:
        """Get allowed features for a tier."""
        if tier == "oracles":
            return {
                "agentflow_types": cls.VALID_AGENTFLOW_TYPES["oracles"],
                "forbidden_features": cls.GENIES_ONLY_FEATURES,
            }
        elif tier == "genies":
            return {
                "agentflow_types": cls.VALID_AGENTFLOW_TYPES["genies"],
                "allowed_features": cls.GENIES_ONLY_FEATURES,
            }
        return {}

    @classmethod
    def validate_tier_compatibility(cls, tier: str, features: List[str]) -> List[str]:
        """Validate tier compatibility with features."""
        issues = []
        tier_features = cls.get_tier_features(tier)

        if tier == "oracles":
            forbidden = tier_features.get("forbidden_features", [])
            for feature in features:
                if feature in forbidden:
                    issues.append(f"Feature '{feature}' requires Genies tier")

        return issues

    @classmethod
    def get_metadata_schema(cls) -> Dict[str, Any]:
        """Get metadata section schema."""
        return {
            "type": "object",
            "required": ["name", "id", "version"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Human-readable agent name",
                    "maxLength": 100,
                },
                "id": {
                    "type": "string",
                    "description": "Unique agent identifier",
                    "pattern": "^[a-z0-9-_]+$",
                    "maxLength": 50,
                },
                "version": {
                    "type": "string",
                    "description": "Semantic version",
                    "pattern": r"^\d+\.\d+\.\d+$",
                },
                "namespace": {
                    "type": "string",
                    "enum": cls.VALID_NAMESPACES,
                    "description": "Logical grouping namespace",
                },
                "level": {
                    "type": "string",
                    "enum": cls.VALID_TIERS,
                    "default": "oracles",
                    "description": "Agent tier level",
                },
                "stage": {
                    "type": "string",
                    "enum": cls.VALID_STAGES,
                    "default": "alpha",
                    "description": "Development stage",
                },
                "agent_type": {
                    "type": "string",
                    "enum": cls.VALID_AGENT_TYPES,
                    "default": "Autonomous",
                    "description": "Agent operational mode",
                },
                "description": {
                    "type": "string",
                    "description": "Brief agent description",
                    "maxLength": 500,
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Categorization tags",
                },
            },
        }

    @classmethod
    def get_language_model_schema(cls) -> Dict[str, Any]:
        """Get language model configuration schema."""
        return {
            "type": "object",
            "required": ["provider", "model"],
            "properties": {
                "location": {
                    "type": "string",
                    "enum": cls.VALID_LM_LOCATIONS,
                    "description": "Model hosting location",
                },
                "provider": {
                    "type": "string",
                    "enum": cls.VALID_LM_PROVIDERS,
                    "description": "Model provider",
                },
                "runtime_mode": {
                    "type": "string",
                    "enum": ["direct", "gateway"],
                    "default": "direct",
                    "description": "Pydantic AI runtime mode. Use 'gateway' to route via gateway endpoints.",
                },
                "model": {"type": "string", "description": "Specific model identifier"},
                "gateway": {
                    "type": "object",
                    "description": "Optional gateway runtime configuration for Pydantic AI.",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "base_url": {
                            "type": "string",
                            "description": "Gateway base URL.",
                        },
                        "api_key_env": {
                            "type": "string",
                            "default": "PYDANTIC_AI_GATEWAY_API_KEY",
                            "description": "Environment variable name containing gateway API key.",
                        },
                        "timeout_sec": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 600,
                            "default": 45,
                        },
                        "model_map": {
                            "type": "object",
                            "description": "Optional logical model map (e.g. task/reflection).",
                            "additionalProperties": {"type": "string"},
                        },
                    },
                },
                "model_type": {
                    "type": "string",
                    "enum": cls.VALID_MODEL_TYPES,
                    "default": "chat",
                },
                "temperature": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "default": 0.0,
                },
                "max_tokens": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100000,
                    "default": 4000,
                },
                "top_p": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 1.0,
                },
                "frequency_penalty": {
                    "type": "number",
                    "minimum": -2.0,
                    "maximum": 2.0,
                    "default": 0.0,
                },
                "presence_penalty": {
                    "type": "number",
                    "minimum": -2.0,
                    "maximum": 2.0,
                    "default": 0.0,
                },
                "cache": {"type": "boolean", "default": True},
                "num_retries": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 10,
                    "default": 3,
                },
                "modalities": {
                    "type": "array",
                    "items": {"enum": cls.VALID_MODALITIES},
                    "default": ["text"],
                },
                "api_key": {
                    "type": "string",
                    "description": "API key for cloud providers",
                },
                "api_base": {"type": "string", "description": "Custom API base URL"},
                "request_timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 600,
                    "description": "Request timeout in seconds",
                },
            },
        }

    @classmethod
    def get_persona_schema(cls) -> Dict[str, Any]:
        """Get persona configuration schema."""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "maxLength": 50},
                "role": {"type": "string", "maxLength": 100},
                "goal": {"type": "string", "maxLength": 200},
                "job_description": {"type": "string", "maxLength": 1000},
                "backstory": {"type": "string", "maxLength": 1000},
                "audience": {"type": "string", "maxLength": 200},
                "traits": {"type": "array", "items": {"type": "string"}},
                "expertise_areas": {"type": "array", "items": {"type": "string"}},
                "communication_preferences": {
                    "type": "object",
                    "properties": {
                        "style": {
                            "type": "string",
                            "enum": cls.VALID_COMMUNICATION_STYLES,
                            "default": "formal",
                        },
                        "tone": {
                            "type": "string",
                            "enum": cls.VALID_COMMUNICATION_TONES,
                            "default": "professional",
                        },
                        "verbosity": {
                            "type": "string",
                            "enum": cls.VALID_VERBOSITY_LEVELS,
                            "default": "concise",
                        },
                        "language": {"type": "string", "default": "en"},
                    },
                },
                "constraints": {"type": "array", "items": {"type": "string"}},
                "ethical_guidelines": {"type": "array", "items": {"type": "string"}},
            },
        }

    @classmethod
    def get_task_schema(cls) -> Dict[str, Any]:
        """Get task definition schema."""
        return {
            "type": "object",
            "required": ["name", "instruction"],
            "properties": {
                "name": {"type": "string", "pattern": "^[a-z0-9_]+$"},
                "description": {"type": "string"},
                "instruction": {"type": "string", "maxLength": 2000},
                "expected_output_format": {"type": "string"},
                "schema": {
                    "type": "object",
                    "properties": {
                        "style": {
                            "type": "string",
                            "enum": cls.VALID_TASK_STYLES,
                            "default": "direct",
                        },
                        "context_fields": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "reasoning_traces": {"type": "boolean", "default": False},
                        "max_depth": {"type": "integer", "minimum": 1, "maximum": 10},
                    },
                },
                "inputs": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "description", "required"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"enum": cls.VALID_INPUT_TYPES},
                            "description": {"type": "string"},
                            "required": {"type": "boolean"},
                            "constraints": {"type": "string"},
                            "examples": {"type": "array", "items": {"type": "string"}},
                            "validation_regex": {"type": "string"},
                        },
                    },
                },
                "outputs": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "description"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"enum": cls.VALID_OUTPUT_TYPES},
                            "description": {"type": "string"},
                            "format_template": {"type": "string"},
                            "post_processing": {"type": "string"},
                        },
                    },
                },
            },
        }

    @classmethod
    def get_agentflow_schema(cls, tier: str) -> Dict[str, Any]:
        """Get agent flow schema for specific tier."""
        allowed_types = cls.get_tier_features(tier).get("agentflow_types", [])

        return {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type", "task"],
                "properties": {
                    "name": {"type": "string"},
                    "type": {"enum": allowed_types},
                    "task": {"type": "string"},
                    "depends_on": {"type": "array", "items": {"type": "string"}},
                    "config": {
                        "type": "object",
                        "properties": {
                            "max_iters": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 10,
                                "default": 5,
                            },
                            "tools": {"type": "array", "items": {"type": "string"}},
                            "retriever": {"type": "string"},
                            "top_k": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 20,
                                "default": 3,
                            },
                            "reasoning_depth": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                            },
                        },
                    },
                    "retry_policy": {
                        "type": "object",
                        "properties": {
                            "max_retries": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 10,
                                "default": 3,
                            },
                            "fallback_step": {"type": "string"},
                            "backoff_strategy": {
                                "enum": cls.VALID_RETRY_STRATEGIES,
                                "default": "exponential",
                            },
                        },
                    },
                },
            },
        }

    @classmethod
    def get_memory_schema(cls) -> Dict[str, Any]:
        """Get memory configuration schema (Genies tier only)."""
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": True},
                "agent_id": {
                    "type": "string",
                    "description": "Unique identifier for agent's memory",
                },
                "backend": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "enum": cls.VALID_MEMORY_BACKENDS,
                            "default": "sqlite",
                        },
                        "config": {
                            "type": "object",
                            "properties": {
                                "storage_path": {
                                    "type": "string",
                                    "default": ".superoptix/memory",
                                },
                                "db_path": {
                                    "type": "string",
                                    "default": ".superoptix/memory.db",
                                },
                                "host": {"type": "string", "default": "localhost"},
                                "port": {"type": "integer", "default": 6379},
                            },
                        },
                    },
                },
                "short_term": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "capacity": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 1000,
                            "default": 100,
                        },
                        "retention_policy": {
                            "enum": cls.VALID_MEMORY_RETENTION_POLICIES,
                            "default": "lru",
                        },
                        "max_conversation_length": {
                            "type": "integer",
                            "minimum": 5,
                            "maximum": 200,
                            "default": 50,
                        },
                    },
                },
                "long_term": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "enable_embeddings": {"type": "boolean", "default": True},
                        "embedding_model": {
                            "type": "string",
                            "default": "all-MiniLM-L6-v2",
                        },
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                            },
                        },
                    },
                },
                "episodic": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "auto_start_episodes": {"type": "boolean", "default": True},
                        "episode_boundary": {
                            "enum": cls.VALID_MEMORY_EPISODE_BOUNDARIES,
                            "default": "interaction",
                        },
                        "max_episode_duration": {
                            "type": "integer",
                            "minimum": 60,
                            "maximum": 86400,
                            "default": 3600,
                        },
                    },
                },
            },
        }

    @classmethod
    def get_tool_calling_schema(cls) -> Dict[str, Any]:
        """Get tool calling configuration schema (Genies tier only)."""
        return {
            "type": "object",
            "required": ["enabled"],
            "properties": {
                "enabled": {"type": "boolean"},
                "available_tools": {"type": "array", "items": {"type": "string"}},
                "tool_selection_strategy": {
                    "enum": cls.VALID_TOOL_SELECTION_STRATEGIES,
                    "default": "automatic",
                },
                "max_tool_calls": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                },
                "builtin_tools": {
                    "type": "array",
                    "items": {"enum": cls.VALID_BUILTIN_TOOLS},
                },
            },
        }

    @classmethod
    def get_rlm_schema(cls) -> Dict[str, Any]:
        """Get DSPy RLM configuration schema (optional, framework-specific)."""
        return {
            "type": "object",
            "description": "Optional DSPy RLM configuration for minimal compile mode",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable dspy.RLM for DSPy minimal pipelines",
                },
                "max_iters": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "Maximum RLM reasoning iterations",
                },
                "max_llm_calls": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 5,
                    "description": "Maximum LLM calls available to RLM helper actions",
                },
            },
        }

    @classmethod
    def get_pydantic_ai_schema(cls) -> Dict[str, Any]:
        """Get Pydantic AI framework-specific schema."""
        return {
            "type": "object",
            "properties": {
                "rlm": {
                    "type": "object",
                    "description": "Optional RLM orchestration for Pydantic AI runs",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "mode": {
                            "type": "string",
                            "enum": ["assist", "replace"],
                            "default": "assist",
                            "description": "assist: RLM draft then Agent.run, replace: RLM only",
                        },
                        "backend": {
                            "type": "string",
                            "default": "litellm",
                            "description": "RLM backend (e.g. litellm, gemini, openai)",
                        },
                        "environment": {
                            "type": "string",
                            "default": "python",
                            "description": "RLM environment (python/local/swebench, etc.)",
                        },
                        "max_iterations": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 8,
                        },
                        "max_depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4,
                            "default": 1,
                        },
                        "verbose": {"type": "boolean", "default": False},
                        "persistent": {"type": "boolean", "default": False},
                        "task_model": {
                            "type": "string",
                            "description": "Optional model override for RLM backend",
                        },
                        "api_key_env": {
                            "type": "string",
                            "description": "Optional env var name for backend API key",
                        },
                        "api_base": {
                            "type": "string",
                            "description": "Optional backend base URL override",
                        },
                        "logger": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": False},
                                "log_dir": {
                                    "type": "string",
                                    "default": ".superoptix/logs/rlm",
                                },
                                "file_name": {
                                    "type": "string",
                                    "default": "pydantic_rlm",
                                },
                            },
                        },
                    },
                }
            },
        }

    @classmethod
    def get_openai_agent_schema(cls) -> Dict[str, Any]:
        """Get OpenAI Agents SDK framework-specific schema."""
        return {
            "type": "object",
            "properties": {
                "rlm": {
                    "type": "object",
                    "description": "Optional RLM orchestration for OpenAI Agents SDK runs",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "mode": {
                            "type": "string",
                            "enum": ["assist", "replace"],
                            "default": "assist",
                            "description": "assist: RLM draft then Runner.run, replace: RLM only",
                        },
                        "backend": {
                            "type": "string",
                            "default": "litellm",
                            "description": "RLM backend (e.g. litellm, gemini, openai)",
                        },
                        "environment": {
                            "type": "string",
                            "default": "python",
                            "description": "RLM environment (python/local/swebench, etc.)",
                        },
                        "max_iterations": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 8,
                        },
                        "max_depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4,
                            "default": 1,
                        },
                        "verbose": {"type": "boolean", "default": False},
                        "persistent": {"type": "boolean", "default": False},
                        "task_model": {
                            "type": "string",
                            "description": "Optional model override for RLM backend",
                        },
                        "api_key_env": {
                            "type": "string",
                            "description": "Optional env var name for backend API key",
                        },
                        "api_base": {
                            "type": "string",
                            "description": "Optional backend base URL override",
                        },
                        "logger": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": False},
                                "log_dir": {
                                    "type": "string",
                                    "default": ".superoptix/logs/rlm",
                                },
                                "file_name": {
                                    "type": "string",
                                    "default": "openai_rlm",
                                },
                            },
                        },
                    },
                }
            },
        }

    @classmethod
    def get_google_adk_schema(cls) -> Dict[str, Any]:
        """Get Google ADK framework-specific schema."""
        return {
            "type": "object",
            "properties": {
                "rlm": {
                    "type": "object",
                    "description": "Optional RLM orchestration for Google ADK runs",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "mode": {
                            "type": "string",
                            "enum": ["assist", "replace"],
                            "default": "assist",
                            "description": "assist: RLM draft then ADK run, replace: RLM only",
                        },
                        "backend": {
                            "type": "string",
                            "default": "litellm",
                            "description": "RLM backend (e.g. litellm, gemini, openai)",
                        },
                        "environment": {
                            "type": "string",
                            "default": "python",
                            "description": "RLM environment (python/local/swebench, etc.)",
                        },
                        "max_iterations": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 8,
                        },
                        "max_depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4,
                            "default": 1,
                        },
                        "verbose": {"type": "boolean", "default": False},
                        "persistent": {"type": "boolean", "default": False},
                        "task_model": {
                            "type": "string",
                            "description": "Optional model override for RLM backend",
                        },
                        "api_key_env": {
                            "type": "string",
                            "description": "Optional env var name for backend API key",
                        },
                        "api_base": {
                            "type": "string",
                            "description": "Optional backend base URL override",
                        },
                        "logger": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": False},
                                "log_dir": {
                                    "type": "string",
                                    "default": ".superoptix/logs/rlm",
                                },
                                "file_name": {
                                    "type": "string",
                                    "default": "adk_rlm",
                                },
                            },
                        },
                    },
                }
            },
        }

    @classmethod
    def get_deepagents_schema(cls) -> Dict[str, Any]:
        """Get DeepAgents framework-specific schema."""
        return {
            "type": "object",
            "properties": {
                "rlm": {
                    "type": "object",
                    "description": "Optional RLM orchestration for DeepAgents runs",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "mode": {
                            "type": "string",
                            "enum": ["assist", "replace"],
                            "default": "assist",
                            "description": "assist: RLM draft then DeepAgents invoke, replace: RLM only",
                        },
                        "backend": {
                            "type": "string",
                            "default": "litellm",
                            "description": "RLM backend (e.g. litellm, gemini, openai)",
                        },
                        "environment": {
                            "type": "string",
                            "default": "python",
                            "description": "RLM environment (python/local/swebench, etc.)",
                        },
                        "max_iterations": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 8,
                        },
                        "max_depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4,
                            "default": 1,
                        },
                        "verbose": {"type": "boolean", "default": False},
                        "persistent": {"type": "boolean", "default": False},
                        "task_model": {
                            "type": "string",
                            "description": "Optional model override for RLM backend",
                        },
                        "api_key_env": {
                            "type": "string",
                            "description": "Optional env var name for backend API key",
                        },
                        "api_base": {
                            "type": "string",
                            "description": "Optional backend base URL override",
                        },
                        "logger": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": False},
                                "log_dir": {
                                    "type": "string",
                                    "default": ".superoptix/logs/rlm",
                                },
                                "file_name": {
                                    "type": "string",
                                    "default": "deepagents_rlm",
                                },
                            },
                        },
                    },
                }
            },
        }

    @classmethod
    def get_crewai_schema(cls) -> Dict[str, Any]:
        """Get CrewAI framework-specific schema."""
        return {
            "type": "object",
            "properties": {
                "rlm": {
                    "type": "object",
                    "description": "Optional RLM orchestration for CrewAI runs",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "mode": {
                            "type": "string",
                            "enum": ["assist", "replace"],
                            "default": "assist",
                            "description": "assist: RLM draft then Crew.kickoff, replace: RLM only",
                        },
                        "backend": {
                            "type": "string",
                            "default": "litellm",
                            "description": "RLM backend (e.g. litellm, gemini, openai)",
                        },
                        "environment": {
                            "type": "string",
                            "default": "python",
                            "description": "RLM environment (python/local/swebench, etc.)",
                        },
                        "max_iterations": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 8,
                        },
                        "max_depth": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4,
                            "default": 1,
                        },
                        "verbose": {"type": "boolean", "default": False},
                        "persistent": {"type": "boolean", "default": False},
                        "task_model": {
                            "type": "string",
                            "description": "Optional model override for RLM backend",
                        },
                        "api_key_env": {
                            "type": "string",
                            "description": "Optional env var name for backend API key",
                        },
                        "api_base": {
                            "type": "string",
                            "description": "Optional backend base URL override",
                        },
                        "logger": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": False},
                                "log_dir": {
                                    "type": "string",
                                    "default": ".superoptix/logs/rlm",
                                },
                                "file_name": {
                                    "type": "string",
                                    "default": "crewai_rlm",
                                },
                            },
                        },
                    },
                }
            },
        }

    @classmethod
    def get_full_schema(cls, tier: str = "oracles") -> Dict[str, Any]:
        """Get complete schema for the specified tier."""
        schema = {
            "type": "object",
            "required": ["apiVersion", "kind", "metadata", "spec"],
            "properties": {
                "apiVersion": {"enum": cls.VALID_API_VERSIONS},
                "kind": {"enum": cls.VALID_KINDS},
                "metadata": cls.get_metadata_schema(),
                "spec": {
                    "type": "object",
                    "required": ["language_model", "tasks"],
                    "properties": {
                        "language_model": cls.get_language_model_schema(),
                        "rlm": cls.get_rlm_schema(),
                        "pydantic_ai": cls.get_pydantic_ai_schema(),
                        "openai_agent": cls.get_openai_agent_schema(),
                        "google_adk": cls.get_google_adk_schema(),
                        "deepagents": cls.get_deepagents_schema(),
                        "crewai": cls.get_crewai_schema(),
                        "persona": cls.get_persona_schema(),
                        "tasks": {
                            "type": "array",
                            "minItems": 1,
                            "items": cls.get_task_schema(),
                        },
                        "agentflow": cls.get_agentflow_schema(tier),
                        "output_mode": {
                            "type": "string",
                            "enum": ["plain", "structured"],
                            "default": "plain",
                            "description": "Output mode for Pydantic AI agents. 'plain' = plain text output (default), 'structured' = use BaseModel structured output. Requires output_fields to be defined.",
                        },
                        "logfire": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean",
                                    "default": True,
                                    "description": "Enable LogFire observability instrumentation for Pydantic AI. Auto-detects if LogFire is installed and configured. Set to false to disable even if LogFire is available.",
                                },
                            },
                            "description": "LogFire observability configuration. Requires logfire package to be installed and configured (logfire.configure() or logfire auth). Defaults to enabled if LogFire is available.",
                        },
                        "optimization": {
                            "type": "object",
                            "description": "Optional optimization configuration",
                            **cls.get_optimization_schema(tier),
                        },
                        "feature_specifications": {
                            "type": "object",
                            "properties": {
                                "scenarios": {
                                    "type": "array",
                                    "description": "BDD scenarios for testing and optimization",
                                    "items": {
                                        "type": "object",
                                        "required": [
                                            "name",
                                            "description",
                                            "input",
                                            "expected_output",
                                        ],
                                        "properties": {
                                            "name": {"type": "string"},
                                            "description": {"type": "string"},
                                            "input": {"type": "object"},
                                            "expected_output": {"type": "object"},
                                            "tags": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "priority": {
                                                "type": "string",
                                                "enum": ["low", "medium", "high"],
                                                "default": "medium",
                                            },
                                        },
                                    },
                                }
                            },
                        },
                    },
                },
            },
        }

        # Add tier-specific features
        if tier == "genies":
            genies_features = {
                "memory": cls.get_memory_schema(),
                "tool_calling": cls.get_tool_calling_schema(),
                "retrieval": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "retriever_type": {"enum": cls.VALID_RETRIEVER_TYPES},
                    },
                },
            }
            schema["properties"]["spec"]["properties"].update(genies_features)

        return schema

    @classmethod
    def get_optimization_schema(cls, tier: str = "oracles") -> Dict[str, Any]:
        """Get optimization configuration schema."""
        compatible_optimizers = cls.OPTIMIZER_TIER_COMPATIBILITY.get(tier, [])

        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "optimize_field_descriptions": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable GEPA optimization of Pydantic model field descriptions (output_fields). "
                    "Optimizes Field(description=...) for better structured data extraction. "
                    "Requires output_fields to be defined. Opt-in feature, defaults to False.",
                },
                "optimizer": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "enum": compatible_optimizers,
                            "description": f"DSPy optimizer compatible with {tier} tier",
                        },
                        "params": {
                            "type": "object",
                            "properties": {
                                # Common parameters for all optimizers
                                "metric": {
                                    "oneOf": [
                                        {
                                            "enum": cls.VALID_BUILTIN_METRICS
                                            + cls.VALID_GEPA_METRICS
                                        },
                                        {"type": "string"},  # Allow custom metrics
                                    ],
                                    "description": "Evaluation metric for optimization",
                                },
                                "trainset": {
                                    "type": "object",
                                    "properties": {
                                        "source": {"enum": cls.VALID_DATA_SOURCES},
                                        "format": {"enum": cls.VALID_DATA_FORMATS},
                                        "path": {"type": "string"},
                                        "size_limit": {"type": "integer", "minimum": 1},
                                    },
                                },
                                # GEPA-specific parameters
                                "auto": {
                                    "type": "string",
                                    "enum": cls.VALID_GEPA_BUDGETS,
                                    "description": "GEPA budget control (GEPA only)",
                                },
                                "backend": {
                                    "type": "string",
                                    "enum": ["universal", "pydantic_native"],
                                    "description": "GEPA execution backend. "
                                    "'universal' uses SuperOptiX UniversalGEPA (default). "
                                    "'pydantic_native' attempts native Pydantic-style optimization and falls back if unavailable.",
                                },
                                "task_model": {
                                    "type": "string",
                                    "description": "Task model used for candidate generation/evaluation during GEPA runs.",
                                },
                                "reflection_model": {
                                    "type": "string",
                                    "description": "Reflection model used for critique/rewrite during GEPA runs.",
                                },
                                "reflection_lm": {
                                    "type": "string",
                                    "description": "Reflection model for GEPA",
                                },
                                "reflection_minibatch_size": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 20,
                                    "default": 3,
                                    "description": "GEPA reflection batch size",
                                },
                                "max_full_evals": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 100,
                                    "description": "Maximum full evaluations",
                                },
                                "skip_perfect_score": {
                                    "type": "boolean",
                                    "default": True,
                                    "description": "Skip optimization if perfect score achieved",
                                },
                                "add_format_failure_as_feedback": {
                                    "type": "boolean",
                                    "default": True,
                                    "description": "Include format failures in GEPA feedback",
                                },
                                "predictor_level_feedback": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Component-level feedback for multi-step pipelines",
                                },
                                # SIMBA-specific parameters
                                "bsize": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 50,
                                    "default": 8,
                                    "description": "SIMBA batch size",
                                },
                                "num_candidates": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 20,
                                    "default": 5,
                                    "description": "Number of candidates (SIMBA/MIPROv2)",
                                },
                                "max_steps": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 20,
                                    "default": 10,
                                    "description": "Maximum optimization steps",
                                },
                                # BootstrapFewShot parameters
                                "max_bootstrapped_demos": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 50,
                                    "default": 4,
                                    "description": "Maximum bootstrapped examples",
                                },
                                "max_labeled_demos": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 50,
                                    "default": 16,
                                    "description": "Maximum labeled examples",
                                },
                                "max_rounds": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 10,
                                    "default": 1,
                                    "description": "Maximum optimization rounds",
                                },
                                "max_errors": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 20,
                                    "default": 5,
                                    "description": "Maximum allowed errors during bootstrapping",
                                },
                                # MIPROv2-specific parameters
                                "init_temperature": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 2.0,
                                    "default": 1.0,
                                    "description": "Initial sampling temperature for MIPROv2",
                                },
                                # Common settings
                                "verbose": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Enable verbose optimization logs",
                                },
                                "timeout": {
                                    "type": "integer",
                                    "minimum": 60,
                                    "maximum": 3600,
                                    "default": 300,
                                    "description": "Optimization timeout in seconds",
                                },
                            },
                        },
                    },
                },
                "evaluation": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": True},
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional evaluation metrics",
                        },
                        "test_split": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 0.5,
                            "default": 0.2,
                            "description": "Fraction of data for testing",
                        },
                        "cross_validation": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": False},
                                "folds": {
                                    "type": "integer",
                                    "minimum": 2,
                                    "maximum": 10,
                                    "default": 5,
                                },
                            },
                        },
                    },
                },
                "hardware_optimization": {
                    "type": "object",
                    "properties": {
                        "target_tier": {
                            "type": "string",
                            "enum": ["lightweight", "standard", "production"],
                            "default": "standard",
                            "description": "Target hardware tier",
                        },
                        "memory_limit_gb": {
                            "type": "integer",
                            "minimum": 4,
                            "maximum": 128,
                            "description": "Memory limit in GB",
                        },
                        "parallel_optimization": {
                            "type": "boolean",
                            "default": False,
                            "description": "Enable parallel optimization",
                        },
                        "max_workers": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 8,
                            "default": 2,
                            "description": "Maximum parallel workers",
                        },
                    },
                },
            },
        }
