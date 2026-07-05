from copy import deepcopy

from stegverse.free_tier_metadata import validate_free_tier_metadata


def sample_metadata():
    return {
        "schema_version": "stegverse.ai_entry.free_tier_trust.v0.1",
        "preview_only": True,
        "bounded_live_use": True,
        "static_demo_only": False,
        "quota": {
            "status": "ALLOW_QUOTA",
            "tier": "free",
            "allowed": True,
            "reasons": [],
            "upgrade_triggers": [],
            "remaining": {
                "governed_inquiries_today": 5,
                "trial_governed_inquiries_total": 25,
                "receipt_exports_today": 1,
                "replays_today": 1,
            },
            "non_claims": {
                "quota_allow_is_admissibility": False,
                "quota_allow_is_execution_authority": False,
                "provider_response_is_authority": False,
                "upgrade_changes_admissibility_requirements": False,
            },
        },
        "receipt_replay_limits": {
            "status": "ALLOW_LIMIT",
            "tier": "free",
            "allowed": True,
            "reasons": [],
            "upgrade_triggers": [],
            "remaining": {
                "receipt_exports_today": 1,
                "replays_today": 1,
                "reconstructions_today": 1,
            },
            "scope": {
                "reconstruction_scope": "recent_session_limited",
                "full_evidence_bundle_retention_enabled": False,
                "exportable_audit_packet_enabled": False,
                "cross_session_reconstruction_enabled": False,
            },
            "non_claims": {
                "limit_allow_is_admissibility": False,
                "limit_allow_is_execution_authority": False,
                "replay_grants_commit_time_standing": False,
                "reconstruction_grants_commit_time_standing": False,
                "receipt_export_is_permanent_retention": False,
            },
        },
        "trust_window": {
            "curiosity_level_meaningful_inquiries": "3-10",
            "reliance_level_evaluation_inquiries": "20-50",
        },
        "upgrade_for": [
            "higher_quota",
            "private_connectors",
            "premium_models",
            "longer_retention",
            "deeper_replay",
            "deeper_reconstruction",
            "team_workspace",
            "api_access",
            "custom_policy",
            "exportable_audit_packet",
        ],
        "non_claims": {
            "free_tier_response_is_authority": False,
            "quota_allow_is_admissibility": False,
            "limit_allow_is_execution_authority": False,
            "upgrade_changes_admissibility_requirements": False,
        },
    }


def test_accepts_adapter_free_tier_metadata_shape():
    result = validate_free_tier_metadata(sample_metadata())

    assert result.accepted is True
    assert result.metadata_status == "accepted_for_non_authorizing_ingestion"
    assert result.errors == []
    assert result.non_claims["sdk_ingestion_is_execution"] is False
    assert result.non_claims["sdk_ingestion_is_admissibility"] is False


def test_rejects_static_demo_only_true():
    metadata = sample_metadata()
    metadata["static_demo_only"] = True

    result = validate_free_tier_metadata(metadata)

    assert result.accepted is False
    assert "static_demo_only must be false" in result.errors


def test_rejects_missing_upgrade_reasons():
    metadata = sample_metadata()
    metadata["upgrade_for"] = ["higher_quota"]

    result = validate_free_tier_metadata(metadata)

    assert result.accepted is False
    assert any(error.startswith("upgrade_for missing required reasons") for error in result.errors)


def test_rejects_quota_authority_escalation():
    metadata = sample_metadata()
    metadata["quota"]["non_claims"]["quota_allow_is_execution_authority"] = True

    result = validate_free_tier_metadata(metadata)

    assert result.accepted is False
    assert "quota.non_claims.quota_allow_is_execution_authority must be false" in result.errors


def test_rejects_replay_commit_time_standing_escalation():
    metadata = sample_metadata()
    metadata["receipt_replay_limits"]["non_claims"]["replay_grants_commit_time_standing"] = True

    result = validate_free_tier_metadata(metadata)

    assert result.accepted is False
    assert "receipt_replay_limits.non_claims.replay_grants_commit_time_standing must be false" in result.errors


def test_rejects_extra_top_level_keys():
    metadata = deepcopy(sample_metadata())
    metadata["unexpected"] = "value"

    result = validate_free_tier_metadata(metadata)

    assert result.accepted is False
    assert "free_tier_trust keys do not match required contract" in result.errors
