from stegverse.activation_evidence import validate_activation_evidence
from stegverse.repository_source_reader import AllowlistedRepositorySourceReader
from stegverse.universal_entry_server_runtime import (
    UniversalEntryServerConfig,
    UniversalEntryServerRuntime,
    UniversalEntryServerRuntimeError,
)


def envelope(message="hello"):
    return {
        "origin": {
            "entry_point": "api",
            "session_id": "session-1",
            "message_id": "message-1",
        },
        "request": {
            "content": message,
            "requested_capabilities": ["conversation"],
            "external_information_allowed": False,
        },
        "routing": {"allowed_lanes": ["conversation"]},
        "continuity": {"transition_id": "transition-1", "run_id": "run-1"},
    }


def registry():
    return {
        "capabilities": {
            "conversation": "operational",
            "ecosystem_read": "unavailable",
            "external_llm": "unavailable",
            "solver": "unavailable",
            "execution": "disabled",
        }
    }


def test_default_runtime_is_disabled_and_non_authorizing():
    runtime = UniversalEntryServerRuntime(UniversalEntryServerConfig())
    result = runtime.process(envelope(), registry())
    assert result["status"] == "routed"
    assert result["server_runtime"] == {
        "source_collection_enabled": False,
        "provider_enabled": False,
        "custody_enabled": False,
        "activation_evidence_enabled": False,
        "credentials_exposed_to_entry_adapter": False,
        "deployment_authorized": False,
        "activation_performed": False,
    }
    assert result["continuation"]["custody_submitted"] is False


def test_unknown_configuration_fails_closed():
    try:
        UniversalEntryServerConfig.from_mapping({"live": True})
    except UniversalEntryServerRuntimeError as exc:
        assert "unknown server runtime configuration" in str(exc)
    else:
        raise AssertionError("unknown configuration must fail")


def test_provider_enablement_requires_provider():
    runtime = UniversalEntryServerRuntime(
        UniversalEntryServerConfig(provider_enabled=True)
    )
    try:
        runtime.process(envelope("Explain continuity"), registry())
    except UniversalEntryServerRuntimeError as exc:
        assert "provider enabled without" in str(exc)
    else:
        raise AssertionError("missing provider must fail")


def test_custody_enablement_requires_client():
    runtime = UniversalEntryServerRuntime(
        UniversalEntryServerConfig(custody_enabled=True)
    )
    try:
        runtime.process(envelope(), registry())
    except UniversalEntryServerRuntimeError as exc:
        assert "custody enabled without" in str(exc)
    else:
        raise AssertionError("missing custody client must fail")


def test_source_collection_builds_authoritative_retriever():
    inventory = [
        {
            "source_id": "sdk-handoff",
            "repository": "StegVerse-org/StegVerse-SDK",
            "path": "docs/UNIVERSAL_ENTRY_INTEGRATION_HANDOFF.md",
            "record_type": "handoff",
            "title": "Universal Entry Integration Handoff",
            "observed_at": "2026-07-14T00:00:00Z",
            "canonical": True,
            "authoritative": True,
            "tags": ["sdk", "universal-entry"],
        }
    ]
    bindings = [
        {
            "source_id": "sdk-handoff",
            "repository": "StegVerse-org/StegVerse-SDK",
            "path": "docs/UNIVERSAL_ENTRY_INTEGRATION_HANDOFF.md",
            "ref": "main",
        }
    ]
    reader = AllowlistedRepositorySourceReader.from_bindings(
        bindings,
        fetcher=lambda binding: {
            "content": "Universal entry routing and custody verification are installed.",
            "repository": binding.repository,
            "path": binding.path,
            "ref": binding.ref,
            "blob_sha": "blob-1",
        },
    )
    runtime = UniversalEntryServerRuntime(
        UniversalEntryServerConfig(
            source_collection_enabled=True,
            catalog_built_at="2026-07-14T00:00:00Z",
            catalog_source_set_id="source-set-1",
        ),
        source_inventory=inventory,
        source_reader=reader,
    )
    request = envelope("What is installed in the SDK handoff?")
    request["request"]["requested_capabilities"] = ["conversation", "ecosystem_read"]
    request["routing"]["allowed_lanes"] = ["conversation", "ecosystem_query"]
    capabilities = registry()
    capabilities["capabilities"]["ecosystem_read"] = "operational"
    result = runtime.process(request, capabilities)
    assert result["status"] == "routed"
    assert "custody verification" in result["response"]


def test_activation_evidence_is_explicitly_disabled_by_default():
    runtime = UniversalEntryServerRuntime(UniversalEntryServerConfig())
    try:
        runtime.evaluate_readiness({})
    except UniversalEntryServerRuntimeError as exc:
        assert "activation evidence evaluation is disabled" in str(exc)
    else:
        raise AssertionError("disabled readiness evaluation must fail")


def test_readiness_packet_never_activates():
    runtime = UniversalEntryServerRuntime(
        UniversalEntryServerConfig(activation_evidence_enabled=True)
    )
    evidence = {
        "sdk_validation": {"status": "PASS", "authorizing": False},
        "site_validation": {
            "status": "PASS",
            "authorizing": False,
            "verified_entry_points": [
                "site_chat",
                "sdk",
                "api",
                "portable_node",
                "stegtalk",
                "agent",
                "external_actor_gateway",
            ],
        },
        "canonical_collection": {
            "schema": "stegverse.canonical_source_collection.v0.1",
            "collection_id": "sha256:collection",
            "source_count": 1,
            "projection_count": 1,
            "authorizing": False,
        },
        "provider_verification": {
            "provider_used": True,
            "provider_receipt_id": "provider-receipt-1",
            "usage_event_verified": True,
            "provider_output_is_authority": False,
            "authorizing": False,
        },
        "custody_verification": {
            "custody_verified": True,
            "master_records_installed": True,
            "reconstructability_status": "PASS",
            "authorizing": False,
        },
    }
    packet = runtime.evaluate_readiness(evidence)
    validate_activation_evidence(packet)
    assert packet["ready_for_separate_activation_decision"] is True
    assert packet["activation_performed"] is False
    assert packet["deployment_authorized"] is False
    assert packet["release_authorized"] is False
