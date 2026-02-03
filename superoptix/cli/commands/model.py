"""
SuperOptiX Model Intelligence System - CLI commands for model management.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
import sys


console = Console()
from ...models.manager import SuperOptiXModelManager
from ...models.utils import (
    SuperOptiXBackendType,
    SuperOptiXModelSize,
    SuperOptiXModelTask,
    SuperOptiXModelStatus,
    SuperOptiXModelFilter,
    get_superoptix_model_discovery_guide,
)
from ...models.config import get_superoptix_model_discovery_settings

app = typer.Typer(name="model", help="🚀 SuperOptiX Model Intelligence System")


@app.command("list")
def list_models(
    backend: Optional[str] = typer.Option(
        None,
        "--backend",
        "-b",
        help="Filter by backend (ollama, mlx, huggingface, lmstudio)",
    ),
    size: Optional[str] = typer.Option(
        None, "--size", "-s", help="Filter by size (tiny, small, medium, large)"
    ),
    task: Optional[str] = typer.Option(
        None, "--task", "-t", help="Filter by task (chat, code, reasoning, embedding)"
    ),
    installed_only: bool = typer.Option(
        True, "--installed-only", help="Show only installed models"
    ),
    all_models: bool = typer.Option(
        False, "--all", help="Show all available models (overrides --installed-only)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
):
    """📋 List SuperOptiX models (installed by default)."""

    # Create filter
    filter_obj = SuperOptiXModelFilter(
        backend=SuperOptiXBackendType(backend) if backend else None,
        size=SuperOptiXModelSize(size) if size else None,
        task=SuperOptiXModelTask(task) if task else None,
        installed_only=not all_models if not all_models else False,
    )

    # Get models
    manager = SuperOptiXModelManager()
    models = manager.list_models(filter_obj)

    if not models:
        if all_models:
            console.print("❌ No models found matching your criteria.")
        else:
            console.print("🤖 No installed models found.")
            console.print("🔍 Discover models: [bold]super model discover[/bold]")
            console.print(
                "📥 Install a model: [bold]super model install <model_name>[/bold]"
            )
        return

    # Create table
    table = Table(
        title=f"🚀 SuperOptiX Model Intelligence - {len(models)} models",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    table.add_column("Model", style="bold white", no_wrap=True)
    table.add_column("Backend", style="cyan", justify="center")
    table.add_column("Status", style="green", justify="center")
    table.add_column("Size", style="yellow", justify="center")
    table.add_column("Task", style="magenta", justify="center")

    if verbose:
        table.add_column("Parameters", style="dim", justify="center")
        table.add_column("Disk Size", style="dim", justify="center")
        table.add_column("Last Used", style="dim", justify="center")

    # Add rows
    for model in models:
        status_emoji = {
            SuperOptiXModelStatus.INSTALLED: "✅",
            SuperOptiXModelStatus.DOWNLOADING: "⬇️",
            SuperOptiXModelStatus.FAILED: "❌",
            SuperOptiXModelStatus.UNKNOWN: "❓",
        }.get(model.status, "❓")

        row = [
            model.name,
            f"🦙 {model.backend.value}"
            if model.backend == SuperOptiXBackendType.OLLAMA
            else f"🍎 {model.backend.value}"
            if model.backend == SuperOptiXBackendType.MLX
            else f"🤗 {model.backend.value}"
            if model.backend == SuperOptiXBackendType.HUGGINGFACE
            else f"🎮 {model.backend.value}"
            if model.backend == SuperOptiXBackendType.LMSTUDIO
            else model.backend.value,
            f"{status_emoji} {model.status.value}",
            model.size.value if model.size else "Unknown",
            model.task.value if model.task else "General",
        ]

        if verbose:
            row.extend(
                [
                    model.parameters or "Unknown",
                    f"{model.size_gb:.1f}GB" if model.size_gb else "Unknown",
                    model.last_used.strftime("%Y-%m-%d")
                    if model.last_used
                    else "Never",
                ]
            )

        table.add_row(*row)

    console.print(table)
    # Always show discovery and install guidance
    console.print()
    console.print("🔍 Discover more models: [bold]super model discover[/bold]")
    console.print("📥 Install a model: [bold]super model install <model_name>[/bold]")


@app.command("discover")
def discover_models():
    """🔍 SuperOptiX Model Discovery Guide."""
    _show_discovery_guide()


@app.command("guide")
def model_guide():
    """📚 SuperOptiX Model Installation Guide."""
    _show_detailed_guide()


def _parse_backend(
    backend: Optional[str], model_name: str
) -> Optional[SuperOptiXBackendType]:
    """Parse backend from model name or specified backend."""
    if backend:
        try:
            return SuperOptiXBackendType(backend.lower())
        except ValueError:
            console.print(f"❌ Invalid backend: {backend}")
            console.print("Valid backends: ollama, mlx, huggingface, lmstudio")
            return None

    # Auto-detect backend from model name
    if model_name.startswith("mlx-community/") or model_name.startswith("mlx/"):
        return SuperOptiXBackendType.MLX
    elif "/" in model_name:
        # Assume HuggingFace for most models with "/"
        return SuperOptiXBackendType.HUGGINGFACE
    else:
        # Default to Ollama for simple model names (like "llama3.2:1b")
        return SuperOptiXBackendType.OLLAMA


def _get_backend_instance(backend_type: SuperOptiXBackendType):
    """Get backend instance for the specified type."""
    manager = SuperOptiXModelManager()
    return manager.backends.get(backend_type)


@app.command("install")
def install_model(
    model_name: str = typer.Argument(..., help="Model name to install"),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Specific backend to use"
    ),
):
    """🚀 Install a SuperOptiX model using native download features."""
    import time
    from pathlib import Path

    start_time = time.time()

    # Parse model name and backend
    parsed_model_name = model_name.strip()
    backend_type = _parse_backend(backend, parsed_model_name)

    if not backend_type:
        console.print(
            "❌ Could not determine backend type. Please specify with --backend"
        )
        raise typer.Exit(1)

    # Get backend instance
    backend_instance = _get_backend_instance(backend_type)
    if not backend_instance:
        console.print(f"❌ Backend {backend_type.value} is not available")
        raise typer.Exit(1)

    # Check if model is already installed
    if backend_instance.is_available_sync():
        installed_models = backend_instance.list_installed_models_sync()
        for model in installed_models:
            if model.name == parsed_model_name or model.full_name == parsed_model_name:
                console.print(
                    f"✅ Model [bold]{parsed_model_name}[/bold] is already installed!"
                )
                console.print(f"📁 Location: {model.local_path}")
                console.print(
                    f"📊 Size: {model.size_gb:.1f} GB"
                    if model.size_gb
                    else "📊 Size: Unknown"
                )
                return

    # Show installation start message with backend information
    backend_emoji = {
        SuperOptiXBackendType.HUGGINGFACE: "🤗",
        SuperOptiXBackendType.MLX: "🍎",
        SuperOptiXBackendType.OLLAMA: "🦙",
        SuperOptiXBackendType.LMSTUDIO: "🎮",
    }.get(backend_type, "")

    console.print(
        f"\n{backend_emoji} SuperOptiX is downloading the model [bold]{parsed_model_name}[/bold] using backend [bold]{backend_type.value}[/bold]"
    )
    console.print("=" * 80)

    # FORCE NATIVE OUTPUT - NO SUPEROPTIX WRAPPER MESSAGES
    # Disable all SuperOptiX progress indicators and use native library output only

    if backend_type == SuperOptiXBackendType.HUGGINGFACE:
        # Force native HuggingFace output
        try:
            from huggingface_hub import snapshot_download
            from huggingface_hub.utils import tqdm

            # Create model directory in cache
            cache_dir = Path("~/.cache/huggingface").expanduser()
            model_dir = cache_dir / parsed_model_name.replace("/", "_")
            model_dir.mkdir(parents=True, exist_ok=True)

            # DIRECT NATIVE CALL - NO WRAPPER MESSAGES
            snapshot_download(
                repo_id=parsed_model_name,
                local_dir=str(model_dir),
                max_workers=1,
                tqdm_class=tqdm,
            )

            # Only show completion message
            end_time = time.time()
            duration = end_time - start_time

            # Calculate disk size
            total_size = 0
            for f in model_dir.rglob("*"):
                if f.is_file() and not f.is_symlink():
                    total_size += f.stat().st_size
            size_gb = total_size / (1024**3)

            console.print(f"\n✅ Model {parsed_model_name} installed successfully!")
            console.print(f"📁 Location: {model_dir}")
            console.print(f"📊 Size: {size_gb:.1f} GB")
            console.print(f"⏱️ Time: {duration:.1f} seconds")

        except Exception as e:
            console.print(f"❌ Failed to install {parsed_model_name}: {e}")
            raise typer.Exit(1)

    elif backend_type == SuperOptiXBackendType.MLX:
        # Force native MLX output
        try:
            from mlx_lm.utils import get_model_path
            import shutil

            # Create model directory
            cache_dir = Path("~/.cache/mlx-models").expanduser()
            model_path = cache_dir / parsed_model_name.replace("/", "_")
            model_path.mkdir(parents=True, exist_ok=True)

            # DIRECT NATIVE CALL - NO WRAPPER MESSAGES
            local_path, hf_path = get_model_path(parsed_model_name)

            # Copy the downloaded model to our cache directory
            if local_path.exists() and local_path != model_path:
                if model_path.exists():
                    shutil.rmtree(model_path)
                shutil.copytree(local_path, model_path)

            # Only show completion message
            end_time = time.time()
            duration = end_time - start_time

            # Calculate disk size
            total_size = 0
            for f in model_path.rglob("*"):
                if f.is_file() and not f.is_symlink():
                    total_size += f.stat().st_size
            size_gb = total_size / (1024**3)

            console.print(f"\n✅ Model {parsed_model_name} installed successfully!")
            console.print(f"📁 Location: {model_path}")
            console.print(f"📊 Size: {size_gb:.1f} GB")
            console.print(f"⏱️ Time: {duration:.1f} seconds")

        except Exception as e:
            console.print(f"❌ Failed to install {parsed_model_name}: {e}")
            raise typer.Exit(1)

    elif backend_type == SuperOptiXBackendType.OLLAMA:
        # Force native Ollama output
        try:
            import subprocess

            # DIRECT NATIVE CALL - NO WRAPPER MESSAGES
            result = subprocess.run(
                ["ollama", "pull", parsed_model_name],
                capture_output=False,  # Let native output show
                text=True,
                check=True,
            )

            # Only show completion message
            end_time = time.time()
            duration = end_time - start_time

            console.print(f"\n✅ Model {parsed_model_name} installed successfully!")
            console.print(f"⏱️ Time: {duration:.1f} seconds")

        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to install {parsed_model_name}: {e}")
            raise typer.Exit(1)
        except FileNotFoundError:
            console.print(
                "❌ Ollama not found. Install with: curl -fsSL https://ollama.ai/install.sh | sh"
            )
            raise typer.Exit(1)

    else:
        # For other backends, use minimal wrapper
        try:
            success = backend_instance.install_model_sync(parsed_model_name)

            if success:
                end_time = time.time()
                duration = end_time - start_time

                console.print(f"\n✅ Model {parsed_model_name} installed successfully!")
                console.print(f"⏱️ Time: {duration:.1f} seconds")
            else:
                console.print(f"❌ Failed to install {parsed_model_name}")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"❌ Failed to install {parsed_model_name}: {e}")
            raise typer.Exit(1)


@app.command("info")
def model_info(
    model_name: str = typer.Argument(..., help="Model name to get info about"),
):
    """ℹ️ Get detailed information about a SuperOptiX model."""

    manager = SuperOptiXModelManager()
    models = manager.list_models()

    # Find the model
    model = None
    for m in models:
        if m.name == model_name or m.full_name == model_name:
            model = m
            break

    if not model:
        console.print(f"❌ Model [bold]{model_name}[/bold] not found.")
        console.print("Use [bold]super model list[/bold] to see available models.")
        return

    # Create info panel
    info_text = f"""
