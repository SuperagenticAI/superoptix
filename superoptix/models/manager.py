"""
SuperOptiX Model Intelligence System - Central model management orchestrator.
"""

from typing import Dict, List, Optional, Any
import logging

from .backends.base import SuperOptiXBaseBackend
from .backends.ollama import SuperOptiXOllamaBackend
from .backends.mlx import SuperOptiXMLXBackend
from .backends.huggingface import SuperOptiXHuggingFaceBackend
from .backends.lmstudio import SuperOptiXLMStudioBackend
from .registry import SuperOptiXModelRegistry
from .config import get_superoptix_global_config
from .utils import (
    SuperOptiXBackendType,
    SuperOptiXModelInfo,
    SuperOptiXBackendInfo,
    SuperOptiXModelFilter,
    get_superoptix_system_info,
    validate_superoptix_model_compatibility,
    parse_superoptix_model_name,
)

logger = logging.getLogger(__name__)


class SuperOptiXModelManager:
    """
    SuperOptiX Model Intelligence System - Central orchestrator for all model operations.

    This class provides a unified interface for managing models across different backends
    while maintaining the SuperOptiX branding and philosophy.
    """

    def __init__(self):
        self.config = get_superoptix_global_config()
        self.registry = SuperOptiXModelRegistry()
        self.backends: Dict[SuperOptiXBackendType, SuperOptiXBaseBackend] = {}
        self._initialize_backends()

    def _initialize_backends(self):
        """Initialize SuperOptiX-compatible backends."""
        # Initialize Ollama backend
        if self.config.is_backend_enabled(SuperOptiXBackendType.OLLAMA):
            try:
                ollama_config = self.config.get_backend_config(
                    SuperOptiXBackendType.OLLAMA
                )
                self.backends[SuperOptiXBackendType.OLLAMA] = SuperOptiXOllamaBackend(
                    host=ollama_config.host,
                    port=ollama_config.port,
                    **ollama_config.settings,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama backend: {e}")

        # Initialize MLX backend
        if self.config.is_backend_enabled(SuperOptiXBackendType.MLX):
            try:
                mlx_config = self.config.get_backend_config(SuperOptiXBackendType.MLX)
                self.backends[SuperOptiXBackendType.MLX] = SuperOptiXMLXBackend(
                    **mlx_config.settings
                )
            except Exception as e:
                logger.warning(f"Failed to initialize MLX backend: {e}")

        # Initialize HuggingFace backend
        if self.config.is_backend_enabled(SuperOptiXBackendType.HUGGINGFACE):
            try:
                hf_config = self.config.get_backend_config(
                    SuperOptiXBackendType.HUGGINGFACE
                )
                self.backends[SuperOptiXBackendType.HUGGINGFACE] = (
                    SuperOptiXHuggingFaceBackend(**hf_config.settings)
                )
            except Exception as e:
                logger.warning(f"Failed to initialize HuggingFace backend: {e}")

        # Initialize LM Studio backend
        if self.config.is_backend_enabled(SuperOptiXBackendType.LMSTUDIO):
            try:
                lmstudio_config = self.config.get_backend_config(
                    SuperOptiXBackendType.LMSTUDIO
                )
                self.backends[SuperOptiXBackendType.LMSTUDIO] = (
                    SuperOptiXLMStudioBackend(**lmstudio_config.settings)
                )
            except Exception as e:
                logger.warning(f"Failed to initialize LM Studio backend: {e}")

    def list_models(
        self, filter_obj: Optional[SuperOptiXModelFilter] = None
    ) -> List[SuperOptiXModelInfo]:
        """
        List SuperOptiX models with intelligent filtering.

        By default, shows only installed models to avoid overwhelming users
        with hundreds of available models that change frequently.
        """
        if filter_obj is None:
            filter_obj = SuperOptiXModelFilter(installed_only=True)

        all_models = []

        # Get models from each backend
        for backend_type, backend in self.backends.items():
            if filter_obj.backend and filter_obj.backend != backend_type:
                continue

            try:
                if filter_obj.installed_only:
                    # Only get installed models to avoid hardcoded lists
                    if hasattr(backend, "list_installed_models_sync"):
                        backend_models = backend.list_installed_models_sync()
                    else:
                        backend_models = backend.list_installed_models()
                else:
                    # Get all available models (use with caution)
                    backend_models = backend.list_available_models()

                # Apply filter
                filtered_models = [
                    model for model in backend_models if filter_obj.matches(model)
                ]
                all_models.extend(filtered_models)

            except Exception as e:
                logger.warning(f"Failed to list models from {backend_type.value}: {e}")

        # Sort by usage and name for better UX
        all_models.sort(key=lambda m: (-m.usage_count, m.name))

        # Update registry with discovered models
        for model in all_models:
            self.registry.add_model(model)

        return all_models

    def search_models(
        self, query: str, filter_obj: Optional[SuperOptiXModelFilter] = None
    ) -> List[SuperOptiXModelInfo]:
        """
        Search SuperOptiX models by name or description.

        Only searches installed models by default to provide relevant results.
        """
        if filter_obj is None:
            filter_obj = SuperOptiXModelFilter(installed_only=True)

        all_models = self.list_models(filter_obj)

        # Simple text search
        query_lower = query.lower()
        matching_models = []

        for model in all_models:
            if (
                query_lower in model.name.lower()
                or (model.description and query_lower in model.description.lower())
                or any(query_lower in tag.lower() for tag in model.tags)
            ):
                matching_models.append(model)

        return matching_models

    def get_model_info(
        self, model_name: str, backend_type: Optional[SuperOptiXBackendType] = None
    ) -> Optional[SuperOptiXModelInfo]:
        """Get detailed information about a specific SuperOptiX model."""
        # Parse model name if it includes backend
        parsed_backend, parsed_name = parse_superoptix_model_name(model_name)
        if parsed_backend:
            backend_type = parsed_backend
            model_name = parsed_name

        # Search in specific backend or all backends
        backends_to_search = (
            [backend_type] if backend_type else list(self.backends.keys())
        )

        for backend_type in backends_to_search:
            if backend_type not in self.backends:
                continue

            try:
                backend = self.backends[backend_type]
                model_info = backend.get_model_info(model_name)
                if model_info:
                    # Update registry
                    self.registry.add_model(model_info)
                    return model_info
            except Exception as e:
                logger.warning(
                    f"Failed to get model info from {backend_type.value}: {e}"
                )

        return None

    def install_model(
        self, model_name: str, backend_type: Optional[SuperOptiXBackendType] = None
    ) -> bool:
        """
        Install a SuperOptiX model using proper download features from the respective libraries.

        This method uses the native download capabilities of each backend:
        - HuggingFace: Uses huggingface_hub.snapshot_download with proper progress tracking
        - MLX: Uses mlx_lm.utils.get_model_path for optimized Apple Silicon downloads
        - Ollama: Uses ollama pull command
        - LM Studio: Manual installation via desktop app
        """
        # Parse model name if it includes backend
        parsed_backend, parsed_name = parse_superoptix_model_name(model_name)
        if parsed_backend:
            backend_type = parsed_backend
            model_name = parsed_name

        if not backend_type:
            # Try to determine backend from model name patterns
            if "mlx-community" in model_name.lower():
                backend_type = SuperOptiXBackendType.MLX
            elif "/" in model_name and not model_name.startswith("mlx-"):
                backend_type = SuperOptiXBackendType.HUGGINGFACE
            elif "lmstudio" in model_name.lower() or model_name.lower().startswith(
                "lm-"
            ):
                backend_type = SuperOptiXBackendType.LMSTUDIO
            else:
                backend_type = SuperOptiXBackendType.OLLAMA

        if backend_type not in self.backends:
            logger.error(f"Backend {backend_type.value} not available")
            return False

        try:
            backend = self.backends[backend_type]

            # Handle different backends with their specific download mechanisms
            if backend_type == SuperOptiXBackendType.HUGGINGFACE:
                # Use HuggingFace's native snapshot_download with progress tracking
                import asyncio
                from rich.console import Console

                console = Console()

                async def install_with_progress():
                    async for progress in backend.install_model(model_name):
                        console.print(progress)
                    return True

                try:
                    success = asyncio.run(install_with_progress())
                except Exception as e:
                    console.print(f"❌ Installation failed: {e}")
                    success = False

            elif backend_type == SuperOptiXBackendType.MLX:
                # Use MLX-LM's native get_model_path for optimized downloads
                success = backend.install_model_sync(model_name)

            elif backend_type == SuperOptiXBackendType.OLLAMA:
                # Use Ollama's native pull command
                success = backend.install_model(model_name)

            else:
                # For other backends (LMStudio), use the sync method
                success = backend.install_model(model_name)

            if success:
                # Verify the model is actually installed before updating registry
                if backend_type == SuperOptiXBackendType.HUGGINGFACE:
                    model_info = backend.get_model_info_sync(model_name)
                else:
                    model_info = backend.get_model_info(model_name)

                # Only add to registry if model info is found (indicating successful installation)
                if model_info:
                    self.registry.add_model(model_info)
                    logger.info(
                        f"✅ Model {model_name} successfully installed and registered"
                    )
                else:
                    logger.warning(
                        f"⚠️ Model {model_name} installation may have failed - no model info found"
                    )
                    return False

            return success

        except Exception as e:
            logger.error(f"Failed to install model {model_name}: {e}")
            return False

    def detect_model_backend(self, model_name: str) -> Optional[SuperOptiXBackendType]:
        """Fast auto-detection of which backend contains a model."""
        try:
            # Use cached model list instead of checking each backend
            from .utils import SuperOptiXModelFilter

            filter_obj = SuperOptiXModelFilter(installed_only=True)
            all_models = self.list_models(filter_obj)

            # Find the model in the cached list
            for model in all_models:
                if model.name == model_name or model.full_name == model_name:
                    return model.backend
                # Handle naming variations (slash vs underscore)
                if model.name == model_name.replace(
                    "/", "_"
                ) or model.full_name == model_name.replace("/", "_"):
                    return model.backend
                if model.name == model_name.replace(
                    "_", "/"
                ) or model.full_name == model_name.replace("_", "/"):
                    return model.backend

            return None
        except Exception as e:
            logger.warning(f"⚠️ Error in auto-detection: {e}")
            return None

    def uninstall_model(
        self, model_name: str, backend_type: Optional[SuperOptiXBackendType] = None
    ) -> bool:
        """Uninstall a SuperOptiX model."""
        # Parse model name if it includes backend
        parsed_backend, parsed_name = parse_superoptix_model_name(model_name)
        if parsed_backend:
            backend_type = parsed_backend
            model_name = parsed_name

        if not backend_type:
            # Find the backend that has this model
            for bt, backend in self.backends.items():
                try:
                    # Use sync wrapper if available, otherwise handle async properly
                    model_info = None

                    # Try exact name first
                    if hasattr(backend, "get_model_info_sync"):
                        model_info = backend.get_model_info_sync(model_name)
                    elif hasattr(backend, "get_model_info"):
                        if hasattr(backend.get_model_info, "__await__"):
                            import asyncio

                            try:
                                model_info = asyncio.run(
                                    backend.get_model_info(model_name)
                                )
                            except Exception as e:
                                logger.debug(
                                    f"Async get_model_info failed for {bt.value}: {e}"
                                )
                                continue
                        else:
                            model_info = backend.get_model_info(model_name)

                    if model_info:
                        backend_type = bt
                        break

                    # Try with underscore conversion (for MLX backend)
                    if bt == SuperOptiXBackendType.MLX:
                        underscore_name = model_name.replace("/", "_")
                        if hasattr(backend, "get_model_info_sync"):
                            model_info = backend.get_model_info_sync(underscore_name)
                        else:
                            model_info = backend.get_model_info(underscore_name)
                        if model_info:
                            backend_type = bt
                            # Update model_name to the format the backend expects
                            model_name = underscore_name
                            break

                    # Try with slash conversion (for other backends)
                    else:
                        slash_name = model_name.replace("_", "/")
                        if hasattr(backend, "get_model_info_sync"):
                            model_info = backend.get_model_info_sync(slash_name)
                        elif hasattr(backend, "get_model_info"):
                            if hasattr(backend.get_model_info, "__await__"):
                                try:
                                    model_info = asyncio.run(
                                        backend.get_model_info(slash_name)
                                    )
                                except Exception as e:
                                    logger.debug(
                                        f"Async get_model_info failed for {bt.value}: {e}"
                                    )
                                    continue
                            else:
                                model_info = backend.get_model_info(slash_name)
                        if model_info:
                            backend_type = bt
                            # Update model_name to the format the backend expects
                            model_name = slash_name
                            break

                except Exception as e:
                    logger.debug(
                        f"Error checking {bt.value} for model {model_name}: {e}"
                    )
                    continue

        if not backend_type or backend_type not in self.backends:
            logger.error(f"Model {model_name} not found in any backend")
            return False

        try:
            backend = self.backends[backend_type]

            # Use sync wrapper if available, otherwise handle async
            if hasattr(backend, "uninstall_model_sync"):
                success = backend.uninstall_model_sync(model_name)
            elif hasattr(backend.uninstall_model, "__await__"):
                import asyncio

                success = asyncio.run(backend.uninstall_model(model_name))
            else:
                success = backend.uninstall_model(model_name)

            if success:
                # Update registry
                self.registry.remove_model(f"{backend_type.value}/{model_name}")
                # Refresh cache after removal
                self.refresh_model_cache()

            return success

        except Exception as e:
            logger.error(f"Failed to uninstall model {model_name}: {e}")
            return False

    def test_model(
        self,
        model_name: str,
        prompt: str = "Hello, world!",
        backend_type: Optional[SuperOptiXBackendType] = None,
    ) -> Dict[str, Any]:
        """Test a SuperOptiX model with a simple prompt."""
        # Only parse model name if no backend is provided
        if not backend_type:
            parsed_backend, parsed_name = parse_superoptix_model_name(model_name)
            if parsed_backend:
                backend_type = parsed_backend
                model_name = parsed_name
            else:
                # Use the detect_model_backend method which handles name conversions properly
                backend_type = self.detect_model_backend(model_name)

        if not backend_type or backend_type not in self.backends:
            return {"success": False, "error": f"Model {model_name} not found"}

        try:
            backend = self.backends[backend_type]

            # Use sync wrapper if available
            if hasattr(backend, "test_model_sync"):
                result = backend.test_model_sync(model_name, prompt)
            else:
                result = backend.test_model(model_name, prompt)

            # Update usage statistics
            try:
                # Use sync wrapper if available
                if hasattr(backend, "get_model_info_sync"):
                    model_info = backend.get_model_info_sync(model_name)
                else:
                    model_info = backend.get_model_info(model_name)
                if model_info:
                    model_info.usage_count += 1
                    self.registry.add_model(model_info)
            except Exception as e:
                # Log but don't fail the operation
                logger.warning(f"Failed to update usage statistics: {e}")

            return result

        except Exception as e:
            logger.error(f"Failed to test model {model_name}: {e}")
            return {"success": False, "error": str(e)}

    def create_dspy_client(
        self,
        model_name: str,
        backend_type: Optional[SuperOptiXBackendType] = None,
        **kwargs,
    ) -> Any:
        """Create a DSPy client for a SuperOptiX model."""
        # Parse model name if it includes backend
        parsed_backend, parsed_name = parse_superoptix_model_name(model_name)
        if parsed_backend:
            backend_type = parsed_backend
            model_name = parsed_name

        if not backend_type:
            # Find the backend that has this model
            for bt, backend in self.backends.items():
                try:
                    # Use sync wrapper if available
                    if hasattr(backend, "get_model_info_sync"):
                        model_info = backend.get_model_info_sync(model_name)
                    else:
                        model_info = backend.get_model_info(model_name)
                    if model_info:
                        backend_type = bt
                        break
                except:
                    continue

        if not backend_type or backend_type not in self.backends:
            raise ValueError(f"Model {model_name} not found in any backend")

        backend = self.backends[backend_type]

        # Use sync wrapper if available for create_dspy_client
        if hasattr(backend, "create_dspy_client_sync"):
            client = backend.create_dspy_client_sync(model_name, **kwargs)
        else:
            client = backend.create_dspy_client(model_name, **kwargs)

        # Update usage statistics
        try:
            # Use sync wrapper if available
            if hasattr(backend, "get_model_info_sync"):
                model_info = backend.get_model_info_sync(model_name)
            else:
                model_info = backend.get_model_info(model_name)
            if model_info:
                model_info.usage_count += 1
                self.registry.add_model(model_info)
        except Exception as e:
            # Log but don't fail the operation
            logger.warning(f"Failed to update usage statistics: {e}")

        return client

    def get_backend_info(self) -> List[SuperOptiXBackendInfo]:
        """Get information about all SuperOptiX backends."""
        backend_info = []

        for backend_type, backend in self.backends.items():
            try:
                # Use sync wrapper if available, otherwise use the original method
                if hasattr(backend, "get_backend_info_sync"):
                    info = backend.get_backend_info_sync()
                else:
                    info = backend.get_backend_info()
                backend_info.append(info)
            except Exception as e:
                # Create error info for failed backends
                backend_info.append(
                    SuperOptiXBackendInfo(
                        type=backend_type, available=False, status="error", error=str(e)
                    )
                )

        return backend_info

    def validate_model_compatibility(self, model_name: str) -> tuple[bool, List[str]]:
        """Validate if a model is compatible with the current SuperOptiX system."""
        model_info = self.get_model_info(model_name)
        if not model_info:
            return False, [f"Model {model_name} not found"]

        return validate_superoptix_model_compatibility(model_info)

    def get_system_info(self) -> Dict[str, Any]:
        """Get SuperOptiX system information."""
        return get_superoptix_system_info()

    def refresh_model_cache(self):
        """Refresh the SuperOptiX model cache."""
        # Clear cached models and re-discover
        for backend in self.backends.values():
            try:
                backend.refresh_cache()
            except Exception as e:
                logger.warning(f"Failed to refresh cache for backend: {e}")

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get SuperOptiX model usage statistics."""
        return self.registry.get_usage_statistics()

    def export_model_data(self, format: str = "json") -> Dict[str, Any]:
        """Export SuperOptiX model data."""
        return self.registry.export_data(format)

    def cleanup(self):
        """Clean up SuperOptiX model manager resources."""
        for backend in self.backends.values():
            try:
                backend.cleanup()
            except Exception as e:
                logger.warning(f"Failed to cleanup backend: {e}")

        self.registry.close()


# Legacy alias for backward compatibility
ModelManager = SuperOptiXModelManager
