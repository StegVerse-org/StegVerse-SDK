"""Manifest binding for governed LLM session packets.

This module turns a governed LLM session packet and its SDK intake result into a
stable manifest object. The manifest is receipt-ready but still non-executing.
Optional system-boundary declarations are validated and bound by deterministic
reference without making them mandatory for legacy packets.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from .governed_llm_session_intake import intake_governed_llm_session_packet
from .system_boundary import validate_system_boundary_declaration


GOVERNED_LLM_MANIFEST_SCHEMA_VERSION = "stegverse.sdk.governed_llm_manifest.v0.1"


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _bind_system_boundary(
    session_packet: Mapping[str, Any],
) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
    declaration = session_packet.get("system_boundary_declaration")
    supplied_ref = session_packet.get("system_boundary_declaration_ref")

    if declaration is None:
        if supplied_ref is not None:
            raise ValueError(
                "system_boundary_declaration_ref cannot be supplied without system_boundary_declaration"
            )
        return None, None

    if not isinstance(declaration, Mapping):
        raise ValueError("system_boundary_declaration must be an object")

    validation = validate_system_boundary_declaration(declaration)
    if not validation.accepted:
        raise ValueError(
            "invalid system_boundary_declaration: " + "; ".join(validation.errors)
        )

    declaration_copy = dict(declaration)
    expected_ref = {
        "algorithm": "sha256",
        "digest": stable_hash(declaration_copy),
        "declaration_id": declaration_copy["declaration_id"],
        "authorizing": False,
        "custody_transferred": False,
        "admissibility_determined": False,
    }

    if supplied_ref is not None:
        if not isinstance(supplied_ref, Mapping):
            raise ValueError("system_boundary_declaration_ref must be an object")
        if dict(supplied_ref) != expected_ref:
            raise ValueError("system_boundary_declaration_ref does not match declaration")

    return declaration_copy, expected_ref


@dataclass(frozen=True)
class GovernedLLMManifest:
    """Receipt-ready manifest for a governed LLM session packet."""

    manifest_type: str
    session_hash: str
    intake_decision: str
    route: str
    retain_record: bool
    source_repo: str = "StegVerse-org/LLM-adapter"
    created_at: str = ""
    schema_version: str = GOVERNED_LLM_MANIFEST_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        data = {
            "schema_version": self.schema_version,
            "created_at": self.created_at or utc_now_iso(),
            "manifest_type": self.manifest_type,
            "source_repo": self.source_repo,
            "session_hash": self.session_hash,
            "intake_decision": self.intake_decision,
            "route": self.route,
            "retain_record": self.retain_record,
        }
        data["manifest_hash"] = stable_hash(data)
        return data


def build_governed_llm_manifest(
    session_packet: Mapping[str, Any],
    *,
    source_repo: str = "StegVerse-org/LLM-adapter",
    manifest_type: str = "governed_llm_session",
) -> dict[str, Any]:
    """Build a receipt-ready manifest for a governed LLM session packet."""

    declaration, declaration_ref = _bind_system_boundary(session_packet)
    intake = intake_governed_llm_session_packet(session_packet)
    manifest = GovernedLLMManifest(
        manifest_type=manifest_type,
        source_repo=source_repo,
        session_hash=intake.session_hash,
        intake_decision=intake.intake_decision,
        route=intake.route,
        retain_record=intake.retain_record,
    )
    result = manifest.to_dict()
    result["intake"] = intake.to_dict()
    if declaration is not None and declaration_ref is not None:
        result["system_boundary_declaration"] = declaration
        result["system_boundary_declaration_ref"] = declaration_ref
        result["manifest_hash"] = stable_hash(
            {key: value for key, value in result.items() if key != "manifest_hash"}
        )
    return result


__all__ = [
    "GOVERNED_LLM_MANIFEST_SCHEMA_VERSION",
    "GovernedLLMManifest",
    "build_governed_llm_manifest",
]
