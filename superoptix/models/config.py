"""
SuperOptiX Model Intelligence System - Configuration management.
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, Any
from .utils import SuperOptiXBackendType, SuperOptiXModelSize, SuperOptiXModelTask


@dataclass
class SuperOptiXBackendConfig:
    """SuperOptiX Backend Intelligence - Configuration for a specific backend."""

    enabled: bool = True
    host: Optional[str] = None
    port: Optional[int] = None
    api_key: Optional[str] = None
    model_path: Optional[str] = None
    settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


@dataclass
class SuperOptiXModelDefaults:
    """SuperOptiX Model Intelligence - Default model configurations."""

    chat_model: Optional[str] = None
    code_model: Optional[str] = None
    reasoning_model: Optional[str] = None
    embedding_model: Optional[str] = None
    vision_model: Optional[str] = None
    audio_model: Optional[str] = None

    # Size preferences
    preferred_size: SuperOptiXModelSize = SuperOptiXModelSize.MEDIUM
    max_size: SuperOptiXModelSize = SuperOptiXModelSize.LARGE

    # Performance preferences
    prefer_quantized: bool = True
    prefer_local: bool = True

    def get_default_for_task(self, task: SuperOptiXModelTask) -> Optional[str]:
        """Get the default model for a specific task."""
        task_mapping = {
            SuperOptiXModelTask.CHAT: self.chat_model,
            SuperOptiXModelTask.CODE: self.code_model,
            SuperOptiXModelTask.REASONING: self.reasoning_model,
            SuperOptiXModelTask.EMBEDDING: self.embedding_model,
            SuperOptiXModelTask.VISION: self.vision_model,
            SuperOptiXModelTask.AUDIO: self.audio_model,
        }
        return task_mapping.get(task)


@dataclass
class SuperOptiXModelConfig:
    """SuperOptiX Model Intelligence - Main configuration class."""

    backends: Dict[str, SuperOptiXBackendConfig] = None
    defaults: SuperOptiXModelDefaults = None

    # SuperOptiX-specific settings
    superoptix_mode: bool = True
    show_only_installed: bool = True
    auto_discover: bool = True
    cache_model_info: bool = True

    # Performance settings
    max_concurrent_downloads: int = 3
    download_timeout: int = 300
    model_cache_size: int = 10

    # UI preferences
    show_model_sizes: bool = True
    show_backend_info: bool = True
    use_rich_formatting: bool = True

    def __post_init__(self):
        if self.backends is None:
            self.backends = self._get_default_backends()
        if self.defaults is None:
            self.defaults = SuperOptiXModelDefaults()

    def _get_default_backends(self) -> Dict[str, SuperOptiXBackendConfig]:
        """Get default SuperOptiX backend configurations."""
        return {
            SuperOptiXBackendType.OLLAMA.value: SuperOptiXBackendConfig(
                enabled=True,
                host="localhost",
                port=11434,
                settings={
                    "pull_timeout": 600,
                    "keep_alive": "5m",
                    "num_ctx": 4096,
                },
            ),
            SuperOptiXBackendType.MLX.value: SuperOptiXBackendConfig(
                enabled=True,
                settings={
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "cache_limit_gb": 4,
                },
            ),
            SuperOptiXBackendType.HUGGINGFACE.value: SuperOptiXBackendConfig(
                enabled=True,
                settings={
                    "cache_dir": None,  # Use default HF cache
                    "trust_remote_code": False,
                    "revision": "main",
                },
            ),
        }

    def get_backend_config(
        self, backend: SuperOptiXBackendType
    ) -> SuperOptiXBackendConfig:
        """Get configuration for a specific backend."""
        return self.backends.get(backend.value, SuperOptiXBackendConfig())

    def set_backend_config(
        self, backend: SuperOptiXBackendType, config: SuperOptiXBackendConfig
    ):
        """Set configuration for a specific backend."""
        self.backends[backend.value] = config

    def enable_backend(self, backend: SuperOptiXBackendType):
        """Enable a specific backend."""
        if backend.value not in self.backends:
            self.backends[backend.value] = SuperOptiXBackendConfig()
        self.backends[backend.value].enabled = True

    def disable_backend(self, backend: SuperOptiXBackendType):
        """Disable a specific backend."""
        if backend.value in self.backends:
            self.backends[backend.value].enabled = False

    def is_backend_enabled(self, backend: SuperOptiXBackendType) -> bool:
        """Check if a backend is enabled."""
        return self.backends.get(backend.value, SuperOptiXBackendConfig()).enabled

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = asdict(self)
        # Convert enum values to strings for JSON serialization
        if "defaults" in result and result["defaults"]:
            if "preferred_size" in result["defaults"]:
                result["defaults"]["preferred_size"] = result["defaults"][
                    "preferred_size"
                ].value
            if "max_size" in result["defaults"]:
                result["defaults"]["max_size"] = result["defaults"]["max_size"].value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuperOptiXModelConfig":
        """Create configuration from dictionary."""
        # Convert string enum values back to enums
        if "defaults" in data and data["defaults"]:
            if "preferred_size" in data["defaults"]:
                data["defaults"]["preferred_size"] = SuperOptiXModelSize(
                    data["defaults"]["preferred_size"]
                )
            if "max_size" in data["defaults"]:
                data["defaults"]["max_size"] = SuperOptiXModelSize(
                    data["defaults"]["max_size"]
                )

        # Create backend configs
        backends = {}
        if "backends" in data:
            for backend_name, backend_data in data["backends"].items():
                backends[backend_name] = SuperOptiXBackendConfig(**backend_data)

        # Create defaults
        defaults = SuperOptiXModelDefaults()
        if "defaults" in data and data["defaults"]:
            defaults = SuperOptiXModelDefaults(**data["defaults"])

        # Create main config
        config_data = {
            k: v for k, v in data.items() if k not in ["backends", "defaults"]
        }
        config = cls(**config_data)
        config.backends = backends
        config.defaults = defaults

        return config

    def save(self, path: Path):
        """Save configuration to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "SuperOptiXModelConfig":
        """Load configuration from file."""
        if not path.exists():
            return cls()

        with open(path, "r") as f:
            data = json.load(f)

        return cls.from_dict(data)


