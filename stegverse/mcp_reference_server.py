"""Inspectable ordinary MCP reference server used by production-artifact tests.

This server contains no StegVerse governance logic. It implements a small JSON-RPC
stdio MCP surface so testers can inspect the complete capability contract and use
it as a known reference target before substituting their own MCP server.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Mapping

SERVER_INFO = {"name": "stegverse-general-mcp", "version": "1.0.0"}
PROTOCOL_VERSION = "2025-06-18"

_STATE: dict[str, Any] = {
    "bounded_value": 0,
    "resources": {},
    "single_use_consumed": False,
}


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "inspect_state",
            "description": "Return the current state of the inspectable reference MCP server.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "write_bounded_value",
            "description": "Set bounded_value to an integer from 0 through 100 inclusive.",
            "inputSchema": {
                "type": "object",
                "properties": {"value": {"type": "integer", "minimum": 0, "maximum": 100}},
                "required": ["value"],
                "additionalProperties": False,
            },
        },
        {
            "name": "create_resource",
            "description": "Create or replace a named in-memory resource with a text value.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1, "maxLength": 64},
                    "value": {"type": "string", "maxLength": 1024},
                },
                "required": ["name", "value"],
                "additionalProperties": False,
            },
        },
        {
            "name": "single_use_operation",
            "description": "Succeed only once for replay/resubmission boundary testing.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    ]


def _text_result(payload: Mapping[str, Any], *, is_error: bool = False) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(dict(payload), sort_keys=True)}],
        "structuredContent": dict(payload),
        "isError": is_error,
    }


def call_tool(name: str, arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
    args = dict(arguments or {})
    if name == "inspect_state":
        return _text_result({"status": "OK", "state": _STATE})
    if name == "write_bounded_value":
        value = args.get("value")
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
            return _text_result({"status": "ERROR", "reason": "VALUE_OUT_OF_RANGE"}, is_error=True)
        _STATE["bounded_value"] = value
        return _text_result({"status": "UPDATED", "bounded_value": value})
    if name == "create_resource":
        resource_name, value = args.get("name"), args.get("value")
        if not isinstance(resource_name, str) or not resource_name or len(resource_name) > 64:
            return _text_result({"status": "ERROR", "reason": "INVALID_RESOURCE_NAME"}, is_error=True)
        if not isinstance(value, str) or len(value) > 1024:
            return _text_result({"status": "ERROR", "reason": "INVALID_RESOURCE_VALUE"}, is_error=True)
        _STATE["resources"][resource_name] = value
        return _text_result({"status": "CREATED", "name": resource_name, "value": value})
    if name == "single_use_operation":
        if _STATE["single_use_consumed"]:
            return _text_result({"status": "ERROR", "reason": "ALREADY_CONSUMED"}, is_error=True)
        _STATE["single_use_consumed"] = True
        return _text_result({"status": "CONSUMED"})
    return _text_result({"status": "ERROR", "reason": "UNKNOWN_TOOL", "tool": name}, is_error=True)


def handle_message(message: Mapping[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tool_definitions()}}
    if method == "tools/call":
        params = message.get("params") if isinstance(message.get("params"), Mapping) else {}
        name = params.get("name")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), Mapping) else {}
        if not isinstance(name, str):
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "tool name is required"}}
        return {"jsonrpc": "2.0", "id": request_id, "result": call_tool(name, arguments)}
    if request_id is None:
        return None
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "method not found"}}


def serve_stdio() -> int:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
            if not isinstance(message, Mapping):
                raise ValueError("message must be an object")
            response = handle_message(message)
        except Exception as exc:  # protocol boundary: return a JSON-RPC error instead of crashing
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


def main() -> int:
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
