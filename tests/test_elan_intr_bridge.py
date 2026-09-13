import pytest

from stegverse_sdk.elan_intr_bridge import (
    BridgeContractError,
    READY_FOR_INTR_ADMISSION,
    RESOLUTION_REQUIRED,
    evaluate_bridge_envelope,
)


def _base_envelope():
    return {
        "bridge_version": "elan.intr.bridge.v1",
        "transport_class": "ELAN_SHAPED_SDK_SUBMISSION",
        "source_framework": "ELAN",
        "source_instance_id": None,
        "source_event_id": "event-3",
        "observed_at": "2026-09-13T15:00:00Z",
        "payload_sha256": "0" * 64,
        "facts": [
            {
                "id": "fact-1",
                "statement": "No emission was observed during the bounded observation window.",
                "evidence_ref": "evidence:event-3",
            }
        ],
        "assertions": [],
        "provenance": ["ELAN-CUMULATIVE-PUBLICATION-001"],
    }


def test_single_survivor_is_ready_for_intr_admission():
    envelope = _base_envelope()
    envelope["resolution_state"] = "SINGLE_SURVIVING_INTERPRETATION"
    envelope["interpretation_candidates"] = [
        {
            "id": "candidate-a",
            "statement": "Non-emission is the admitted observable state.",
            "status": "SURVIVING",
            "elimination_reasons": [],
            "consequence_class": "ALLOW",
        },
        {
            "id": "candidate-b",
            "statement": "Event 3 is missing.",
            "status": "ELIMINATED",
            "elimination_reasons": ["fact-1 records an observable non-emission event"],
            "consequence_class": "DENY",
        },
    ]

    receipt = evaluate_bridge_envelope(envelope)

    assert receipt["admission_disposition"] == READY_FOR_INTR_ADMISSION
    assert receipt["consequence_divergent"] is False
    assert receipt["consequence_relation"] == "EQUIVALENT"
    assert receipt["intr_transition_authority_granted"] is False


def test_unresolved_divergent_candidates_require_resolution():
    envelope = _base_envelope()
    envelope["resolution_state"] = "UNRESOLVED_INTERPRETATION_SET"
    envelope["interpretation_candidates"] = [
        {
            "id": "candidate-a",
            "statement": "Non-emission is an admitted state transition.",
            "status": "SURVIVING",
            "elimination_reasons": [],
            "consequence_class": "ALLOW",
        },
        {
            "id": "candidate-b",
            "statement": "Required event evidence is absent.",
            "status": "SURVIVING",
            "elimination_reasons": [],
            "consequence_class": "DENY",
        },
    ]

    receipt = evaluate_bridge_envelope(envelope)

    assert receipt["admission_disposition"] == RESOLUTION_REQUIRED
    assert receipt["consequence_divergent"] is True
    assert receipt["consequence_relation"] == "DIVERGENT"
    assert set(receipt["consequence_classes"]) == {"ALLOW", "DENY"}


def test_unresolved_equivalent_candidates_still_require_resolution():
    envelope = _base_envelope()
    envelope["resolution_state"] = "UNRESOLVED_INTERPRETATION_SET"
    envelope["interpretation_candidates"] = [
        {
            "id": "candidate-a",
            "statement": "Silence is deliberate.",
            "status": "SURVIVING",
            "elimination_reasons": [],
            "consequence_class": "ALLOW",
        },
        {
            "id": "candidate-b",
            "statement": "Silence intent is unknown.",
            "status": "SURVIVING",
            "elimination_reasons": [],
            "consequence_class": "ALLOW",
        },
    ]

    receipt = evaluate_bridge_envelope(envelope)

    assert receipt["admission_disposition"] == RESOLUTION_REQUIRED
    assert receipt["consequence_divergent"] is False
    assert receipt["consequence_relation"] == "EQUIVALENT"
    assert receipt["resolution_state"] == "UNRESOLVED_INTERPRETATION_SET"


def test_eliminated_candidate_requires_reason():
    envelope = _base_envelope()
    envelope["resolution_state"] = "SINGLE_SURVIVING_INTERPRETATION"
    envelope["interpretation_candidates"] = [
        {
            "id": "candidate-a",
            "statement": "One candidate survives.",
            "status": "SURVIVING",
            "elimination_reasons": [],
            "consequence_class": "ALLOW",
        },
        {
            "id": "candidate-b",
            "statement": "This candidate was removed without evidence.",
            "status": "ELIMINATED",
            "elimination_reasons": [],
            "consequence_class": "DENY",
        },
    ]

    with pytest.raises(BridgeContractError):
        evaluate_bridge_envelope(envelope)
