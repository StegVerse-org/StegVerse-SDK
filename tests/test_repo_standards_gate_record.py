from __future__ import annotations

import pytest

from stegverse import (
    REPO_STANDARDS_GATE_ALLOWED_STATES,
    REPO_STANDARDS_GATE_RECORD_SCHEMA_VERSION,
    RepoStandardsGateRecordError,
    build_repo_standards_gate_record,
    normalize_repo_standards_gate_record,
    validate_repo_standards_gate_record,
)


def make_record() -> dict:
    return build_repo_standards_gate_record(
        record_id="repo-standards-release-tag",
        repository="StegVerse-org/StegVerse-SDK",
        gate_state="PENDING",
        source_repository="StegVerse-Labs/repo-standards",
        source_ref="release/tag",
        evidence_refs=["status/release.json", "receipt/validation.json"],
        owner="upstream gate owner",
        next_action="wait for durable release evidence",
    )


def test_public_exports_are_available() -> None:
    assert REPO_STANDARDS_GATE_RECORD_SCHEMA_VERSION == "1.0.0"
    assert REPO_STANDARDS_GATE_ALLOWED_STATES == {
        "PENDING",
        "SATISFIED",
        "BLOCKED",
        "NOT_APPLICABLE",
    }


def test_builds_deterministic_gate_record() -> None:
    first = make_record()
    second = make_record()
    validate_repo_standards_gate_record(first)
    assert first == second
    assert len(first["record_sha256"]) == 64
    assert first["evidence_refs"] == sorted(first["evidence_refs"])


def test_rejects_authority_elevation() -> None:
    record = make_record()
    record.pop("record_sha256")
    record["authority_boundaries"]["record_presence_is_gate_satisfaction"] = True
    with pytest.raises(RepoStandardsGateRecordError):
        normalize_repo_standards_gate_record(record)


def test_rejects_missing_continuation_owner() -> None:
    record = make_record()
    record.pop("record_sha256")
    record["continuation"]["owner"] = ""
    with pytest.raises(RepoStandardsGateRecordError):
        normalize_repo_standards_gate_record(record)
