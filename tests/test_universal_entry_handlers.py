from stegverse.universal_entry_dispatch import dispatch_universal_entry
from stegverse.universal_entry_handlers import (
    EcosystemQueryHandler,
    ExternalLLMHandler,
    build_default_handler_registry,
    conversation_handler,
    solver_handler,
)


def envelope(message, capabilities, *, external=False):
    return {
        "schema": "stegverse.universal_entry_envelope.v0.1",
        "origin": {
            "entry_point": "test",
            "session_id": "session-1",
            "message_id": "message-1",
        },
        "request": {
            "content_type": "text",
            "content": message,
            "requested_capabilities": capabilities,
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
        "authority": {"class": "none", "execution_authority_granted": False},
        "receipt": {"required": False, "expected_types": []},
        "continuity": {"transition_id": "t-1", "run_id": "r-1"},
    }


def registry(**overrides):
    values = {
        "conversation": "operational",
        "ecosystem_read": "operational",
        "external_llm": "operational",
        "solver": "operational",
        "execution": "disabled",
    }
    values.update(overrides)
    return {"capabilities": values}


def test_conversation_greeting_is_operational():
    result = conversation_handler(envelope("Good morning!", ["conversation"]), {"lane_results": []})
    assert result["status"] == "completed"
    assert result["response"].startswith("Good morning!")
    assert result["execution_authority_granted"] is False


def test_general_local_conversation_is_honestly_degraded():
    result = conversation_handler(envelope("Tell me a story", ["conversation"]), {"lane_results": []})
    assert result["status"] == "degraded"
    assert result["reason"] == "GENERAL_CONVERSATION_MODEL_NOT_ATTACHED"


def test_ecosystem_handler_uses_authoritative_retriever():
    def retrieve(query, context):
        return [
            {
                "text": "Site activation remains blocked pending current-main evidence.",
                "source": "StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md",
            }
        ]

    result = EcosystemQueryHandler(retrieve)(
        envelope("What blocks Site activation?", ["ecosystem_read"]), {}
    )
    assert result["status"] == "completed"
    assert result["retrieval_authoritative"] is True
    assert result["evidence_count"] == 1
    assert result["sources"]


def test_ecosystem_handler_does_not_fake_missing_retrieval():
    result = EcosystemQueryHandler()(envelope("Site status", ["ecosystem_read"]), {})
    assert result["status"] == "unavailable"
    assert result["reason"] == "ECOSYSTEM_RETRIEVER_NOT_CONFIGURED"


def test_external_handler_preserves_provider_usage():
    def provider(prompt, context):
        return {
            "response": "External result",
            "provider": "test-provider",
            "model": "test-model",
            "usage": {"input_units": 4, "output_units": 2},
            "receipt_id": "provider-receipt-1",
        }

    result = ExternalLLMHandler(provider)(
        envelope("Search the web for current news", ["external_llm"], external=True), {}
    )
    assert result["status"] == "completed"
    assert result["provider"] == "test-provider"
    assert result["usage"]["input_units"] == 4
    assert result["provider_receipt"] == "provider-receipt-1"


def test_external_handler_does_not_fake_unconfigured_provider():
    result = ExternalLLMHandler()(
        envelope("Search the web", ["external_llm"], external=True), {}
    )
    assert result["status"] == "unavailable"
    assert result["reason"] == "EXTERNAL_LLM_PROVIDER_NOT_CONFIGURED"


def test_solver_completes_bounded_arithmetic():
    result = solver_handler(envelope("calculate 2 + 3 * 4", ["solver"]), {})
    assert result["status"] == "completed"
    assert result["result"] == 14
    assert result["checked_locally"] is True


def test_solver_declares_symbolic_limit():
    result = solver_handler(envelope("solve x + 2 = 5", ["solver"]), {})
    assert result["status"] == "degraded"
    assert result["reason"] == "SYMBOLIC_OR_UNSUPPORTED_SOLVER_REQUEST"


def test_mixed_dispatch_runs_operational_lanes_before_conversation_synthesis():
    order = []

    def retrieve(query, context):
        order.append("ecosystem_query")
        return [{"text": "Ecosystem evidence.", "source": "repo/handoff.md"}]

    def provider(prompt, context):
        order.append("external_llm")
        assert context["lane_results"][0]["lane"] == "ecosystem_query"
        return {"response": "External evidence.", "provider": "p", "model": "m"}

    handlers = build_default_handler_registry(
        ecosystem_retriever=retrieve,
        external_llm_provider=provider,
    )
    result = dispatch_universal_entry(
        envelope(
            "Compare the latest public web research with the StegVerse receipt model",
            ["ecosystem_read", "external_llm"],
            external=True,
        ),
        registry(),
        handlers,
    )
    assert order == ["ecosystem_query", "external_llm"]
    assert [item["lane"] for item in result["lane_results"]] == [
        "ecosystem_query",
        "external_llm",
        "conversation",
    ]
    assert result["response"] == "Ecosystem evidence.\n\nExternal evidence."
    assert result["lane_results"][-1]["synthesis"] is True


def test_handler_outputs_remain_non_authorizing():
    handlers = build_default_handler_registry()
    result = dispatch_universal_entry(
        envelope("Good morning!", ["conversation"]), registry(), handlers
    )
    assert result["authority"] == {
        "execution_authority_granted": False,
        "admissibility_determined": False,
        "custody_transferred": False,
    }
    assert result["dispatch_receipt"]["authorizing"] is False