[bold]Name:[/bold] {model.name}
[bold]Backend:[/bold] {model.backend.value}
[bold]Status:[/bold] {model.status.value}
[bold]Size:[/bold] {model.size.value if model.size else "Unknown"}
[bold]Task:[/bold] {model.task.value if model.task else "General"}
[bold]Parameters:[/bold] {model.parameters or "Unknown"}
[bold]Disk Size:[/bold] {f"{model.size_gb:.1f}GB" if model.size_gb else "Unknown"}
[bold]Usage Count:[/bold] {model.usage_count}
[bold]Last Used:[/bold] {model.last_used.strftime("%Y-%m-%d %H:%M") if model.last_used else "Never"}
"""

    if model.description:
        info_text += f"\n[bold]Description:[/bold] {model.description}"

    if model.tags:
        info_text += f"\n[bold]Tags:[/bold] {', '.join(model.tags)}"

    panel = Panel(
        info_text.strip(),
        title=f"🚀 SuperOptiX Model Info - {model.display_name}",
        border_style="blue",
    )

    console.print(panel)


@app.command("backends")
def list_backends():
    """🔧 Show SuperOptiX backend status."""

    manager = SuperOptiXModelManager()
    backends = manager.get_backend_info()

    table = Table(
        title="🔧 SuperOptiX Backend Status",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    table.add_column("Backend", style="bold white")
    table.add_column("Status", style="green", justify="center")
    table.add_column("Version", style="yellow", justify="center")
    table.add_column("Models", style="magenta", justify="center")
    table.add_column("Configuration", style="dim")

    for backend in backends:
        status_emoji = "✅" if backend.available else "❌"
        status_text = f"{status_emoji} {backend.status}"

        config_text = ""
        if backend.host and backend.port:
            config_text = f"{backend.host}:{backend.port}"
        elif backend.host:
            config_text = backend.host

        table.add_row(
            f"{'🦙' if backend.type == SuperOptiXBackendType.OLLAMA else '🍎' if backend.type == SuperOptiXBackendType.MLX else '🤗' if backend.type == SuperOptiXBackendType.HUGGINGFACE else '🎮' if backend.type == SuperOptiXBackendType.LMSTUDIO else ''} {backend.type.value}",
            status_text,
            backend.version or "Unknown",
            str(backend.models_count),
            config_text,
        )

    console.print(table)


@app.command("dspy")
def create_dspy_client(
    model_name: str = typer.Argument(..., help="Model name for DSPy client"),
    temperature: float = typer.Option(
        0.7, "--temperature", "-t", help="Temperature for generation"
    ),
    max_tokens: int = typer.Option(2048, "--max-tokens", "-m", help="Maximum tokens"),
):
    """🧠 Create a DSPy client for SuperOptiX model."""

    manager = SuperOptiXModelManager()

    try:
        client = manager.create_dspy_client(
            model_name, temperature=temperature, max_tokens=max_tokens
        )
        console.print(f"✅ Created DSPy client for [bold cyan]{model_name}[/bold cyan]")
        console.print(f"Client type: [bold]{type(client).__name__}[/bold]")
        console.print()
        console.print("Example usage:")
        console.print("  [dim]import dspy[/dim]")
        console.print("  [dim]dspy.configure(lm=client)[/dim]")

    except Exception as e:
        console.print(f"❌ Failed to create DSPy client: {e}")


@app.command("server")
def start_server(
    backend: str = typer.Argument(
        ..., help="Backend type (mlx, huggingface, lmstudio)"
    ),
    model_name: str = typer.Argument(..., help="Model name to start server for"),
    port: int = typer.Option(None, "--port", "-p", help="Port to run server on"),
):
    """🚀 Start a local server for SuperOptiX models.

    Examples:
      super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit
      super model server huggingface microsoft/DialoGPT-small --port 8001
      super model server lmstudio llama-3.2-1b-instruct

    Backends:
      mlx          Apple Silicon optimized (default: port 8000)
      huggingface  Transformers models (default: port 8001)
      lmstudio     Desktop app models (default: port 1234)

    Note: Ollama servers use 'ollama serve' command separately.
    """

    # Custom help handler
    if any(flag in sys.argv for flag in ["--help", "-h"]):
        try:
            console = Console()
            help_text = Text()
            help_text.append(
                "\n🚀 Start local model servers for MLX, HuggingFace, or LM Studio.\n\n",
                style="bold cyan",
            )
            help_text.append("Examples:\n", style="bold yellow")
            help_text.append(
                "  super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit\n",
                style="white",
            )
            help_text.append(
                "  super model server huggingface microsoft/DialoGPT-small --port 8001\n",
                style="white",
            )
            help_text.append(
                "  super model server lmstudio llama-3.2-1b-instruct\n\n", style="white"
            )
            help_text.append("Backends:\n", style="bold yellow")
            help_text.append(
                "  mlx         Apple Silicon (default: 8000)\n", style="white"
            )
            help_text.append(
                "  huggingface Transformers (default: 8001)\n", style="white"
            )
            help_text.append(
                "  lmstudio    Desktop app (default: 1234)\n\n", style="white"
            )
            help_text.append(
                "Note: Ollama uses 'ollama serve' separately.\n", style="bold magenta"
            )
            panel = Panel(help_text, title="super model server", border_style="blue")
            console.print(panel)
        except Exception:
            print(
                "\n🚀 Start local model servers for MLX, HuggingFace, or LM Studio.\n"
            )
            print("Examples:")
            print("  super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit")
            print(
                "  super model server huggingface microsoft/DialoGPT-small --port 8001"
            )
            print("  super model server lmstudio llama-3.2-1b-instruct\n")
            print("Backends:")
            print("  mlx         Apple Silicon (default: 8000)")
            print("  huggingface Transformers (default: 8001)")
            print("  lmstudio    Desktop app (default: 1234)\n")
            print("Note: Ollama uses 'ollama serve' separately.\n")
        sys.exit(0)

    if backend.lower() == "mlx":
        if port is None:
            port = 8000
        start_mlx_server(model_name, port)
    elif backend.lower() == "huggingface":
        if port is None:
            port = 8001
        start_huggingface_server(model_name, port)
    elif backend.lower() == "lmstudio":
        if port is None:
            port = 1234
        start_lmstudio_server(model_name, port)
    else:
        console.print(f"❌ Unsupported backend: [bold red]{backend}[/bold red]")
        console.print("Supported backends: mlx, huggingface, lmstudio")


@app.command("refresh")
def refresh_models():
    """🔄 Refresh SuperOptiX model cache and re-discover installed models."""

    console.print("🔄 Refreshing SuperOptiX model cache...")

    # Get manager and refresh cache
    manager = SuperOptiXModelManager()

    # Clear all cached model lists
    for backend_type, backend_instance in manager.backends.items():
        try:
            if hasattr(backend_instance, "refresh_cache"):
                backend_instance.refresh_cache()
            console.print(f"✅ Refreshed {backend_type.value} backend cache")
        except Exception as e:
            console.print(f"⚠️ Error refreshing {backend_type.value} backend: {e}")

    # Refresh the main model cache
    manager.refresh_model_cache()

    # Re-discover models
    console.print("🔍 Re-discovering installed models...")
    all_models = manager.list_models()

    console.print("✅ Model cache refreshed successfully!")
    console.print(f"📋 Found {len(all_models)} installed models")
    console.print("📋 Run [bold]super model list[/bold] to see updated models.")


@app.command("remove")
def remove_model(
    model_name: str = typer.Argument(..., help="Model name to remove"),
    backend: Optional[str] = typer.Option(
        None,
        "--backend",
        "-b",
        help="Specific backend to use (auto-detected if not specified)",
    ),
    all_backends: bool = typer.Option(
        False, "--all-backends", help="Remove model from all backends where it exists"
    ),
):
    """🗑️ Remove SuperOptiX models completely from cache and update list."""
    from superoptix.cli.utils import suppress_warnings
    import asyncio

    with suppress_warnings():
        # Parse backend type
        backend_type = None
        if backend:
            try:
                backend_type = SuperOptiXBackendType(backend.lower())
            except ValueError:
                console.print(f"❌ Invalid backend: {backend}")
                console.print("Valid backends: ollama, mlx, huggingface, lmstudio")
                raise typer.Exit(1)

        # Initialize manager
        manager = SuperOptiXModelManager()

        # Fast auto-detect backend if not specified
        if not backend_type:
            console.print("🔍 Detecting model location...")
            backend_type = manager.detect_model_backend(model_name)

            if backend_type:
                console.print(f"✅ Found {model_name} in {backend_type.value} backend")
            else:
                console.print(
                    f"❌ Model [bold]{model_name}[/bold] not found in any backend"
                )
                console.print("💡 [bold]Possible solutions:[/bold]")
                console.print("  • Check for typos in the model name")
                console.print(
                    "  • Run [bold]super model list[/bold] to see available models"
                )
                console.print(
                    "  • Try [bold]super model discover[/bold] to find similar models"
                )
                console.print("  • The model may not be installed yet")
                console.print(
                    "  • Use [bold]super model install {model_name}[/bold] to install it first"
                )
                raise typer.Exit(1)

        # Handle all backends removal
        if all_backends:
            console.print("🗑️ Checking all backends for model removal...")
            removed_from = []
            for bt, backend_instance in manager.backends.items():
                try:
                    # Check if backend is available
                    if hasattr(backend_instance, "is_available_sync"):
                        is_available = backend_instance.is_available_sync()
                    elif hasattr(backend_instance, "is_available"):
                        try:
                            is_available = asyncio.run(backend_instance.is_available())
                        except Exception:
                            is_available = False
                    else:
                        is_available = (
                            backend_instance.is_available()
                            if hasattr(backend_instance, "is_available")
                            else False
                        )

                    if is_available:
                        # Check if model exists in this backend
                        model_info = None
                        if hasattr(backend_instance, "get_model_info_sync"):
                            model_info = backend_instance.get_model_info_sync(
                                model_name
                            )
                        elif hasattr(backend_instance, "get_model_info"):
                            if hasattr(backend_instance.get_model_info, "__await__"):
                                try:
                                    model_info = asyncio.run(
                                        backend_instance.get_model_info(model_name)
                                    )
                                except Exception:
                                    model_info = None
                            else:
                                model_info = backend_instance.get_model_info(model_name)

                        if model_info:
                            console.print(f"🗑️ Removing {model_name} from {bt.value}...")
                            success = _remove_model_completely(manager, model_name, bt)
                            if success:
                                removed_from.append(bt.value)
                                console.print(
                                    f"✅ Removed {model_name} from {bt.value}"
                                )
                            else:
                                console.print(
                                    f"❌ Failed to remove {model_name} from {bt.value}"
                                )
                except Exception as e:
                    console.print(f"⚠️ Error checking {bt.value}: {e}")

            if removed_from:
                console.print(
                    f"🎉 Successfully removed {model_name} from: {', '.join(removed_from)}"
                )
                # Refresh cache after removal
                console.print("🔄 Refreshing model cache...")
                manager.refresh_model_cache()
                console.print("✅ Model cache refreshed")
            else:
                console.print(
                    f"❌ Model [bold]{model_name}[/bold] not found in any backend"
                )
                console.print("💡 [bold]Possible solutions:[/bold]")
                console.print("  • Check for typos in the model name")
                console.print(
                    "  • Run [bold]super model list[/bold] to see available models"
                )
                console.print(
                    "  • Try [bold]super model discover[/bold] to find similar models"
                )
                console.print("  • The model may not be installed yet")
                console.print(
                    "  • Use [bold]super model install {model_name}[/bold] to install it first"
                )
            return

        # Single backend removal
        console.print(f"🗑️ Removing {model_name} from {backend_type.value}...")
        success = _remove_model_completely(manager, model_name, backend_type)

        if success:
            console.print(
                f"🎉 Successfully removed {model_name} from {backend_type.value}"
            )
            # Refresh cache after removal
            console.print("🔄 Refreshing model cache...")
            manager.refresh_model_cache()
            console.print("✅ Model cache refreshed")
        else:
            console.print(f"❌ Failed to remove {model_name} from {backend_type.value}")
            console.print("💡 [bold]Troubleshooting:[/bold]")
            console.print("  • The model may not exist in this backend")
            console.print("  • The model may be in use by another process")
            console.print("  • Check file permissions in the model cache directory")
            console.print(
                "  • Run [bold]super model list[/bold] to see available models"
            )


def _remove_model_completely(
    manager, model_name: str, backend_type: SuperOptiXBackendType
) -> bool:
    """Completely remove a model from cache and registry."""
    try:
        from pathlib import Path
        import shutil

        backend_instance = manager.backends.get(backend_type)
        if not backend_instance:
            return False

        # Get model info to find exact location
        model_info = None
        if hasattr(backend_instance, "get_model_info_sync"):
            model_info = backend_instance.get_model_info_sync(model_name)
        elif hasattr(backend_instance, "get_model_info"):
            if hasattr(backend_instance.get_model_info, "__await__"):
                try:
                    import asyncio

                    model_info = asyncio.run(
                        backend_instance.get_model_info(model_name)
                    )
                except Exception:
                    model_info = None
            else:
                model_info = backend_instance.get_model_info(model_name)

        if not model_info:
            return False

        # Remove from cache directories
        removed = False

        # 1. Remove from SuperOptiX cache directory
        if hasattr(backend_instance, "cache_dir"):
            cache_dir = backend_instance.cache_dir
            model_dir = cache_dir / model_name.replace("/", "_")
            if model_dir.exists():
                shutil.rmtree(model_dir)
                removed = True
                console.print(f"🗑️ Removed from cache: {model_dir}")

        # 2. Remove from HuggingFace cache (for HuggingFace backend)
        if backend_type == SuperOptiXBackendType.HUGGINGFACE:
            hf_cache_dirs = [
                Path("~/.cache/huggingface").expanduser()
                / f"models--{model_name.replace('/', '--')}",
                Path("~/.cache/huggingface").expanduser()
                / model_name.replace("/", "_"),
                Path("~/.cache/huggingface/hub").expanduser()
                / f"models--{model_name.replace('/', '--')}",
            ]

            for hf_dir in hf_cache_dirs:
                if hf_dir.exists():
                    shutil.rmtree(hf_dir)
                    removed = True
                    console.print(f"🗑️ Removed from HuggingFace cache: {hf_dir}")

        # 3. Remove from MLX cache (for MLX backend)
        elif backend_type == SuperOptiXBackendType.MLX:
            mlx_cache_dirs = [
                Path("~/.cache/mlx-models").expanduser() / model_name.replace("/", "_"),
                Path("~/.cache/mlx-models").expanduser() / model_name,
            ]

            for mlx_dir in mlx_cache_dirs:
                if mlx_dir.exists():
                    shutil.rmtree(mlx_dir)
                    removed = True
                    console.print(f"🗑️ Removed from MLX cache: {mlx_dir}")

        # 4. Remove from Ollama (for Ollama backend)
        elif backend_type == SuperOptiXBackendType.OLLAMA:
            try:
                import subprocess

                result = subprocess.run(
                    ["ollama", "rm", model_name],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                removed = True
                console.print(f"🗑️ Removed from Ollama: {model_name}")
            except subprocess.CalledProcessError as e:
                console.print(f"⚠️ Ollama removal failed: {e}")
            except FileNotFoundError:
                console.print("⚠️ Ollama not found")

        # 5. Remove from LM Studio cache
        elif backend_type == SuperOptiXBackendType.LMSTUDIO:
            lmstudio_cache_dirs = [
                Path("~/.cache/lm-studio/models").expanduser() / model_name,
                Path("~/Library/Application Support/LM Studio/models").expanduser()
                / model_name,
            ]

            for lmstudio_dir in lmstudio_cache_dirs:
                if lmstudio_dir.exists():
                    shutil.rmtree(lmstudio_dir)
                    removed = True
                    console.print(f"🗑️ Removed from LM Studio cache: {lmstudio_dir}")

        # Remove from registry
        try:
            manager.registry.remove_model(f"{backend_type.value}/{model_name}")
        except Exception as e:
            console.print(f"⚠️ Registry removal warning: {e}")

        return removed

    except Exception as e:
        console.print(f"❌ Error removing model: {e}")
        return False


@app.command("run")
def run_model(
    model_name: str = typer.Argument(..., help="Model name to run"),
    prompt: str = typer.Argument(..., help="Prompt to send to the model"),
    backend: Optional[str] = typer.Option(
        None,
        "--backend",
        "-b",
        help="Specific backend to use (auto-detected if not specified)",
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Run in interactive mode"
    ),
    max_tokens: int = typer.Option(
        2048, "--max-tokens", "-m", help="Maximum tokens to generate"
    ),
    temperature: float = typer.Option(
        0.7, "--temperature", "-t", help="Temperature for generation (0.0-2.0)"
    ),
):
    """🚀 Run a SuperOptiX model with a prompt."""

    manager = SuperOptiXModelManager()

    # Auto-detect backend if not specified
    if not backend:
        console.print("🔍 Auto-detecting backend...")
        backend_type = manager.detect_model_backend(model_name)
        if backend_type:
            backend = backend_type.value
            console.print(f"✅ Found {model_name} in {backend} backend")
        else:
            console.print(
                f"📥 Model [bold]{model_name}[/bold] not found in any backend"
            )
            console.print("🔄 Attempting to install {model_name} in mlx...")

            # Try to install in MLX backend
            success = manager.install_model(
                model_name, backend_type=SuperOptiXBackendType.MLX
            )
            if success:
                console.print(f"✅ Successfully installed {model_name} in mlx")
                backend = "mlx"
            else:
                console.print("❌ Failed to install model")
                return

    # Validate backend
    try:
        backend_type = SuperOptiXBackendType(backend)
    except ValueError:
        console.print(f"❌ Invalid backend: {backend}")
        console.print("Valid backends: ollama, mlx, huggingface, lmstudio")
        return

    # Check if model exists in specified backend
    from superoptix.models.utils import SuperOptiXModelFilter

    filter_obj = SuperOptiXModelFilter(backend=backend_type)
    backend_models = manager.list_models(filter_obj=filter_obj)
    model_exists = any(
        m.name == model_name or m.full_name == model_name for m in backend_models
    )

    if not model_exists:
        console.print(f"📥 Model [bold]{model_name}[/bold] not found in {backend}")
        console.print(f"🔄 Attempting to install {model_name} in {backend}...")

        success = manager.install_model(model_name, backend_type=backend_type)
        if not success:
            console.print("❌ Failed to install model")
            return
        console.print(f"✅ Successfully installed {model_name} in {backend}")

    # Run the model
    console.print(f"🚀 Running {model_name} ({backend})...")

    try:
        if interactive:
            console.print("💬 Interactive mode - type 'quit' to exit")
            console.print("=" * 50)

            while True:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    break

                if not user_input.strip():
                    continue

                # Run the model
                result = manager.test_model(
                    model_name, user_input, backend_type=backend_type
                )

                if result.get("success"):
                    response = result.get("response", "")
                    console.print(f"\n[bold green]Assistant:[/bold green] {response}")

                    # Show performance info in interactive mode
                    response_time = result.get("response_time", 0)
                    tokens = result.get("tokens", 0)

                    if response_time:
                        if tokens > 0:
                            tps = tokens / response_time
                            console.print(
                                f"[dim]⏱️ {response_time:.2f}s | 🚀 {tps:.1f} t/s | 📊 {tokens} tokens[/dim]"
                            )
                        else:
                            estimated_tokens = len(response.split()) * 1.3
                            tps = estimated_tokens / response_time
                            console.print(
                                f"[dim]⏱️ {response_time:.2f}s | 🚀 {tps:.1f} t/s | 📊 ~{estimated_tokens:.0f} tokens[/dim]"
                            )
                else:
                    error = result.get("error", "Unknown error")
                    console.print(f"\n[bold red]Error:[/bold red] {error}")
        else:
            # Single prompt mode
            result = manager.test_model(model_name, prompt, backend_type=backend_type)

            if result.get("success"):
                response = result.get("response", "")
                console.print("📝 Response:")
                console.print("-" * 50)
                console.print(response)
                console.print("-" * 50)

                # Show timing and performance info
                response_time = result.get("response_time", 0)
                tokens = result.get("tokens", 0)
                prompt_tokens = result.get("prompt_tokens", 0)

                if response_time:
                    console.print(f"⏱️ Response time: {response_time:.2f}s")

                    # Calculate tokens per second if we have token information
                    if tokens > 0:
                        tps = tokens / response_time
                        console.print(f"🚀 Tokens per second: {tps:.1f} t/s")
                        console.print(f"📊 Generated tokens: {tokens}")
                    elif prompt_tokens > 0:
                        # If we only have prompt tokens, estimate generated tokens
                        estimated_tokens = len(response.split()) * 1.3  # Rough estimate
                        tps = estimated_tokens / response_time
                        console.print(f"🚀 Estimated tokens per second: {tps:.1f} t/s")
                        console.print(
                            f"📊 Estimated generated tokens: {estimated_tokens:.0f}"
                        )
                    else:
                        # Fallback: estimate tokens from response length
                        estimated_tokens = len(response.split()) * 1.3
                        tps = estimated_tokens / response_time
                        console.print(f"🚀 Estimated tokens per second: {tps:.1f} t/s")
                        console.print(
                            f"📊 Estimated generated tokens: {estimated_tokens:.0f}"
                        )

                    # Show backend info
                    console.print(f"🔧 Backend: {backend}")
            else:
                error = result.get("error", "Unknown error")
                console.print(f"❌ Error: {error}")

    except Exception as e:
        console.print(f"❌ An error occurred: {e}")


@app.command("convert")
def convert_model(
    hf_model: str = typer.Argument(
        ..., help="HuggingFace model to convert (e.g., 'microsoft/phi-2')"
    ),
    output_path: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for converted model (default: model name)",
    ),
    quantize: bool = typer.Option(
        False, "--quantize", "-q", help="Generate a quantized model"
    ),
    q_bits: int = typer.Option(
        4, "--bits", help="Bits per weight for quantization (default: 4)"
    ),
    q_group_size: int = typer.Option(
        64, "--group-size", help="Group size for quantization (default: 64)"
    ),
    quant_recipe: Optional[str] = typer.Option(
        None,
        "--quant-recipe",
        help="Mixed quantization recipe (mixed_2_6, mixed_3_4, mixed_3_6, mixed_4_6)",
    ),
    dtype: Optional[str] = typer.Option(
        None, "--dtype", help="Data type (float16, bfloat16, float32)"
    ),
    upload_repo: Optional[str] = typer.Option(
        None, "--upload", help="HuggingFace repo to upload converted model to"
    ),
    dequantize: bool = typer.Option(
        False, "--dequantize", help="Dequantize a quantized model"
    ),
    trust_remote_code: bool = typer.Option(
        False, "--trust-remote-code", help="Trust remote code from HuggingFace"
    ),
):
    """🔄 Convert HuggingFace model to MLX format (MLX backend only)."""

    # Check if MLX is available
    manager = SuperOptiXModelManager()
    mlx_backend = manager.backends.get(SuperOptiXBackendType.MLX)

    if not mlx_backend or not mlx_backend.is_available():
        console.print("❌ MLX backend is not available")
        console.print("💡 MLX requires Apple Silicon (M1/M2/M3) with macOS")
        console.print("📦 Install with: pip install mlx mlx-lm")
        return

    # Set default output path if not specified
    if not output_path:
        output_path = hf_model.replace("/", "_")

    console.print(f"🔄 Converting {hf_model} to MLX format...")
    console.print(f"📁 Output path: {output_path}")

    if quantize:
        console.print(
            f"⚡ Quantizing with {q_bits}-bit precision (group size: {q_group_size})"
        )
        if quant_recipe:
            console.print(f"🎛️ Using mixed quantization recipe: {quant_recipe}")

    if dequantize:
        console.print("🔄 Dequantizing model...")

    if dtype:
        console.print(f"📊 Using dtype: {dtype}")

    if upload_repo:
        console.print(f"📤 Will upload to: {upload_repo}")

    try:
        # Import MLX-LM convert function
        import sys
        from pathlib import Path

        # Add mlx-lm-main to path
        mlx_lm_path = Path(__file__).parent.parent.parent.parent / "mlx-lm-main"
        if mlx_lm_path.exists():
            sys.path.insert(0, str(mlx_lm_path))

        from mlx_lm.convert import convert

        # Call the convert function
        convert(
            hf_path=hf_model,
            mlx_path=output_path,
            quantize=quantize,
            q_group_size=q_group_size,
            q_bits=q_bits,
            dtype=dtype,
            upload_repo=upload_repo,
            dequantize=dequantize,
            quant_predicate=quant_recipe,
            trust_remote_code=trust_remote_code,
        )

        console.print("✅ Model conversion completed successfully!")
        console.print(f"📁 Converted model saved to: {output_path}")

        if upload_repo:
            console.print(f"📤 Model uploaded to: {upload_repo}")

        # Show next steps
        console.print("\n🎯 Next steps:")
        console.print(f"  • Install: super model install {output_path} --backend mlx")

    except ImportError as e:
        console.print(f"❌ Failed to import MLX-LM: {e}")
        console.print("💡 Make sure mlx-lm is installed: pip install mlx-lm")
    except Exception as e:
        console.print(f"❌ Conversion failed: {e}")
        console.print("💡 Check that the HuggingFace model exists and is accessible")


@app.command("quantize")
def quantize_model(
    model_name: str = typer.Argument(..., help="MLX model to quantize"),
    output_path: str = typer.Option(
        None, "--output", "-o", help="Output path for quantized model"
    ),
    q_bits: int = typer.Option(
        4, "--bits", help="Bits per weight for quantization (default: 4)"
    ),
    q_group_size: int = typer.Option(
        64, "--group-size", help="Group size for quantization (default: 64)"
    ),
    quant_recipe: Optional[str] = typer.Option(
        None,
        "--recipe",
        help="Mixed quantization recipe (mixed_2_6, mixed_3_4, mixed_3_6, mixed_4_6)",
    ),
    dequantize: bool = typer.Option(
        False, "--dequantize", help="Dequantize instead of quantize"
    ),
):
    """⚡ Quantize or dequantize an MLX model (MLX backend only)."""

    # Check if MLX is available
    manager = SuperOptiXModelManager()
    mlx_backend = manager.backends.get(SuperOptiXBackendType.MLX)

    if not mlx_backend or not mlx_backend.is_available():
        console.print("❌ MLX backend is not available")
        console.print("💡 MLX requires Apple Silicon (M1/M2/M3) with macOS")
        return

    # Set default output path if not specified
    if not output_path:
        if dequantize:
            output_path = f"{model_name}_dequantized"
        else:
            output_path = f"{model_name}_q{q_bits}"

    console.print(
        f"🔄 {'Dequantizing' if dequantize else 'Quantizing'} {model_name}..."
    )
    console.print(f"📁 Output path: {output_path}")

    if not dequantize:
        console.print(
            f"⚡ Quantizing with {q_bits}-bit precision (group size: {q_group_size})"
        )
        if quant_recipe:
            console.print(f"🎛️ Using mixed quantization recipe: {quant_recipe}")

    try:
        # Import MLX-LM convert function
        import sys
        from pathlib import Path

        # Add mlx-lm-main to path
        mlx_lm_path = Path(__file__).parent.parent.parent.parent / "mlx-lm-main"
        if mlx_lm_path.exists():
            sys.path.insert(0, str(mlx_lm_path))

        from mlx_lm.convert import convert

        # Call the convert function for quantization
        convert(
            hf_path=model_name,  # Use the model as input
            mlx_path=output_path,
            quantize=not dequantize,  # Quantize if not dequantizing
            dequantize=dequantize,
            q_group_size=q_group_size,
            q_bits=q_bits,
            quant_predicate=quant_recipe,
        )

        action = "dequantization" if dequantize else "quantization"
        console.print(f"✅ Model {action} completed successfully!")
        console.print(f"📁 Processed model saved to: {output_path}")

        # Show next steps
        console.print("\n🎯 Next steps:")
        console.print(f"  • Install: super model install {output_path} --backend mlx")

    except ImportError as e:
        console.print(f"❌ Failed to import MLX-LM: {e}")
        console.print("💡 Make sure mlx-lm is installed: pip install mlx-lm")
    except Exception as e:
        console.print(
            f"❌ {'Dequantization' if dequantize else 'Quantization'} failed: {e}"
        )


def start_mlx_server(model_name: str, port: int = 8000):
    """Start a local MLX server for the specified model."""
    console.print()
    console.print("🍎 [bold]MLX Local Server[/bold]")
    console.print(
        f"Starting MLX server for [bold cyan]{model_name}[/bold cyan] on port {port}..."
    )

    # Check if model is installed
    manager = SuperOptiXModelManager()
    installed_models = manager.list_models(
        SuperOptiXModelFilter(backend=SuperOptiXBackendType.MLX)
    )

    model_found = False
    for model in installed_models:
        if model.name == model_name or model.name.replace("_", "/") == model_name:
            model_found = True
            break

    if not model_found:
        console.print(
            f"❌ Model [bold red]{model_name}[/bold red] not found in installed MLX models"
        )
        console.print(
            "💡 Install the model first: [bold]super model install -b mlx <model_name>[/bold]"
        )
        return False

    console.print("🚀 Starting MLX server...")
    console.print(
        f"📡 Server will be available at: [bold green]http://localhost:{port}[/bold green]"
    )
    console.print("💡 Use this URL in your playbook's api_base configuration")
    console.print()
    console.print("🔧 Manual server startup command:")
    console.print(f"   python -m mlx_lm.server --model {model_name} --port {port}")
    console.print()
    console.print("📋 Example playbook configuration:")
    console.print(f"""   language_model:
     provider: mlx
     model: {model_name}
     api_base: http://localhost:{port}""")

    # Actually start the MLX server
    try:
        import subprocess
        import sys

        # Start the MLX server as a subprocess
        cmd = [
            sys.executable,
            "-m",
            "mlx_lm.server",
            "--model",
            model_name,
            "--port",
            str(port),
        ]

        console.print(f"🔄 Executing: {' '.join(cmd)}")
        console.print("⏳ Server is starting... (Press Ctrl+C to stop)")

        # Run the server process
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to start MLX server: {e}")
        console.print("💡 Make sure mlx-lm is installed: pip install mlx-lm")
        return False
    except KeyboardInterrupt:
        console.print("\n🛑 MLX server stopped by user")
        return True
    except Exception as e:
        console.print(f"❌ Unexpected error starting MLX server: {e}")
        return False

    return True


