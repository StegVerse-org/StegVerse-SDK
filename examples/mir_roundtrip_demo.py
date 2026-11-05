"""Demonstrate the MIR governed round trip at SDK scope.

The capability (owner identification, DEMO__LINE__ADDENDUM__01):
the governed round trip completing — a manifested packet is
submitted, its transitions are dispositioned, destination
evidence is retained, and the governed return is exported to
the submitter (STEGVERSE_RETURN_EXIT) or the return closes
governed FAIL_CLOSED.

Canonical sequence (StegVerse-Labs/.github
docs/CANONICAL_MASTER_RECORDS_STATE_TRANSITION_CUSTODY_MIRROR_HANDOFF.md):

    MIR_EVENT_MATERIALIZATION_REQUEST_QUEUED
    -> authentic /intr/materialization INGRESS_ADMITTED
    -> CURRENT_INTERLOCK_INTR_INGRESS_RECEIVED
    -> RTC-STEGVERSE-EGRESS-007
    -> RTC-INTERLOCK-INTR-TRANSPORT-008
    -> RTC-FARSIDE-FINAL-009
    -> MIR_DESTINATION_EVIDENCE_RETAINED
    -> EXACT_GOVERNED_RETURN_PACKET_RETAINED
    -> STEGVERSE_RETURN_EXIT or MIR_GOVERNED_RETURN_FAIL_CLOSED

Grade: DEMONSTRATED CAPABILITY ONLY. No authentic MIR
INGRESS_ADMITTED receipt, RTC-008/009 receipt, or governed-
return receipt has been observed in canonical evidence; those
runtime predicates remain false and this demo states them
NOT_OBSERVED rather than performing them. No live MIR
submission is made and no credential is used.
"""

from __future__ import annotations

import json

from stegverse.manifest_builder import build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_execution import execute_manifest
from stegverse.publisher_return_binding import (
    PublisherReturnBindingError,
    assemble_publisher_return,
)
from stegverse.source_evidence_packet import (
    build_source_evidence_packet,
    verify_source_evidence_packet,
)

DEMO_GRADE = "DEMONSTRATED_CAPABILITY"
MANIFEST_RECEIPT_ID = "MR-0123456789ABCDEF"

CANONICAL_SEQUENCE = [
    "MIR_EVENT_MATERIALIZATION_REQUEST_QUEUED",
    "INGRESS_ADMITTED",
    "CURRENT_INTERLOCK_INTR_INGRESS_RECEIVED",
    "RTC-STEGVERSE-EGRESS-007",
    "RTC-INTERLOCK-INTR-TRANSPORT-008",
    "RTC-FARSIDE-FINAL-009",
    "MIR_DESTINATION_EVIDENCE_RETAINED",
    "EXACT_GOVERNED_RETURN_PACKET_RETAINED",
    "STEGVERSE_RETURN_EXIT",
]

# States whose authentic form this demo cannot produce. The
# demo produces their SDK-scope analogues or readiness states
# and grades the authentic state NOT_OBSERVED.
NOT_OBSERVED_STATES = {
    "INGRESS_ADMITTED",
    "RTC-INTERLOCK-INTR-TRANSPORT-008",
    "RTC-FARSIDE-FINAL-009",
    "STEGVERSE_RETURN_EXIT",
}


def governance_request():
    return {
        "candidate": {"actor_class": "external_framework", "action": "test", "target": "mirror", "scope": "test", "parameters": {"external_side_effect": False}},
        "judgment": {"refusal_available": True, "operator_recoverability": "available", "workload_state": "supported", "time_pressure": "normal", "isolation_state": "supported", "evidence_refs": ["test:1"]},
        "signal": {"admitted_signal_refs": ["test:1"], "excluded_signal_refs": [], "transformations": [], "missing_inputs": [], "uncertainty_state": "bounded", "reference_state_hash": "a" * 64, "expected_reference_state_hash": "a" * 64, "reconstruction_available": True, "transformation_provenance_complete": True},
        "execution": {"actor_authority_current": True, "policy_current": True, "delegation_current": True, "evidence_current": True, "affected_entity_conditions_represented": True, "recoverability_profile": "recoverable", "validity_window_open": True, "policy_ref": "test:policy", "delegation_ref": "test:delegation", "evidence_refs": ["test:1"]},
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }


def publisher_return_bytes() -> bytes:
    value = {
        "schema": "stegverse.publisher.artifact-return/v1",
        "authority_effect": "NONE",
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "transfer_id": "transfer-mir-roundtrip-demo",
        "source_export_id": "export-mir-roundtrip-demo",
        "source_export_sha256": "sha256:" + "b" * 64,
        "generation_id": "generation-mir-roundtrip-demo",
        "manifest": {"artifacts": []},
        "artifacts": [],
    }
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_roundtrip_manifest():
    return build_manifest(
        data={"signal": "mir-roundtrip-demo"},
        source_framework="MIR_TEST",
        source_output_id="mir-roundtrip-demo-001",
        processor_request=governance_request(),
        publisher_destination={"type": "SDK_CONSOLE_SESSION", "session_ref": "mir-roundtrip-demo"},
        destination_profile="MIR",
        created_at="2026-11-05T12:00:00Z",
    )


