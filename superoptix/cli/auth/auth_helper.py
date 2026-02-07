"""Authentication helper utilities for Super CLI.

Note: Authentication logic has been disabled for the Open Source version.
This file is kept for compatibility with existing code that imports it.
"""

from typing import Optional
from functools import wraps
from .token_storage import TokenStorage


def is_authenticated() -> bool:
    """Check if user is currently authenticated.

    Returns:
        False (Authentication disabled in OSS version)
    """
    return False


def get_current_user() -> Optional[dict]:
    """Get current authenticated user information.

    Returns:
        None (Authentication disabled in OSS version)
    """
    return None


def get_access_token() -> Optional[str]:
    """Get current access token.

    Returns:
        None (Authentication disabled in OSS version)
    """
    return None


def get_authenticated_client():
    """Get authenticated client.

    Returns:
        None (Authentication disabled in OSS version)
    """
    return None


def require_auth(func):
    """Decorator to require authentication for CLI commands.
    
    Since auth is disabled, this effectively disables the command or warns.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print()

        auth_required_panel = Panel(
            "[yellow]⚠️  Authentication Disabled[/yellow]\n\n"
            "This feature requires authentication, which is disabled in the open source version.\n",
            border_style="yellow",
            padding=(1, 2),
            title="[bold yellow]Login Disabled[/bold yellow]",
        )

        console.print(auth_required_panel)
        console.print()
        return None

    return wrapper


def show_auth_status(console=None):
    """Display current authentication status."""
    return


def refresh_token_if_needed() -> bool:
    """Automatically refresh token if expired or about to expire.

    Returns:
        False (Authentication disabled)
    """
    return False