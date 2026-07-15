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


def test_runtime_attaches_validated_continuation_chain():
    result = run_universal_entry(envelope(), registry(), build_default_handler_registry())
    assert result["status"] == "routed"
    assert [event["event_type"] for event in result["continuation_events"]] == [
        "routing",
        "solver",
        "synthesis",
    ]
    assert result["continuation"]["event_count"] == 3
    assert result["continuation"]["custody_submitted"] is False
    assert result["continuation"]["master_records_installed"] is False
    assert result["continuation"]["last_event_id"] == result["continuation_events"][-1]["event_id"]


def test_runtime_failed_closed_still_emits_routing_event():
    restricted = envelope("delete repository")
    restricted["request"]["requested_capabilities"] = ["execution"]
    restricted["routing"]["allowed_lanes"] = ["execution"]
    result = run_universal_entry(restricted, registry(), {})
    assert result["status"] == "failed_closed"
    assert len(result["continuation_events"]) == 1
    assert result["continuation_events"][0]["event_type"] == "routing"
