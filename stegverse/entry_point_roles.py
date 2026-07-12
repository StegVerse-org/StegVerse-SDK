"""Canonical descriptions for StegVerse ecosystem entry points.

Entry-point acceptance, translation, or display does not create execution
authority or admissibility. The registry describes interaction roles and the
session/usage obligations shared across entry points.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, Mapping

SCHEMA_VERSION = "1.0.0"


class EntryPointRoleError(ValueError):
    """Raised when an entry-point role declaration violates the contract."""


def _stable_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _role(
    entry_point_id: str,
    display_name: str,
    primary_role: str,
    audiences: list[str],
    interactions: list[str],
    accepted: list[str],
    produced: list[str],
    related: list[str],
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "entry_point_id": entry_point_id,
        "display_name": display_name,
        "primary_role": primary_role,
        "related_roles": related,
        "primary_audiences": audiences,
        "interaction_types": interactions,
        "accepted_inputs": accepted,
        "produced_outputs": produced,
        "authority_boundaries": {
            "acceptance_is_authority": False,
            "translation_is_admissibility": False,
            "display_is_execution": False,
        },
        "usage_reporting": {
            "emits_usage_events": True,
            "metric_owner_required": True,
            "measurement_id_required": True,
        },
        "session_continuity": {
            "preserves_session_id": True,
            "preserves_transition_lineage": True,
            "supports_return_to_origin": True,
        },
    }


ENTRY_POINT_ROLES: Dict[str, Dict[str, Any]] = {
    "sdk": _role(
        "sdk",
        "StegVerse SDK",
        "Developer-native programmatic intake, testing, integration, and observation boundary.",
        ["developers", "researchers", "module authors", "external applications"],
        [
            "raw_data_governance_test",
            "module_compatibility_test",
            "schema_validation",
            "manifest_generation",
            "receipt_validation",
            "sandbox_route",
            "runtime_comparison",
            "developer_integration",
        ],
        ["raw data", "modules", "schemas", "transition candidates", "session packets"],
        ["validated packages", "manifests", "transport envelopes", "receipts", "test results"],
        ["testing harness", "integration contract", "transport boundary", "evidence inspection"],
    ),
    "llm_adapter": _role(
        "llm_adapter",
        "StegVerse LLM Adapter",
        "Machine-readable translation and interoperability boundary for models, agents, tools, and external frameworks.",
        ["LLM providers", "agent frameworks", "developers", "external systems"],
        [
            "provider_output_normalization",
            "agent_trace_conversion",
            "recursive_call_telemetry",
            "external_framework_intake",
            "machine_readable_governance_conversion",
            "provider_neutral_response_packaging",
        ],
        ["prompts", "provider responses", "tool traces", "agent traces", "external packages"],
        ["canonical intent", "transition packages", "telemetry envelopes", "machine-readable results"],
        ["provider abstraction", "normalization layer", "compatibility bridge", "telemetry capture"],
    ),
    "ecosystem_chat": _role(
        "ecosystem_chat",
        "StegVerse Ecosystem Chat",
        "Universal browser interface for governed conversation, discovery, development, testing, and orchestration.",
        ["general users", "developers", "researchers", "organizations"],
        [
            "governed_conversation",
            "ecosystem_discovery",
            "guided_testing",
            "governed_coding",
            "governed_research",
            "governed_social_posting",
            "module_creation_guidance",
            "receipt_and_usage_review",
            "cross_entry_session_continuation",
        ],
        ["natural language", "files", "data", "code", "module proposals", "publication requests"],
        ["governed responses", "guided routes", "developer packages", "receipts", "usage views"],
        ["ecosystem navigator", "governed assistant", "development console", "orchestration surface"],
    ),
}


def validate_entry_point_role(role: Mapping[str, Any]) -> None:
    required = {
        "schema_version", "entry_point_id", "display_name", "primary_role",
        "primary_audiences", "interaction_types", "accepted_inputs",
        "produced_outputs", "authority_boundaries", "usage_reporting",
        "session_continuity",
    }
    missing = required - set(role)
    if missing:
        raise EntryPointRoleError(f"missing role fields: {sorted(missing)}")
    if role["schema_version"] != SCHEMA_VERSION:
        raise EntryPointRoleError("unsupported entry-point role schema version")
    for field in ("primary_audiences", "interaction_types", "accepted_inputs", "produced_outputs"):
        values = role[field]
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise EntryPointRoleError(f"{field} must be a non-empty unique list")
    boundaries = role["authority_boundaries"]
    if any(boundaries.get(name) is not False for name in (
        "acceptance_is_authority", "translation_is_admissibility", "display_is_execution"
    )):
        raise EntryPointRoleError("entry points may not self-grant authority, admissibility, or execution")
    usage = role["usage_reporting"]
    if usage.get("metric_owner_required") is not True or usage.get("measurement_id_required") is not True:
        raise EntryPointRoleError("usage records require metric ownership and stable measurement identity")
    continuity = role["session_continuity"]
    if continuity.get("preserves_session_id") is not True or continuity.get("preserves_transition_lineage") is not True:
        raise EntryPointRoleError("entry points must preserve session and transition lineage")


def get_entry_point_role(entry_point_id: str) -> Dict[str, Any]:
    try:
        role = deepcopy(ENTRY_POINT_ROLES[entry_point_id])
    except KeyError as exc:
        raise EntryPointRoleError(f"unknown entry point: {entry_point_id}") from exc
    validate_entry_point_role(role)
    role["role_sha256"] = _stable_hash(role)
    return role


def list_entry_point_roles() -> list[Dict[str, Any]]:
    return [get_entry_point_role(key) for key in sorted(ENTRY_POINT_ROLES)]
