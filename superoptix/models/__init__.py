"""
SuperOptiX Model Intelligence System.

This module provides a comprehensive model management system for SuperOptiX,
supporting multiple backends and providing a unified interface for model operations.

The SuperOptiX Model Intelligence System focuses on:
- Showing only installed models by default
- Providing discovery guides for model sources
- SuperOptiX-branded model intelligence
- Seamless DSPy integration
- Privacy-focused local model management
"""

from .manager import SuperOptiXModelManager
from .registry import SuperOptiXModelRegistry
from .utils import (
    SuperOptiXBackendType,
    SuperOptiXModelInfo,
    SuperOptiXModelStatus,
    SuperOptiXModelSize,
    SuperOptiXModelTask,
    SuperOptiXBackendInfo,
    SuperOptiXModelFilter,
    get_superoptix_system_info,
    format_size,
    parse_superoptix_model_name,
    get_superoptix_model_discovery_guide,
    validate_superoptix_model_compatibility,
)
from .config import (
    SuperOptiXModelConfig,
    SuperOptiXBackendConfig,
    SuperOptiXModelDefaults,
    get_superoptix_global_config,
    save_superoptix_global_config,
    get_superoptix_project_config,
    save_superoptix_project_config,
    get_superoptix_config_dir,
    get_superoptix_model_discovery_settings,
)

# Legacy aliases for backward compatibility (discouraged)
from .manager import ModelManager
from .utils import (
    BackendType,
    ModelInfo,
    ModelStatus,
    ModelSize,
    ModelTask,
    BackendInfo,
    ModelSearchFilter,
)
from .config import (
    ModelConfig,
    BackendConfig,
    ModelDefaults,
)

__all__ = [
    # SuperOptiX Model Intelligence System (Primary - Use These!)
    "SuperOptiXModelManager",
    "SuperOptiXModelRegistry",
    "SuperOptiXBackendType",
    "SuperOptiXModelInfo",
    "SuperOptiXModelStatus",
    "SuperOptiXModelSize",
    "SuperOptiXModelTask",
    "SuperOptiXBackendInfo",
    "SuperOptiXModelFilter",
    "SuperOptiXModelConfig",
    "SuperOptiXBackendConfig",
    "SuperOptiXModelDefaults",
    # SuperOptiX Utility Functions
    "get_superoptix_system_info",
    "format_size",
    "parse_superoptix_model_name",
    "get_superoptix_model_discovery_guide",
    "validate_superoptix_model_compatibility",
    "get_superoptix_global_config",
    "save_superoptix_global_config",
    "get_superoptix_project_config",
    "save_superoptix_project_config",
    "get_superoptix_config_dir",
    "get_superoptix_model_discovery_settings",
    # Legacy aliases (deprecated - avoid using these)
    "ModelManager",
    "BackendType",
    "ModelInfo",
    "ModelStatus",
    "ModelSize",
    "ModelTask",
    "BackendInfo",
    "ModelSearchFilter",
    "ModelConfig",
    "BackendConfig",
    "ModelDefaults",
]
