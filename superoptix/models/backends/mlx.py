"""
SuperOptiX Model Intelligence System - MLX backend implementation.
"""

import logging
import platform
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console

from ..utils import (
    SuperOptiXModelInfo,
    SuperOptiXBackendInfo,
    SuperOptiXModelStatus,
    SuperOptiXBackendType,
    SuperOptiXModelSize,
    SuperOptiXModelTask,
)
from .base import SuperOptiXBaseBackend

logger = logging.getLogger(__name__)

console = Console()


class SuperOptiXMLXBackend(SuperOptiXBaseBackend):
    """SuperOptiX MLX backend for Apple Silicon model management."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_dir = Path(
            kwargs.get("cache_dir", "~/.cache/mlx-models")
        ).expanduser()
        self.default_quantization = kwargs.get("default_quantization", "4bit")

    @property
    def backend_type(self) -> SuperOptiXBackendType:
        return SuperOptiXBackendType.MLX

    def is_available(self) -> bool:
        """Check if MLX is available (Apple Silicon only)."""
        try:
            # Check if we're on Apple Silicon
            if platform.system() != "Darwin" or platform.machine() != "arm64":
                return False

            # Try to import MLX
            import mlx.core as mx  # noqa: F401
            import mlx.nn as nn  # noqa: F401

            return True
        except ImportError:
            return False

    def is_available_sync(self) -> bool:
        """Synchronous wrapper for is_available."""
        return self.is_available()

    def get_backend_info(self) -> SuperOptiXBackendInfo:
        """Get SuperOptiX MLX backend information."""
        try:
            if not self.is_available():
                return SuperOptiXBackendInfo(
                    type=self.backend_type,
                    available=False,
                    error="MLX requires Apple Silicon (M1/M2/M3) with macOS",
                    config=self.config,
                )

            # Get MLX version
            import mlx

            # Count installed models
            installed_models = self.list_installed_models()

            return SuperOptiXBackendInfo(
                type=self.backend_type,
                available=True,
                version=getattr(mlx, "__version__", "unknown"),
                status="available",
                models_count=len(installed_models),
                config=self.config,
            )
        except Exception as e:
            return SuperOptiXBackendInfo(
                type=self.backend_type,
                available=False,
                error=str(e),
                config=self.config,
            )

    def list_available_models(self) -> List[SuperOptiXModelInfo]:
        """List all available SuperOptiX MLX models."""
        # Return installed models plus some popular MLX-compatible models
        installed = self.list_installed_models()

        # Add popular models that can be converted to MLX
        popular_models = [
            (
                "mlx-community/Llama-3.2-1B-Instruct-4bit",
                "1B",
                SuperOptiXModelSize.TINY,
                SuperOptiXModelTask.CHAT,
                "Llama 3.2 1B quantized for MLX",
            ),
            (
                "mlx-community/Llama-3.2-3B-Instruct-4bit",
                "3B",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.CHAT,
                "Llama 3.2 3B quantized for MLX",
            ),
            (
                "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
                "8B",
                SuperOptiXModelSize.MEDIUM,
                SuperOptiXModelTask.CHAT,
                "Llama 3.1 8B quantized for MLX",
            ),
            (
                "mlx-community/CodeLlama-7b-Instruct-hf-4bit",
                "7B",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.CODE,
                "CodeLlama 7B quantized for MLX",
            ),
            (
                "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
                "7B",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.CHAT,
                "Mistral 7B quantized for MLX",
            ),
            (
                "mlx-community/Qwen2.5-7B-Instruct-4bit",
                "7B",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.REASONING,
                "Qwen 2.5 7B quantized for MLX",
            ),
            (
                "mlx-community/phi-3-mini-4k-instruct-4bit",
                "3.8B",
                SuperOptiXModelSize.SMALL,
                SuperOptiXModelTask.CHAT,
                "Phi-3 Mini quantized for MLX",
            ),
        ]

        # Track installed model names to avoid duplicates
        installed_names = {model.name for model in installed}

        # Add popular models that aren't installed
        for name, params, size, task, desc in popular_models:
            if name not in installed_names:
                installed.append(
                    SuperOptiXModelInfo(
                        name=name,
                        backend=self.backend_type,
                        status=SuperOptiXModelStatus.AVAILABLE,
                        size=size,
                        task=task,
                        description=desc,
                        parameters=params,
                        quantization=self.default_quantization,
                        tags=["popular", "mlx", task.value],
                    )
                )

        return installed

    def list_installed_models(self) -> List[SuperOptiXModelInfo]:
        """List installed SuperOptiX MLX models."""
        try:
            if not self.is_available():
                return []

            models = []

            # Check cache directory for downloaded models
            if self.cache_dir.exists():
                for model_dir in self.cache_dir.iterdir():
                    if model_dir.is_dir() and (model_dir / "config.json").exists():
                        # Validate MLX format
                        is_valid, message = self._validate_mlx_format(model_dir)

                        if is_valid:
                            # Parse model info from directory
                            name = model_dir.name

                            # Get directory size
                            disk_size = sum(
                                f.stat().st_size
                                for f in model_dir.rglob("*")
                                if f.is_file()
                            )

                            # Infer model characteristics
                            size_category = self._infer_model_size(name)
                            task = self._infer_model_task(name)
                            parameters = self._extract_parameters(name)

                            models.append(
                                SuperOptiXModelInfo(
                                    name=name,
                                    backend=self.backend_type,
                                    status=SuperOptiXModelStatus.INSTALLED,
                                    size=size_category,
                                    task=task,
                                    parameters=parameters,
                                    quantization="4bit" if "4bit" in name else None,
                                    disk_size=disk_size,
                                    local_path=model_dir,
                                    tags=[
                                        "installed",
                                        "mlx",
                                        task.value if task else "unknown",
                                    ],
                                )
                            )

            return models
        except Exception as e:
            logger.error(f"Error listing installed MLX models: {e}")
            return []

    def list_installed_models_sync(self) -> List[SuperOptiXModelInfo]:
        """List installed SuperOptiX MLX models (sync version)."""
        return self.list_installed_models()

    def install_model(self, model_name: str, **kwargs) -> bool:
        """Install a SuperOptiX model for MLX using proper MLX-LM download features."""
        try:
            if not self.is_available():
                console.print(
                    "❌ MLX is not available. Install with: pip install mlx mlx-lm"
                )
                return False

            # REMOVE ALL WRAPPER MESSAGES - LET NATIVE OUTPUT SHOW
            try:
                from mlx_lm.utils import get_model_path

                # Create model directory
                model_path = self.cache_dir / model_name.replace("/", "_")
                model_path.mkdir(parents=True, exist_ok=True)

                # DIRECT NATIVE CALL - NO WRAPPER MESSAGES AT ALL
                local_path, hf_path = get_model_path(model_name)

                # Copy the downloaded model to our cache directory
                if local_path.exists() and local_path != model_path:
                    import shutil

                    if model_path.exists():
                        shutil.rmtree(model_path)
                    shutil.copytree(local_path, model_path)

                # NO SUCCESS MESSAGE - LET NATIVE OUTPUT HANDLE IT
                return True

            except Exception as e:
                console.print(f"❌ Failed to download {model_name}: {e}")
                return False

        except Exception as e:
            console.print(f"❌ Failed to install {model_name}: {e}")
            return False

    def uninstall_model(self, model_name: str) -> bool:
        """Uninstall a SuperOptiX model from MLX."""
        try:
            model_path = self.cache_dir / model_name.replace("/", "_")
            if model_path.exists():
                import shutil

                shutil.rmtree(model_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error uninstalling MLX model {model_name}: {e}")
            return False

    def get_model_info_sync(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Get information about a specific SuperOptiX model (sync version)."""
        return self.get_model_info(model_name)

    def get_model_info(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Get information about a specific SuperOptiX model."""
        try:
            # First check if it's installed
            installed_models = self.list_installed_models()
            for model in installed_models:
                # Check exact name match
                if model.name == model_name:
                    return model
                # Check if it's the same model with different naming (e.g., microsoft/phi-2 vs microsoft_phi-2)
                if model.name == model_name.replace("/", "_"):
                    return model
                if model.name.replace("_", "/") == model_name:
                    return model

            # If not installed, check if it's available
            available_models = self.list_available_models()
            for model in available_models:
                if model.name == model_name:
                    return model

            return None
        except Exception as e:
            logger.debug(f"Error getting MLX model info for {model_name}: {e}")
            return None

    def test_model(
        self, model_name: str, prompt: str = "Hello, world!"
    ) -> Dict[str, Any]:
        """Test a SuperOptiX model with a simple prompt."""
        try:
            # Import MLX dependencies
            from mlx_lm import load, generate

            # Find model path
            model_path = self.cache_dir / model_name.replace("/", "_")
            if not model_path.exists():
                return {
                    "success": False,
                    "error": f"Model {model_name} not found locally",
                    "model": model_name,
                    "prompt": prompt,
                }

            start_time = datetime.now()

            # Check for proper MLX format
            has_safetensors = any(
                f.name.endswith(".safetensors")
                for f in model_path.iterdir()
                if f.is_file()
            )
            has_weights = (model_path / "weights.npz").exists()

            if not (has_safetensors or has_weights):
                return {
                    "success": False,
                    "error": f"Model {model_name} does not have proper MLX format (safetensors or weights.npz)",
                    "model": model_name,
                    "prompt": prompt,
                }

            # Load model and tokenizer
            model, tokenizer = load(str(model_path))

            # Tokenize input to get prompt tokens
            prompt_tokens = len(tokenizer.encode(prompt))

            # Generate response
            response = generate(model, tokenizer, prompt, max_tokens=50)

            # Estimate response tokens (MLX doesn't provide exact count)
            response_tokens = len(response.split()) * 1.3  # Rough estimate

            end_time = datetime.now()

            return {
                "success": True,
                "response": response,
                "model": model_name,
                "prompt": prompt,
                "response_time": (end_time - start_time).total_seconds(),
                "prompt_tokens": prompt_tokens,
                "tokens": int(response_tokens),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name,
                "prompt": prompt,
            }

    def create_dspy_client(self, model_name: str, **kwargs):
        """Create a DSPy-compatible client for SuperOptiX MLX."""
        try:
            # Use the same pattern as Ollama - dspy.LM with custom_openai/ prefix
            # LiteLLM supports MLX through the custom_openai provider
            import dspy

            # Extract parameters and avoid conflicts
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 2048)
            api_base = kwargs.pop("api_base", "http://localhost:8000")

            return dspy.LM(
                model=f"custom_openai/{model_name}",
                api_base=api_base,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

        except ImportError as e:
            raise RuntimeError(f"Failed to import DSPy: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create MLX DSPy client: {e}")

    def _infer_model_size(self, model_name: str) -> Optional[SuperOptiXModelSize]:
        """Infer model size from name."""
        name_lower = model_name.lower()

        if any(x in name_lower for x in ["1b", "1.3b", "1.5b"]):
            return SuperOptiXModelSize.TINY
        elif any(x in name_lower for x in ["3b", "7b", "6.7b"]):
            return SuperOptiXModelSize.SMALL
        elif any(x in name_lower for x in ["8b", "13b", "14b"]):
            return SuperOptiXModelSize.MEDIUM
        elif any(x in name_lower for x in ["30b", "34b", "70b", "72b"]):
            return SuperOptiXModelSize.LARGE

        return None

    def _infer_model_task(self, model_name: str) -> Optional[SuperOptiXModelTask]:
        """Infer model task from name."""
        name_lower = model_name.lower()

        if any(x in name_lower for x in ["code", "coder"]):
            return SuperOptiXModelTask.CODE
        elif any(x in name_lower for x in ["embed", "embedding"]):
            return SuperOptiXModelTask.EMBEDDING
        elif any(x in name_lower for x in ["vision", "llava"]):
            return SuperOptiXModelTask.VISION
        elif any(x in name_lower for x in ["qwen", "reasoning"]):
            return SuperOptiXModelTask.REASONING
        else:
            return SuperOptiXModelTask.CHAT

    def _extract_parameters(self, model_name: str) -> Optional[str]:
        """Extract parameter count from model name."""

        # Look for patterns like 1B, 3B, 7B, etc.
        match = re.search(r"(\d+(?:\.\d+)?[bm])", model_name.lower())
        if match:
            return match.group(1).upper()

        return None

    def _validate_mlx_format(self, model_path: Path) -> tuple[bool, str]:
        """Validate that a model is in proper MLX format."""
        try:
            # Check for essential MLX files
            required_files = []
            optional_files = []

            # Essential files for MLX
            if (model_path / "config.json").exists():
                required_files.append("config.json")
            else:
                return False, "Missing config.json"

            # Check for tokenizer files (multiple formats supported)
            tokenizer_files = []
            if (model_path / "tokenizer.json").exists():
                tokenizer_files.append("tokenizer.json")
            if (model_path / "vocab.json").exists():
                tokenizer_files.append("vocab.json")
            if (model_path / "tokenizer_config.json").exists():
                tokenizer_files.append("tokenizer_config.json")

            if tokenizer_files:
                required_files.extend(tokenizer_files)
            else:
                return (
                    False,
                    "Missing tokenizer files (expected tokenizer.json, vocab.json, or tokenizer_config.json)",
                )

            # Check for MLX-specific model files
            mlx_model_files = []

            # Check for safetensors files (most common MLX format)
            safetensors_files = list(model_path.glob("*.safetensors"))
            if safetensors_files:
                mlx_model_files.extend([f.name for f in safetensors_files])

            # Check for weights.npz (alternative MLX format)
            if (model_path / "weights.npz").exists():
                mlx_model_files.append("weights.npz")

            # Check for safetensors index files
            safetensors_index_files = list(model_path.glob("*.safetensors.index.json"))
            if safetensors_index_files:
                mlx_model_files.extend([f.name for f in safetensors_index_files])

            # Check for pytorch_model.bin (should NOT be present in MLX format)
            pytorch_files = list(model_path.glob("*.bin"))
            if pytorch_files:
                return (
                    False,
                    f"Found PyTorch files: {[f.name for f in pytorch_files]}. MLX models should not contain .bin files.",
                )

            # Must have at least one MLX model file
            if not mlx_model_files:
                return (
                    False,
                    "No MLX model files found (expected .safetensors, weights.npz, or .safetensors.index.json)",
                )

            # Accept any model that has the required files, regardless of naming pattern
            # (MLX can work with any HuggingFace model that's been converted)
            return (
                True,
                f"Valid MLX format with files: {required_files + mlx_model_files}",
            )

        except Exception as e:
            return False, f"Error validating MLX format: {e}"

    def _estimate_download_time(self, model_name: str) -> Optional[str]:
        """Estimate download time based on model size and name patterns."""
        try:
            # Estimate based on model name patterns
            name_lower = model_name.lower()

            # Small models (1-3B parameters)
            if any(
                x in name_lower
                for x in [
                    "1b",
                    "1.3b",
                    "1.5b",
                    "2b",
                    "2.7b",
                    "3b",
                    "phi-1",
                    "phi-2",
                    "dialo",
                ]
            ):
                return "2-5 minutes"

            # Medium models (7-13B parameters)
            elif any(x in name_lower for x in ["7b", "8b", "13b", "14b"]):
                return "5-15 minutes"

            # Large models (30B+ parameters)
            elif any(x in name_lower for x in ["30b", "34b", "70b", "72b"]):
                return "15-45 minutes"

            # Very large models (100B+ parameters)
            elif any(x in name_lower for x in ["100b", "175b", "200b"]):
                return "30-90 minutes"

            # Default estimate for unknown models
            else:
                return "5-20 minutes"

        except Exception:
            return None

    def install_model_sync(self, model_name: str, **kwargs) -> bool:
        """Synchronous wrapper for install_model (for compatibility with model manager)."""
        return self.install_model(model_name, **kwargs)

    def get_model_info_sync(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Synchronous wrapper for get_model_info."""
        return self.get_model_info(model_name)
