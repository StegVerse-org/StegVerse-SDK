"""Canonical user-facing SDK surface registry.

This registry describes callable, non-authorizing SDK functions that are safe to
discover from the generic console. It intentionally contains no person-specific
routes and does not advertise external integrations that are not locally usable.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

SDK_SURFACES: Dict[str, Dict[str, Any]] = {
    "admissibility": {
        "summary": "Evaluate a governed admissibility tester packet locally.",
        "mode": "local",
        "input": "JSON tester packet file",
        "command": "stegverse run admissibility --input <packet.json>",
        "module": "stegverse.admissibility.evaluate_admissibility_packet",
        "documentation": "docs/DYNAMIC_ADMISSIBILITY.md",
        "authority_effect": "NONE",
    },
    "llm-admissibility": {
        "summary": "Evaluate LLM text under the SDK dynamic-admissibility bridge.",
        "mode": "local",
        "input": "provider/model/prompt/output values",
        "command": "stegverse run llm-admissibility --provider <name> --model <name> --prompt <text> --output <text>",
        "module": "stegverse.llm_admissibility.evaluate_llm_output_admissibility",
        "documentation": "docs/DYNAMIC_ADMISSIBILITY.md",
        "authority_effect": "NONE",
    },
    "math-admissibility": {
        "summary": "Evaluate a math/formalism artifact under the SDK admissibility bridge.",
        "mode": "local",
        "input": "formalism id, artifact type, artifact summary",
        "command": "stegverse run math-admissibility --formalism <id> --artifact-type <type> --summary <text>",
        "module": "stegverse.math_admissibility.evaluate_math_artifact_admissibility",
        "documentation": "docs/DYNAMIC_ADMISSIBILITY.md",
        "authority_effect": "NONE",
    },
    "admittedcode": {
        "summary": "Verify a portable AdmittedCode provider-harness receipt at the SDK boundary.",
        "mode": "local",
        "input": "AdmittedCode receipt JSON file",
        "command": "stegverse run admittedcode --input <receipt.json>",
        "demo_command": "stegverse demo admittedcode",
        "module": "stegverse.admittedcode_receipt.verify_admittedcode_receipt",
        "documentation": "docs/SDK_CONSOLE.md#admittedcode",
        "authority_effect": "NONE",
        "result_semantics": "SDK ACCEPTED validates the portable receipt boundary and preserves the underlying ALLOW/DENY/FAIL_CLOSED decision.",
        "repository_examples": [
            "examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json",
            "examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json",
        ],
    },
    "mcp-production-artifact-test": {
        "summary": "Test MCP discovery and a proposed tools/call through canonical StegVerse production artifacts.",
        "mode": "canonical-sovereign-production-test",
        "input": "StegVerse General MCP or safe external stdio MCP descriptor, exact tool, JSON arguments",
        "command": "stegverse-mcp-test --select 000|00|0|1|2",
        "module": "stegverse.mcp_cli.main",
        "documentation": "docs/MCP_PRODUCTION_ARTIFACT_TESTS.md",
        "authority_effect": "NONE_UNTIL_CANONICAL_GOVERNANCE",
        "result_semantics": "MCP discovery and portable packet binding are evidence only; the actual tools/call is reachable only as the bounded consequence of the canonical StegCore/StegGate transaction lifecycle.",
        "repository_examples": [
            "inspection/examples/mcp-reference-inspect-state-arguments.json",
            "inspection/examples/mcp-reference-write-bounded-arguments.json",
            "inspection/examples/mcp-external-stdio-descriptor.example.json",
        ],
    },
    "universal-entry": {
        "summary": "Route a universal-entry envelope against an explicitly supplied capability registry.",
        "mode": "local",
        "input": "envelope JSON and capability-registry JSON files",
        "command": "stegverse run universal-entry --input <envelope.json> --registry <capabilities.json>",
        "module": "stegverse.universal_entry.process_universal_entry",
        "documentation": "docs/UNIVERSAL_ENTRY.md",
        "authority_effect": "NONE",
    },
    "bridges": {
        "summary": "List registered dynamic-admissibility bridges.",
        "mode": "local",
        "input": "none",
        "command": "stegverse run bridges",
        "module": "stegverse.bridge_registry.list_dynamic_bridges",
        "documentation": "docs/DYNAMIC_ADMISSIBILITY.md",
        "authority_effect": "NONE",
    },
    "entry-points": {
        "summary": "List canonical StegVerse entry-point roles and their boundaries.",
        "mode": "local",
        "input": "none",
        "command": "stegverse run entry-points",
        "module": "stegverse.entry_point_roles.list_entry_point_roles",
        "documentation": "docs/ENTRY_POINT_ROLES.md",
        "authority_effect": "NONE",
    },
}

ALIASES = {
    "admitted-code": "admittedcode",
    "admissibility-llm": "llm-admissibility",
    "admissibility-math": "math-admissibility",
    "mcp": "mcp-production-artifact-test",
    "mcp-test": "mcp-production-artifact-test",
}


def canonical_surface_name(name: str) -> str:
    lowered = name.strip().lower()
    return ALIASES.get(lowered, lowered)


def list_sdk_surfaces() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for surface_id in sorted(SDK_SURFACES):
        row = {"id": surface_id, **deepcopy(SDK_SURFACES[surface_id])}
        rows.append(row)
    return rows


def get_sdk_surface(name: str) -> Dict[str, Any] | None:
    surface_id = canonical_surface_name(name)
    value = SDK_SURFACES.get(surface_id)
    return {"id": surface_id, **deepcopy(value)} if value is not None else None


__all__ = ["SDK_SURFACES", "canonical_surface_name", "list_sdk_surfaces", "get_sdk_surface"]