def start_huggingface_server(model_name: str, port: int = 8001):
    """Start a local HuggingFace server for the specified model."""
    console.print()
    console.print("🤗 [bold]HuggingFace Local Server[/bold]")
    console.print(
        f"Starting HuggingFace server for [bold cyan]{model_name}[/bold cyan] on port {port}..."
    )

    try:
        # Import and start the HuggingFace server
        from superoptix.models.backends.huggingface_server import (
            start_huggingface_server as start_hf_server,
        )

        console.print("🚀 Starting HuggingFace server...")
        console.print(
            f"📡 Server will be available at: [bold green]http://localhost:{port}[/bold green]"
        )
        console.print("💡 Use this URL in your playbook's api_base configuration")
        console.print()
        console.print("🔧 Manual server startup command:")
        console.print(
            f"   python -m superoptix.models.backends.huggingface_server {model_name} --port {port}"
        )
        console.print()
        console.print("📋 Example playbook configuration:")
        console.print(f"""   language_model:
     provider: huggingface
     model: {model_name}
     api_base: http://localhost:{port}""")

        # Start the server
        start_hf_server(model_name, port)

    except ImportError as e:
        console.print(f"❌ Failed to import HuggingFace server: {e}")
        console.print("💡 Make sure you have the required dependencies:")
        console.print("   pip install fastapi uvicorn torch transformers")
        console.print("   or")
        console.print("   uv pip install fastapi uvicorn torch transformers")
        return False
    except Exception as e:
        console.print(f"❌ Failed to start HuggingFace server: {e}")
        return False

    return True


