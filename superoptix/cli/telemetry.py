"""Anonymous telemetry for SuperOptiX CLI.

Tracks usage patterns to improve the product while respecting user privacy.
Users can opt-out anytime.
"""

import uuid
import os
import json
import platform
from pathlib import Path
from typing import Optional, Dict, Any
import threading
import warnings

warnings.filterwarnings("ignore")


class AnonymousTelemetry:
    """Anonymous usage tracking with user consent and opt-out."""

    def __init__(self):
        """Initialize telemetry."""
        self.telemetry_id_file = Path.home() / ".superoptix_telemetry_id"
        self.config_file = Path.home() / ".superoptix_config.json"

        self.enabled = self._is_enabled()
        self.anonymous_id = self._get_or_create_id()
        self.endpoint = os.getenv(
            "SUPEROPTIX_TELEMETRY_URL", "https://superoptix.ai/api/telemetry"
        )

    def _is_enabled(self) -> bool:
        """Check if telemetry is enabled."""
        # Check environment variable (for CI/CD to disable)
        if os.getenv("SUPEROPTIX_TELEMETRY", "true").lower() == "false":
            return False

        # Check config file
        if self.config_file.exists():
            try:
                config = json.loads(self.config_file.read_text())
                return config.get("telemetry_enabled", True)
            except:
                return True

        return True  # Enabled by default (opt-out, not opt-in)

    def _get_or_create_id(self) -> str:
        """Get or create anonymous user ID."""
        if self.telemetry_id_file.exists():
            try:
                return self.telemetry_id_file.read_text().strip()
            except:
                pass

        # Create new anonymous ID
        anon_id = str(uuid.uuid4())

        try:
            self.telemetry_id_file.parent.mkdir(parents=True, exist_ok=True)
            self.telemetry_id_file.write_text(anon_id)
        except:
            pass

        return anon_id

    def track_command(
        self,
        command: str,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Track command usage anonymously.

        Args:
                command: Command name (e.g., 'spec.generate', 'agent.compile')
                success: Whether command succeeded
                metadata: Optional metadata (no sensitive data!)
        """
        if not self.enabled:
            return

        # Run in background thread (non-blocking)
        thread = threading.Thread(
            target=self._send_telemetry,
            args=(command, success, metadata or {}),
            daemon=True,
        )
        thread.start()

    def _send_telemetry(self, command: str, success: bool, metadata: Dict[str, Any]):
        """Send telemetry data (runs in background thread)."""
        try:
            import requests
            from superoptix import __version__

            payload = {
                "anonymous_id": self.anonymous_id,
                "command": command,
                "success": success,
                "version": __version__,
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "metadata": self._sanitize_metadata(metadata),
            }

            # Send with short timeout (non-blocking)
            requests.post(
                self.endpoint,
                json=payload,
                timeout=2,
                headers={"Content-Type": "application/json"},
            )

        except:
            # Silently fail - telemetry should never break CLI
            pass

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove any potentially sensitive data from metadata.

        Args:
                metadata: Original metadata

        Returns:
                Sanitized metadata
        """
        # Allowed metadata keys (whitelist approach)
        allowed_keys = {
            "tier",
            "namespace",
            "framework",
            "provider",
            "optimization_level",
            "auto_level",
            "model_provider",
            "command_type",
            "feature_used",
        }

        return {k: v for k, v in metadata.items() if k in allowed_keys}

    def disable(self):
        """Disable telemetry for this user."""
        if self.config_file.exists():
            try:
                config = json.loads(self.config_file.read_text())
            except:
                config = {}
        else:
            config = {}

        config["telemetry_enabled"] = False

        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(config, indent=2))
        except:
            pass

        self.enabled = False

    def enable(self):
        """Enable telemetry for this user."""
        if self.config_file.exists():
            try:
                config = json.loads(self.config_file.read_text())
            except:
                config = {}
        else:
            config = {}

        config["telemetry_enabled"] = True

        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(config, indent=2))
        except:
            pass

        self.enabled = True


# Global telemetry instance
_telemetry_instance: Optional[AnonymousTelemetry] = None


def get_telemetry() -> AnonymousTelemetry:
    """Get global telemetry instance."""
    global _telemetry_instance

    if _telemetry_instance is None:
        _telemetry_instance = AnonymousTelemetry()

    return _telemetry_instance


def track(command: str, success: bool = True, **metadata):
    """Convenience function to track command usage.

    Args:
            command: Command name
            success: Success status
            **metadata: Optional metadata
    """
    try:
        telemetry = get_telemetry()
        telemetry.track_command(command, success, metadata)
    except:
        pass  # Never let telemetry break the CLI
