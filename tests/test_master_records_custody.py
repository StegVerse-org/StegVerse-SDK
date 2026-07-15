from copy import deepcopy

import pytest

from stegverse.master_records_custody import (
    MasterRecordsCustodyClient,
    MasterRecordsCustodyError,
    build_custody_submission,
    validate_custody_receipt,
    verify_reconstruction,
)
from stegverse.universal_entry_events import build_continuation_event


def _envelope():
    return {
        "origin": {
            "entry_point": "sdk",
            "session_id": "session-1",
            "message_id": "message-1",
        },
        "continuity": {"transition_id": "transition-1", "run_id": "run-1"},
    }


def _events():
    first = build_continuation_event(
        event_type="routing",
        envelope=_envelope(),
        payload={"selected_lanes": ["conversation"]},
    )
    second = build_continuation_event(
        event_type="synthesis",
        envelope=_envelope(),
        payload={"status": "completed"},
        prior_event_id=first["event_id"],
    )
    return [first, second]


def _receipt(submission):
    from stegverse.master_records_custody import _digest

    body = {
        "schema": "stegverse.master_records_custody_receipt.v0.1",
        "submission_id": submission["submission_id"],
        "session_id": submission["session_id"],
        "message_id": submission["message_id"],
        "transition_id": submission["transition_id"],
        "run_id": submission["run_id"],
        "first_event_id": submission["first_event_id"],
        "last_event_id": submission["last_event_id"],
        "event_count": submission["event_count"],
        "events_digest": submission["events_digest"],
        "custody_recorded": True,
        "reconstruction_available": True,
        "authorizing": False,
        "execution_authority_granted": False,
        "admissibility_determined": False,
    }
    body["receipt_id"] = _digest(body)
    return body


def _reconstruction(submission):
    return {
        "schema": "stegverse.master_records_reconstruction.v0.1",
        "submission_id": submission["submission_id"],
        "events": submission["events"],
        "reconstructability_status": "PASS",
        "authorizing": False,
    }


def test_build_submission_preserves_identity_and_chain():
    submission = build_custody_submission(_events())
    assert submission["event_count"] == 2
    assert submission["session_id"] == "session-1"
    assert submission["first_event_id"] == submission["events"][0]["event_id"]
    assert submission["last_event_id"] == submission["events"][-1]["event_id"]
    assert submission["custody_requested"] is True
    assert submission["authorizing"] is False


def test_receipt_identity_mismatch_fails_closed():
    submission = build_custody_submission(_events())
    receipt = _receipt(submission)
    receipt["run_id"] = "other-run"
    with pytest.raises(MasterRecordsCustodyError, match="identity mismatch"):
        validate_custody_receipt(submission, receipt)


def test_receipt_digest_tamper_fails_closed():
    submission = build_custody_submission(_events())
    receipt = _receipt(submission)
    receipt["custody_recorded"] = False
    with pytest.raises(MasterRecordsCustodyError):
        validate_custody_receipt(submission, receipt)


def test_reconstruction_event_drift_fails_closed():
    submission = build_custody_submission(_events())
    reconstruction = _reconstruction(submission)
    reconstruction["events"] = deepcopy(reconstruction["events"])
    reconstruction["events"][1]["payload"]["status"] = "changed"
    with pytest.raises(MasterRecordsCustodyError):
        verify_reconstruction(submission, reconstruction)


def test_reconstruction_requires_pass():
    submission = build_custody_submission(_events())
    reconstruction = _reconstruction(submission)
    reconstruction["reconstructability_status"] = "PENDING"
    with pytest.raises(MasterRecordsCustodyError, match="did not pass"):
        verify_reconstruction(submission, reconstruction)


def test_client_submit_and_verify_success():
    state = {}

    def submit_transport(submission):
        state["submission"] = submission
        return _receipt(submission)

    def reconstruct_transport(receipt_id):
        assert receipt_id == _receipt(state["submission"])["receipt_id"]
        return _reconstruction(state["submission"])

    result = MasterRecordsCustodyClient(
        submit_transport=submit_transport,
        reconstruct_transport=reconstruct_transport,
    ).submit_and_verify(_events())

    assert result["verification"]["status"] == "PASS"
    assert result["verification"]["custody_verified"] is True
    assert result["verification"]["master_records_installed"] is True
    assert result["verification"]["authorizing"] is False
