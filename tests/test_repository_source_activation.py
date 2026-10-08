from copy import deepcopy

import pytest

from stegverse.activation_evidence import (
    LEGACY_ORGANIZATION_RECORD_CLAIM_FIELD,
    LEGACY_ORGANIZATION_RECORD_NOT_VERIFIED,
    ORGANIZATION_RECORD_CLAIM_FIELD,
    ORGANIZATION_RECORD_NOT_VERIFIED,
    ActivationEvidenceError,
    _digest as _activation_digest,
    evaluate_activation_evidence,
    is_organization_record_blocker,
    validate_activation_evidence,
)
from stegverse.canonical_source_collector import CanonicalSourceCollector
from stegverse.repository_source_reader import (
    AllowlistedRepositorySourceReader,
    RepositorySourceReaderError,
)


def inventory():
    return [
        {
            "source_id": "site-handoff",
            "repository": "StegVerse-Labs/Site",
            "path": "docs/SITE_MIRROR_HANDOFF.md",
            "record_type": "handoff",
            "title": "Site handoff",
            "observed_at": "2026-07-14T20:00:00Z",
            "canonical": True,
            "authoritative": True,
        }
    ]


def bindings():
    return [
        {
            "source_id": "site-handoff",
            "repository": "StegVerse-Labs/Site",
            "path": "docs/SITE_MIRROR_HANDOFF.md",
            "ref": "main",
            "expected_blob_sha": "blob-1",
        }
    ]


def test_allowlisted_reader_collects_verified_source():
    def fetcher(binding):
        return {
            "content": "Current Site handoff content",
            "repository": binding.repository,
            "path": binding.path,
            "ref": binding.ref,
            "blob_sha": "blob-1",
            "receipt_ref": "github-read:1",
        }

    reader = AllowlistedRepositorySourceReader.from_bindings(bindings(), fetcher=fetcher)
    collector = CanonicalSourceCollector.from_inventory(inventory(), reader=reader)
    result = collector.collect()
    assert result["source_count"] == 1
    assert result["projections"][0]["repository"] == "StegVerse-Labs/Site"
    assert result["evidence"][0]["reader_receipt_ref"] == "github-read:1"


def test_reader_rejects_unbound_source():
    reader = AllowlistedRepositorySourceReader.from_bindings([], fetcher=lambda binding: "x")
    collector = CanonicalSourceCollector.from_inventory(inventory(), reader=reader)
    with pytest.raises(RepositorySourceReaderError, match="not allowlisted"):
        collector.collect()


def test_reader_rejects_ref_or_blob_mismatch():
    def fetcher(binding):
        return {
            "content": "content",
            "repository": binding.repository,
            "path": binding.path,
            "ref": "develop",
            "blob_sha": "wrong",
        }

    reader = AllowlistedRepositorySourceReader.from_bindings(bindings(), fetcher=fetcher)
    collector = CanonicalSourceCollector.from_inventory(inventory(), reader=reader)
    with pytest.raises(RepositorySourceReaderError, match="ref mismatch"):
        collector.collect()


def complete_evidence():
    entry_points = [
        "site_chat",
        "sdk",
        "api",
        "portable_node",
        "stegtalk",
        "agent",
        "external_actor_gateway",
    ]
    return {
        "sdk_validation": {"status": "PASS", "authorizing": False},
        "site_validation": {
            "status": "PASS",
            "authorizing": False,
            "verified_entry_points": entry_points,
        },
        "canonical_collection": {
            "schema": "stegverse.canonical_source_collection.v0.1",
            "collection_id": "sha256:collection",
            "source_count": 2,
            "projection_count": 2,
            "authorizing": False,
        },
        "provider_verification": {
            "status": "PASS",
            "provider_used": True,
            "provider_receipt_id": "provider:receipt:1",
            "usage_event_verified": True,
            "provider_output_is_authority": False,
            "authorizing": False,
        },
        "organization_record_verification": {
            "status": "PASS",
            "organization_record_installed": True,
            "reconstructability_status": "PASS",
            "authorizing": False,
        },
    }


def legacy_evidence():
    """Evidence shaped by peers deployed before the organization-record migration."""
    evidence = complete_evidence()
    del evidence["organization_record_verification"]
    evidence["custody_verification"] = {
        "status": "PASS",
        "custody_verified": True,
        "master_records_installed": True,
        "reconstructability_status": "PASS",
        "authorizing": False,
    }
    return evidence


def test_activation_evidence_ready_but_does_not_activate():
    packet = evaluate_activation_evidence(complete_evidence())
    assert packet["ready_for_separate_activation_decision"] is True
    assert packet["activation_performed"] is False
    assert packet["deployment_authorized"] is False
    assert packet["release_authorized"] is False
    assert validate_activation_evidence(packet) == packet


