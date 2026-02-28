"""ACP client for interactive Super CLI sessions."""

from __future__ import annotations

import json
import selectors
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional


@dataclass
class ACPSessionConfig:
    agent: str
    command: str
    model: Optional[str] = None
    cwd: Optional[str] = None


@dataclass
class ACPClient:
    """Minimal synchronous ACP JSON-RPC subprocess client."""

    project_root: Path
    on_event: Optional[Callable[[Dict[str, Any]], None]] = None

    _process: Optional[subprocess.Popen] = field(default=None, init=False, repr=False)
    _request_id: int = field(default=0, init=False)
    _session_id: str = field(default="", init=False)
    _connected_config: Optional[ACPSessionConfig] = field(default=None, init=False)
    _selector: Optional[selectors.BaseSelector] = field(default=None, init=False, repr=False)

    def connect(self, config: ACPSessionConfig) -> bool:
        if self._process:
            return True

        cmd = config.command
        if config.model:
            cmd = f"{cmd} -m {shlex.quote(config.model)}"
        cwd = config.cwd or str(self.project_root)

        try:
            self._process = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                text=True,
                bufsize=1,
            )
            self._selector = selectors.DefaultSelector()
            self._selector.register(self._process.stdout, selectors.EVENT_READ)

            self._initialize()
            self._new_session(cwd)
            self._connected_config = config
            return True
        except Exception:
            self.disconnect()
            return False

    def disconnect(self) -> None:
        if self._selector:
            try:
                self._selector.close()
            except Exception:
                pass
            self._selector = None

        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None

        self._session_id = ""
        self._connected_config = None

    def is_connected(self) -> bool:
        return self._process is not None and self._session_id != ""

    def connected_agent(self) -> Optional[str]:
        if not self._connected_config:
            return None
        return self._connected_config.agent

    def send_prompt(self, prompt: str) -> Dict[str, Any]:
        if not self.is_connected():
            return {"ok": False, "error": "ACP client is not connected"}
        try:
            response = self._call(
                "session/prompt",
                prompt=[{"type": "text", "text": prompt}],
                sessionId=self._session_id,
            )
            return {"ok": True, "result": response}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _initialize(self) -> Dict[str, Any]:
        return self._call(
            "initialize",
            protocolVersion=1,
            clientCapabilities={"terminal": True, "fs": {"readTextFile": True, "writeTextFile": True}},
            clientInfo={"name": "SuperOptiX", "title": "Super CLI", "version": "0.2"},
        )

    def _new_session(self, cwd: str) -> Dict[str, Any]:
        response = self._call("session/new", cwd=cwd, mcpServers=[])
        self._session_id = response.get("sessionId", "")
        return response

    def _call(self, method: str, **params) -> Dict[str, Any]:
        self._request_id += 1
        req_id = self._request_id
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": req_id}
        self._send_json(payload)
        return self._read_response(req_id=req_id, timeout_seconds=120)

    def _send_json(self, payload: Dict[str, Any]) -> None:
        if not self._process or not self._process.stdin:
            raise RuntimeError("ACP process is not running")
        self._process.stdin.write(json.dumps(payload) + "\n")
        self._process.stdin.flush()

    def _read_response(self, req_id: int, timeout_seconds: float) -> Dict[str, Any]:
        if not self._selector or not self._process or not self._process.stdout:
            raise RuntimeError("ACP selector is not available")

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            timeout = max(0.1, deadline - time.time())
            events = self._selector.select(timeout=timeout)
            if not events:
                continue

            line = self._process.stdout.readline()
            if not line:
                continue
            text = line.strip()
            if not text:
                continue

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                if self.on_event:
                    self.on_event({"type": "log", "text": text})
                continue

            # Response for request
            if data.get("id") == req_id and ("result" in data or "error" in data):
                if "error" in data:
                    raise RuntimeError(str(data["error"]))
                return data["result"]

            # Notification or other response
            if self.on_event:
                self.on_event({"type": "notification", "payload": data})

        raise TimeoutError(f"Timed out waiting for ACP response to request id {req_id}")

    # Backward-compatible wrappers used by slash command module
    def connect_sync(self, config: ACPSessionConfig) -> bool:
        return self.connect(config)

    def disconnect_sync(self) -> None:
        self.disconnect()

    def send_prompt_sync(self, prompt: str) -> Dict[str, Any]:
        return self.send_prompt(prompt)
