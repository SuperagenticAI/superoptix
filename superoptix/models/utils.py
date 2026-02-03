"""
SuperOptiX Model Intelligence System - Utility classes and types.
"""

import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class SuperOptiXBackendType(Enum):
    """SuperOptiX supported model backends."""

    OLLAMA = "ollama"
    MLX = "mlx"
    HUGGINGFACE = "huggingface"
    LMSTUDIO = "lmstudio"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class SuperOptiXModelStatus(Enum):
    """SuperOptiX model availability status."""

    INSTALLED = "installed"
    DOWNLOADING = "downloading"
    FAILED = "failed"
    UNKNOWN = "unknown"


class SuperOptiXModelSize(Enum):
    """SuperOptiX model size categories."""

    TINY = "tiny"  # < 1B parameters
    SMALL = "small"  # 1B - 7B parameters
    MEDIUM = "medium"  # 7B - 30B parameters
    LARGE = "large"  # 30B+ parameters


class SuperOptiXModelTask(Enum):
    """SuperOptiX model task specializations."""

    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"


@dataclass
class SuperOptiXModelInfo:
    """SuperOptiX Model Intelligence - Information about a model."""

    name: str
    backend: SuperOptiXBackendType
    status: SuperOptiXModelStatus
    size: Optional[SuperOptiXModelSize] = None
    task: Optional[SuperOptiXModelTask] = None
    description: Optional[str] = None
    tags: List[str] = None
    parameters: Optional[str] = None  # e.g., "7B", "13B"
    quantization: Optional[str] = None  # e.g., "4bit", "8bit"
    license: Optional[str] = None
    context_length: Optional[int] = None
    local_path: Optional[Path] = None
    download_size: Optional[int] = None  # in bytes
    disk_size: Optional[int] = None  # in bytes
    last_used: Optional[datetime] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        if self.parameters:
            return f"{self.name} ({self.parameters})"
        return self.name

    @property
    def full_name(self) -> str:
        """Full name including backend."""
        return f"{self.backend.value}/{self.name}"

    @property
    def is_local(self) -> bool:
        """Whether the model is available locally."""
        return self.status == SuperOptiXModelStatus.INSTALLED

    @property
    def size_mb(self) -> Optional[float]:
        """Model size in MB."""
        if self.disk_size:
            return self.disk_size / (1024 * 1024)
        return None

    @property
    def size_gb(self) -> Optional[float]:
        """Model size in GB."""
        if self.disk_size:
            return self.disk_size / (1024 * 1024 * 1024)
        return None


@dataclass
class SuperOptiXBackendInfo:
    """SuperOptiX Backend Intelligence - Information about a backend."""

    type: SuperOptiXBackendType
    available: bool
    version: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    status: str = "unknown"
    error: Optional[str] = None
    models_count: int = 0
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class SuperOptiXModelFilter:
    """SuperOptiX Model Intelligence - Filters for model search."""

    backend: Optional[SuperOptiXBackendType] = None
    size: Optional[SuperOptiXModelSize] = None
    task: Optional[SuperOptiXModelTask] = None
    status: Optional[SuperOptiXModelStatus] = None
    tags: List[str] = None
    license: Optional[str] = None
    quantized: Optional[bool] = None
    local_only: bool = False
    installed_only: bool = True  # Default to showing only installed models

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def matches(self, model: SuperOptiXModelInfo) -> bool:
        """Check if a model matches the filter criteria."""
        if self.backend and model.backend != self.backend:
            return False

        if self.size and model.size != self.size:
            return False

        if self.task and model.task != self.task:
            return False

        if self.status and model.status != self.status:
            return False

        if self.license and model.license != self.license:
            return False

        if self.quantized is not None:
            has_quantization = model.quantization is not None
            if self.quantized != has_quantization:
                return False

        if self.local_only and not model.is_local:
            return False

        if self.installed_only and model.status != SuperOptiXModelStatus.INSTALLED:
            return False

        if self.tags:
            if not any(tag in model.tags for tag in self.tags):
                return False

        return True


