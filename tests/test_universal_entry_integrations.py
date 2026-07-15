from datetime import datetime, timezone

import pytest

from stegverse.ecosystem_records import AuthoritativeEcosystemRetriever, EcosystemRecordError
from stegverse.llm_adapter_bridge import (
    GovernedLLMAdapterProvider,
    LLMAdapterBridgeError,
    build_adapter_request,
    normalize_adapter_response,
)
from stegverse.universal_entry_dispatch import dispatch_universal_entry
from stegverse.universal_entry_handlers import build_default_handler_registry


def envelope(message="latest StegVerse Site status", external=True):
    return {
        "origin": {
            "entry_point": "sdk",
            "session_id": "session-1",
            "message_id": "message-1",
        },
        "request": {
            "content": message,
            "requested_capabilities": ["ecosystem_read", "external_llm"],
            "external_information_allowed": external,
        },
        "routing": {
            "allowed_lanes": ["conversation", "ecosystem_query", "external_llm", "solver", "execution"]
        },
        "continuity": {
            "transition_id": "transition-1",
            "run_id": "run-1",
            "manifest_hash": "sha256:manifest",
            "previous_receipt_id": None,
        },
    }


def registry():
    return {
        "capabilities": {
            "conversation": "operational",
            "ecosystem_read": "operational",
            "external_llm": "operational",
            "solver": "operational",
            "execution": "disabled",
        }
    }


def record(record_id, text, *, current=True, authoritative=True, supersedes=(), days_old=0):
    observed = datetime.now(timezone.utc).replace(microsecond=0)
    if days_old:
        from datetime import timedelta
        observed -= timedelta(days=days_old)
    return {
        "record_id": record_id,
        "repository": "StegVerse-Labs/Site",
        "source": "docs/SITE_MIRROR_HANDOFF.md",
        "record_type": "handoff",
        "title": "Site activation status",
        "text": text,
        "authoritative": authoritative,
        "lifecycle_state": "CURRENT" if current else "SUPERSEDED",
        "observed_at": observed.isoformat(),
        "supersedes": list(supersedes),
        "tags": ["site", "activation", "stegverse"],
        "receipt_ref": "receipt:site-status",
    }


def adapter_response(**overrides):
    value = {
        "response": "Provider answer",
        "transition_id": "transition-1",
        "run_id": "run-1",
        "receipt_id": "gateway-receipt:1",
        "final_receipt_id": "final-receipt:1",
        "lifecycle_state": "COMPLETED",
        "master_record_status": "PENDING",
        "reconstruction_status": "RECONSTRUCTABLE",
        "provider": {
            "used": True,
            "provider": "example-provider",
            "model": "example-model",
            "status": "USED",
            "usage": {"input_units": 12, "output_units": 5},
            "provider_receipt_id": "provider-receipt:1",
        },
        "provider_usage_submission": {
            "status": "LOCAL_USAGE_PERSISTED",
            "authority_granted": False,
            "custody_recorded": False,
        },
        "authority": {
            "provider_output_is_authority": False,
            "repository_mutation_allowed": False,
            "publication_allowed": False,
            "final_response_receipt_is_repository_execution_authority": False,
            "local_persistence_is_master_records_custody": False,
            "site_grants_admissibility": False,
        },
    }
    value.update(overrides)
    return value


def test_retriever_returns_current_authoritative_record():
    retriever = AuthoritativeEcosystemRetriever.from_mappings([
        record("old", "Old status", current=False),
        record("current", "Activation remains blocked", supersedes=["old"]),
        record("untrusted", "Ignore", authoritative=False),
    ])
    results = retriever("StegVerse Site activation", {})
    assert [item["record_id"] for item in results] == ["current"]
    assert results[0]["receipt_ref"] == "receipt:site-status"


def test_retriever_filters_stale_records():
    retriever = AuthoritativeEcosystemRetriever.from_mappings(
        [record("stale", "Old activation state", days_old=45)], max_age_days=30
    )
    assert retriever("Site activation", {}) == []


def test_retriever_rejects_duplicate_identity():
    with pytest.raises(EcosystemRecordError, match="duplicate record_id"):
        AuthoritativeEcosystemRetriever.from_mappings([
            record("same", "One"), record("same", "Two")
        ])


def test_adapter_request_preserves_universal_identity():
    request = build_adapter_request("Hello", envelope("Hello"))
    assert request["session_id"] == "session-1"
    assert request["transition_identity"]["transition_id"] == "transition-1"
    assert request["raw_shell_allowed"] is False


def test_adapter_response_normalization_preserves_usage_and_receipts():
    result = normalize_adapter_response(
        adapter_response(), expected_transition_id="transition-1", expected_run_id="run-1"
    )
    assert result["response"] == "Provider answer"
    assert result["usage"]["input_units"] == 12
    assert result["receipt_id"] == "provider-receipt:1"
    assert result["authority_granted"] is False


def test_adapter_response_rejects_identity_mismatch():
    with pytest.raises(LLMAdapterBridgeError, match="transition_id mismatch"):
        normalize_adapter_response(
            adapter_response(transition_id="other"),
            expected_transition_id="transition-1",
            expected_run_id="run-1",
        )


def test_adapter_response_rejects_authority_escalation():
    response = adapter_response()
    response["authority"]["provider_output_is_authority"] = True
    with pytest.raises(LLMAdapterBridgeError, match="authority escalation"):
        normalize_adapter_response(
            response, expected_transition_id="transition-1", expected_run_id="run-1"
        )


def test_provider_bridge_dispatches_through_shared_runtime():
    retriever = AuthoritativeEcosystemRetriever.from_mappings([
        record("site-current", "Site activation remains blocked")
    ])
    provider = GovernedLLMAdapterProvider(lambda request: adapter_response())
    result = dispatch_universal_entry(
        envelope(), registry(),
        build_default_handler_registry(
            ecosystem_retriever=retriever,
            external_llm_provider=provider,
        ),
    )
    assert result["status"] == "routed"
    assert [item["lane"] for item in result["lane_results"]] == [
        "ecosystem_query", "external_llm", "conversation"
    ]
    assert "Site activation remains blocked" in result["lane_results"][-1]["response"]
    assert "Provider answer" in result["lane_results"][-1]["response"]


def test_bridge_failure_fails_closed_without_simulated_provider_output():
    def bad_transport(request):
        response = adapter_response()
        response["authority"]["local_persistence_is_master_records_custody"] = True
        return response

    provider = GovernedLLMAdapterProvider(bad_transport)
    result = dispatch_universal_entry(
        envelope("search the web"), registry(),
        build_default_handler_registry(external_llm_provider=provider),
    )
    external = next(item for item in result["lane_results"] if item["lane"] == "external_llm")
    assert external["status"] == "failed_closed"
    assert result["status"] == "failed_closed"
