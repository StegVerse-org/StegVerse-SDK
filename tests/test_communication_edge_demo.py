import copy
import json
from pathlib import Path

import pytest

from stegverse.communication_edge_demo import (
    CommunicationDemoError,
    run_demo,
    simulate_recovery,
    simulate_selection,
)


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "communication_edge_demo.json"


def load_packet():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_demo_prefers_native_stegtalk_over_sms_when_more_capable():
    result = run_demo(load_packet())
    selection = result["selection"]
    assert selection["sdk_simulation_only"] is True
    assert selection["authority_granted"] is False
    assert selection["execution_performed"] is False
    assert selection["selected_edge_id"] == "sdk-demo:gateway"
    assert selection["selected_bearer"] == "stegtalk-ip"
    assert selection["fallback_order"][0]["edge_id"] == "sdk-demo:phone"


def test_ambiguous_post_dispatch_never_falls_through():
    selection = simulate_selection(load_packet())
    recovery = simulate_recovery(selection, "TIMEOUT_AFTER_DISPATCH")
    assert recovery["action"] == "VERIFY_EXTERNALLY"
    assert "fallback" not in recovery


def test_confirmed_pre_side_effect_failure_uses_exact_ordered_fallback():
    selection = simulate_selection(load_packet())
    recovery = simulate_recovery(selection, "FAILED", side_effect_absence_confirmed=True)
    assert recovery["action"] == "TRY_FALLBACK"
    assert recovery["fallback"]["edge_id"] == "sdk-demo:phone"


def test_remote_edge_denial_keeps_selection_on_current_edge():
    packet = load_packet()
    packet["constraints"]["remote_edge_execution_authorized"] = False
    packet["constraints"]["current_edge_id"] = "sdk-demo:phone"
    selection = simulate_selection(packet)
    assert selection["selected_edge_id"] == "sdk-demo:phone"
    assert any(item["edge_id"] == "sdk-demo:gateway" and "REMOTE_EDGE_DENIED" in item["reasons"] for item in selection["excluded_paths"])


def test_unknown_recipient_uses_explicit_safe_fallback_only():
    packet = load_packet()
    packet["recipient"] = {"state": "UNKNOWN", "safe_fallback_bearers": ["sms"]}
    selection = simulate_selection(packet)
    assert selection["selected_edge_id"] == "sdk-demo:phone"
    assert selection["selected_bearer"] == "sms"


def test_unattested_high_scoring_edge_is_excluded():
    packet = load_packet()
    packet["edges"][0]["attested"] = False
    selection = simulate_selection(packet)
    assert selection["selected_edge_id"] == "sdk-demo:phone"
    assert selection["excluded_paths"][0]["edge_id"] == "sdk-demo:gateway"


def test_no_admissible_edge_fails_closed():
    packet = load_packet()
    for edge in packet["edges"]:
        edge["attested"] = False
    with pytest.raises(CommunicationDemoError):
        simulate_selection(packet)


def test_selection_is_deterministic_for_identical_packet():
    first = simulate_selection(load_packet())
    second = simulate_selection(copy.deepcopy(load_packet()))
    assert first == second
    assert first["selection_sha256"] == second["selection_sha256"]
