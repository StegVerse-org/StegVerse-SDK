import copy

import pytest

from stegverse.canonical_source_collector import (
    CanonicalSourceCollector,
    CanonicalSourceCollectorError,
    validate_collection,
)
from stegverse.governed_conversation import (
    GovernedConversationError,
    GovernedConversationHandler,
)


def source_inventory():
    return [
        {
            "source_id": "site-handoff",
            "repository": "StegVerse-Labs/Site",
            "path": "docs/SITE_MIRROR_HANDOFF.md",
            "record_type": "handoff",
            "title": "Site mirror handoff",
            "observed_at": "2026-07-14T00:00:00Z",
            "canonical": True,
            "authoritative": True,
            "tags": ["site", "handoff"],
        }
    ]


def conversation_envelope(*, external_allowed=True):
    return {
        "origin": {
            "entry_point": "portable_node",
            "session_id": "session-1",
            "message_id": "message-1",
        },
        "request": {
            "content": "Explain why continuity matters in a collaborative system.",
            "requested_capabilities": ["conversation"],
            "external_information_allowed": external_allowed,
        },
        "routing": {"allowed_lanes": ["conversation", "external_llm"]},
        "continuity": {"transition_id": "transition-1", "run_id": "run-1"},
    }


def test_collector_builds_and_validates_projected_collection():
    collector = CanonicalSourceCollector.from_inventory(
        source_inventory(),
        reader=lambda spec: {
            "repository": spec.repository,
            "path": spec.path,
            "text": "Site remains prepared but not deployed.",
            "receipt_ref": "receipt:source-read:1",
        },
    )
    collection = collector.collect()
    validated = validate_collection(collection)
    assert validated["source_count"] == 1
    assert validated["projection_count"] == 1
    assert validated["projections"][0]["canonical_source_declared"] is True
    assert validated["projections"][0]["repository"] == "StegVerse-Labs/Site"


def test_collector_rejects_repository_identity_mismatch():
    collector = CanonicalSourceCollector.from_inventory(
        source_inventory(),
        reader=lambda spec: {
            "repository": "other/repository",
            "path": spec.path,
            "text": "mismatch",
        },
    )
    with pytest.raises(CanonicalSourceCollectorError, match="repository identity mismatch"):
        collector.collect()


def test_collection_detects_tamper():
    collector = CanonicalSourceCollector.from_inventory(
        source_inventory(), reader=lambda spec: "Canonical content"
    )
    collection = collector.collect()
    tampered = copy.deepcopy(collection)
    tampered["projections"][0]["text"] = "changed"
    with pytest.raises(CanonicalSourceCollectorError, match="collection digest mismatch"):
        validate_collection(tampered)


def test_general_conversation_uses_governed_provider_when_allowed():
    provider = lambda prompt, context: {
        "response": "Continuity preserves reconstructable relationships across change.",
        "provider": "governed-test-provider",
        "model": "test-model",
        "usage": {"input_tokens": 12, "output_tokens": 8},
        "receipt_id": "provider-receipt:1",
        "lifecycle_state": "COMPLETED",
        "master_record_status": "PENDING",
        "reconstruction_status": "NOT_SUBMITTED",
        "authorizing": False,
        "execution_authority_granted": False,
        "custody_transferred": False,
        "admissibility_determined": False,
    }
    result = GovernedConversationHandler(provider)(conversation_envelope(), {})
    assert result["status"] == "completed"
    assert result["provider_fallback_used"] is True
    assert result["provider_receipt"] == "provider-receipt:1"
    assert result["authorizing"] is False


def test_general_conversation_does_not_use_provider_without_manifest_permission():
    called = False

    def provider(prompt, context):
        nonlocal called
        called = True
        return {"response": "should not be used"}

    result = GovernedConversationHandler(provider)(
        conversation_envelope(external_allowed=False), {}
    )
    assert called is False
    assert result["status"] == "degraded"
    assert result["reason"] == "GENERAL_CONVERSATION_PROVIDER_NOT_ALLOWED"


def test_local_greeting_does_not_invoke_provider():
    called = False

    def provider(prompt, context):
        nonlocal called
        called = True
        return {"response": "unused"}

    envelope = conversation_envelope()
    envelope["request"]["content"] = "Good morning!"
    result = GovernedConversationHandler(provider)(envelope, {})
    assert result["status"] == "completed"
    assert result["provider_fallback_used"] is False
    assert called is False


def test_general_conversation_rejects_provider_authority_escalation():
    provider = lambda prompt, context: {
        "response": "bad",
        "authorizing": True,
    }
    with pytest.raises(GovernedConversationError, match="authority escalation"):
        GovernedConversationHandler(provider)(conversation_envelope(), {})
