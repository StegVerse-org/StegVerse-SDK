import copy

import pytest

from stegverse.integration_config import (
    IntegrationConfigError,
    build_integration_config,
    validate_integration_config,
)


def source_binding():
    return {
        "source_id": "sdk-handoff",
        "repository": "StegVerse-org/StegVerse-SDK",
        "path": "docs/UNIVERSAL_ENTRY_INTEGRATION_HANDOFF.md",
        "ref": "cbb27a93b0f9bd65b787e789f6e3b26748cd6bb1",
        "expected_blob_sha": "blob-1",
        "expected_content_digest": "sha256:content",
        "read_receipt_required": True,
        "credential_ref": "secret-manager://github/read-only",
    }


def provider_binding():
    return {
        "enabled": True,
        "base_url": "https://gateway.example.test",
        "credential_ref": "secret-manager://llm-adapter/service",
        "expected_service": "stegverse-ecosystem-chat-gateway",
        "expected_schema_version": "1.3.0",
        "session_identity_required": True,
    }


def custody_binding():
    return {
        "enabled": True,
        "base_url": "https://records.example.test",
        "credential_ref": "secret-manager://master-records/custody",
        "expected_service": "stegverse-master-records",
        "expected_schema_version": "1.0.0",
        "session_identity_required": True,
    }


def packet():
    return build_integration_config(
        environment="staging",
        source_bindings=[source_binding()],
        provider=provider_binding(),
        custody=custody_binding(),
        site_same_origin_route="/api/universal-entry",
    )


def test_build_and_validate_non_secret_configuration():
    result = packet()
    assert validate_integration_config(result) == result
    assert result["credentials_embedded"] is False
    assert result["credentials_exposed_to_entry_adapter"] is False
    assert result["deployment_authorized"] is False
    assert result["activation_performed"] is False
    assert result["provider"]["required_path"] == "/api/ecosystem-chat"
    assert result["custody"]["required_path"] == "/api/custody/universal-entry"


def test_configuration_is_deterministic_across_source_order():
    second = source_binding()
    second.update(
        {
            "source_id": "site-handoff",
            "repository": "StegVerse-Labs/Site",
            "path": "docs/SITE_MIRROR_HANDOFF.md",
            "ref": "0c076216f980f6b3c91677571d0692153d7ce94f",
        }
    )
    first = build_integration_config(
        environment="staging",
        source_bindings=[source_binding(), second],
    )
    reversed_packet = build_integration_config(
        environment="staging",
        source_bindings=[second, source_binding()],
    )
    assert first == reversed_packet


def test_embedded_secret_is_rejected():
    provider = provider_binding()
    provider["token"] = "do-not-store-this"
    with pytest.raises(IntegrationConfigError, match="embedded credential material"):
        build_integration_config(environment="staging", provider=provider)


def test_remote_http_endpoint_is_rejected():
    provider = provider_binding()
    provider["base_url"] = "http://gateway.example.test"
    with pytest.raises(IntegrationConfigError, match="must use HTTPS"):
        build_integration_config(environment="staging", provider=provider)


def test_url_embedded_credentials_are_rejected():
    provider = provider_binding()
    provider["base_url"] = "https://user:password@gateway.example.test"
    with pytest.raises(IntegrationConfigError, match="must not contain credentials"):
        build_integration_config(environment="staging", provider=provider)


def test_site_route_must_be_same_origin_path():
    with pytest.raises(IntegrationConfigError, match="same-origin"):
        build_integration_config(
            environment="staging",
            site_same_origin_route="https://gateway.example.test/api/universal-entry",
        )


def test_duplicate_source_binding_is_rejected():
    with pytest.raises(IntegrationConfigError, match="duplicate source_id"):
        build_integration_config(
            environment="staging",
            source_bindings=[source_binding(), source_binding()],
        )


def test_required_service_path_mismatch_is_rejected():
    built = packet()
    provider = dict(built["provider"])
    provider["required_path"] = "/api/other"
    with pytest.raises(IntegrationConfigError, match="required path mismatch"):
        build_integration_config(
            environment="staging",
            source_bindings=built["source_bindings"],
            provider=provider,
            custody=built["custody"],
            site_same_origin_route=built["site_same_origin_route"],
        )


def test_tamper_and_authority_escalation_fail_closed():
    altered = copy.deepcopy(packet())
    altered["deployment_authorized"] = True
    with pytest.raises(IntegrationConfigError, match="escalated deployment_authorized"):
        validate_integration_config(altered)

    altered = copy.deepcopy(packet())
    altered["environment"] = "production"
    with pytest.raises(IntegrationConfigError, match="digest mismatch"):
        validate_integration_config(altered)
