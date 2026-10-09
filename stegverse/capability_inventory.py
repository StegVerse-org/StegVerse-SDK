"""Source-only installed-capability discovery and requirement qualification.

This module derives capability inventory from the canonical published SDK route table.
It never grants execution authority, substitutes a route, or treats source installation
as proof of an observed runtime transition.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence

from .route_resolution import PUBLISHED_ROUTES

DISPOSITIONS = {
    "SUPPORTED",
    "MISSING_INPUT",
    "UNSUPPORTED",
    "PROBE_REQUIRED",
    "VERSION_INCOMPATIBLE",
}

def _sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def installed_capability_inventory() -> tuple[dict[str, Any], ...]:
    rows = []
    for route_id, route in sorted(PUBLISHED_ROUTES.items()):
        rows.append({
            "capability_id": route["processor_capability"],
            "route_id": route_id,
            "runtime_binding": route.get("runtime_binding"),
            "runtime_installed": route.get("runtime_installed") is True,
            "lane_class": route.get("lane_class"),
            "routing_surface": route.get("routing_surface"),
            "containment": route.get("containment"),
            "external_consequence_enabled": route.get("external_consequence_enabled") is True,
            "execution_authorized": False,
            "route_substitution_permitted": False,
            "evidence_ceiling": "SOURCE_DECLARATION_ONLY",
        })
    return tuple(rows)

def qualify_requirements(
    manifest: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    inventory = installed_capability_inventory()
    by_capability: dict[str, list[dict[str, Any]]] = {}
    for row in inventory:
        by_capability.setdefault(row["capability_id"], []).append(row)

    results = []
    for req in requirements:
        req_id = req.get("requirement_id")
        capability = req.get("capability_id")
        route_id = req.get("route_id")
        required_inputs = tuple(req.get("required_inputs") or ())
        missing = [name for name in required_inputs if name not in manifest]
        disposition = "SUPPORTED"
        predicate = "INSTALLED_CAPABILITY_AND_ROUTE_MATCH"
        correction = None
        matched = None

        if missing:
            disposition = "MISSING_INPUT"
            predicate = "REQUIRED_INPUT_PRESENT"
            correction = {"supply_inputs": missing}
        elif capability not in by_capability:
            disposition = "UNSUPPORTED"
            predicate = "CAPABILITY_INSTALLED"
            correction = {"request_supported_capability": sorted(by_capability)}
        else:
            candidates = by_capability[capability]
            if route_id is not None:
                matched = next((row for row in candidates if row["route_id"] == route_id), None)
                if matched is None:
                    disposition = "UNSUPPORTED"
                    predicate = "EXACT_ROUTE_INSTALLED"
                    correction = {"supported_routes": sorted(row["route_id"] for row in candidates)}
            else:
                matched = candidates[0]

        if disposition == "SUPPORTED" and matched is not None and not matched["runtime_installed"]:
            disposition = "UNSUPPORTED"
            predicate = "RUNTIME_BINDING_INSTALLED"
            correction = {"install_declared_runtime_binding": matched["route_id"]}

        if disposition == "SUPPORTED" and req.get("version_compatible") is False:
            disposition = "VERSION_INCOMPATIBLE"
            predicate = "REQUESTED_VERSION_COMPATIBLE"
            correction = {"use_compatible_version": True}
        elif disposition == "SUPPORTED" and req.get("authentic_runtime_evidence_required") is True:
            disposition = "PROBE_REQUIRED"
            predicate = "AUTHENTIC_RUNTIME_EVIDENCE_OBSERVED"
            correction = {"invoke_existing_manifest_directed_transition": True}

        results.append({
            "requirement_id": req_id,
            "capability_id": capability,
            "requested_route_id": route_id,
            "disposition": disposition,
            "failed_predicate": None if disposition == "SUPPORTED" else predicate,
            "matched": matched,
            "permitted_correction": correction,
        })

    return {
        "schema": "stegverse.sdk-capability-qualification/v1",
        "manifest_sha256": _sha256(manifest),
        "inventory": inventory,
        "results": tuple(results),
        "execution_authorized": False,
        "route_substitution_permitted": False,
    }


# --- Per-node readiness evidence (SDK#368) ----------------------------------
# A node is READY only on authenticated, invocation-bound, fresh evidence that
# the caller supplies. The SDK does not probe, poll or discover devices, and it
# never treats source installation as readiness.
READY = "READY"
OFFLINE = "OFFLINE"
UNVERIFIED = "UNVERIFIED"
INCOMPATIBLE = "INCOMPATIBLE"
NOT_REQUIRED = "NOT_REQUIRED"
NODE_STATES = (READY, OFFLINE, UNVERIFIED, INCOMPATIBLE, NOT_REQUIRED)
PROVEN_FAILURE_STATES = frozenset({OFFLINE, INCOMPATIBLE})

READINESS_EVIDENCE_SCHEMA = "stegverse.component-readiness-evidence/v1"
ATTEMPTED_TRANSITION = "ATTEMPTED_TRANSITION"
INVOCATION_PROBE = "INVOCATION_PROBE"
OBSERVATION_KINDS = (ATTEMPTED_TRANSITION, INVOCATION_PROBE)
OPERATIONAL = "OPERATIONAL"
NON_OPERATIONAL = "NON_OPERATIONAL"
DEFAULT_MAX_EVIDENCE_AGE_SECONDS = 300
_EVIDENCE_TEXT_FIELDS = (
    "node_id", "contract_ref", "invocation_binding_sha256", "observed_at", "provenance", "evidence_ref",
)

EvidenceVerifier = Callable[[Mapping[str, Any]], bool]


def readiness_evidence_signing_bytes(evidence: Mapping[str, Any]) -> bytes:
    """Canonical bytes covered by an evidence authenticator (all fields but itself)."""
    body = {key: value for key, value in evidence.items() if key != "authenticator"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _key_bytes(key: bytes | str) -> bytes:
    return key if isinstance(key, bytes) else bytes.fromhex(key)


def sign_readiness_evidence(evidence: Mapping[str, Any], *, key_id: str, key: bytes | str) -> dict[str, Any]:
    """Attach an HMAC-SHA256 authenticator; used by the evidence producer, not the SDK gate."""
    signed = {k: v for k, v in evidence.items() if k != "authenticator"}
    mac = hmac.new(_key_bytes(key), readiness_evidence_signing_bytes(signed), hashlib.sha256).hexdigest()
    signed["authenticator"] = {"scheme": "HMAC-SHA256", "key_id": key_id, "mac": mac}
    return signed


def hmac_evidence_verifier(keys: Mapping[str, bytes | str]) -> EvidenceVerifier:
    """Verifier over caller-configured evidence keys (stdlib HMAC; no new dependency)."""
    trusted = {key_id: _key_bytes(key) for key_id, key in keys.items()}

    def verify(evidence: Mapping[str, Any]) -> bool:
        auth = evidence.get("authenticator")
        if not isinstance(auth, Mapping) or auth.get("scheme") != "HMAC-SHA256":
            return False
        key = trusted.get(auth.get("key_id"))
        mac = auth.get("mac")
        if key is None or not isinstance(mac, str):
            return False
        expected = hmac.new(key, readiness_evidence_signing_bytes(evidence), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, mac)

    return verify


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _node_result(node: Mapping[str, Any], state: str, predicate: str | None, evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        "node_id": node["node_id"],
        "role": node["role"],
        "route_id": node["route_id"],
        "component": node["component"],
        "required": node["required"],
        "depends_on": list(node["depends_on"]),
        "contract_ref": node["contract_ref"],
        "state": state,
        "failed_predicate": predicate,
        "observed_at": evidence.get("observed_at") if evidence else None,
        "provenance": evidence.get("provenance") if evidence else None,
        "evidence_ref": evidence.get("evidence_ref") if evidence else None,
        "evidence_sha256": _sha256(dict(evidence)) if evidence else None,
        "proven_failure": state in PROVEN_FAILURE_STATES,
        "source_runtime_installed": node.get("source_runtime_installed") is True,
        "runtime_installed_is_readiness": False,
    }


def classify_node_readiness(
    node: Mapping[str, Any],
    evidence_records: Sequence[Mapping[str, Any]],
    *,
    invocation_binding_sha256: str,
    verifier: EvidenceVerifier | None,
    now: datetime,
    max_evidence_age_seconds: int = DEFAULT_MAX_EVIDENCE_AGE_SECONDS,
) -> dict[str, Any]:
    """Classify one dependency node from the most recent evidence naming it.

    Absence of evidence is UNVERIFIED, never OFFLINE. OFFLINE requires an
    authenticated attempted-transition record. A newer unauthenticated record
    masks an older valid one, which fails closed rather than open.
    """
    if not node.get("required"):
        return _node_result(node, NOT_REQUIRED, None, None)
    candidates = [
        record for record in evidence_records
        if isinstance(record, Mapping) and record.get("node_id") == node["node_id"]
    ]
    if not candidates:
        return _node_result(node, UNVERIFIED, "AUTHENTICATED_INVOCATION_BOUND_EVIDENCE_PRESENT", None)
    evidence = max(candidates, key=lambda record: str(record.get("observed_at") or ""))
    if (
        evidence.get("schema") != READINESS_EVIDENCE_SCHEMA
        or any(not isinstance(evidence.get(field), str) or not evidence.get(field) for field in _EVIDENCE_TEXT_FIELDS)
        or evidence.get("observation_kind") not in OBSERVATION_KINDS
        or evidence.get("observed_state") not in (OPERATIONAL, NON_OPERATIONAL)
    ):
        return _node_result(node, UNVERIFIED, "EVIDENCE_SCHEMA_VALID", evidence)
    if verifier is None or verifier(evidence) is not True:
        return _node_result(node, UNVERIFIED, "EVIDENCE_AUTHENTICATED", evidence)
    if evidence["invocation_binding_sha256"] != invocation_binding_sha256:
        return _node_result(node, UNVERIFIED, "EVIDENCE_INVOCATION_BOUND", evidence)
    observed = _parse_time(evidence["observed_at"])
    if observed is None or observed > now or (now - observed).total_seconds() > max_evidence_age_seconds:
        return _node_result(node, UNVERIFIED, "EVIDENCE_FRESH", evidence)
    if evidence["contract_ref"] != node["contract_ref"]:
        return _node_result(node, INCOMPATIBLE, "COMPONENT_CONTRACT_COMPATIBLE", evidence)
    if evidence["observed_state"] == NON_OPERATIONAL:
        if evidence["observation_kind"] != ATTEMPTED_TRANSITION:
            return _node_result(node, UNVERIFIED, "OFFLINE_REQUIRES_ATTEMPTED_TRANSITION", evidence)
        return _node_result(node, OFFLINE, "COMPONENT_OPERATIONAL_ON_ATTEMPTED_TRANSITION", evidence)
    return _node_result(node, READY, None, evidence)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
