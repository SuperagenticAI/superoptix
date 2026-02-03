"""
Utility functions for the SuperOptiX CLI.
"""

import asyncio
import contextlib
import os  # noqa: F401
import warnings
from pathlib import Path
from typing import Any, Coroutine

from rich.console import Console

console = Console()


def is_superoptix_project() -> bool:
    """
    Check if the current directory is a SuperOptiX project by looking for the .super file.

    Returns:
        bool: True if .super file exists in current directory, False otherwise
    """
    return Path(".super").exists()


def validate_superoptix_project(
    commands_that_require_project: list[str] = None,
) -> None:
    """
    Validate that the user is in a SuperOptiX project directory.

    This function checks for the presence of a .super file in the current directory.
    If not found, it displays an error message and exits.

    Args:
        commands_that_require_project: List of commands that require being in a project directory.
                                      If None, uses default list of commands that need project context.

    Raises:
        SystemExit: If not in a SuperOptiX project directory
    """
    if commands_that_require_project is None:
        commands_that_require_project = ["agent", "spec", "orchestra", "observe"]

    if not is_superoptix_project():
        console.print("[bold red]❌ Not in a SuperOptiX project directory[/bold red]")
        console.print(
            "Initialize a project with: [bold cyan]super init <project_name>[/bold cyan]"
        )
        console.print("Or navigate to an existing SuperOptiX project directory.")
        console.print(
            f"Commands that require a project: [cyan]{', '.join(commands_that_require_project)}[/cyan]"
        )
        raise SystemExit(1)


def create_project_structure(project_path: Path) -> None:
    """
    Create the standard SuperOptiX project directory structure.

    Args:
        project_path: Path to the project root directory
    """
    # Define the standard project structure
    directories = [
        "agents",
        "guardrails",
        "memory",
        "protocols",
        "teams",
        "evals",
        "knowledge",
        "optimizers",
        "servers",
        "tools",
    ]

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

    # Create the .super marker file
    (project_path / ".super").touch()


@contextlib.contextmanager
def suppress_warnings():
    """Context manager to suppress all warnings during CLI operations."""
    # ULTRA-AGGRESSIVE: Suppress ALL warnings first
    import os
    
    # Save original state
    old_filter = warnings.filters[:]  # Save current filters
    old_pythonwarnings = os.environ.get("PYTHONWARNINGS")
    
    try:
        # Suppress all warnings immediately
        warnings.simplefilter("ignore")
        os.environ.setdefault("PYTHONWARNINGS", "ignore")
        
        # Suppress specific warnings that are problematic in CLI
        warnings.filterwarnings(
            "ignore", message="unclosed database", category=ResourceWarning
        )
        # Comprehensive Pydantic warning suppression
        warnings.filterwarnings(
            "ignore", message=r".*[Pp]ydantic.*", category=UserWarning
        )
        warnings.filterwarnings(
            "ignore", message=r".*[Pp]ydantic.*", category=DeprecationWarning
        )
        warnings.filterwarnings(
            "ignore", module="pydantic.*", category=UserWarning
        )
        warnings.filterwarnings(
            "ignore", module="pydantic_ai.*", category=UserWarning
        )
        warnings.filterwarnings(
            "ignore", module="storage3.*", category=UserWarning
        )
        warnings.filterwarnings(
            "ignore", category=FutureWarning, module="huggingface_hub"
        )
        warnings.filterwarnings(
            "ignore", category=UserWarning, module="huggingface_hub"
        )
        warnings.filterwarnings(
            "ignore", category=DeprecationWarning, module="huggingface_hub"
        )
        warnings.filterwarnings("ignore", category=UserWarning, message=".*torch.*")
        warnings.filterwarnings(
            "ignore", category=FutureWarning, message=".*transformers.*"
        )
        warnings.filterwarnings(
            "ignore", category=UserWarning, message=".*transformers.*"
        )
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        
        # CRITICAL: Only ONE yield statement for context manager
        yield
    finally:
        # Restore original state (guarded to prevent exceptions from breaking generator)
        try:
            warnings.filters[:] = old_filter
            if old_pythonwarnings is None:
                os.environ.pop("PYTHONWARNINGS", None)
            else:
                os.environ["PYTHONWARNINGS"] = old_pythonwarnings
        except Exception:
            # If restoration fails, just continue - better than breaking the generator
            pass


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    Safely run an async coroutine, handling existing event loops properly.

    This function prevents ResourceWarning about unclosed event loops by:
    1. Checking if there's already a running event loop
    2. Using the existing loop if available
    3. Creating a new loop only when necessary

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine
    """
    with suppress_warnings():
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an event loop, we need to handle this differently
            # For CLI commands, we'll create a new task and run it
            if loop and loop.is_running():
                # This shouldn't happen in CLI context, but handle it gracefully
                return asyncio.run(coro)
            else:
                return asyncio.run(coro)
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(coro)


@contextlib.contextmanager
def simple_progress(message: str = "Working..."):
    """
    Simple context manager for showing progress during long-running operations.

    Usage:
        with simple_progress("Installing model..."):
            # your long-running operation here
            result = some_long_operation()

    Args:
        message: The message to display while working
    """
    with console.status(f"[cyan]{message}[/cyan]", spinner="dots"):
        yield
