"""Immutable manifest-to-derived-plan construction for SDK 1.5 source qualification.

The plan is a source artifact only. It binds the original manifest digest, requested
requirements, resolved capability qualification, and bounded adaptation directives.
It does not grant authority, execute work, substitute routes, or claim runtime evidence.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Callable, Mapping, Sequence

from .capability_inventory import (
    DEFAULT_MAX_EVIDENCE_AGE_SECONDS,
    READY,
    EvidenceVerifier,
    classify_node_readiness,
    qualify_requirements,
    utc_now,
)
from .route_resolution import (
    DECLARED_ALTERNATIVE_ROUTES,
    PUBLISHED_ROUTES,
    route_readiness_dependencies,
    route_semantics,
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def derive_execution_plan(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    qualification = qualify_requirements(manifest, requirements)

    steps = []
    for result in qualification["results"]:
        disposition = result["disposition"]
        step = {
            "requirement_id": result["requirement_id"],
            "capability_id": result["capability_id"],
            "requested_route_id": result["requested_route_id"],
            "qualification_disposition": disposition,
            "failed_predicate": result["failed_predicate"],
            "matched": result["matched"],
            "permitted_correction": result["permitted_correction"],
            "adaptation": None,
            "runtime_probe_required": disposition == "PROBE_REQUIRED",
        }
        if disposition == "SUPPORTED":
            step["adaptation"] = {
                "kind": "EXACT_DECLARED_CAPABILITY",
                "route_id": result["matched"]["route_id"] if result["matched"] else None,
                "bounded": True,
            }
        steps.append(step)

    plan_core = {
        "schema": "stegverse.sdk-derived-plan/v1",
        "source_manifest_sha256": qualification["manifest_sha256"],
        "requirements_sha256": _sha256(list(requirements)),
        "steps": tuple(steps),
        "execution_authorized": False,
        "runtime_execution_observed": False,
        "route_substitution_permitted": False,
        "source_evidence_ceiling": "SOURCE_DERIVED_PLAN_ONLY",
    }

    return {
        **plan_core,
        "derived_plan_sha256": _sha256(plan_core),
    }


def verify_plan_lineage(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
    plan: Mapping[str, Any],
) -> bool:
    expected = derive_execution_plan(manifest, requirements)
    # Every field is covered; digest equality alone cannot authenticate siblings.
    return dict(plan) == expected


# --- Manifest readiness qualification (SDK#368) -----------------------------
# Non-authorizing. A READY qualification only says every required node of the
# manifest-selected path had authenticated, invocation-bound, fresh evidence
# supplied for this attempt. It is not a runtime ALLOW.
READINESS_QUALIFICATION_SCHEMA = "stegverse.manifest-readiness-qualification/v1"
INCIDENT_NOTIFICATION_SCHEMA = "stegverse.steghealth-incident-notification-record/v1"
NOTIFICATION_DELIVERY_SCHEMA = "stegverse.incident-notification-delivery/v1"
QUALIFIED_READY = "READY"
NOT_READY = "NOT_READY"
NO_VERIFIED_WORKAROUND = "NO_VERIFIED_WORKAROUND"
VERIFIED_WORKAROUND_AVAILABLE = "VERIFIED_WORKAROUND_AVAILABLE"
INCIDENT_NOTIFICATION_ROUTE_EXTENSION = "stegverse_incident_notification_route"
INCIDENT_NOTIFICATION_CAPABILITY = "incident_notification"
STEGHEALTH_REMEDIATION = {
    "owner_task": "STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001",
    "repository": "StegVerse-Labs/StegHealth",
    "issue": "StegVerse-Labs/StegHealth#51",
    "intake": "EXISTING_STEGHEALTH_FAILURE_MAP_INTAKE",
}
SOURCE_TASK_REF = "StegVerse-org/StegVerse-SDK#368"
REASSESSMENT = {
    "trigger": "NEW_AUTHENTICATED_EVIDENCE_OR_NEW_ATTEMPTED_TRANSITION",
    "passive_polling": False,
    "device_discovery": False,
    "scheduled": False,
}


def _manifest_route_id(manifest: Mapping[str, Any]) -> str:
    extensions = manifest.get("extensions")
    route = extensions.get("stegverse_route") if isinstance(extensions, Mapping) else None
    route_id = route.get("route_id") if isinstance(route, Mapping) else None
    if not isinstance(route_id, str) or not route_id:
        raise ValueError("READINESS_ROUTE_DECLARATION_REQUIRED: manifest declares no stegverse_route.route_id")
    return route_id


def readiness_invocation_binding(
    *,
    manifest_sha256: str,
    attempt_id: str,
    route_id: str,
    processing_capability: str,
    payload_sha256: str,
    source_framework: str,
    source_output_id: str,
) -> str:
    """Digest every evidence record must carry to be bound to this invocation.

    Build and validate the draft first. Payload identity alone does not bind
    authorization, consequence, initiator, return path or workaround selection.
    Evidence for a different draft must never qualify this invocation.
    """
    if not isinstance(attempt_id, str) or not attempt_id.strip():
        raise ValueError("READINESS_ATTEMPT_ID_REQUIRED")
    if (
        not isinstance(manifest_sha256, str)
        or len(manifest_sha256) != 64
        or any(c not in "0123456789abcdef" for c in manifest_sha256)
    ):
        raise ValueError("READINESS_CANONICAL_MANIFEST_DIGEST_REQUIRED")
    return _sha256({
        "schema": "stegverse.readiness-invocation-binding/v2",
        "manifest_sha256": manifest_sha256,
        "attempt_id": attempt_id.strip(),
        "route_id": route_id,
        "processing_capability": processing_capability,
        "payload_sha256": payload_sha256,
        "source_framework": source_framework,
        "source_output_id": source_output_id,
    })


def _invocation_binding_for(manifest: Mapping[str, Any], route_id: str, attempt_id: str) -> str:
    from .manifest_contract import validate_ingress_manifest

    processing = manifest.get("processing") or {}
    hashes = manifest.get("hashes") or {}
    return readiness_invocation_binding(
        manifest_sha256=validate_ingress_manifest(manifest)["canonical_manifest_sha256"],
        attempt_id=attempt_id,
        route_id=route_id,
        processing_capability=str(processing.get("capability")),
        payload_sha256=str(hashes.get("payload_sha256")),
        source_framework=str(manifest.get("source_framework")),
        source_output_id=str(manifest.get("source_output_id")),
    )


def derive_readiness_dag(
    manifest: Mapping[str, Any],
    *,
    route_id: str | None = None,
    published_routes: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Dependency DAG for the manifest-selected path (or one declared alternative)."""
    selected = route_id or _manifest_route_id(manifest)
    nodes = list(route_readiness_dependencies(selected, published_routes=published_routes))
    completion = manifest.get("completion")
    publisher = completion.get("publisher") if isinstance(completion, Mapping) else None
    previous = next((n["node_id"] for n in reversed(nodes) if n["required"]), None)
    nodes.append({
        "node_id": f"{selected}#publisher",
        "role": "publisher",
        "route_id": selected,
        "component": "PUBLISHER" if isinstance(publisher, Mapping) else None,
        "required": isinstance(publisher, Mapping),
        "depends_on": [previous] if previous else [],
        "contract_ref": _sha256({
            "route_id": selected,
            "role": "publisher",
            "package_profile": publisher.get("package_profile") if isinstance(publisher, Mapping) else None,
        }),
        "source_runtime_installed": False,
    })
    return tuple(nodes)


