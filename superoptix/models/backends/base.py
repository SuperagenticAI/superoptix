"""
SuperOptiX Model Intelligence System - Base backend interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..utils import (
    SuperOptiXModelInfo,
    SuperOptiXBackendInfo,
    SuperOptiXModelStatus,
    SuperOptiXBackendType,
)


class SuperOptiXBaseBackend(ABC):
    """SuperOptiX Model Intelligence - Base class for model backends."""

    def __init__(self, **kwargs):
        self.config = kwargs
        self._models_cache: Optional[List[SuperOptiXModelInfo]] = None
        self._cache_timestamp: Optional[float] = None
        self.cache_ttl = 300  # 5 minutes

    @property
    @abstractmethod
    def backend_type(self) -> SuperOptiXBackendType:
        """The SuperOptiX backend type."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the SuperOptiX backend is available."""
        pass

    @abstractmethod
    def get_backend_info(self) -> SuperOptiXBackendInfo:
        """Get SuperOptiX backend information."""
        pass

    @abstractmethod
    def list_available_models(self) -> List[SuperOptiXModelInfo]:
        """List all available models from the SuperOptiX backend."""
        pass

    @abstractmethod
    def list_installed_models(self) -> List[SuperOptiXModelInfo]:
        """List installed SuperOptiX models."""
        pass

    @abstractmethod
    def install_model(self, model_name: str, **kwargs) -> bool:
        """Install a SuperOptiX model."""
        pass

    @abstractmethod
    def uninstall_model(self, model_name: str) -> bool:
        """Uninstall a SuperOptiX model."""
        pass

    @abstractmethod
    def get_model_info(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Get information about a specific SuperOptiX model."""
        pass

    @abstractmethod
    def test_model(
        self, model_name: str, prompt: str = "Hello, world!"
    ) -> Dict[str, Any]:
        """Test a SuperOptiX model with a simple prompt."""
        pass

    def create_dspy_client(self, model_name: str, **kwargs):
        """Create a DSPy-compatible client for the SuperOptiX model."""
        # Default implementation - subclasses should override for better integration
        from dspy import LM

        # Convert to DSPy format
        dspy_model = f"{self.backend_type.value}/{model_name}"

        # Merge default config with kwargs
        client_config = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            **kwargs,
        }

        return LM(model=dspy_model, **client_config)

    def search_models(self, query: str, limit: int = 10) -> List[SuperOptiXModelInfo]:
        """Search for SuperOptiX models by name or description."""
        models = self.list_installed_models()  # Focus on installed models

        # Simple text search
        query_lower = query.lower()
        matches = []

        for model in models:
            if query_lower in model.name.lower():
                matches.append(model)
            elif model.description and query_lower in model.description.lower():
                matches.append(model)
            elif any(query_lower in tag.lower() for tag in model.tags):
                matches.append(model)

        return matches[:limit]

    def get_model_status(self, model_name: str) -> SuperOptiXModelStatus:
        """Get the status of a specific SuperOptiX model."""
        try:
            model_info = self.get_model_info(model_name)
            return model_info.status if model_info else SuperOptiXModelStatus.UNKNOWN
        except Exception:
            return SuperOptiXModelStatus.UNKNOWN

    def refresh_cache(self):
        """Refresh the SuperOptiX models cache."""
        self._models_cache = None
        self._cache_timestamp = None

    def _get_cached_models(
        self, force_refresh: bool = False
    ) -> List[SuperOptiXModelInfo]:
        """Get SuperOptiX models with caching."""
        import time

        now = time.time()

        if (
            not force_refresh
            and self._models_cache is not None
            and self._cache_timestamp is not None
            and now - self._cache_timestamp < self.cache_ttl
        ):
            return self._models_cache

        models = self.list_installed_models()  # Focus on installed models
        self._models_cache = models
        self._cache_timestamp = now

        return models

    def validate_model_name(self, model_name: str) -> bool:
        """Validate if a model name is valid for this SuperOptiX backend."""
        try:
            model_info = self.get_model_info(model_name)
            return model_info is not None
        except Exception:
            return False

    def get_model_size(self, model_name: str) -> Optional[int]:
        """Get the size of a SuperOptiX model in bytes."""
        model_info = self.get_model_info(model_name)
        return model_info.disk_size if model_info else None

    def cleanup(self):
        """Clean up SuperOptiX backend resources."""
        self.refresh_cache()

    def __str__(self) -> str:
        return f"SuperOptiX{self.__class__.__name__}({self.backend_type.value})"

    def __repr__(self) -> str:
        return f"SuperOptiX{self.__class__.__name__}(backend_type={self.backend_type.value}, config={self.config})"


# Legacy alias for backward compatibility
BaseBackend = SuperOptiXBaseBackend
