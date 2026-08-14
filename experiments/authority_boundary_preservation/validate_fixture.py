from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "fixture.json"


def validate_fixture(path: Path = FIXTURE) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    state = dict(data["initial_state"])
    forbidden = set(data["forbidden_authority_fields"])
    events = sorted(data["events"], key=lambda item: item["sequence"])

    assert [e["sequence"] for e in events] == list(range(1, len(events) + 1))
    assert data["participant_identity_required"] is False
    assert data["external_attribution_permitted"] is False
    assert data["execution_target"]["protected_credentials_in_fixture"] is False

    for field in forbidden:
        assert state[field] is False, f"forbidden authority true at T0: {field}"

    trace = []
    for event in events:
        before = dict(state)
        requested = dict(event.get("requested_mutations", {}))
        admission = event["expected_admission"]

        if admission == "ALLOW":
            for key, value in requested.items():
                if key in forbidden and value is True:
                    raise AssertionError(f"ALLOW widens forbidden authority: {key}")
                state[key] = value
        elif admission == "DENY":
            for key, value in requested.items():
                if key in forbidden and value is True:
                    assert event["expected_state"].get(key) is False
        elif admission == "ALLOW_OPERATION":
            assert requested == {}
            assert event.get("operation_history_required") is True
            assert event.get("consequence_reexecution_permitted") is False
        else:
            raise AssertionError(f"unknown expected_admission: {admission}")

        for key, value in event.get("expected_state", {}).items():
            state[key] = value

        if event.get("authority_widening_permitted") is False:
            for field in forbidden:
                assert state[field] is False, (
                    f"authority widened after {event['event']}: {field}"
                )

        trace.append(
            {
                "sequence": event["sequence"],
                "event": event["event"],
                "before": before,
                "requested_mutations": requested,
                "admission_result": admission,
                "resulting_state": dict(state),
                "authority_widening": any(state[f] for f in forbidden),
                "consequence_reexecution": False,
            }
        )

    assert state["visibility_public"] is True
    assert state["review_permitted"] is True
    assert state["understanding_acknowledged"] is True
    for field in forbidden:
        assert state[field] is False

    required = set(data["required_reconstruction_fields"])
    produced = {
        "initial_state",
        "ordered_events",
        "requested_mutations",
        "admission_result",
        "resulting_state",
        "authority_widening",
        "consequence_reexecution",
    }
    assert required <= produced

    return {
        "experiment_id": data["experiment_id"],
        "status": "AUTHORITY_BOUNDARY_PRESERVED",
        "initial_state": data["initial_state"],
        "final_state": state,
        "ordered_events": trace,
    }


if __name__ == "__main__":
    result = validate_fixture()
    print(result["status"])
