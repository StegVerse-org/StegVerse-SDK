"""Deterministic non-authorizing SDK 1.5 source evidence packet.

A source packet is not an InTr, WorkerCoordinator, or Master Records receipt.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .capability_inventory import qualify_requirements
from .manifest_plan import derive_execution_plan, verify_plan_lineage


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def build_source_evidence_packet(
    manifest: Mapping[str, Any], requirements: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Bind the complete qualification and derived plan without granting execution."""
    qualification = qualify_requirements(manifest, requirements)
    plan = derive_execution_plan(manifest, requirements)
    if not verify_plan_lineage(manifest, requirements, plan):
        raise ValueError("DERIVED_PLAN_LINEAGE_INVALID")
    failures = tuple({
        "requirement_id": row["requirement_id"],
        "disposition": row["disposition"],
        "failed_predicate": row["failed_predicate"],
        "permitted_correction": row["permitted_correction"],
    } for row in qualification["results"] if row["disposition"] != "SUPPORTED")
    core = {
        "schema": "stegverse.sdk-source-evidence-packet/v1",
        "source_manifest_sha256": qualification["manifest_sha256"],
        "qualification_sha256": _digest(qualification),
        "derived_plan_sha256": plan["derived_plan_sha256"],
        "requirements_sha256": plan["requirements_sha256"],
        "lineage_verified": True,
        "non_allow_results": failures,
        "execution_authorized": False,
        "runtime_execution_observed": False,
        "route_substitution_permitted": False,
        "evidence_ceiling": "SOURCE_ONLY",
    }
    return {**core, "packet_sha256": _digest(core)}


def verify_source_evidence_packet(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
    packet: Mapping[str, Any],
) -> bool:
    """Reconstruct every packet field; reject injected authority and forged receipts."""
    return dict(packet) == build_source_evidence_packet(manifest, requirements)
