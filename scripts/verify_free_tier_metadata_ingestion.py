#!/usr/bin/env python3
"""Verify SDK ingestion of LLM-adapter free-tier trust metadata."""

from __future__ import annotations

import json
from pathlib import Path

from stegverse.free_tier_metadata import validate_free_tier_metadata

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "FREE_TIER_METADATA_INGESTION.md"
MODULE_PATH = ROOT / "stegverse" / "free_tier_metadata.py"
TEST_PATH = ROOT / "tests" / "test_free_tier_metadata.py"


def sample_metadata() -> dict:
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


def main() -> int:
    accepted = validate_free_tier_metadata(sample_metadata()).to_dict()
    bad = sample_metadata()
    bad["receipt_replay_limits"]["non_claims"]["reconstruction_grants_commit_time_standing"] = True
    denied = validate_free_tier_metadata(bad).to_dict()

    checks = {
        "doc_exists": DOC_PATH.exists(),
        "module_exists": MODULE_PATH.exists(),
        "tests_exist": TEST_PATH.exists(),
        "valid_metadata_accepted": accepted["accepted"] is True
        and accepted["metadata_status"] == "accepted_for_non_authorizing_ingestion",
        "accepted_non_authorizing": accepted["non_claims"]["sdk_ingestion_is_execution"] is False
        and accepted["non_claims"]["sdk_ingestion_is_admissibility"] is False
        and accepted["non_claims"]["sdk_ingestion_grants_commit_time_standing"] is False,
        "standing_escalation_denied": denied["accepted"] is False
        and "receipt_replay_limits.non_claims.reconstruction_grants_commit_time_standing must be false" in denied["errors"],
    }

    status = "PASS" if all(checks.values()) else "FAIL"
    print(json.dumps({"status": status, "checks": checks}, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
