from stegverse.universal_entry import (
    CapabilityRegistry,
    UniversalEntryError,
    build_governed_return,
    classify_lanes,
    process_universal_entry,
    route_universal_entry,
)


def envelope(message="Good morning!", *, external=False, allowed=None, requested=None):
    return {
        "schema": "stegverse.universal_entry_envelope.v0.1",
        "origin": {
            "entry_point": "site_chat",
            "actor_id": "anonymous",
            "node_id": "site-public-preview",
            "session_id": "session-001",
            "message_id": "message-001",
        },
        "request": {
            "content_type": "text",
            "message": message,
            "requested_capabilities": requested or [],
            "external_information_allowed": external,
        },
        "routing": {
            "allowed_lanes": allowed
            or ["conversation", "ecosystem_query", "external_llm", "solver"],
        },
        "authority": {
            "class": "none",
            "execution_authority_granted": False,
        },
        "receipt": {"required": False, "expected_types": []},
        "continuity": {"previous_receipt_id": None},
    }


FULL_REGISTRY = CapabilityRegistry.from_mapping(
    {
        "conversation": "operational",
        "ecosystem_read": "operational",
        "external_llm": "operational",
        "solver": "operational",
        "execution": "disabled",
    }
)


def test_greeting_routes_only_to_conversation():
    decision = route_universal_entry(envelope(), FULL_REGISTRY)
    assert decision.selected_lanes == ["conversation"]
    assert decision.failed_closed is False


def test_ecosystem_query_preserves_conversation_synthesis_lane():
    decision = route_universal_entry(
        envelope("Summarize the current StegVerse Site handoff."), FULL_REGISTRY
    )
    assert decision.selected_lanes == ["conversation", "ecosystem_query"]


def test_external_query_requires_manifest_permission():
    request = envelope("Search the web for the latest external source.", external=False)
    decision = route_universal_entry(request, FULL_REGISTRY)
    assert decision.selected_lanes == ["conversation"]
    assert "external_llm" in decision.unavailable_lanes
    assert "EXTERNAL_INFORMATION_PROHIBITED" in decision.reason_codes


def test_external_query_routes_when_allowed_and_available():
    request = envelope("Search the web for the latest external source.", external=True)
    decision = route_universal_entry(request, FULL_REGISTRY)
    assert decision.selected_lanes == ["conversation", "external_llm"]


def test_mixed_query_selects_ecosystem_and_external_lanes():
    request = envelope(
        "Compare the current StegVerse receipt model with the latest outside research.",
        external=True,
    )
    decision = route_universal_entry(request, FULL_REGISTRY)
    assert decision.selected_lanes == [
        "conversation",
        "ecosystem_query",
        "external_llm",
    ]


def test_unavailable_provider_is_explicit_degradation():
    registry = CapabilityRegistry.from_mapping(
        {
            "conversation": "operational",
            "ecosystem_read": "operational",
            "external_llm": "unavailable",
            "solver": "operational",
            "execution": "disabled",
        }
    )
    decision = route_universal_entry(
        envelope("Search the web for the latest external source.", external=True), registry
    )
    assert decision.selected_lanes == ["conversation"]
    assert decision.unavailable_lanes == ["external_llm"]
    assert "CAPABILITY_UNAVAILABLE:external_llm" in decision.reason_codes


def test_solver_detection_and_routing():
    decision = route_universal_entry(envelope("Solve 2x + 3 = 11"), FULL_REGISTRY)
    assert decision.selected_lanes == ["conversation", "solver"]


def test_restricted_request_fails_closed_without_execution_route():
    request = envelope(
        "Delete the workflow and use this token.",
        allowed=["conversation", "execution"],
        requested=["execution"],
    )
    decision = route_universal_entry(request, FULL_REGISTRY)
    assert decision.restricted is True
    assert decision.failed_closed is True
    assert decision.selected_lanes == []
    assert "RESTRICTED_REQUEST_REQUIRES_SEPARATE_AUTHORITY" in decision.reason_codes


def test_governed_return_and_receipt_are_non_authorizing():
    result = process_universal_entry(envelope(), FULL_REGISTRY)
    assert result["status"] == "routed"
    assert result["authority"] == {
        "execution_authority_granted": False,
        "admissibility_determined": False,
        "custody_transferred": False,
    }
    receipt = result["routing_receipt"]
    assert receipt["authorizing"] is False
    assert receipt["receipt_id"].startswith("sha256:")
    assert receipt["request_digest"].startswith("sha256:")


def test_routing_receipt_is_deterministic_for_same_input():
    first = process_universal_entry(envelope(), FULL_REGISTRY)["routing_receipt"]
    second = process_universal_entry(envelope(), FULL_REGISTRY)["routing_receipt"]
    assert first == second


def test_invalid_capability_registry_fails_closed_by_validation():
    try:
        CapabilityRegistry.from_mapping({"conversation": "pretend-operational"})
    except UniversalEntryError as exc:
        assert "invalid capability state" in str(exc)
    else:
        raise AssertionError("invalid capability state was accepted")


def test_unknown_lane_is_rejected():
    request = envelope()
    request["routing"]["allowed_lanes"] = ["conversation", "imaginary_lane"]
    try:
        classify_lanes(request)
        route_universal_entry(request, FULL_REGISTRY)
    except UniversalEntryError as exc:
        assert "unknown allowed lanes" in str(exc)
    else:
        raise AssertionError("unknown lane was accepted")