def start_lmstudio_server(model_name: str, port: int = 1234):
    """Start a local LM Studio server for the specified model."""
    console.print()
    console.print("🎮 [bold]LM Studio Local Server[/bold]")
    console.print(
        f"Starting LM Studio server for [bold cyan]{model_name}[/bold cyan] on port {port}..."
    )

    # Import the LM Studio backend
    from superoptix.models.backends.lmstudio import SuperOptiXLMStudioBackend

    # Create backend instance
    backend = SuperOptiXLMStudioBackend()

    # Check if LM Studio CLI is available
    if not backend.is_available_sync():
        console.print("❌ LM Studio CLI is not available on your system.")
        console.print()
        console.print("📥 [bold]Install LM Studio:[/bold]")
        console.print("  🌐 Visit: [bold cyan]https://lmstudio.ai[/bold cyan]")
        console.print("  📥 Download and install for your platform")
        console.print("  🔧 The lms CLI will be available after installation")
        console.print()
        console.print("💡 After installing LM Studio, run this command again:")
        console.print(
            f"  [bold green]super model server lmstudio {model_name}[/bold green]"
        )
        return False

    # Get installed models
    try:
        installed_models = backend.list_installed_models_sync()
    except Exception as e:
        console.print(f"❌ Failed to list installed models: {e}")
        return False

    # Check for exact match first
    exact_match = None
    for model in installed_models:
        if model.name == model_name:
            exact_match = model
            break

    if exact_match:
        # Exact match found - load and start server
        console.print(
            f"✅ Found exact match: [bold green]{exact_match.name}[/bold green]"
        )
        console.print()
        console.print("🔄 Loading model and starting server...")

        try:
            # Load the model
            backend._run_lms_command(["load", exact_match.name])
            console.print(
                f"✅ Model [bold green]{exact_match.name}[/bold green] loaded successfully!"
            )

            # Start the server
            console.print("🚀 Starting LM Studio server...")
            console.print(
                f"📡 Server will be available at: [bold green]http://localhost:{port}[/bold green]"
            )
            console.print()
            console.print("💡 The server is now running in the background.")
            console.print("🎯 You can now use this model with SuperOptiX:")
            console.print(
                f"  [bold green]super model dspy lmstudio/{exact_match.name}[/bold green]"
            )
            console.print()
            console.print("📋 Example playbook configuration:")
            console.print(f"""   language_model:
     provider: lmstudio
     model: {exact_match.name}
     api_base: http://localhost:{port}""")
            console.print()
            console.print(
                "🛑 To stop the server, use Ctrl+C or close the LM Studio application"
            )

            # Start the server process
            import subprocess

            # Start lms server start command
            cmd = ["lms", "server", "start"]
            console.print(f"🔄 Executing: {' '.join(cmd)}")
            console.print("⏳ Server is starting... (Press Ctrl+C to stop)")

            # Run the server process
            subprocess.run(cmd, check=True)

        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to start LM Studio server: {e}")
            console.print("💡 Make sure LM Studio is properly installed and configured")
            return False
        except KeyboardInterrupt:
            console.print("\n🛑 LM Studio server stopped by user")
            return True
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}")
            return False

        return True

    else:
        # No exact match - show fuzzy matching
        console.print(f"❌ No exact match found for [bold red]{model_name}[/bold red]")
        console.print()
        console.print("🔍 [bold]Available LM Studio models:[/bold]")

        if not installed_models:
            console.print("❌ No models found in LM Studio.")
            console.print("💡 Install models first using the LM Studio application")
            console.print(
                "   or use: [bold green]super model install -b lmstudio <model_name>[/bold green]"
            )
            return False

        # Show available models in a table
        from rich.table import Table

        table = Table(
            title="🎮 Available LM Studio Models",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )

        table.add_column("Model Name", style="bold white", no_wrap=True)
        table.add_column("Size", style="yellow", justify="center")
        table.add_column("Task", style="magenta", justify="center")
        table.add_column("Parameters", style="dim", justify="center")

        for i, model in enumerate(installed_models, 1):
            table.add_row(
                f"{i}. {model.name}",
                model.size.value if model.size else "Unknown",
                model.task.value if model.task else "General",
                model.parameters or "Unknown",
            )

        console.print(table)
        console.print()
        console.print("💡 [bold]To use a specific model:[/bold]")
        console.print("  • Use the exact model name from the list above")
        console.print(
            "  • Example: [bold green]super model server lmstudio llama-3.2-1b-instruct[/bold green]"
        )
        console.print()
        console.print("🔍 [bold]Fuzzy matching examples:[/bold]")
        console.print("  • 'llama3.2' → Look for models containing 'llama3.2'")
        console.print("  • 'llama' → Look for models containing 'llama'")
        console.print("  • '3b' → Look for models containing '3b'")

        # Show fuzzy matches if any
        fuzzy_matches = []
        model_name_lower = model_name.lower()
        for model in installed_models:
            if model_name_lower in model.name.lower():
                fuzzy_matches.append(model)

        if fuzzy_matches:
            console.print()
            console.print("🎯 [bold]Fuzzy matches found:[/bold]")
            for i, model in enumerate(fuzzy_matches, 1):
                console.print(f"  {i}. [bold green]{model.name}[/bold green]")
            console.print()
            console.print("💡 Use one of the exact model names above:")
            for model in fuzzy_matches:
                console.print(
                    f"  [bold green]super model server lmstudio {model.name}[/bold green]"
                )
        else:
            console.print()
            console.print("❌ [bold]No fuzzy matches found for '{model_name}'[/bold]")
            console.print("💡 Try a different search term or install the model first:")
            console.print(
                "   [bold green]super model install -b lmstudio <model_name>[/bold green]"
            )

        return False


