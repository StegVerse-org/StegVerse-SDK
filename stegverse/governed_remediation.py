"""Perform a governed RESUBMIT or RE-MANIFEST after a non-ALLOW.

Every non-ALLOW follows one path (StegVerse-SDK#368, issuecomment-6134521056):
the DENY or FAIL_CLOSED is retained; StegHealer maps the failure to RESUBMIT
(unchanged valid manifest; the error was at the denying site) or RE-MANIFEST
(corrected envelope through the Manifest Builder); that classification is
decided through the organization ``.github`` governance interfaces, and the
decision returns to the SDK. Only then does the SDK act, as a fresh governed
attempt with its own disposition.

The decision travels the existing governance loop: a ``governance`` manifest
whose candidate carries the Healer classification goes out through the
organization's egress, the deciding organization answers, and
``governance_decision_return`` hands the organization's result back. This
module checks that the result is an ALLOW for exactly that candidate, bound to
exactly the retained non-ALLOW and its request, then prepares the new handoff.
It contacts nothing, mints no receipt and grants no admission: the handoff is
the start of a new attempt, which receives its own disposition.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_state_transition_runtime import (
    build_intr_handoff,
    derive_execution_request,
    validate_runtime_result,
)
from .route_resolution import canonical_sha256

SCHEMA = "stegverse.sdk.governed-remediation-attempt/v1"
CLASSIFICATION_SCHEMA = "stegverse.healer.sdk-deny-classification/v1"
CANDIDATE_ACTOR_CLASS = "governed_remediation"
CANDIDATE_SCOPE = "sdk_non_allow_remediation"
ACTIONS = ("RESUBMIT", "RE_MANIFEST")


def _request_document_sha256(request: Mapping[str, Any]) -> str:
    return canonical_sha256(dict(request))


def _wire_manifest_sha256(request: Mapping[str, Any]) -> str:
    # Requests derived before SDK #323 carry no wire_manifest_sha256 field; their
    # wire identity is the digest of the canonical_manifest they hold (53a6749).
    declared = request.get("wire_manifest_sha256")
    if isinstance(declared, str) and declared:
        return declared
    original = request.get("canonical_manifest")
    if not isinstance(original, Mapping):
        raise ValueError("REMEDIATION_REQUEST_WIRE_IDENTITY_REQUIRED")
    return canonical_sha256(dict(original))


def _bind_classification(classification: Mapping[str, Any], request: Mapping[str, Any]) -> str:
    if classification.get("schema") != CLASSIFICATION_SCHEMA:
        raise ValueError("REMEDIATION_CLASSIFICATION_SCHEMA_REQUIRED")
    if (classification.get("governance_disposition") != "NOT_EVALUATED"
            or classification.get("execution_authority_granted") is not False
            or classification.get("authority_effect") != "NONE_CLASSIFICATION_ONLY"):
        raise ValueError("REMEDIATION_CLASSIFICATION_AUTHORITY_ESCALATION")
    if classification.get("original_request_sha256") != request.get("request_sha256"):
        raise ValueError("REMEDIATION_CLASSIFICATION_BINDING_MISMATCH:original_request_sha256")
    if classification.get("original_request_document_sha256") != _request_document_sha256(request):
        raise ValueError("REMEDIATION_CLASSIFICATION_BINDING_MISMATCH:original_request_document_sha256")
    if classification.get("original_wire_manifest_sha256") != _wire_manifest_sha256(request):
        raise ValueError("REMEDIATION_CLASSIFICATION_BINDING_MISMATCH:original_wire_manifest_sha256")
    action = classification.get("suggested_action")
    if action not in ACTIONS:
        raise ValueError("REMEDIATION_ACTION_NOT_MAPPED")
    return action


def remediation_candidate(
    classification: Mapping[str, Any],
    original_request: Mapping[str, Any],
    non_allow: Mapping[str, Any],
) -> dict[str, Any]:
    """The governance candidate the deciding organization rules on.

    It names the mapped action and binds it to the exact retained non-ALLOW, the
    request it answered and the Healer classification. A governance manifest
    carrying it is built with the existing Manifest Builder (process
    ``governance``); nothing here decides it.
    """
    if non_allow.get("disposition") not in ("DENY", "FAIL_CLOSED"):
        raise ValueError("REMEDIATION_REQUIRES_NON_ALLOW")
    action = _bind_classification(classification, original_request)
    return {
        "actor_class": CANDIDATE_ACTOR_CLASS,
        "action": action,
        "target": original_request["request_sha256"],
        "scope": CANDIDATE_SCOPE,
        "parameters": {
            "external_side_effect": False,
            "original_request_sha256": original_request["request_sha256"],
            "original_request_document_sha256": _request_document_sha256(original_request),
            "original_wire_manifest_sha256": _wire_manifest_sha256(original_request),
            "original_non_allow_sha256": canonical_sha256(dict(non_allow)),
            "original_non_allow_disposition": non_allow["disposition"],
            "healer_classification_sha256": canonical_sha256(dict(classification)),
            "healer_classification": deepcopy(dict(classification)),
        },
    }


def perform_governed_remediation(
    original_manifest: Mapping[str, Any],
    original_request: Mapping[str, Any],
    non_allow: Mapping[str, Any],
    governance_manifest: Mapping[str, Any],
    governance_result: Mapping[str, Any],
    organization_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Act on a returned governance decision for a mapped remediation.

    ``governance_result`` is the organization's result for ``governance_manifest``
    as ``governance_decision_return`` hands it back. Anything but an ALLOW for
    the exact candidate leaves the original non-ALLOW standing: the return is
    reported, and no new attempt is prepared.
    """
    checked_original = validate_runtime_result(non_allow, original_request)
    if checked_original.get("disposition") not in ("DENY", "FAIL_CLOSED"):
        raise ValueError("REMEDIATION_REQUIRES_NON_ALLOW")
    governance_request = derive_execution_request(governance_manifest, organization_boundary)
    if governance_request.get("processing_capability") != "governance":
        raise ValueError("REMEDIATION_DECISION_REQUIRES_GOVERNANCE_MANIFEST")
    decision = validate_runtime_result(governance_result, governance_request)

    candidate = governance_manifest.get("candidate")
    if not isinstance(candidate, Mapping) or candidate.get("actor_class") != CANDIDATE_ACTOR_CLASS \
            or candidate.get("scope") != CANDIDATE_SCOPE:
        raise ValueError("REMEDIATION_DECISION_IS_NOT_FOR_A_REMEDIATION_CANDIDATE")
    parameters = candidate.get("parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError("REMEDIATION_CANDIDATE_PARAMETERS_REQUIRED")
    classification = parameters.get("healer_classification")
    if not isinstance(classification, Mapping):
        raise ValueError("REMEDIATION_CANDIDATE_CLASSIFICATION_REQUIRED")
    expected = remediation_candidate(classification, original_request, non_allow)
    if dict(candidate) != expected:
        raise ValueError("REMEDIATION_CANDIDATE_BINDING_MISMATCH")
    action = expected["action"]

    base = {
        "schema": SCHEMA,
        "action": action,
        "original_request_sha256": original_request["request_sha256"],
        "original_non_allow_sha256": parameters["original_non_allow_sha256"],
        "original_disposition": dict(checked_original),
        "governance_request_sha256": governance_request["request_sha256"],
        "governance_disposition": decision.get("disposition"),
        "authority_effect": "NONE_MANIFEST_HANDOFF_ONLY",
    }
    if decision.get("disposition") != "ALLOW":
        # A governance DENY or FAIL_CLOSED of the remediation leaves the original
        # non-ALLOW in place; it is not retried here.
        return {**base, "state": "REMEDIATION_NOT_AUTHORIZED", "disposition": decision.get("disposition"),
                "failed_predicate": decision.get("failed_predicate") or "REMEDIATION_NOT_AUTHORIZED",
                "handoff": None, "remediated_request": None}

    if action == "RESUBMIT":
        # The manifest was valid; the failure was at the denying site. The same
        # manifest is submitted again, through the same boundary, to the same
        # destination, as a new governed attempt.
        remediated = derive_execution_request(original_manifest, organization_boundary)
        if remediated["wire_manifest_sha256"] != _wire_manifest_sha256(original_request):
            raise ValueError("RESUBMIT_IS_NOT_THE_ORIGINAL_SUBMISSION:wire_manifest_sha256")
        for key in ("canonical_manifest_sha256", "manifest_declared_destination"):
            if remediated.get(key) != original_request.get(key):
                raise ValueError(f"RESUBMIT_IS_NOT_THE_ORIGINAL_SUBMISSION:{key}")
    else:
        from .manifest_builder import correct_manifest_binding_deny
        remediated = correct_manifest_binding_deny(
            original_manifest, original_request, checked_original, organization_boundary)

    handoff = build_intr_handoff(remediated)
    allowed = handoff.get("disposition") == "ALLOW"
    return {
        **base,
        "state": "GOVERNED_REMEDIATION_HANDED_OFF" if allowed else "FAIL_CLOSED",
        "disposition": "ALLOW" if allowed else "FAIL_CLOSED",
        "failed_predicate": None if allowed else (handoff.get("failed_predicate") or "REMEDIATION_HANDOFF_NOT_ALLOWED"),
        "handoff": handoff,
        "remediated_request": dict(remediated),
    }


__all__ = ["perform_governed_remediation", "remediation_candidate", "SCHEMA"]