def test_activation_evidence_preserves_blockers():
    evidence = complete_evidence()
    evidence["provider_verification"]["provider_used"] = False
    evidence["organization_record_verification"]["reconstructability_status"] = "PENDING"
    evidence["site_validation"]["verified_entry_points"] = ["site_chat"]
    packet = evaluate_activation_evidence(evidence)
    assert packet["ready_for_separate_activation_decision"] is False
    assert "LIVE_PROVIDER_RESULT_NOT_VERIFIED" in packet["blockers"]
    assert "RECONSTRUCTABILITY_NOT_PASS" in packet["blockers"]
    assert any(value.startswith("ENTRY_POINT_PARITY_NOT_VERIFIED:") for value in packet["blockers"])


def test_activation_evidence_rejects_missing_or_escalating_records():
    evidence = complete_evidence()
    del evidence["sdk_validation"]
    with pytest.raises(ActivationEvidenceError, match="missing activation evidence"):
        evaluate_activation_evidence(evidence)

    evidence = complete_evidence()
    evidence["site_validation"]["deployment_authorized"] = True
    with pytest.raises(ActivationEvidenceError, match="authority escalation"):
        evaluate_activation_evidence(evidence)


def test_activation_evidence_detects_tamper():
    packet = evaluate_activation_evidence(complete_evidence())
    tampered = deepcopy(packet)
    tampered["verified_entry_points"].append("unknown")
    with pytest.raises(ActivationEvidenceError, match="digest mismatch"):
        validate_activation_evidence(tampered)


def test_activation_packet_writes_only_organization_record_names():
    packet = evaluate_activation_evidence(complete_evidence())
    assert packet[ORGANIZATION_RECORD_CLAIM_FIELD] is False
    assert LEGACY_ORGANIZATION_RECORD_CLAIM_FIELD not in packet
    assert "organization_record_verification" in packet["evidence_digests"]
    assert "custody_verification" not in packet["evidence_digests"]


def test_organization_record_must_exist_and_be_reconstructable():
    evidence = complete_evidence()
    evidence["organization_record_verification"]["organization_record_installed"] = False
    packet = evaluate_activation_evidence(evidence)
    assert packet["ready_for_separate_activation_decision"] is False
    assert ORGANIZATION_RECORD_NOT_VERIFIED in packet["blockers"]
    assert ORGANIZATION_RECORD_NOT_VERIFIED == "MASTER_RECORDS_ORGANIZATION_RECORD_NOT_VERIFIED"
    assert LEGACY_ORGANIZATION_RECORD_NOT_VERIFIED not in packet["blockers"]

    evidence = complete_evidence()
    evidence["organization_record_verification"]["reconstructability_status"] = "PENDING"
    packet = evaluate_activation_evidence(evidence)
    assert packet["blockers"] == ["RECONSTRUCTABILITY_NOT_PASS"]


def test_legacy_evidence_names_are_still_read():
    packet = evaluate_activation_evidence(legacy_evidence())
    assert packet["ready_for_separate_activation_decision"] is True
    assert validate_activation_evidence(packet) == packet

    for field in ("custody_verified", "master_records_installed"):
        evidence = legacy_evidence()
        evidence["custody_verification"][field] = False
        packet = evaluate_activation_evidence(evidence)
        assert packet["blockers"] == [ORGANIZATION_RECORD_NOT_VERIFIED]


def test_legacy_and_new_evidence_keys_together_are_rejected():
    evidence = complete_evidence()
    evidence["custody_verification"] = dict(evidence["organization_record_verification"])
    with pytest.raises(ActivationEvidenceError, match="legacy name"):
        evaluate_activation_evidence(evidence)


def test_legacy_blocker_codes_are_recognized():
    assert is_organization_record_blocker("MASTER_RECORDS_ORGANIZATION_RECORD_NOT_VERIFIED")
    assert is_organization_record_blocker("MASTER_RECORDS_CUSTODY_NOT_VERIFIED")
    assert is_organization_record_blocker("MASTER_RECORDS_INSTALLATION_NOT_VERIFIED")
    assert not is_organization_record_blocker("RECONSTRUCTABILITY_NOT_PASS")


def test_legacy_packet_claim_field_is_still_validated():
    packet = evaluate_activation_evidence(complete_evidence())
    legacy = {k: v for k, v in packet.items() if k not in ("evidence_packet_id", ORGANIZATION_RECORD_CLAIM_FIELD)}
    legacy[LEGACY_ORGANIZATION_RECORD_CLAIM_FIELD] = False
    legacy["evidence_packet_id"] = _activation_digest(legacy)
    assert validate_activation_evidence(legacy) == legacy

    escalated = dict(legacy)
    escalated[LEGACY_ORGANIZATION_RECORD_CLAIM_FIELD] = True
    with pytest.raises(ActivationEvidenceError, match="escalation"):
        validate_activation_evidence(escalated)
