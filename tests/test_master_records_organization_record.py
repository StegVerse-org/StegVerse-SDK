from copy import deepcopy

import pytest

from stegverse.master_records_organization_record import (
    LEGACY_ORGANIZATION_RECORD_RECEIPT_SCHEMA,
    LEGACY_RECEIPT_RECORDED_FIELD,
    ORGANIZATION_RECORD_RECEIPT_SCHEMA,
    MasterRecordsOrganizationRecordClient,
    MasterRecordsOrganizationRecordError,
    _digest,
    build_organization_record_request,
    validate_organization_record_receipt,
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


def _receipt(submission, *, legacy=False):
    body = {
        "schema": (
            LEGACY_ORGANIZATION_RECORD_RECEIPT_SCHEMA if legacy else ORGANIZATION_RECORD_RECEIPT_SCHEMA
        ),
        "submission_id": submission["submission_id"],
        "session_id": submission["session_id"],
        "message_id": submission["message_id"],
        "transition_id": submission["transition_id"],
        "run_id": submission["run_id"],
        "first_event_id": submission["first_event_id"],
        "last_event_id": submission["last_event_id"],
        "event_count": submission["event_count"],
        "events_digest": submission["events_digest"],
        (LEGACY_RECEIPT_RECORDED_FIELD if legacy else "organization_record_recorded"): True,
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
    submission = build_organization_record_request(_events())
    assert submission["event_count"] == 2
    assert submission["session_id"] == "session-1"
    assert submission["first_event_id"] == submission["events"][0]["event_id"]
    assert submission["last_event_id"] == submission["events"][-1]["event_id"]
    assert submission["record_requested"] is True
    assert "custody_requested" not in submission
    assert submission["schema"] == "stegverse.universal_entry_organization_record_request.v0.1"
    assert submission["authorizing"] is False


def test_receipt_identity_mismatch_fails_closed():
    submission = build_organization_record_request(_events())
    receipt = _receipt(submission)
    receipt["run_id"] = "other-run"
    with pytest.raises(MasterRecordsOrganizationRecordError, match="identity mismatch"):
        validate_organization_record_receipt(submission, receipt)


def test_receipt_digest_tamper_fails_closed():
    submission = build_organization_record_request(_events())
    receipt = _receipt(submission)
    receipt["organization_record_recorded"] = False
    with pytest.raises(MasterRecordsOrganizationRecordError):
        validate_organization_record_receipt(submission, receipt)


def test_reconstruction_event_drift_fails_closed():
    submission = build_organization_record_request(_events())
    reconstruction = _reconstruction(submission)
    reconstruction["events"] = deepcopy(reconstruction["events"])
    reconstruction["events"][1]["payload"]["status"] = "changed"
    with pytest.raises(MasterRecordsOrganizationRecordError):
        verify_reconstruction(submission, reconstruction)


def test_reconstruction_requires_pass():
    submission = build_organization_record_request(_events())
    reconstruction = _reconstruction(submission)
    reconstruction["reconstructability_status"] = "PENDING"
    with pytest.raises(MasterRecordsOrganizationRecordError, match="did not pass"):
        verify_reconstruction(submission, reconstruction)


def test_client_submit_and_verify_success():
    state = {}

    def submit_transport(submission):
        state["submission"] = submission
        return _receipt(submission)

    def reconstruct_transport(receipt_id):
        assert receipt_id == _receipt(state["submission"])["receipt_id"]
        return _reconstruction(state["submission"])

    result = MasterRecordsOrganizationRecordClient(
        submit_transport=submit_transport,
        reconstruct_transport=reconstruct_transport,
    ).submit_and_verify(_events())

    assert result["verification"]["status"] == "PASS"
    assert result["verification"]["organization_record_installed"] is True
    assert "master_records_installed" not in result["verification"]
    assert result["organization_record_receipt"]["schema"] == ORGANIZATION_RECORD_RECEIPT_SCHEMA
    assert result["verification"]["authorizing"] is False


def test_legacy_receipt_schema_and_field_are_still_read():
    submission = build_organization_record_request(_events())
    receipt = _receipt(submission, legacy=True)
    assert validate_organization_record_receipt(submission, receipt) == receipt

    receipt = _receipt(submission, legacy=True)
    receipt[LEGACY_RECEIPT_RECORDED_FIELD] = False
    receipt.pop("receipt_id")
    receipt["receipt_id"] = _digest(receipt)
    with pytest.raises(MasterRecordsOrganizationRecordError, match="does not record"):
        validate_organization_record_receipt(submission, receipt)


def test_unknown_receipt_schema_fails_closed():
    submission = build_organization_record_request(_events())
    receipt = _receipt(submission)
    receipt["schema"] = "stegverse.unknown_receipt.v0.1"
    with pytest.raises(MasterRecordsOrganizationRecordError, match="unsupported"):
        validate_organization_record_receipt(submission, receipt)
