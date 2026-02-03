"""
SuperOptiX Model Intelligence System - Ollama backend implementation.
"""

import re
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
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

console = Console()


class SuperOptiXOllamaBackend(SuperOptiXBaseBackend):
    """SuperOptiX Model Intelligence - Ollama backend for local model management."""

    def __init__(self, host: str = "localhost", port: int = 11434, **kwargs):
        super().__init__(**kwargs)
        self.host = f"http://{host}:{port}"

    @property
    def backend_type(self) -> SuperOptiXBackendType:
        return SuperOptiXBackendType.OLLAMA

    def _run_ollama_command(
        self, command: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run an ollama command using subprocess."""
        try:
            return subprocess.run(
                ["ollama"] + command,
                capture_output=capture_output,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ollama command failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Ollama command not found. Please install Ollama first.")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            # Check if ollama command exists
            if not shutil.which("ollama"):
                return False

            # Check if ollama service is running by trying to list models
            self._run_ollama_command(["list"])
            return True
        except Exception:
            return False

    def is_available_sync(self) -> bool:
        """Synchronous wrapper for is_available."""
        return self.is_available()

    def get_backend_info(self) -> SuperOptiXBackendInfo:
        """Get SuperOptiX Ollama backend information."""
        try:
            if not self.is_available():
                return SuperOptiXBackendInfo(
                    type=self.backend_type,
                    available=False,
                    error="Ollama not installed or service not running",
                    config=self.config,
                )

            # Get installed models
            result = self._run_ollama_command(["list"])
            models = []

            # Parse the output (skip header line)
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        models.append(parts[0])  # Model name

            parsed_host = urlparse(self.host)

            return SuperOptiXBackendInfo(
                type=self.backend_type,
                available=True,
                version="latest",  # Ollama doesn't expose version via CLI
                host=parsed_host.hostname,
                port=parsed_host.port or 11434,
                status="running",
                models_count=len(models),
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
        """List all available SuperOptiX models (focus on installed for SuperOptiX philosophy)."""
        # SuperOptiX philosophy: Focus on what you actually have installed
        # This avoids overwhelming users with hundreds of models that change frequently
        return self.list_installed_models()

    def list_installed_models(self) -> List[SuperOptiXModelInfo]:
        """List installed SuperOptiX Ollama models."""
        try:
            result = self._run_ollama_command(["list"])
            models = []

            # Parse the output (skip header line)
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        name = parts[0]
                        size_str = parts[2]
                        modified_str = (
                            parts[3] + " " + parts[4] if len(parts) > 4 else "Unknown"
                        )

                        # Convert size to bytes (approximate)
                        size_bytes = self._parse_size(size_str)

                        # Parse modified date
                        modified = self._parse_date(modified_str)

                        # Infer model characteristics from name
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
                                disk_size=size_bytes,
                                last_used=modified,
                                tags=[
                                    "superoptix",
                                    "installed",
                                    task.value if task else "unknown",
                                ],
                            )
                        )

            return models
        except Exception:
            return []

    def list_installed_models_sync(self) -> List[SuperOptiXModelInfo]:
        """List installed SuperOptiX Ollama models (sync version)."""
        return self.list_installed_models()

    def install_model(self, model_name: str, **kwargs) -> bool:
        """Install a SuperOptiX model from Ollama."""
        # Step 1: Check if Ollama is installed
        if not shutil.which("ollama"):
            console.print("❌ Ollama is not installed on your system.")
            console.print()
            console.print("[bold]Install Ollama:[/bold]")
            console.print("  🌐 Visit: [bold cyan]https://ollama.com[/bold cyan]")
            console.print("  📥 Download and install for your platform")
            console.print("  🔧 Or use the installer script:")
            console.print(
                "     [bold cyan]curl -fsSL https://ollama.com/install.sh | sh[/bold cyan]"
            )
            console.print()
            console.print("💡 After installing Ollama, run this command again:")
            console.print(
                f"  [bold green]super model install {model_name}[/bold green]"
            )
            return False

        # Step 2: Check if Ollama service is running
        try:
            self._run_ollama_command(["list"])
        except Exception:
            console.print("❌ Ollama service is not running.")
            console.print()
            console.print("🚀 [bold]Start Ollama:[/bold]")
            console.print("  [bold cyan]ollama serve[/bold cyan]")
            console.print()
            console.print("💡 Or start it in the background:")
            console.print("  [bold cyan]ollama serve &[/bold cyan]")
            console.print()
            console.print("After starting Ollama, run this command again:")
            console.print(
                f"  [bold green]super model install {model_name}[/bold green]"
            )
            return False

        # Step 3: Check if model is already installed
        try:
            installed_models = self.list_installed_models()
            for model in installed_models:
                if model.name == model_name:
                    console.print(
                        f"✅ Model [bold green]{model_name}[/bold green] is already installed!"
                    )
                    return True
        except Exception as e:
            console.print(f"⚠️  Warning: Could not check installed models: {e}")

        # Step 4: Pull the model
        console.print(
            f"🦙 Pulling model [bold cyan]{model_name}[/bold cyan] from Ollama..."
        )
        console.print(
            "⏳ This may take a few minutes depending on your internet connection and model size."
        )
        console.print()

        try:
            # Run ollama pull command
            self._run_ollama_command(["pull", model_name], capture_output=False)

            console.print("✅ Model pulled successfully!")
            console.print()
            console.print("📊 Model details:")
            # Try to get model info after installation
            try:
                model_info = self.get_model_info(model_name)
                if model_info:
                    console.print(
                        f"  • Size: {model_info.size.value if model_info.size else 'Unknown'}"
                    )
                    console.print(
                        f"  • Task: {model_info.task.value if model_info.task else 'General'}"
                    )
                    console.print(
                        f"  • Parameters: {model_info.parameters or 'Unknown'}"
                    )
                    if model_info.size_gb:
                        console.print(f"  • Disk Size: {model_info.size_gb:.1f}GB")
            except Exception:
                pass

            return True

        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to pull model: {e}")
            return False
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}")
            return False

    def uninstall_model(self, model_name: str) -> bool:
        """Uninstall a SuperOptiX model from Ollama."""
        try:
            self._run_ollama_command(["rm", model_name])
            return True
        except Exception:
            return False

    def get_model_info(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Get information about a specific SuperOptiX model."""
        try:
            # Check if it's installed (SuperOptiX focus on installed models)
            installed_models = self.list_installed_models()
            for model in installed_models:
                if model.name == model_name:
                    return model

            return None
        except Exception:
            return None

    def test_model(
        self, model_name: str, prompt: str = "Hello, world!"
    ) -> Dict[str, Any]:
        """Test a SuperOptiX model with a simple prompt."""
        try:
            start_time = datetime.now()
            result = self._run_ollama_command(["run", model_name, prompt])
            end_time = datetime.now()

            response = result.stdout.strip()

            # Estimate tokens (Ollama CLI doesn't provide exact counts)
            estimated_tokens = len(response.split()) * 1.3  # Rough estimate
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimate

            return {
                "success": True,
                "response": response,
                "model": model_name,
                "prompt": prompt,
                "response_time": (end_time - start_time).total_seconds(),
                "tokens": int(estimated_tokens),
                "prompt_tokens": int(prompt_tokens),
                "superoptix": True,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name,
                "prompt": prompt,
                "superoptix": True,
            }

    async def create_dspy_client(self, model_name: str, **kwargs):
        """Create a DSPy-compatible client for Ollama."""
        try:
            # Try to use the direct Ollama client from DSPy if available
            import sys

            sys.path.insert(
                0, str(Path(__file__).parent.parent.parent.parent / "dspy-latest")
            )
            from dspy.clients.ollama_direct import OllamaDirect

            # Extract parameters and avoid conflicts
            temperature = kwargs.pop("temperature", 0.0)
            max_tokens = kwargs.pop("max_tokens", 4000)

            return OllamaDirect(
                model=model_name,
                api_base=self.host,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except ImportError:
            # Fall back to standard DSPy LM with ollama prefix
            import sys

            sys.path.insert(
                0, str(Path(__file__).parent.parent.parent.parent / "dspy-latest")
            )
            import dspy

            # Extract parameters and avoid conflicts
            temperature = kwargs.pop("temperature", 0.0)
            max_tokens = kwargs.pop("max_tokens", 4000)

            return dspy.LM(
                model=f"ollama/{model_name}",
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

    def _parse_size(self, size_str: str) -> Optional[int]:
        """Parse size string from ollama list output."""
        try:
            if "GB" in size_str:
                return int(float(size_str.replace("GB", "")) * 1024 * 1024 * 1024)
            elif "MB" in size_str:
                return int(float(size_str.replace("MB", "")) * 1024 * 1024)
            elif "KB" in size_str:
                return int(float(size_str.replace("KB", "")) * 1024)
            else:
                return int(size_str)
        except:
            return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from ollama list output."""
        try:
            # Handle formats like "5 months ago", "9 days ago", etc.
            if "ago" in date_str:
                # For now, return current time as approximation
                return datetime.now()
            else:
                # Try to parse actual date
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except:
            return None

    def _infer_model_size(self, model_name: str) -> Optional[SuperOptiXModelSize]:
        """Infer model size from name."""
        name_lower = model_name.lower()

        if any(x in name_lower for x in ["1b", "1.3b", "1.5b"]):
            return SuperOptiXModelSize.TINY
        elif any(x in name_lower for x in ["3b", "7b", "6.7b"]):
            return SuperOptiXModelSize.SMALL
        elif any(x in name_lower for x in ["8b", "13b", "14b", "8x7b"]):
            return SuperOptiXModelSize.MEDIUM
        elif any(x in name_lower for x in ["30b", "34b", "70b", "72b", "8x22b"]):
            return SuperOptiXModelSize.LARGE

        return None

    def _infer_model_task(self, model_name: str) -> Optional[SuperOptiXModelTask]:
        """Infer model task from name."""
        name_lower = model_name.lower()

        if any(x in name_lower for x in ["code", "coder", "starcoder"]):
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
        # Look for patterns like :7b, :13b, etc.
        match = re.search(r":(\d+(?:\.\d+)?[bm])", model_name.lower())
        if match:
            return match.group(1).upper()

        # Look for patterns like 8x7b
        match = re.search(r"(\d+x\d+[bm])", model_name.lower())
        if match:
            return match.group(1).upper()

        return None
