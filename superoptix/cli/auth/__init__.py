"""Authentication module for Super CLI.

Provides GitHub OAuth + Supabase authentication for the CLI.
"""

from .token_storage import TokenStorage
from .auth_helper import (
    get_authenticated_client,
    require_auth,
    is_authenticated,
    get_current_user,
)

__all__ = [
    "TokenStorage",
    "get_authenticated_client",
    "require_auth",
    "is_authenticated",
    "get_current_user",
]