def get_superoptix_config_dir() -> Path:
    """Get the SuperOptiX configuration directory."""
    # Check for SuperOptiX-specific config directory
    if "SUPEROPTIX_CONFIG_DIR" in os.environ:
        return Path(os.environ["SUPEROPTIX_CONFIG_DIR"])

    # Default to user's config directory
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA", "")) / "SuperOptiX"
    else:  # Unix-like
        config_dir = Path.home() / ".config" / "superoptix"

    return config_dir


def get_superoptix_global_config() -> SuperOptiXModelConfig:
    """Get the global SuperOptiX model configuration."""
    config_path = get_superoptix_config_dir() / "model_config.json"
    return SuperOptiXModelConfig.load(config_path)


def save_superoptix_global_config(config: SuperOptiXModelConfig):
    """Save the global SuperOptiX model configuration."""
    config_path = get_superoptix_config_dir() / "model_config.json"
    config.save(config_path)


def get_superoptix_project_config(project_dir: Path = None) -> SuperOptiXModelConfig:
    """Get the SuperOptiX project-specific model configuration."""
    if project_dir is None:
        project_dir = Path.cwd()

    config_path = project_dir / ".superoptix" / "model_config.json"
    if config_path.exists():
        return SuperOptiXModelConfig.load(config_path)

    # Fall back to global config
    return get_superoptix_global_config()


def save_superoptix_project_config(
    config: SuperOptiXModelConfig, project_dir: Path = None
):
    """Save the SuperOptiX project-specific model configuration."""
    if project_dir is None:
        project_dir = Path.cwd()

    config_path = project_dir / ".superoptix" / "model_config.json"
    config.save(config_path)


def get_superoptix_model_discovery_settings() -> Dict[str, Any]:
    """Get SuperOptiX model discovery settings and guides."""
    return {
        "discovery_enabled": True,
        "show_only_installed": True,
        "auto_refresh": True,
        "cache_duration": 3600,  # 1 hour
        "guides": {
            "ollama": {
                "title": "🦙 Ollama Models",
                "description": "Local models with easy installation",
                "quick_start": [
                    "1. Install Ollama from https://ollama.com",
                    "2. Browse models at https://ollama.com/library",
                    "3. Install with: ollama pull <model_name>",
                    "4. Use with SuperOptiX: super model dspy ollama/<model_name>",
                ],
                "popular_models": [
                    "llama3.2:3b - Great for beginners",
                    "codellama:7b - Perfect for coding",
                    "mistral:7b - Excellent reasoning",
                    "qwen2.5:7b - Multilingual support",
                ],
            },
            "mlx": {
                "title": "🍎 MLX Community",
                "description": "Apple Silicon optimized models",
                "quick_start": [
                    "1. Ensure you have Apple Silicon (M1/M2/M3)",
                    "2. Browse models at https://huggingface.co/mlx-community",
                    "3. Install with SuperOptiX: super model install <mlx-model>",
                    "4. Enjoy optimized performance!",
                ],
                "popular_models": [
                    "mlx-community/Llama-3.2-3B-Instruct-4bit",
                    "mlx-community/CodeLlama-7b-Instruct-hf-4bit",
                    "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
                ],
            },
            "huggingface": {
                "title": "🤗 HuggingFace Hub",
                "description": "Largest collection of AI models",
                "quick_start": [
                    "1. Create account at https://huggingface.co",
                    "2. Browse models at https://huggingface.co/models",
                    "3. Install with: pip install transformers",
                    "4. Use with SuperOptiX model management",
                ],
                "popular_models": [
                    "microsoft/DialoGPT-medium",
                    "google/flan-t5-base",
                    "sentence-transformers/all-MiniLM-L6-v2",
                ],
            },
        },
    }


# Legacy aliases for backward compatibility
BackendConfig = SuperOptiXBackendConfig
ModelDefaults = SuperOptiXModelDefaults
ModelConfig = SuperOptiXModelConfig