def state_mapping(execution: dict, binding: dict, packet_verified: bool) -> list[dict]:
    """Per-state grades for the canonical sequence.

    DEMONSTRATED means this surface performed the leg and the
    named artifact evidences it. NOT_OBSERVED means the
    authentic state was not produced; the evidence column names
    what was produced instead.
    """
    return [
        {
            "state": "MIR_EVENT_MATERIALIZATION_REQUEST_QUEUED",
            "grade": "DEMONSTRATED",
            "evidence": "manifest built with destination_profile MIR; the manifested packet is the materialization request",
        },
        {
            "state": "INGRESS_ADMITTED",
            "grade": "NOT_OBSERVED",
            "evidence": "ingress form validated by validate_ingress_manifest; authentic admission not observed (execution intr_admission_observed is False)",
        },
        {
            "state": "CURRENT_INTERLOCK_INTR_INGRESS_RECEIVED",
            "grade": "DEMONSTRATED",
            "evidence": f"generic execution received and dispositioned the manifest: disposition {execution['disposition']}, handoff_sha256 bound; organization_receipt_observed is False",
        },
        {
            "state": "RTC-STEGVERSE-EGRESS-007",
            "grade": "DEMONSTRATED",
            "evidence": "publisher return assembled under the MIR destination profile (assemble_publisher_return)",
        },
        {
            "state": "RTC-INTERLOCK-INTR-TRANSPORT-008",
            "grade": "NOT_OBSERVED",
            "evidence": "binding interlock_intr_egress_observed is False; no live InTr hop was performed",
        },
        {
            "state": "RTC-FARSIDE-FINAL-009",
            "grade": "NOT_OBSERVED",
            "evidence": "binding far_side_transition_observed is False; no far-side transition was performed",
        },
        {
            "state": "MIR_DESTINATION_EVIDENCE_RETAINED",
            "grade": "DEMONSTRATED",
            "evidence": f"source evidence packet built over the manifest and verified at this surface (verify_source_evidence_packet: {packet_verified}); retention inside MIR itself is NOT_OBSERVED",
        },
        {
            "state": "EXACT_GOVERNED_RETURN_PACKET_RETAINED",
            "grade": "DEMONSTRATED",
            "evidence": "the assembled binding is the exact governed return packet, retained in this report with its egress profile and state",
        },
        {
            "state": "STEGVERSE_RETURN_EXIT",
            "grade": "NOT_OBSERVED",
            "evidence": f"readiness produced instead: communication_state {binding['communication_state']}; the exit transition is the far-side leg (RTC-008/009)",
        },
    ]


def run_roundtrip() -> dict:
    manifest = build_roundtrip_manifest()
    canonical = validate_ingress_manifest(manifest)
    assert canonical["completion"]["egress"]["destination_profile"] == "MIR"

    execution = execute_manifest(manifest)

    requirements = [{
        "requirement_id": "mir-roundtrip-governance",
        "capability_id": manifest["processing"]["capability"],
        "route_id": manifest["processing"]["route_id"],
    }]
    packet = build_source_evidence_packet(manifest, requirements, evaluator_id="mir-roundtrip-demo")
    packet_verified = verify_source_evidence_packet(manifest, requirements, packet)

    binding = assemble_publisher_return(
        manifest=manifest,
        manifest_receipt_id=MANIFEST_RECEIPT_ID,
        publisher_return_bytes=publisher_return_bytes(),
    )

    # Negative leg: a return that attempts authority expansion
    # is refused at assembly, with the exact reason — the
    # governed FAIL_CLOSED outcome for this surface.
    forged = json.loads(publisher_return_bytes())
    forged["publication_authorized"] = True
    negative = {"outcome": "MIR_GOVERNED_RETURN_FAIL_CLOSED", "refused": False, "reason": None}
    try:
        assemble_publisher_return(
            manifest=manifest,
            manifest_receipt_id=MANIFEST_RECEIPT_ID,
            publisher_return_bytes=json.dumps(forged, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        )
    except PublisherReturnBindingError as exc:
        negative["refused"] = True
        negative["reason"] = str(exc)

    return {
        "demo": "mir-roundtrip-demo",
        "demo_grade": DEMO_GRADE,
        "authentic_runtime_completion": False,
        "destination_profile": binding["egress"]["destination_profile"],
        "execution_disposition": execution["disposition"],
        "execution_handoff_sha256": execution["handoff_sha256"],
        "intr_admission_observed": execution["intr_admission_observed"],
        "organization_receipt_observed": execution["organization_receipt_observed"],
        "communication_state": binding["communication_state"],
        "interlock_intr_egress_observed": binding["interlock_intr_egress_observed"],
        "far_side_transition_observed": binding["far_side_transition_observed"],
        "evidence_packet_verified": packet_verified,
        "evidence_packet_conditions": [
            {"requirement_id": c["requirement_id"], "disposition": c["qualification_disposition"]}
            for c in packet["conditions"]
        ],
        "state_mapping": state_mapping(execution, binding, packet_verified),
        "negative_leg": negative,
    }


def main() -> None:
    print(json.dumps(run_roundtrip(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
