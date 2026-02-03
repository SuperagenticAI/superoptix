"""Secure token storage for CLI authentication."""

from pathlib import Path
import json
import os
from typing import Optional, Dict
from datetime import datetime


class TokenStorage:
    """Secure token storage for CLI authentication.

    Stores authentication tokens in the user's home directory with
    proper permissions for security.

    Example:
        >>> storage = TokenStorage()
        >>> storage.save_token({'access_token': 'abc123', 'user': {...}})
        >>> token = storage.load_token()
        >>> print(token['access_token'])
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize token storage.

        Args:
            config_dir: Custom config directory (defaults to ~/.superoptix)
        """
        # Store in user's home directory
        if config_dir:
            self.config_dir = config_dir
        else:
            self.config_dir = Path.home() / ".superoptix"

        self.token_file = self.config_dir / "auth.json"

        # Ensure directory exists with proper permissions
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure config directory exists with secure permissions."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            # Set directory permissions to user-only (rwx------)
            os.chmod(self.config_dir, 0o700)

    def save_token(self, token_data: Dict):
        """Save authentication token securely.

        Args:
            token_data: Dictionary containing token and user data
                Expected keys:
                - access_token: str
                - refresh_token: str (optional)
                - expires_at: int (optional, unix timestamp)
                - user: dict (optional, user metadata)

        Example:
            >>> storage.save_token({
            ...     'access_token': 'abc123',
            ...     'refresh_token': 'xyz789',
            ...     'expires_at': 1234567890,
            ...     'user': {'email': 'user@example.com'}
            ... })
        """
        # Add timestamp
        token_data["saved_at"] = datetime.now().isoformat()

        # Ensure config directory exists
        self._ensure_config_dir()

        # Save token data
        with open(self.token_file, "w") as f:
            json.dump(token_data, f, indent=2)

        # Set file permissions to user-only (rw-------)
        os.chmod(self.token_file, 0o600)

    def load_token(self) -> Optional[Dict]:
        """Load authentication token.

        Returns:
            Dictionary containing token data, or None if no token exists

        Example:
            >>> token = storage.load_token()
            >>> if token:
            ...     print(f"Logged in as {token['user']['email']}")
            ... else:
            ...     print("Not logged in")
        """
        if not self.token_file.exists():
            return None

        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupted token file
            return None

    def delete_token(self):
        """Delete authentication token.

        Example:
            >>> storage.delete_token()
            >>> assert storage.has_token() == False
        """
        if self.token_file.exists():
            self.token_file.unlink()

    def has_token(self) -> bool:
        """Check if token exists.

        Returns:
            True if token file exists, False otherwise

        Example:
            >>> if storage.has_token():
            ...     print("Already logged in")
            ... else:
            ...     print("Please login")
        """
        return self.token_file.exists() and self.load_token() is not None

    def get_user(self) -> Optional[Dict]:
        """Get user information from stored token.

        Returns:
            User metadata dictionary, or None if not logged in

        Example:
            >>> user = storage.get_user()
            >>> if user:
            ...     print(f"Username: {user.get('user_metadata', {}).get('user_name')}")
        """
        token_data = self.load_token()
        if not token_data:
            return None

        return token_data.get("user")

    def is_token_expired(self) -> bool:
        """Check if the stored token is expired.

        Returns:
            True if token is expired, False otherwise

        Example:
            >>> if storage.is_token_expired():
            ...     print("Token expired, please login again")
        """
        token_data = self.load_token()
        if not token_data:
            return True

        expires_at = token_data.get("expires_at")
        if not expires_at:
            # No expiration info, assume valid
            return False

        from time import time

        return time() > expires_at

    def update_token(self, updates: Dict):
        """Update specific fields in the stored token.

        Args:
            updates: Dictionary of fields to update

        Example:
            >>> storage.update_token({
            ...     'access_token': 'new_token',
            ...     'expires_at': new_expiry
            ... })
        """
        token_data = self.load_token()
        if token_data:
            token_data.update(updates)
            self.save_token(token_data)

    def get_config_path(self) -> Path:
        """Get the config directory path.

        Returns:
            Path to config directory

        Example:
            >>> print(f"Config stored at: {storage.get_config_path()}")
        """
        return self.config_dir
