from stegverse.master_records_organization_record import (
    ORGANIZATION_RECORD_RECEIPT_SCHEMA,
    MasterRecordsOrganizationRecordClient,
    _digest,
)
from stegverse.universal_entry_handlers import build_default_handler_registry
from stegverse.universal_entry_runtime import run_universal_entry


def envelope(message="calculate 2 + 3"):
    return {
        "origin": {
            "entry_point": "portable_node",
            "session_id": "session-1",
            "message_id": "message-1",
        },
        "request": {
            "content": message,
            "requested_capabilities": ["conversation", "solver"],
            "external_information_allowed": False,
        },
        "routing": {"allowed_lanes": ["conversation", "solver"]},
        "continuity": {"transition_id": "transition-1", "run_id": "run-1"},
    }


def registry():
    return {
        "capabilities": {
            "conversation": "operational",
            "ecosystem_read": "unavailable",
            "external_llm": "unavailable",
            "solver": "operational",
            "execution": "disabled",
        }
    }


def _receipt(submission):
    body = {
        "schema": ORGANIZATION_RECORD_RECEIPT_SCHEMA,
        "submission_id": submission["submission_id"],
        "session_id": submission["session_id"],
        "message_id": submission["message_id"],
        "transition_id": submission["transition_id"],
        "run_id": submission["run_id"],
        "first_event_id": submission["first_event_id"],
        "last_event_id": submission["last_event_id"],
        "event_count": submission["event_count"],
        "events_digest": submission["events_digest"],
        "organization_record_recorded": True,
        "reconstruction_available": True,
        "authorizing": False,
        "execution_authority_granted": False,
        "admissibility_determined": False,
    }
    body["receipt_id"] = _digest(body)
    return body


def test_runtime_attaches_validated_continuation_chain():
    result = run_universal_entry(envelope(), registry(), build_default_handler_registry())
    assert result["status"] == "routed"
    assert [event["event_type"] for event in result["continuation_events"]] == [
        "routing",
        "solver",
        "synthesis",
    ]
    assert result["continuation"]["event_count"] == 3
    assert result["continuation"]["record_submitted"] is False
    assert result["continuation"]["organization_record_installed"] is False
    assert "master_records_installed" not in result["continuation"]
    assert result["continuation"]["reconstructability_status"] == "NOT_SUBMITTED"
    assert result["continuation"]["last_event_id"] == result["continuation_events"][-1]["event_id"]


def test_runtime_failed_closed_still_emits_routing_event():
    restricted = envelope("delete repository")
    restricted["request"]["requested_capabilities"] = ["execution"]
    restricted["routing"]["allowed_lanes"] = ["execution"]
    result = run_universal_entry(restricted, registry(), {})
    assert result["status"] == "failed_closed"
    assert len(result["continuation_events"]) == 1
    assert result["continuation_events"][0]["event_type"] == "routing"


def _transports():
    state = {}

    def submit(submission):
        state["submission"] = submission
        return _receipt(submission)

    def reconstruct(receipt_id):
        assert receipt_id == _receipt(state["submission"])["receipt_id"]
        return {
            "schema": "stegverse.master_records_reconstruction.v0.1",
            "submission_id": state["submission"]["submission_id"],
            "events": state["submission"]["events"],
            "reconstructability_status": "PASS",
            "authorizing": False,
        }

    return submit, reconstruct


def test_runtime_marks_organization_record_only_after_receipt_and_reconstruction_pass():
    submit, reconstruct = _transports()
    result = run_universal_entry(
        envelope(),
        registry(),
        build_default_handler_registry(),
        organization_record_client=MasterRecordsOrganizationRecordClient(submit, reconstruct),
    )
    assert result["continuation"]["record_submitted"] is True
    assert result["continuation"]["organization_record_installed"] is True
    assert result["continuation"]["reconstructability_status"] == "PASS"
    assert result["continuation"]["organization_record_receipt_id"].startswith("sha256:")
    assert result["organization_record"]["verification"]["authorizing"] is False


def test_runtime_still_accepts_legacy_client_keyword():
    submit, reconstruct = _transports()
    result = run_universal_entry(
        envelope(),
        registry(),
        build_default_handler_registry(),
        custody_client=MasterRecordsOrganizationRecordClient(submit, reconstruct),
    )
    assert result["continuation"]["organization_record_installed"] is True