def get_superoptix_system_info() -> Dict[str, Any]:
    """Get SuperOptiX-compatible system information for model compatibility."""
    return {
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "has_metal": platform.system() == "Darwin" and platform.machine() == "arm64",
        "has_cuda": False,  # TODO: Detect CUDA availability
        "superoptix_compatible": True,
    }


def format_size(size_bytes: int) -> str:
    """Format byte size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def parse_superoptix_model_name(
    model_name: str,
) -> tuple[Optional[SuperOptiXBackendType], str]:
    """Parse a SuperOptiX model name to extract backend and model."""
    if "/" in model_name:
        backend_str, model = model_name.split("/", 1)
        try:
            backend = SuperOptiXBackendType(backend_str)
            return backend, model
        except ValueError:
            # If the backend_str is not a valid backend, treat the entire string as a model name
            # This handles cases like "openai/gpt-oss-120b" where "openai" is part of the model name
            pass
    return None, model_name


def get_superoptix_model_discovery_guide() -> Dict[str, Dict[str, str]]:
    """Get SuperOptiX Model Discovery Guide for different backends."""
    return {
        "ollama": {
            "name": "🦙 Ollama",
            "description": "Local models with easy installation",
            "install_cmd": "1. Install Ollama: Visit https://ollama.com\n2. Pull model: ollama pull <model_name>",
            "browse_url": "https://ollama.com/library",
            "popular_models": "llama3.2:3b, codellama:7b, mistral:7b, qwen2.5:7b",
            "benefits": "• No API keys needed\n• Run completely offline\n• Fast local inference\n• Privacy-focused",
            "requirements": "Ollama installed locally (visit https://ollama.com)",
        },
        "mlx": {
            "name": "🍎 MLX Community",
            "description": "Apple Silicon optimized models",
            "install_cmd": "Use SuperOptiX: super model install <mlx-model>",
            "browse_url": "https://huggingface.co/mlx-community",
            "popular_models": "mlx-community/Llama-3.2-3B-Instruct-4bit, mlx-community/CodeLlama-7b-Instruct-hf-4bit",
            "benefits": "• Optimized for M1/M2/M3 chips\n• 4-bit quantization for efficiency\n• Fast inference on Apple Silicon\n• Memory efficient",
            "requirements": "Apple Silicon Mac (M1/M2/M3)",
        },
        "huggingface": {
            "name": "🤗 HuggingFace Hub",
            "description": "Largest collection of AI models",
            "install_cmd": "Use transformers: AutoModel.from_pretrained('<model_name>')",
            "browse_url": "https://huggingface.co/models",
            "popular_models": "microsoft/Phi-4, google/gemma-7b-it",
            "benefits": "• Largest model ecosystem\n• Research and production models\n• Fine-tuned variants\n• Community contributions",
            "requirements": "transformers library installed",
        },
    }


def validate_superoptix_model_compatibility(
    model_info: SuperOptiXModelInfo,
) -> tuple[bool, List[str]]:
    """Validate if a model is compatible with the current SuperOptiX system."""
    issues = []
    system_info = get_superoptix_system_info()

    # Check platform compatibility
    if model_info.backend == SuperOptiXBackendType.MLX:
        if not system_info["has_metal"]:
            issues.append(
                "MLX models require Apple Silicon (M1/M2/M3) with Metal support"
            )

    # Check memory requirements (rough estimates)
    if model_info.parameters:
        param_count = model_info.parameters.lower()
        if "70b" in param_count or "72b" in param_count:
            issues.append(
                "Large models (70B+) require significant RAM (64GB+ recommended)"
            )
        elif "30b" in param_count or "33b" in param_count:
            issues.append(
                "Medium-large models (30B+) require substantial RAM (32GB+ recommended)"
            )

    return len(issues) == 0, issues


# Legacy aliases for backward compatibility (but discouraged)
BackendType = SuperOptiXBackendType
ModelStatus = SuperOptiXModelStatus
ModelSize = SuperOptiXModelSize
ModelTask = SuperOptiXModelTask
ModelInfo = SuperOptiXModelInfo
BackendInfo = SuperOptiXBackendInfo
ModelSearchFilter = SuperOptiXModelFilter
