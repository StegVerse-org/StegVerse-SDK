from stegverse.universal_entry import CapabilityRegistry
from stegverse.universal_entry_dispatch import dispatch_universal_entry


def envelope(message, *, external=False, requested=None):
    return {
        "schema": "stegverse.universal_entry_envelope.v0.1",
        "origin": {
            "entry_point": "sdk",
            "actor_id": "tester",
            "node_id": "portable-node-reference",
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
            "allowed_lanes": [
                "conversation",
                "ecosystem_query",
                "external_llm",
                "solver",
                "execution",
            ]
        },
        "authority": {
            "class": "none",
            "execution_authority_granted": False,
        },
        "receipt": {"required": False, "expected_types": []},
        "continuity": {"previous_receipt_id": None},
    }


REGISTRY = CapabilityRegistry.from_mapping(
    {
        "conversation": "operational",
        "ecosystem_read": "operational",
        "external_llm": "operational",
        "solver": "operational",
        "execution": "disabled",
    }
)


def completed(text):
    def handler(_envelope, _context):
        return {
            "status": "completed",
            "output": text,
            "authorizing": False,
            "execution_authority_granted": False,
            "custody_transferred": False,
            "admissibility_determined": False,
        }

    return handler


def test_conversation_handler_is_invoked_for_greeting():
    result = dispatch_universal_entry(
        envelope("Good morning!"),
        REGISTRY,
        {"conversation": completed("Good morning!")},
    )
    assert result["status"] == "routed"
    assert [item["lane"] for item in result["lane_results"]] == ["conversation"]
    assert result["lane_results"][0]["output"] == "Good morning!"


def test_mixed_query_dispatch_preserves_lane_order_and_context():
    observed = []

    def conversation_handler(_envelope, context):
        observed.append(("conversation", list(context["lane_results"])))
        return {"status": "completed", "output": "interpreted"}

    def ecosystem_handler(_envelope, context):
        observed.append(("ecosystem_query", [r["lane"] for r in context["lane_results"]]))
        return {"status": "completed", "evidence": ["handoff"]}

    def external_handler(_envelope, context):
        observed.append(("external_llm", [r["lane"] for r in context["lane_results"]]))
        return {"status": "completed", "provider": "fixture-provider"}

    result = dispatch_universal_entry(
        envelope(
            "Compare the current StegVerse receipt model with the latest outside research.",
            external=True,
        ),
        REGISTRY,
        {
            "conversation": conversation_handler,
            "ecosystem_query": ecosystem_handler,
            "external_llm": external_handler,
        },
    )

    assert [r["lane"] for r in result["lane_results"]] == [
        "conversation",
        "ecosystem_query",
        "external_llm",
    ]
    assert observed[1] == ("ecosystem_query", ["conversation"])
    assert observed[2] == ("external_llm", ["conversation", "ecosystem_query"])


def test_missing_handler_is_reported_as_unavailable_not_simulated():
    result = dispatch_universal_entry(
        envelope("Search the web for the latest outside research.", external=True),
        REGISTRY,
        {"conversation": completed("interpreted")},
    )
    assert result["status"] == "routed"
    external = [r for r in result["lane_results"] if r["lane"] == "external_llm"][0]
    assert external["status"] == "unavailable"
    assert external["reason"] == "HANDLER_NOT_REGISTERED"


def test_handler_exception_fails_closed_without_leaking_exception_text():
    def broken(_envelope, _context):
        raise RuntimeError("provider secret should not be exposed")

    result = dispatch_universal_entry(
        envelope("Search the web for the latest outside research.", external=True),
        REGISTRY,
        {
            "conversation": completed("interpreted"),
            "external_llm": broken,
        },
    )
    assert result["status"] == "failed_closed"
    failure = [r for r in result["lane_results"] if r["lane"] == "external_llm"][0]
    assert failure["reason"] == "HANDLER_FAILURE:RuntimeError"
    assert "secret" not in str(result)


def test_authority_escalation_from_handler_fails_closed():
    def escalating(_envelope, _context):
        return {
            "status": "completed",
            "authorizing": True,
            "execution_authority_granted": True,
        }

    result = dispatch_universal_entry(
        envelope("Good morning!"),
        REGISTRY,
        {"conversation": escalating},
    )
    assert result["status"] == "failed_closed"
    assert result["lane_results"][0]["reason"] == "HANDLER_FAILURE:UniversalDispatchError"
    assert result["authority"]["execution_authority_granted"] is False


def test_restricted_request_invokes_no_handlers():
    invoked = []

    def execution_handler(_envelope, _context):
        invoked.append(True)
        return {"status": "completed"}

    result = dispatch_universal_entry(
        envelope("Delete the workflow and use this token.", requested=["execution"]),
        REGISTRY,
        {"execution": execution_handler},
    )
    assert result["status"] == "failed_closed"
    assert result["lane_results"] == []
    assert invoked == []


def test_dispatch_receipt_is_deterministic():
    handlers = {"conversation": completed("hello")}
    first = dispatch_universal_entry(envelope("Hello"), REGISTRY, handlers)
    second = dispatch_universal_entry(envelope("Hello"), REGISTRY, handlers)
    assert first["dispatch_receipt"] == second["dispatch_receipt"]
    assert first["dispatch_receipt"]["authorizing"] is False
