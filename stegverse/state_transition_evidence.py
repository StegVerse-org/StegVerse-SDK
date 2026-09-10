"""Provider-neutral state-transition evidence for inter-Entity manifests.

The profile records known applicable predicates, ambiguity, and discovered
unknowns without changing the universal ingress-manifest class. It is evidence,
not authority. A genuinely unknown-unknown cannot be represented before it is
discovered; once discovered it becomes known state and an unresolved discovery
forces PROBE_REQUIRED until durable evidence resolves it.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest

STATE_TRANSITION_PROFILE = "stegverse.state-transition-evidence.v1"
READINESS_READY = "READY"
READINESS_PROBE_REQUIRED = "PROBE_REQUIRED"

_PREDICATE_APPLICABILITY = {"APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"}
_PREDICATE_EVIDENCE = {"SATISFIED", "UNRESOLVED", "NOT_REQUIRED"}
_RESOLUTION_STATUS = {"OPEN", "RESOLVED"}


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise ValueError(f"state_transition.{key} is required")
    return item.strip()


def _normalize_predicates(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("state_transition.applicable_predicates must be an array")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, Mapping):
            raise ValueError(f"state_transition.applicable_predicates[{index}] must be an object")
        predicate_id = raw.get("predicate_id")
        if not isinstance(predicate_id, str) or not predicate_id.strip():
            raise ValueError(f"state_transition.applicable_predicates[{index}].predicate_id is required")
        predicate_id = predicate_id.strip()
        if predicate_id in seen:
            raise ValueError(f"duplicate state-transition predicate: {predicate_id}")
        seen.add(predicate_id)
        applicability = raw.get("applicability")
        evidence_status = raw.get("evidence_status")
        if applicability not in _PREDICATE_APPLICABILITY:
            raise ValueError(f"invalid applicability for predicate {predicate_id}")
        if evidence_status not in _PREDICATE_EVIDENCE:
            raise ValueError(f"invalid evidence_status for predicate {predicate_id}")
        if applicability == "APPLICABLE" and evidence_status == "NOT_REQUIRED":
            raise ValueError(f"applicable predicate {predicate_id} cannot use NOT_REQUIRED")
        if applicability == "NOT_APPLICABLE" and evidence_status != "NOT_REQUIRED":
            raise ValueError(f"not-applicable predicate {predicate_id} must use NOT_REQUIRED")
        item = dict(raw)
        item["predicate_id"] = predicate_id
        normalized.append(item)
    return normalized


def _normalize_resolution_items(value: Any, field: str, id_field: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"state_transition.{field} must be an array")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, Mapping):
            raise ValueError(f"state_transition.{field}[{index}] must be an object")
        item_id = raw.get(id_field)
        status = raw.get("status")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"state_transition.{field}[{index}].{id_field} is required")
        item_id = item_id.strip()
        if item_id in seen:
            raise ValueError(f"duplicate state_transition.{field} id: {item_id}")
        seen.add(item_id)
        if status not in _RESOLUTION_STATUS:
            raise ValueError(f"state_transition.{field}[{index}].status must be OPEN or RESOLVED")
        item = dict(raw)
        item[id_field] = item_id
        normalized.append(item)
    return normalized


def normalize_state_transition_evidence(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate evidence and derive fail-closed readiness.

    READY is permitted only when every known applicable predicate is satisfied,
    no predicate has unknown applicability, and all recorded ambiguity/discovered
    unknown items are resolved. The caller cannot override that derivation.
    """
    if not isinstance(value, Mapping):
        raise ValueError("state_transition must be an object")
    if value.get("profile") != STATE_TRANSITION_PROFILE:
        raise ValueError(f"state_transition.profile must be {STATE_TRANSITION_PROFILE}")

    normalized = deepcopy(dict(value))
    normalized["transition_id"] = _required_text(value, "transition_id")
    normalized["state_domain"] = _required_text(value, "state_domain")
    normalized["new_state_ref"] = _required_text(value, "new_state_ref")
    normalized["change_type"] = _required_text(value, "change_type")

    prior_state_ref = value.get("prior_state_ref")
    if prior_state_ref is not None and (not isinstance(prior_state_ref, str) or not prior_state_ref.strip()):
        raise ValueError("state_transition.prior_state_ref must be null or a non-empty string")
    normalized["prior_state_ref"] = prior_state_ref.strip() if isinstance(prior_state_ref, str) else None

    predicates = _normalize_predicates(value.get("applicable_predicates"))
    ambiguities = _normalize_resolution_items(value.get("ambiguities"), "ambiguities", "ambiguity_id")
    discoveries = _normalize_resolution_items(
        value.get("discovered_unknowns"), "discovered_unknowns", "unknown_id"
    )
    normalized["applicable_predicates"] = predicates
    normalized["ambiguities"] = ambiguities
    normalized["discovered_unknowns"] = discoveries

    probe_reasons: list[str] = []
    for predicate in predicates:
        if predicate["applicability"] == "UNKNOWN":
            probe_reasons.append(f"predicate:{predicate['predicate_id']}:applicability_unknown")
        elif predicate["applicability"] == "APPLICABLE" and predicate["evidence_status"] != "SATISFIED":
            probe_reasons.append(f"predicate:{predicate['predicate_id']}:evidence_unresolved")
    probe_reasons.extend(
        f"ambiguity:{item['ambiguity_id']}:open" for item in ambiguities if item["status"] == "OPEN"
    )
    probe_reasons.extend(
        f"discovered_unknown:{item['unknown_id']}:open" for item in discoveries if item["status"] == "OPEN"
    )

    derived = READINESS_PROBE_REQUIRED if probe_reasons else READINESS_READY
    claimed = value.get("readiness")
    if claimed is not None and claimed not in {READINESS_READY, READINESS_PROBE_REQUIRED}:
        raise ValueError("state_transition.readiness must be READY or PROBE_REQUIRED")
    if claimed is not None and claimed != derived:
        raise ValueError(
            f"state_transition.readiness {claimed} contradicts derived readiness {derived}"
        )

    normalized["readiness"] = derived
    normalized["probe_reasons"] = probe_reasons
    normalized["evidence_grants_authority"] = False
    normalized["unknown_unknown_policy"] = "ENFORCE_AFTER_DISCOVERY_AS_KNOWN_STATE"
    return normalized


def attach_state_transition_evidence(
    manifest: Mapping[str, Any], state_transition: Mapping[str, Any]
) -> dict[str, Any]:
    """Attach transition evidence under extensions without changing manifest class."""
    output = deepcopy(dict(manifest))
    extensions = output.get("extensions")
    if not isinstance(extensions, Mapping):
        raise ValueError("manifest extensions are required before state-transition attachment")
    output["extensions"] = deepcopy(dict(extensions))
    output["extensions"]["stegverse_state_transition"] = normalize_state_transition_evidence(
        state_transition
    )
    validate_ingress_manifest(output)
    return output


__all__ = [
    "READINESS_PROBE_REQUIRED",
    "READINESS_READY",
    "STATE_TRANSITION_PROFILE",
    "attach_state_transition_evidence",
    "normalize_state_transition_evidence",
]
