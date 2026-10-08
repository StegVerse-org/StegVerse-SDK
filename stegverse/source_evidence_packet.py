"""Deterministic, non-authorizing SDK 1.5 multi-condition source evidence packets.

No original InTr, WorkerCoordinator, organization or Master Records evidence is
fabricated. A source packet is never an execution receipt.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .manifest_plan import derive_execution_plan, verify_plan_lineage
from .organization_record_names import LEGACY_SOURCE_PACKET_ORGANIZATION_RECORD_OBSERVED_FIELD, ORGANIZATION_RECORD_OBSERVED_FIELD


def _hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_source_evidence_packet(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
    *,
    evaluator_id: str,
) -> dict[str, Any]:
    """Bind every condition and its failed predicate to an immutable plan digest."""
    if not isinstance(evaluator_id, str) or not evaluator_id.strip():
        raise ValueError("EVALUATOR_ID_REQUIRED")
    if not isinstance(requirements, (tuple, list)) or not requirements:
        raise ValueError("NONEMPTY_REQUIREMENTS_REQUIRED")
    identifiers = [req.get("requirement_id") for req in requirements]
    if any(not isinstance(item, str) or not item.strip() for item in identifiers):
        raise ValueError("REQUIREMENT_ID_REQUIRED")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("DUPLICATE_REQUIREMENT_ID")
    plan = derive_execution_plan(manifest, requirements)
    if not verify_plan_lineage(manifest, requirements, plan):
        raise ValueError("DERIVED_PLAN_LINEAGE_INVALID")
    conditions = tuple({
        "requirement_id": step["requirement_id"],
        "capability_id": step["capability_id"],
        "requested_route_id": step["requested_route_id"],
        "qualification_disposition": step["qualification_disposition"],
        "failed_predicate": step["failed_predicate"],
        "matched_route_id": (step["matched"] or {}).get("route_id"),
        "bounded_adaptation": step["adaptation"],
        "runtime_probe_required": step["runtime_probe_required"],
    } for step in plan["steps"])
    packet = {
        "schema": "stegverse.sdk-source-evidence-packet/v1",
        "evaluator_id": evaluator_id,
        "source_manifest_sha256": plan["source_manifest_sha256"],
        "requirements_sha256": plan["requirements_sha256"],
        "derived_plan_sha256": plan["derived_plan_sha256"],
        "conditions": conditions,
        "source_qualification_complete": all(
            row["qualification_disposition"] == "SUPPORTED" for row in conditions
        ),
        "execution_authorized": False,
        "authentic_intr_disposition_observed": False,
        "workercoordinator_claim_fence_observed": False,
        ORGANIZATION_RECORD_OBSERVED_FIELD: False,
        "evidence_ceiling": "SOURCE_QUALIFICATION_ONLY",
    }
    return {**packet, "source_packet_sha256": _hash(packet)}


def verify_source_evidence_packet(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
    packet: Mapping[str, Any],
) -> bool:
    if not isinstance(packet, Mapping):
        return False
    try:
        expected = build_source_evidence_packet(
            manifest, requirements, evaluator_id=packet["evaluator_id"]
        )
    except (KeyError, TypeError, ValueError):
        return False
    if LEGACY_SOURCE_PACKET_ORGANIZATION_RECORD_OBSERVED_FIELD in packet:
        # Packets built before the organization-record migration carry the legacy
        # flag name inside their digest; verify them in that legacy form.
        legacy = {key: value for key, value in expected.items() if key != "source_packet_sha256"}
        legacy[LEGACY_SOURCE_PACKET_ORGANIZATION_RECORD_OBSERVED_FIELD] = legacy.pop(
            ORGANIZATION_RECORD_OBSERVED_FIELD
        )
        expected = {**legacy, "source_packet_sha256": _hash(legacy)}
    return dict(packet) == expected
