"""Manifest binding for governed LLM session packets.

This module turns a governed LLM session packet and its SDK intake result into a
stable manifest object. The manifest is receipt-ready but still non-executing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from .governed_llm_session_intake import intake_governed_llm_session_packet


GOVERNED_LLM_MANIFEST_SCHEMA_VERSION = "stegverse.sdk.governed_llm_manifest.v0.1"


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
    return result


__all__ = [
    "GOVERNED_LLM_MANIFEST_SCHEMA_VERSION",
    "GovernedLLMManifest",
    "build_governed_llm_manifest",
]
