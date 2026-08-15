"""MCP production-artifact testing through the canonical StegVerse route."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping
import uuid

from .mcp_transport import MCPTransportError, StdioMCPClient, load_descriptor, reference_descriptor
from .sovereign_validation_runtime import run_sovereign_validation


class MCPGovernanceError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _tool_by_name(tools: list[dict[str, Any]], name: str) -> dict[str, Any]:
    matches = [tool for tool in tools if tool.get("name") == name]
    if len(matches) != 1:
        raise MCPGovernanceError(f"expected exactly one discovered MCP tool named {name!r}; found {len(matches)}")
    return matches[0]


def _descriptor(source: str, descriptor_path: str | None) -> dict[str, Any]:
    if source == "reference":
        if descriptor_path:
            raise MCPGovernanceError("--mcp-descriptor is not used with --mcp-source reference")
        return reference_descriptor()
    if source == "external":
        if not descriptor_path:
            raise MCPGovernanceError("--mcp-descriptor <descriptor.json> is required with --mcp-source external")
        try:
            return load_descriptor(descriptor_path)
        except MCPTransportError as exc:
            raise MCPGovernanceError(str(exc)) from exc
    raise MCPGovernanceError("mcp source must be reference or external")


def load_arguments(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise MCPGovernanceError(f"unable to read MCP arguments: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise MCPGovernanceError(f"MCP arguments are not valid JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise MCPGovernanceError("MCP arguments must be a JSON object")
    return dict(value)


def build_portable_packet(
    *,
    descriptor_name: str,
    protocol_version: str,
    server_info: Mapping[str, Any],
    tool: Mapping[str, Any],
    arguments: Mapping[str, Any],
) -> dict[str, Any]:
    contract = {
        "descriptor_name": descriptor_name,
        "protocol_version": protocol_version,
        "server_info": dict(server_info),
        "tool": dict(tool),
    }
    contract_hash = _sha256(contract)
    call = {
        "contract_hash": contract_hash,
        "tool_name": tool.get("name"),
        "arguments": dict(arguments),
    }
    return {
        "schema": "stegverse.mcp-portable-authority-test-packet.v1",
        "mcp_contract": contract,
        "mcp_contract_hash": contract_hash,
        "proposed_call": call,
        "proposed_call_hash": _sha256(call),
        "authority_effect": "NONE_UNTIL_CANONICAL_GOVERNANCE",
        "credential_authority": "TV/TVC_ONLY",
    }


def build_governed_request(packet: Mapping[str, Any]) -> dict[str, Any]:
    tool = ((packet.get("mcp_contract") or {}).get("tool") or {})
    tool_name = str(tool.get("name") or "unknown")
    contract_hash = str(packet["mcp_contract_hash"])
    call_hash = str(packet["proposed_call_hash"])
    return {
        "schema_version": "1.0",
        "request_id": "mcp-" + uuid.uuid4().hex,
        "case_profile": "ordinary",
        "execution_provenance": {
            "lane_class": "PRODUCTION_VALIDATION",
            "routing_surface": "CANONICAL_PRODUCTION",
            "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
            "sandbox_required": False,
            "sandbox_tier": "NONE",
            "origin_surface": "StegVerse-org/StegVerse-SDK:mcp-production-artifact-test",
            "external_consequence_enabled": False,
        },
        "input": {
            "steggate_request": {
                "candidate": {
                    "actor_class": "ai",
                    "action": f"mcp.tools.call:{tool_name}",
                    "target": str((packet.get("mcp_contract") or {}).get("descriptor_name") or "mcp-server"),
                    "scope": "mcp-portable-authority-test",
                    "parameters": {
                        "mcp_contract_hash": contract_hash,
                        "mcp_call_hash": call_hash,
                        "tool_name": tool_name,
                        "arguments": dict((packet.get("proposed_call") or {}).get("arguments") or {}),
                    },
                },
                "judgment": {
                    "refusal_available": True,
                    "operator_recoverability": "available",
                    "workload_state": "supported",
                    "time_pressure": "normal",
                    "isolation_state": "supported",
                    "evidence_refs": [f"mcp-contract:{contract_hash}", f"mcp-call:{call_hash}"],
                },
                "signal": {
                    "admitted_signal_refs": [f"mcp-tools-list:{contract_hash}"],
                    "transformations": ["mcp-tools-list-canonicalize:json-sort-v1"],
                    "missing_inputs": [],
                    "uncertainty_state": "bounded",
                    "reference_state_hash": contract_hash,
                    "expected_reference_state_hash": contract_hash,
                    "reconstruction_available": True,
                    "transformation_provenance_complete": True,
                },
                "execution": {
                    "actor_authority_current": True,
                    "policy_current": True,
                    "delegation_current": True,
                    "evidence_current": True,
                    "affected_entity_conditions_represented": True,
                    "recoverability_profile": "recoverable",
                    "validity_window_open": True,
                    "policy_ref": "policy:mcp-portable-authority-test-v1",
                    "delegation_ref": "delegation:mcp-production-artifact-test",
                    "evidence_refs": [f"mcp-contract:{contract_hash}", f"mcp-call:{call_hash}"],
                },
                "capability": {"allowed": True},
                "continuity": {
                    "required": True,
                    "previous_receipt_verified": True,
                    "previous_receipt_hash": "receipt:mcp-test-entry",
                },
                "approval": {"required": False},
                "permission_present": False,
            },
            "input_data": {
                "mcp_contract_hash": contract_hash,
                "mcp_call_hash": call_hash,
                "tool_name": tool_name,
                "phase": "mcp-production-artifact-test",
            },
        },
        "return_projection": "ALL",
        "manifest_labels": True,
        "authority_claim": False,
        "notes": "MCP production-artifact test using canonical Core-Lite/StegCore/StegGate/Master Records path.",
    }


def run_mcp_governed_test(
    *,
    source: str,
    descriptor_path: str | None,
    tool_name: str,
    arguments: Mapping[str, Any],
    custody_db: str | Path,
    host_identity: str = "stegverse-sovereign-local",
) -> dict[str, Any]:
    descriptor = _descriptor(source, descriptor_path)
    try:
        with StdioMCPClient(descriptor) as client:
            tools = client.list_tools()
            tool = _tool_by_name(tools, tool_name)
            packet = build_portable_packet(
                descriptor_name=str(descriptor.get("name") or "mcp-server"),
                protocol_version=str(client.protocol_version or ""),
                server_info=client.server_info,
                tool=tool,
                arguments=arguments,
            )
            request = build_governed_request(packet)

            def execute() -> Mapping[str, Any]:
                result = client.call_tool(tool_name, arguments)
                return {
                    "status": "MCP_TOOL_RESULT_OBSERVED",
                    "external_side_effect": True,
                    "mcp_contract_hash": packet["mcp_contract_hash"],
                    "mcp_call_hash": packet["proposed_call_hash"],
                    "mcp_result": result,
                }

            governed = run_sovereign_validation(
                request,
                custody_db=custody_db,
                host_identity=host_identity,
                consequence_executor=execute,
                consequence_metadata={
                    "mcp_packet": packet,
                    "discovered_tool_count": len(tools),
                    "credential_authority": "TV/TVC_ONLY",
                    "transport": "stdio",
                },
                route_source="StegVerse-SDK:mcp-production-artifact-test",
                route_purpose="mcp-portable-authority-production-artifact-test",
            )
    except MCPTransportError as exc:
        raise MCPGovernanceError(str(exc)) from exc

    return {
        "schema": "stegverse.mcp-production-artifact-test-result.v1",
        "source": source,
        "descriptor_name": descriptor.get("name"),
        "portable_packet": packet,
        "governed_result": governed,
        "master_records_custody_status": governed.get("master_records_custody_status"),
        "manifest_receipt_id": governed.get("manifest_receipt_id"),
        "return_path": "canonical-ingestion/CGE->SDK",
    }
