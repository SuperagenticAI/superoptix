"""Persistent Super CLI connection state for ACP/BYOK/LOCAL/MCP."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import yaml


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state() -> Dict[str, Any]:
    return {
        "version": 1,
        "profiles": {
            "default": {
                "active_connection": None,
                "connection_history": [],
                "byok": {},
                "local": {},
                "acp": {},
                "mcp": {"servers": {}},
                "updated_at": _utc_now_iso(),
            }
        },
        "active_profile": "default",
    }


class ConnectionStateStore:
    """Load/save connection settings under ~/.superoptix/super_cli.yaml."""

    def __init__(self, state_path: Path | None = None) -> None:
        if state_path is not None:
            self.state_path = state_path
        else:
            env_path = Path(os.environ.get("SUPEROPTIX_STATE_PATH", str(Path.home() / ".superoptix" / "super_cli.yaml")))
            self.state_path = env_path
        self.fallback_state_path = Path.cwd() / ".superoptix" / "super_cli.yaml"

    def load(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return _default_state()
        with self.state_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return _default_state()
        return self._ensure_shape(data)

    def save(self, data: Dict[str, Any]) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with self.state_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False)
            return
        except OSError:
            # Fallback to project-local state path for restricted environments.
            self.fallback_state_path.parent.mkdir(parents=True, exist_ok=True)
            with self.fallback_state_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False)
            self.state_path = self.fallback_state_path

    def profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        active_profile = data.get("active_profile", "default")
        return data["profiles"].setdefault(
            active_profile,
            {
                "active_connection": None,
                "connection_history": [],
                "byok": {},
                "local": {},
                "acp": {},
                "mcp": {"servers": {}},
                "updated_at": _utc_now_iso(),
            },
        )

    def set_active(self, connection_type: str, name: str | None = None) -> Dict[str, Any]:
        data = self.load()
        profile = self.profile(data)
        entry = {
            "type": connection_type,
            "name": name,
            "updated_at": _utc_now_iso(),
        }
        profile["active_connection"] = entry
        history = profile.setdefault("connection_history", [])
        history = [h for h in history if h.get("type") != connection_type or h.get("name") != name]
        history.insert(0, entry)
        profile["connection_history"] = history[:20]
        profile["updated_at"] = _utc_now_iso()
        self.save(data)
        return data

    def connection_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        data = self.load()
        profile = self.profile(data)
        history = profile.get("connection_history") or []
        if not isinstance(history, list):
            return []
        return [h for h in history if isinstance(h, dict)][:limit]

    def set_byok(
        self,
        provider: str,
        model: str,
        api_key_env: str | None = None,
        base_url: str | None = None,
    ) -> Dict[str, Any]:
        data = self.load()
        profile = self.profile(data)
        profile["byok"] = {
            "provider": provider,
            "model": model,
            "api_key_env": api_key_env,
            "base_url": base_url,
            "updated_at": _utc_now_iso(),
        }
        profile["updated_at"] = _utc_now_iso()
        self.save(data)
        return data

    def set_local(
        self,
        provider: str,
        model: str,
        endpoint: str | None = None,
    ) -> Dict[str, Any]:
        data = self.load()
        profile = self.profile(data)
        profile["local"] = {
            "provider": provider,
            "model": model,
            "endpoint": endpoint,
            "updated_at": _utc_now_iso(),
        }
        profile["updated_at"] = _utc_now_iso()
        self.save(data)
        return data

    def set_acp(
        self,
        agent: str,
        model: str | None = None,
        command: str | None = None,
    ) -> Dict[str, Any]:
        data = self.load()
        profile = self.profile(data)
        profile["acp"] = {
            "agent": agent,
            "model": model,
            "command": command,
            "updated_at": _utc_now_iso(),
        }
        profile["updated_at"] = _utc_now_iso()
        self.save(data)
        return data

    def set_mcp_server(
        self,
        name: str,
        transport: str,
        command: str | None = None,
        args: list[str] | None = None,
        url: str | None = None,
        enabled: bool = True,
    ) -> Dict[str, Any]:
        data = self.load()
        profile = self.profile(data)
        mcp = profile.setdefault("mcp", {"servers": {}})
        servers = mcp.setdefault("servers", {})
        servers[name] = {
            "name": name,
            "transport": transport,
            "command": command,
            "args": args or [],
            "url": url,
            "enabled": enabled,
            "updated_at": _utc_now_iso(),
        }
        profile["updated_at"] = _utc_now_iso()
        self.save(data)
        return data

    def _ensure_shape(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if "profiles" not in data or not isinstance(data["profiles"], dict):
            data["profiles"] = {}
        if "active_profile" not in data:
            data["active_profile"] = "default"
        self.profile(data)
        if "version" not in data:
            data["version"] = 1
        return data
