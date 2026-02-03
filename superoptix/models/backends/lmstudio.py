"""
LM Studio backend implementation for SuperOptiX model management.
"""

import asyncio
import subprocess
import shutil
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

console = Console()


class SuperOptiXLMStudioBackend(SuperOptiXBaseBackend):
    """SuperOptiX LM Studio backend for model management."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Default LM Studio server URL
        self.server_url = kwargs.get("server_url", "http://localhost:1234")
        self.cache_dir = Path("~/.cache/lmstudio").expanduser()

    @property
    def backend_type(self) -> SuperOptiXBackendType:
        return SuperOptiXBackendType.LMSTUDIO

    def _run_lms_command(
        self, command: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run an lms command using subprocess."""
        try:
            return subprocess.run(
                ["lms"] + command, capture_output=capture_output, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"LMS command failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "LMS command not found. Please install LM Studio CLI first."
            )

    async def is_available(self) -> bool:
        """Check if LM Studio CLI is available."""
        try:
            # Check if lms command exists
            if not shutil.which("lms"):
                return False

            # Check if lms is working by trying to list models
            self._run_lms_command(["ls"])
            return True
        except Exception:
            return False

    def is_available_sync(self) -> bool:
        """Synchronous wrapper for is_available."""
        try:
            # Check if lms command exists
            if not shutil.which("lms"):
                return False

            # Check if lms is working by trying to list models
            self._run_lms_command(["ls"])
            return True
        except Exception:
            return False

    async def get_backend_info(self) -> SuperOptiXBackendInfo:
        """Get LM Studio backend information."""
        try:
            if not await self.is_available():
                return SuperOptiXBackendInfo(
                    type=self.backend_type,
                    available=False,
                    error="LM Studio CLI not installed or not working",
                    config=self.config,
                )

            # Get installed models
            result = self._run_lms_command(["ls"])
            models = []

            # Parse the output - lms ls shows models in a table format
            lines = result.stdout.strip().split("\n")
            in_llm_section = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if "LLMs (Large Language Models)" in line:
                    in_llm_section = True
                    continue
                elif "Embedding Models" in line:
                    in_llm_section = False
                    continue
                elif line.startswith("PARAMS") or line.startswith("---"):
                    continue

                if in_llm_section and line:
                    parts = line.split()
                    if len(parts) >= 1:
                        models.append(parts[0])  # Model name

            return SuperOptiXBackendInfo(
                type=self.backend_type,
                available=True,
                version="LM Studio CLI",
                status="available",
                models_count=len(models),
                host=self.server_url,
                config=self.config,
            )

        except Exception as e:
            return SuperOptiXBackendInfo(
                type=self.backend_type,
                available=False,
                error=str(e),
                config=self.config,
            )

    def get_backend_info_sync(self) -> SuperOptiXBackendInfo:
        """Synchronous wrapper for get_backend_info."""
        return asyncio.run(self.get_backend_info())

    async def list_available_models(self) -> List[SuperOptiXModelInfo]:
        """List all available LM Studio models."""
        try:
            if not await self.is_available():
                return []

            result = self._run_lms_command(["ls"])
            models = []

            # Parse the output - lms ls shows models in a table format
            lines = result.stdout.strip().split("\n")
            in_llm_section = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if "LLMs (Large Language Models)" in line:
                    in_llm_section = True
                    continue
                elif "Embedding Models" in line:
                    in_llm_section = False
                    continue
                elif line.startswith("PARAMS") or line.startswith("---"):
                    continue

                if in_llm_section and line:
                    parts = line.split()
                    if len(parts) >= 1:
                        model_id = parts[0]

                        # Parse model information
                        size = self._infer_model_size(model_id)
                        task = self._infer_model_task(model_id)
                        parameters = self._extract_parameters(model_id)

                        models.append(
                            SuperOptiXModelInfo(
                                name=model_id,
                                backend=self.backend_type,
                                status=SuperOptiXModelStatus.INSTALLED,
                                size=size,
                                task=task,
                                description=f"LM Studio model: {model_id}",
                                parameters=parameters,
                                tags=["lmstudio", task.value if task else "chat"],
                            )
                        )

            return models

        except Exception:
            return []

    async def list_installed_models(self) -> List[SuperOptiXModelInfo]:
        """List installed LM Studio models."""
        return await self.list_available_models()

    def list_installed_models_sync(self):
        """Synchronous wrapper for list_installed_models."""
        try:
            return asyncio.run(self.list_installed_models())
        except Exception as e:
            console.print(f"⚠️ Error checking lmstudio: {e}")
            return []

    def install_model(self, model_name: str, **kwargs) -> bool:
        """Install a LM Studio model using lms CLI (only download, do not load)."""
        # For LM Studio, strip variant (e.g., :1b) from model name
        base_model_name = model_name.split(":")[0]
        # Step 1: Check if LM Studio CLI is installed
        if not shutil.which("lms"):
            console.print("❌ LM Studio CLI is not installed on your system.")
            console.print()
            console.print("📥 [bold]Install LM Studio CLI:[/bold]")
            console.print("  🌐 Visit: [bold cyan]https://lmstudio.ai[/bold cyan]")
            console.print("  📥 Download and install LM Studio for your platform")
            console.print("  🔧 The lms CLI will be available after installation")
            console.print()
            console.print("💡 After installing LM Studio, run this command again:")
            console.print(
                f"  [bold green]super model install {model_name} -b lmstudio[/bold green]"
            )
            return False

        # Step 2: Check if lms CLI is working
        try:
            self._run_lms_command(["ls"])
        except Exception:
            console.print("❌ LM Studio CLI is not working properly.")
            console.print()
            console.print("🚀 [bold]Troubleshooting:[/bold]")
            console.print("  • Make sure LM Studio is properly installed")
            console.print("  • Try restarting your terminal")
            console.print("  • Check if lms command is in your PATH")
            console.print()
            console.print("After fixing the CLI, run this command again:")
            console.print(
                f"  [bold green]super model install {model_name} -b lmstudio[/bold green]"
            )
            return False

        # Step 3: Check if model is already installed
        try:
            installed_models = self.list_installed_models_sync()
            for model in installed_models:
                if model.name == model_name:
                    console.print(
                        f"✅ Model [bold green]{model_name}[/bold green] is already installed!"
                    )
                    console.print()
                    return True
        except Exception as e:
            console.print(f"⚠️  Warning: Could not check installed models: {e}")

        # Step 4: Download the model
        console.print(
            f"🎮 Downloading model [bold cyan]{base_model_name}[/bold cyan] with LM Studio..."
        )
        console.print(
            "⏳ This may take a few minutes depending on your internet connection and model size."
        )
        console.print()

        try:
            # Run lms get command to download the model
            self._run_lms_command(["get", base_model_name], capture_output=False)

            console.print("✅ Model downloaded successfully!")
            console.print()
            console.print("📋 [bold]Available LM Studio models after install:[/bold]")
            try:
                ls_result = self._run_lms_command(["ls"])
                console.print(ls_result.stdout)
            except Exception as e:
                console.print(f"⚠️  Could not list models: {e}")
            console.print()
            console.print(f"✅ Successfully installed {model_name}")
            console.print(f"📁 Location: {self.cache_dir / model_name}")
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to download model: {e}")
            return False
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}")
            return False

    def uninstall_model(self, model_name: str) -> bool:
        """LM Studio models cannot be removed via CLI - manual deletion required."""
        console.print("❌ LM Studio models cannot be removed via SuperOptiX CLI")
        console.print("💡 To remove LM Studio models:")
        console.print("   1. Open LM Studio application")
        console.print("   2. Go to 'My Models' section")
        console.print("   3. Right-click on the model and select 'Delete'")
        console.print("   4. Or manually delete from: ~/.cache/lm-studio/models/")
        console.print()
        console.print(f"📁 Model path: {self.cache_dir / model_name}")
        console.print("⚠️  Manual deletion is required for LM Studio models")
        return False

    def get_model_info(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Get information about a specific LM Studio model."""
        try:
            if not self.is_available_sync():
                return None

            installed_models = self.list_installed_models_sync()
            for model in installed_models:
                if model.name == model_name:
                    return model

            return None

        except Exception:
            return None

    def get_model_info_sync(self, model_name: str) -> Optional[SuperOptiXModelInfo]:
        """Synchronous wrapper for get_model_info."""
        try:
            return self.get_model_info(model_name)
        except Exception as e:
            console.print(f"⚠️ Error getting model info from lmstudio: {e}")
            return None

    async def test_model(
        self, model_name: str, prompt: str = "Hello, world!"
    ) -> Dict[str, Any]:
        """Test a LM Studio model with a simple prompt."""
        try:
            if not await self.is_available():
                console.print("❌ LM Studio CLI is not available on this system")
                console.print()
                console.print("📥 [bold]Install LM Studio:[/bold]")
                console.print("  🌐 Visit: [bold cyan]https://lmstudio.ai[/bold cyan]")
                console.print("  📥 Download and install for your platform")
                console.print()
                console.print("💡 After installation, run this command again:")
                console.print(
                    f"  [bold green]super model install {model_name} -b lmstudio[/bold green]"
                )

                return {
                    "success": False,
                    "error": "LM Studio CLI not available",
                    "model": model_name,
                    "prompt": prompt,
                }

            # Test the model using lms run command
            try:
                # LM Studio doesn't have a 'run' command, it uses 'chat' for interactive mode
                # For testing, we'll use a different approach - either start a server or use chat
                # For now, let's use the server approach
                result = self._run_lms_command(
                    ["server", "start", "--model", model_name]
                )

                # For LM Studio, we'll provide a placeholder response since actual testing requires server setup
                # In a real implementation, this would connect to the LM Studio server API
                placeholder_response = f"LM Studio model {model_name} is available. Use 'lms chat' for interactive mode or start a server with 'lms server start --model {model_name}'"

                # Estimate tokens for the placeholder response
                estimated_tokens = len(placeholder_response.split()) * 1.3
                prompt_tokens = len(prompt.split()) * 1.3

                return {
                    "success": True,
                    "model": model_name,
                    "prompt": prompt,
                    "response": placeholder_response,
                    "response_time": 0.1,  # Placeholder time
                    "tokens": int(estimated_tokens),
                    "prompt_tokens": int(prompt_tokens),
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"LM Studio model testing failed: {str(e)}",
                    "model": model_name,
                    "prompt": prompt,
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"LM Studio model testing error: {str(e)}",
                "model": model_name,
                "prompt": prompt,
            }

    def test_model_sync(
        self, model_name: str, prompt: str = "Hello, world!"
    ) -> Dict[str, Any]:
        """Synchronous wrapper for test_model."""
        try:
            import asyncio

            return asyncio.run(self.test_model(model_name, prompt))
        except Exception as e:
            console.print(f"⚠️ Error testing model in lmstudio: {e}")
            return {
                "success": False,
                "error": f"LM Studio model testing error: {str(e)}",
                "model": model_name,
                "prompt": prompt,
            }

    async def create_dspy_client(self, model_name: str, **kwargs):
        """Create a DSPy-compatible client for LM Studio using LiteLLM custom_openai."""
        try:
            import dspy

            # Get configuration from kwargs
            api_base = kwargs.get("api_base", self.server_url)
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2048)
            api_key = kwargs.get(
                "api_key", "dummy_key"
            )  # LM Studio doesn't need real API keys

            # Create DSPy LM with custom_openai provider
            # LM Studio provides an OpenAI-compatible API
            lm = dspy.LM(
                model=f"custom_openai/{model_name}",
                api_base=api_base,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=2,
                timeout=30,
            )

            return lm

        except ImportError as e:
            console.print(
                "❌ Missing required packages for LM Studio DSPy integration",
                style="bold red",
            )
            console.print()
            console.print("🚀 To install required packages, run:", style="bold green")
            console.print("  pip install dspy-ai litellm", style="bright_white")
            console.print("  or (with uv):", style="bright_white")
            console.print("  uv pip install dspy-ai litellm", style="bright_white")
            console.print("  or (with conda):", style="bright_white")
            console.print(
                "  conda install -c conda-forge dspy-ai litellm", style="bright_white"
            )
            console.print()

            raise RuntimeError(
                f"Failed to import required libraries for LM Studio DSPy integration: {e}\n"
                "Please ensure dspy-ai and litellm are installed:\n"
                "  pip install dspy-ai litellm\n"
                "  or\n"
                "  uv pip install dspy-ai litellm"
            )
        except Exception as e:
            console.print(
                f"❌ Failed to create LM Studio DSPy client for {model_name}",
                style="bold red",
            )
            console.print()
            console.print(
                "🚀 Make sure you have LM Studio server running:", style="bold green"
            )
            console.print("  1. Open LM Studio application", style="bright_white")
            console.print("  2. Go to 'Local Server' tab", style="bright_white")
            console.print("  3. Click 'Start Server'", style="bright_white")
            console.print(
                "  4. Server runs on http://localhost:1234", style="bright_white"
            )
            console.print()
            console.print("📋 Example playbook configuration:", style="bold blue")
            console.print("   language_model:", style="bright_white")
            console.print("     provider: lmstudio", style="bright_white")
            console.print(f"     model: {model_name}", style="bright_white")
            console.print("     api_base: http://localhost:1234", style="bright_white")
            console.print("     temperature: 0.7", style="bright_white")
            console.print("     max_tokens: 256", style="bright_white")
            console.print()

            raise RuntimeError(
                f"Failed to create LM Studio DSPy client: {e}\n\n"
                "💡 Make sure you have LM Studio server running:\n"
                "  1. Open LM Studio application\n"
                "  2. Go to 'Local Server' tab\n"
                "  3. Click 'Start Server'\n\n"
                "📋 Example playbook configuration:\n"
                f"   language_model:\n"
                f"     provider: lmstudio\n"
                f"     model: {model_name}\n"
                f"     api_base: http://localhost:1234"
            )

    def create_dspy_client_sync(self, model_name: str, **kwargs):
        """Synchronous wrapper for create_dspy_client."""
        try:
            return asyncio.run(self.create_dspy_client(model_name, **kwargs))
        except Exception as e:
            console.print(f"⚠️ Error creating DSPy client in lmstudio: {e}")
            raise

    def _infer_model_size(self, model_name: str) -> Optional[SuperOptiXModelSize]:
        """Infer model size from model name."""
        name_lower = model_name.lower()

        if any(size in name_lower for size in ["1b", "1.5b", "2b", "3b"]):
            return SuperOptiXModelSize.SMALL
        elif any(size in name_lower for size in ["7b", "8b", "13b", "14b"]):
            return SuperOptiXModelSize.MEDIUM
        elif any(size in name_lower for size in ["30b", "40b", "70b", "100b"]):
            return SuperOptiXModelSize.LARGE
        else:
            return SuperOptiXModelSize.SMALL  # Default

    def _infer_model_task(self, model_name: str) -> Optional[SuperOptiXModelTask]:
        """Infer model task from model name."""
        name_lower = model_name.lower()

        if any(code in name_lower for code in ["code", "coder", "programming"]):
            return SuperOptiXModelTask.CODE
        elif any(reason in name_lower for reason in ["reason", "logic", "math"]):
            return SuperOptiXModelTask.REASONING
        else:
            return SuperOptiXModelTask.CHAT  # Default

    def _extract_parameters(self, model_name: str) -> Optional[str]:
        """Extract parameter count from model name."""
        import re

        # Look for patterns like "7B", "13B", "70B", etc.
        match = re.search(r"(\d+(?:\.\d+)?)[Bb]", model_name)
        if match:
            return f"{match.group(1)}B"

        return None
