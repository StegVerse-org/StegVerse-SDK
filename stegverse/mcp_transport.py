"""Credential-free MCP transport boundary for production-artifact testing.

Only local stdio transport is implemented in this lane. Caller-supplied secret,
token, authorization-header, environment-credential, or shell-string surfaces are
rejected. Protected credentials, when later required, remain TV/TVC-owned.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence


class MCPTransportError(RuntimeError):
    pass


_FORBIDDEN_KEYS = {
    "authorization", "auth", "token", "secret", "api_key", "apikey", "password",
    "bearer", "headers", "env", "environment", "credential", "credentials",
}


def _contains_forbidden(value: Any, *, path: str = "descriptor") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in _FORBIDDEN_KEYS or any(part in key_text for part in ("token", "secret", "password", "credential")):
                return f"{path}.{key}"
            nested = _contains_forbidden(child, path=f"{path}.{key}")
            if nested:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _contains_forbidden(child, path=f"{path}[{index}]")
            if nested:
                return nested
    return None


def validate_descriptor(descriptor: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(descriptor)
    forbidden = _contains_forbidden(data)
    if forbidden:
        raise MCPTransportError(
            f"caller-managed credential material is prohibited at {forbidden}; external MCP credentials are TV/TVC_ONLY"
        )
    if data.get("transport") != "stdio":
        raise MCPTransportError("this production-artifact test lane currently accepts transport=stdio only")
    command = data.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
        raise MCPTransportError("stdio descriptor.command must be a non-empty JSON string array")
    if any("\n" in item or "\r" in item for item in command):
        raise MCPTransportError("descriptor command entries must not contain line breaks")
    return {"transport": "stdio", "command": list(command), "name": str(data.get("name") or "external-mcp")}


def load_descriptor(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise MCPTransportError(f"unable to read MCP descriptor: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise MCPTransportError(f"MCP descriptor is not valid JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise MCPTransportError("MCP descriptor must be a JSON object")
    return validate_descriptor(value)


def reference_descriptor() -> dict[str, Any]:
    return {
        "transport": "stdio",
        "name": "stegverse-general-mcp",
        "command": [sys.executable, "-m", "stegverse.mcp_reference_server"],
    }


class StdioMCPClient:
    def __init__(self, descriptor: Mapping[str, Any], *, timeout: float = 10.0):
        self.descriptor = validate_descriptor(descriptor)
        self.timeout = timeout
        self._proc: subprocess.Popen[str] | None = None
        self._next_id = 1
        self.server_info: dict[str, Any] = {}
        self.protocol_version: str | None = None

    def __enter__(self) -> "StdioMCPClient":
        command: Sequence[str] = self.descriptor["command"]
        try:
            self._proc = subprocess.Popen(
                list(command),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise MCPTransportError(f"unable to launch MCP stdio server: {exc}") from exc
        initialized = self._request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "stegverse-sdk-mcp-test", "version": "1"},
        })
        self.protocol_version = str(initialized.get("protocolVersion") or "")
        info = initialized.get("serverInfo")
        self.server_info = dict(info) if isinstance(info, Mapping) else {}
        self._notify("notifications/initialized", {})
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        proc = self._proc
        self._proc = None
        if proc is None:
            return
        if proc.stdin:
            try:
                proc.stdin.close()
            except OSError:
                pass
        try:
            proc.terminate()
            proc.wait(timeout=1)
        except Exception:
            proc.kill()

    def _send(self, payload: Mapping[str, Any]) -> None:
        if not self._proc or not self._proc.stdin:
            raise MCPTransportError("MCP stdio process is not running")
        self._proc.stdin.write(json.dumps(dict(payload), separators=(",", ":")) + "\n")
        self._proc.stdin.flush()

    def _read(self) -> Mapping[str, Any]:
        if not self._proc or not self._proc.stdout:
            raise MCPTransportError("MCP stdio process is not running")
        line = self._proc.stdout.readline()
        if not line:
            stderr = self._proc.stderr.read() if self._proc.stderr else ""
            raise MCPTransportError(f"MCP server closed before responding: {stderr.strip()}")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MCPTransportError(f"MCP server returned invalid JSON: {exc}") from exc
        if not isinstance(value, Mapping):
            raise MCPTransportError("MCP server response must be a JSON object")
        return value

    def _request(self, method: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": dict(params)})
        response = self._read()
        if response.get("id") != request_id:
            raise MCPTransportError("MCP response id does not match request id")
        if "error" in response:
            raise MCPTransportError(f"MCP server error for {method}: {response['error']}")
        result = response.get("result")
        if not isinstance(result, Mapping):
            raise MCPTransportError(f"MCP result for {method} must be an object")
        return result

    def _notify(self, method: str, params: Mapping[str, Any]) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": dict(params)})

    def list_tools(self) -> list[dict[str, Any]]:
        result = self._request("tools/list", {})
        tools = result.get("tools")
        if not isinstance(tools, list) or not all(isinstance(tool, Mapping) for tool in tools):
            raise MCPTransportError("MCP tools/list result must contain a tools array")
        return [dict(tool) for tool in tools]

    def call_tool(self, name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        return dict(self._request("tools/call", {"name": name, "arguments": dict(arguments)}))