def _show_discovery_guide():
    """Show the SuperOptiX model discovery guide."""
    guide = get_superoptix_model_discovery_guide()

    console.print()
    console.print("🔍 [bold cyan]SuperOptiX Model Discovery Guide[/bold cyan]")
    console.print()

    panels = []
    for backend_name, info in guide.items():
        content = f"""
[bold]Description:[/bold] {info["description"]}

[bold]Example Models:[/bold]
{info["popular_models"]}

[bold]Benefits:[/bold]
{info["benefits"]}

[bold]Browse:[/bold] {info["browse_url"]}
[bold]Install:[/bold] {info["install_cmd"]}
"""

        panel = Panel(
            content.strip(),
            title=info["name"],
            border_style="blue",
        )
        panels.append(panel)

    console.print(Columns(panels))

    console.print()
    console.print("🚀 [bold cyan]Example Commands for Each Backend[/bold cyan]")
    console.print()

    # Ollama Examples
    console.print("🦙 [bold]Ollama (Local Models):[/bold]")
    console.print("  [yellow]Install Ollama:[/yellow]")
    console.print("    curl -fsSL https://ollama.com/install.sh | sh")
    console.print("  [yellow]Install a model:[/yellow]")
    console.print("    ollama pull llama3.2:3b")
    console.print("  [yellow]Use with SuperOptiX:[/yellow]")
    console.print("    super model dspy ollama/llama3.2:3b")
    console.print()

    # MLX Examples
    console.print("🍎 [bold]MLX (Apple Silicon):[/bold]")
    console.print("  [yellow]Install a model:[/yellow]")
    console.print(
        "    super model install -b mlx mlx-community/Llama-3.2-3B-Instruct-4bit"
    )
    console.print("  [yellow]Start a local server:[/yellow]")
    console.print(
        "    super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit --port 8000"
    )
    console.print("  [yellow]Use with SuperOptiX:[/yellow]")
    console.print("    super model dspy mlx-community/Llama-3.2-3B-Instruct-4bit")
    console.print()

    # HuggingFace Examples
    console.print("🤗 [bold]HuggingFace (Transformers):[/bold]")
    console.print("  [yellow]Install a model:[/yellow]")
    console.print("    super model install -b huggingface microsoft/Phi-4")
    console.print("  [yellow]Start a local server:[/yellow]")
    console.print("    super model server huggingface microsoft/Phi-4 --port 8001")
    console.print("  [yellow]Use with SuperOptiX:[/yellow]")
    console.print("    super model dspy microsoft/Phi-4")
    console.print()

    # LM Studio Examples
    console.print("🎮 [bold]LM Studio (Desktop App):[/bold]")
    console.print("  [yellow]Install a model:[/yellow]")
    console.print("    Download via the LM Studio app")
    console.print("  [yellow]Start a local server:[/yellow]")
    console.print("    Start server in LM Studio app (usually runs on localhost:1234)")
    console.print("  [yellow]Use with SuperOptiX:[/yellow]")
    console.print("    super model dspy lmstudio/your-model-name")
    console.print()

    console.print("💡 [bold]Quick Start:[/bold]")
    console.print("  1. Choose a backend above")
    console.print("  2. Browse their model library")
    console.print("  3. Install models using their tools")
    console.print("  4. Use [bold]super model list[/bold] to see installed models")


def _show_detailed_guide():
    """Show detailed installation guide."""
    settings = get_superoptix_model_discovery_settings()

    console.print("📚 [bold cyan]SuperOptiX Model Installation Guide[/bold cyan]")
    console.print()

    for backend_name, guide_info in settings["guides"].items():
        console.print(f"## {guide_info['title']}")
        console.print(f"{guide_info['description']}")
        console.print()

        console.print("### Quick Start:")
        for step in guide_info["quick_start"]:
            console.print(f"  {step}")
        console.print()

        console.print("### Popular Models:")
        for model in guide_info["popular_models"]:
            console.print(f"  • {model}")
        console.print()
        console.print("---")
        console.print()

    console.print("🔍 [bold]Want to explore?[/bold]")
    console.print("  Use [bold]super model discover[/bold] for the interactive guide")


if __name__ == "__main__":
    app()
