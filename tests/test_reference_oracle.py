"""The frozen reference fails closed: unknown queries, edited fixtures and missing fixtures never pass."""
import hashlib
import json

import pytest

from tests import reference_oracle


def test_fixture_matches_its_pinned_digest():
    raw = reference_oracle.FIXTURE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == reference_oracle.PINNED_FIXTURE_SHA256
    document = json.loads(raw)
    assert document["schema"] == reference_oracle.FIXTURE_SCHEMA
    assert document["authority_effect"] == "NONE"
    assert document["is_valid"] and document["check_schema"]


def test_a_query_the_fixture_does_not_hold_fails_closed():
    validator = reference_oracle.Draft202012Validator({"type": "string", "x-never-recorded": True})
    with pytest.raises(reference_oracle.ReferenceFixtureMiss, match="REFERENCE_FIXTURE_MISS"):
        validator.is_valid("anything")
    with pytest.raises(reference_oracle.ReferenceFixtureMiss):
        reference_oracle.Draft202012Validator.check_schema({"x-never-recorded": True})


SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
              "owning_existing_goal", "next_attempt")


def test_every_refusal_carries_the_six_fields(tmp_path):
    with pytest.raises(reference_oracle.ReferenceFixtureMiss) as miss:
        reference_oracle.Draft202012Validator({"x-never-recorded": 1}).is_valid(0)
    records = [miss.value.disposition, json.loads(str(miss.value))]
    for path in (tmp_path / "absent.json",):
        records.append(json.loads(reference_oracle.fixture_status(path, require=True)[1]))
    edited = tmp_path / "edited.json"
    edited.write_bytes(reference_oracle.FIXTURE.read_bytes().replace(b'"NONE"', b'"NONE" ', 1))
    records.append(json.loads(reference_oracle.fixture_status(edited, require=True)[1]))
    codes = [r["failure_code"] for r in records]
    assert codes == ["REFERENCE_FIXTURE_MISS", "REFERENCE_FIXTURE_MISS", "REFERENCE_FIXTURE_MISSING",
                     "REFERENCE_FIXTURE_DIGEST_MISMATCH"]
    for record in records:
        assert record["disposition"] == "FAIL_CLOSED"
        assert all(isinstance(record[f], str) and record[f] for f in SIX_FIELDS), record


def test_recorded_verdicts_replay_including_rejections():
    # Both directions are recorded: a reference rejection must replay as a rejection.
    rejects = reference_oracle.Draft202012Validator({"type": "array", "items": {"type": "integer"}})
    assert rejects.is_valid([1, 2]) is True
    assert rejects.is_valid([1, "x"]) is False
    with pytest.raises(reference_oracle.ValidationError):
        rejects.validate([1, "x"])


def test_required_reference_rejects_an_edited_or_missing_fixture(tmp_path):
    edited = tmp_path / "verdicts.json"
    edited.write_bytes(reference_oracle.FIXTURE.read_bytes().replace(b'"NONE"', b'"NONE" ', 1))
    assert reference_oracle.fixture_status(reference_oracle.FIXTURE, require=True)[0] is True
    assert reference_oracle.fixture_status(edited, require=True)[0] is False
    assert reference_oracle.fixture_status(edited, require=False)[0] is True
    assert reference_oracle.fixture_status(tmp_path / "absent.json", require=True)[0] is False
    assert reference_oracle.fixture_status(tmp_path / "absent.json", require=False)[0] is False


def test_no_test_imports_jsonschema():
    from pathlib import Path
    here = Path(__file__).resolve()
    offenders = []
    for path in here.parent.glob("test_*.py"):
        text = path.read_text(encoding="utf-8")
        if path != here and ("import jsonschema" in text or "from jsonschema" in text):
            offenders.append(path.name)
    assert offenders == []
