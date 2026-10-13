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

from .governance_return_evidence import verify_governance_decision_return
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


PREFLIGHT_SCHEMA = "stegverse.organization.remediation-return-preflight/v1"
REMEDIATION_TASK = "STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001"
REMEDIATION_GOVERNANCE_REQUEST_SCHEMA = "stegverse.remediation-governance-request/v1"


def remediation_governance_manifest(
    classification: Mapping[str, Any],
    original_request: Mapping[str, Any],
    non_allow: Mapping[str, Any],
    *,
    preflight: Mapping[str, Any],
    evidence_refs: list[str],
    organization_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """The governance manifest that asks the deciding organization to rule on a mapped remediation.

    Built by the existing Manifest Builder (process ``governance``) for the existing
    governance route; no second authorization mechanism. It carries only what is
    evidenced: the remediation candidate bound to the retained non-ALLOW, the
    organization's non-authorizing preflight, and the receipt references the
    lineage rests on. No authority is asserted that the evidence does not carry:
    actor authority, delegation and permission are not claimed, and an
    authenticated grant and approval are declared as missing inputs. StegCore
    decides on what is present, and the SDK acts only on a read-back ALLOW
    (``perform_governed_remediation``).
    """
    from .manifest_builder import build_manifest

    candidate = remediation_candidate(classification, original_request, non_allow)
    if (preflight.get("schema") != PREFLIGHT_SCHEMA
            or preflight.get("proposed_action") != candidate["action"]
            or preflight.get("original_request_sha256") != original_request.get("request_sha256")
            or preflight.get("authority_effect") != "NONE_PREFLIGHT_ONLY"
            or preflight.get("execution_authority_granted") is not False):
        raise ValueError("REMEDIATION_PREFLIGHT_NOT_BOUND_TO_THIS_CANDIDATE")
    refs = [ref for ref in evidence_refs if isinstance(ref, str) and ref]
    if not refs:
        raise ValueError("REMEDIATION_LINEAGE_EVIDENCE_REQUIRED")
    payload = {
        "schema": REMEDIATION_GOVERNANCE_REQUEST_SCHEMA,
        "request_id": "REMEDIATION-" + canonical_sha256(candidate)[:24],
        "task_id": REMEDIATION_TASK,
        "original_request_sha256": original_request["request_sha256"],
        "original_non_allow_sha256": candidate["parameters"]["original_non_allow_sha256"],
        "healer_classification_sha256": candidate["parameters"]["healer_classification_sha256"],
        "preflight_sha256": canonical_sha256(dict(preflight)),
        "evidence_refs": refs,
        "request_granted_authority": False,
        "authority_effect": "NONE_REQUEST_ONLY",
    }
    payload_hash = canonical_sha256(payload)
    request = {
        "candidate": candidate,
        "judgment": {"refusal_available": True, "operator_recoverability": "available",
                     "workload_state": "supported", "time_pressure": "normal",
                     "isolation_state": "supported", "evidence_refs": refs},
        "signal": {"admitted_signal_refs": refs, "excluded_signal_refs": [], "transformations": [],
                   "missing_inputs": ["authenticated_current_grant", "approval"],
                   "uncertainty_state": "bounded",
                   "reference_state_hash": payload_hash, "expected_reference_state_hash": payload_hash,
                   "reconstruction_available": True, "transformation_provenance_complete": True},
        "execution": {"actor_authority_current": False, "policy_current": True, "delegation_current": False,
                      "evidence_current": True, "affected_entity_conditions_represented": True,
                      "recoverability_profile": "recoverable", "validity_window_open": True,
                      "policy_ref": "canonical-task-registry:" + REMEDIATION_TASK,
                      "delegation_ref": None, "evidence_refs": refs},
        "capability": {"allowed": True},
        "continuity": {"required": True},
        "approval": {"required": True},
        "permission_present": False,
    }
    return build_manifest(
        data=payload, source_framework="StegVerse-Labs/StegVerse-Healer",
        source_output_id=payload["request_id"], processor_request=request, process="governance",
        return_depth="result+evidence",
        created_at=(original_request.get("canonical_manifest") or {}).get("created_at"),
        declared_intent="Decide the mapped remediation of a retained non-ALLOW.",
        requested_consequence="On a read-back ALLOW only, the SDK performs the mapped RESUBMIT or RE-MANIFEST as a new governed attempt.",
        publisher_required=False, initiator_class="canonical_task", initiator_ref=REMEDIATION_TASK)


def perform_governed_remediation(
    original_manifest: Mapping[str, Any],
    original_request: Mapping[str, Any],
    non_allow: Mapping[str, Any],
    governance_manifest: Mapping[str, Any],
    governance_result: Mapping[str, Any],
    organization_boundary: Mapping[str, Any] | None = None,
    *,
    decision_return_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Act on a returned governance decision for a mapped remediation.

    ``governance_result`` is the organization's result for ``governance_manifest``
    as ``governance_decision_return`` hands it back. Anything but an ALLOW for
    the exact candidate leaves the original non-ALLOW standing: the return is
    reported, and no new attempt is prepared.

    A result shaped as an ALLOW does not authorize the new attempt by itself.
    ``decision_return_evidence`` carries the ledger readbacks of that return
    (``return_readback``, ``sender_readback``, ``deciding_readback`` and
    ``request_packet_id``); only when ``verify_governance_decision_return``
    accepts them, and they record the same ALLOW, is the attempt prepared.
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

    evidence = decision_return_evidence if isinstance(decision_return_evidence, Mapping) else {}
    acceptance = verify_governance_decision_return(
        evidence.get("return_readback"),
        sender_readback=evidence.get("sender_readback"),
        deciding_readback=evidence.get("deciding_readback"),
        request_packet_id=str(evidence.get("request_packet_id") or ""),
    )
    if acceptance.get("disposition") == "ALLOW" and acceptance.get("governance_disposition") != "ALLOW":
        acceptance = {**acceptance, "disposition": "FAIL_CLOSED",
                      "failure_code": "END_TO_END_REQUIRES_A_VERIFIED_GOVERNANCE_DECISION_RETURN",
                      "failed_predicate": "READ_BACK_GOVERNANCE_DECISION_IS_ALLOW",
                      "required_evidence_or_repair": "a read-back governance decision of ALLOW; observed "
                                                     + str(acceptance.get("governance_disposition")),
                      "retry_entrypoint": "stegverse/governed_remediation.py::perform_governed_remediation",
                      "next_attempt": "act on the decision the ledger records, not on the result handed in"}
    if acceptance.get("disposition") != "ALLOW":
        # A caller-supplied ALLOW without authenticated ledger readback grants
        # nothing; the original non-ALLOW stands.
        return {**base, "state": "REMEDIATION_NOT_AUTHORIZED", "disposition": "FAIL_CLOSED",
                **{k: acceptance.get(k) for k in ("failure_code", "failed_predicate",
                                                  "required_evidence_or_repair", "retry_entrypoint",
                                                  "owning_existing_goal", "next_attempt")},
                "handoff": None, "remediated_request": None}
    base["decision_return_acceptance"] = acceptance

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


__all__ = ["perform_governed_remediation", "remediation_candidate", "remediation_governance_manifest", "SCHEMA"]