def _qualify_route(
    manifest: Mapping[str, Any],
    route_id: str,
    *,
    attempt_id: str,
    readiness_evidence: Sequence[Mapping[str, Any]],
    evidence_verifier: EvidenceVerifier | None,
    now: datetime,
    max_evidence_age_seconds: int,
    published_routes: Mapping[str, Mapping[str, Any]] | None,
) -> dict[str, Any]:
    binding = _invocation_binding_for(manifest, route_id, attempt_id)
    nodes = [
        classify_node_readiness(
            node, readiness_evidence, invocation_binding_sha256=binding, verifier=evidence_verifier,
            now=now, max_evidence_age_seconds=max_evidence_age_seconds,
        )
        for node in derive_readiness_dag(manifest, route_id=route_id, published_routes=published_routes)
    ]
    failing = [node for node in nodes if node["required"] and node["state"] != READY]
    return {
        "route_id": route_id,
        "invocation_binding_sha256": binding,
        "qualification": NOT_READY if failing else QUALIFIED_READY,
        "nodes": nodes,
        "failing_nodes": failing,
    }


def incident_notification_record(
    node: Mapping[str, Any],
    *,
    manifest_sha256: str,
    attempt_id: str,
    original_evidence: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Idempotent StegHealth incident record for one proven failure. No transport."""
    if not node.get("proven_failure"):
        raise ValueError("INCIDENT_REQUIRES_PROVEN_FAILURE: UNVERIFIED is not a proven failure")
    identity = {
        "task_ref": SOURCE_TASK_REF,
        "node_id": node["node_id"],
        "component": node["component"],
        "route_id": node["route_id"],
        "state": node["state"],
        "failed_predicate": node["failed_predicate"],
        "evidence_sha256": node["evidence_sha256"],
        "attempt_id": attempt_id,
        "manifest_sha256": manifest_sha256,
    }
    idempotency_key = _sha256(identity)
    record = {
        "schema": INCIDENT_NOTIFICATION_SCHEMA,
        "idempotency_key": idempotency_key,
        **identity,
        "observed_at": node["observed_at"],
        "provenance": node["provenance"],
        "evidence_ref": node["evidence_ref"],
        "original_evidence": dict(original_evidence) if original_evidence else None,
        "remediation_owner": dict(STEGHEALTH_REMEDIATION),
        "corrective_task_hint": f"STEGHEALTH_REMEDIATE:{node['role'].upper()}:{node['failed_predicate']}",
        "transport": None,
        "delivered": False,
        "authority_effect": "NONE_RECORD_ONLY",
    }
    record["record_sha256"] = _sha256(record)
    return record


def deliver_incident_notification(
    record: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    deliver: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]] | None = None,
    published_routes: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Delivery is its own transition: FAIL_CLOSED unless a manifest-selected route exists.

    The SDK has no notification transport of its own and never fabricates
    delivery. ``deliver`` is the bound transport of the declared route only.
    """
    routes = PUBLISHED_ROUTES if published_routes is None else published_routes
    out = {
        "schema": NOTIFICATION_DELIVERY_SCHEMA,
        "idempotency_key": record.get("idempotency_key"),
        "record_sha256": record.get("record_sha256"),
        "route_id": None,
        "delivered_by_sdk": False,
        "authority_effect": "NONE_DELIVERY_TRANSITION_REPORT",
    }
    extensions = manifest.get("extensions")
    route_id = extensions.get(INCIDENT_NOTIFICATION_ROUTE_EXTENSION) if isinstance(extensions, Mapping) else None
    route = routes.get(route_id) if isinstance(route_id, str) else None
    if not isinstance(route, Mapping) or route.get("processor_capability") != INCIDENT_NOTIFICATION_CAPABILITY:
        return {**out, "disposition": "FAIL_CLOSED", "failed_predicate": "NOTIFICATION_ROUTE_NOT_RESOLVED",
                "evidence": {"declared_route_id": route_id}}
    out["route_id"] = route_id
    if deliver is None:
        return {**out, "disposition": "FAIL_CLOSED", "failed_predicate": "NOTIFICATION_TRANSPORT_NOT_BOUND",
                "evidence": {"route_id": route_id}}
    try:
        ack = deliver(dict(record), dict(route))
    except Exception as exc:  # the transport's own failure is the delivery evidence
        return {**out, "disposition": "FAIL_CLOSED", "failed_predicate": "NOTIFICATION_DELIVERY_FAILED",
                "evidence": f"{type(exc).__name__}: {exc}"}
    if (
        not isinstance(ack, Mapping)
        or ack.get("idempotency_key") != record.get("idempotency_key")
        or not isinstance(ack.get("ack_ref"), str) or not ack.get("ack_ref")
    ):
        return {**out, "disposition": "FAIL_CLOSED", "failed_predicate": "NOTIFICATION_ACK_BOUND_TO_RECORD",
                "evidence": dict(ack) if isinstance(ack, Mapping) else repr(ack)}
    return {**out, "disposition": "ALLOW", "failed_predicate": None, "evidence": dict(ack)}


def _alternative_candidate(
    manifest: Mapping[str, Any],
    primary_id: str,
    alt_id: str,
    *,
    routes: Mapping[str, Mapping[str, Any]],
    qualify: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    primary = routes[primary_id]
    alt = routes.get(alt_id)
    base = {"route_id": alt_id, "requires_explicit_user_selection": True,
            "new_manifest_digest_required": True, "automatic_substitution_permitted": False}
    if not isinstance(alt, Mapping) or alt.get("processor_capability") != primary.get("processor_capability"):
        return {**base, "candidate_state": "INADMISSIBLE",
                "failed_predicate": "ALTERNATE_ROUTE_PUBLISHED_FOR_SAME_CAPABILITY"}
    want, have = route_semantics(primary), route_semantics(alt)
    for key, predicate in (
        ("custody", "ALTERNATE_ROUTE_CUSTODY_SEMANTICS_PRESENT"),
        ("authorization", "ALTERNATE_ROUTE_AUTHORIZATION_SEMANTICS_PRESENT"),
        ("consequence", "ALTERNATE_ROUTE_CONSEQUENCE_SEMANTICS_PRESENT"),
    ):
        if want[key] and not have[key]:
            return {**base, "candidate_state": "INADMISSIBLE", "failed_predicate": predicate,
                    "missing_functions": [key]}
    degraded = sorted(
        f"{key}:{want[key]}->{have[key]}"
        for key in ("authorization", "custody", "containment", "return")
        if want[key] != have[key]
    )
    qualified = qualify(alt_id)
    verified = qualified["qualification"] == QUALIFIED_READY
    return {
        **base,
        "candidate_state": "VERIFIED_REQUIRES_USER_SELECTION" if verified else "NOT_VERIFIED",
        "failed_predicate": None if verified else "ALTERNATE_ROUTE_INDEPENDENTLY_READY",
        "preserved_functions": sorted(
            key for key in ("authorization", "custody", "consequence", "containment", "return")
            if want[key] == have[key]
        ),
        "degraded_functions": degraded,
        "semantics_changed": bool(degraded),
        "security_authority_custody_equivalent": not degraded,
        "expected_user_visible_difference": degraded,
        "qualification": qualified,
    }


def enumerate_workarounds(
    manifest: Mapping[str, Any],
    *,
    qualify: Callable[[str], dict[str, Any]],
    alternative_routes: Sequence[str] = (),
    published_routes: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Enumerate only declared alternatives; never select one."""
    routes = PUBLISHED_ROUTES if published_routes is None else published_routes
    primary_id = _manifest_route_id(manifest)
    declared = list(DECLARED_ALTERNATIVE_ROUTES.get(primary_id, ()))
    declared += [route for route in alternative_routes if route not in declared and route != primary_id]
    candidates = [
        _alternative_candidate(manifest, primary_id, alt_id, routes=routes, qualify=qualify)
        for alt_id in declared
    ]
    verified = sorted(
        (c for c in candidates if c["candidate_state"] == "VERIFIED_REQUIRES_USER_SELECTION"),
        key=lambda c: (len(c["degraded_functions"]), c["route_id"]),
    )
    out = {
        "state": VERIFIED_WORKAROUND_AVAILABLE if verified else NO_VERIFIED_WORKAROUND,
        "declared_alternative_routes": declared,
        "candidates": candidates,
        "preferred_verified_route_id": verified[0]["route_id"] if verified else None,
        "automatic_selection_permitted": False,
        "selection_requires": ["EXPLICIT_USER_SELECTION", "NEW_MANIFEST_DIGEST", "FRESH_READINESS_QUALIFICATION"],
    }
    if not verified:
        out["remediation_reference"] = dict(STEGHEALTH_REMEDIATION)
    return out


def qualify_manifest_readiness(
    manifest: Mapping[str, Any],
    *,
    attempt_id: str,
    readiness_evidence: Sequence[Mapping[str, Any]] = (),
    evidence_verifier: EvidenceVerifier | None = None,
    now: datetime | None = None,
    max_evidence_age_seconds: int = DEFAULT_MAX_EVIDENCE_AGE_SECONDS,
    alternative_routes: Sequence[str] = (),
    published_routes: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Qualify the manifest-selected path. Non-authorizing; never dispatches."""
    from .manifest_contract import validate_ingress_manifest

    manifest_sha256 = validate_ingress_manifest(manifest)["canonical_manifest_sha256"]
    observed_now = now or utc_now()
    evidence = [dict(record) for record in readiness_evidence if isinstance(record, Mapping)]
    route_id = _manifest_route_id(manifest)

    def qualify(selected: str) -> dict[str, Any]:
        return _qualify_route(
            manifest, selected, attempt_id=attempt_id, readiness_evidence=evidence,
            evidence_verifier=evidence_verifier, now=observed_now,
            max_evidence_age_seconds=max_evidence_age_seconds, published_routes=published_routes,
        )

    primary = qualify(route_id)
    ready = primary["qualification"] == QUALIFIED_READY
    by_sha = {_sha256(record): record for record in evidence}
    incidents = [
        incident_notification_record(
            node, manifest_sha256=manifest_sha256, attempt_id=attempt_id,
            original_evidence=by_sha.get(node["evidence_sha256"]),
        )
        for node in primary["failing_nodes"] if node["proven_failure"]
    ]
    qualification = {
        "schema": READINESS_QUALIFICATION_SCHEMA,
        "manifest_sha256": manifest_sha256,
        "attempt_id": attempt_id,
        "route_id": route_id,
        "invocation_binding_sha256": primary["invocation_binding_sha256"],
        "evaluated_at": observed_now.isoformat().replace("+00:00", "Z"),
        "qualification": primary["qualification"],
        "disposition": "ALLOW" if ready else "FAIL_CLOSED",
        "failed_predicate": None if ready else "REQUIRED_NODES_READY",
        "disposition_scope": "READINESS_QUALIFICATION_ONLY",
        "nodes": primary["nodes"],
        "failing_nodes": primary["failing_nodes"],
        "executable": ready,
        "draft_preserved": True,
        "workarounds": None if ready else enumerate_workarounds(
            manifest, qualify=qualify, alternative_routes=alternative_routes, published_routes=published_routes,
        ),
        "incident_notifications": incidents,
        "incident_notification_delivery": [
            deliver_incident_notification(record, manifest=manifest, published_routes=published_routes)
            for record in incidents
        ],
        "reassessment": dict(REASSESSMENT),
        "execution_authorized": False,
        "runtime_allow_claimed": False,
        "route_substitution_permitted": False,
        "authority_effect": "NONE_QUALIFICATION_ONLY",
    }
    qualification["qualification_sha256"] = _sha256(qualification)
    return qualification


def require_ready_qualification(manifest: Mapping[str, Any], qualification: Mapping[str, Any]) -> None:
    """Refuse dispatch unless this exact manifest carries a READY qualification."""
    from .manifest_contract import validate_ingress_manifest

    digest = validate_ingress_manifest(manifest)["canonical_manifest_sha256"]
    if qualification.get("manifest_sha256") != digest:
        raise ValueError("READINESS_QUALIFICATION_MANIFEST_DIGEST_MISMATCH")
    body = {key: value for key, value in qualification.items() if key != "qualification_sha256"}
    if qualification.get("qualification_sha256") != _sha256(body):
        raise ValueError("READINESS_QUALIFICATION_DIGEST_MISMATCH")
    if qualification.get("qualification") != QUALIFIED_READY or qualification.get("executable") is not True:
        raise ValueError("MANIFEST_NOT_READY: required nodes are not READY")
