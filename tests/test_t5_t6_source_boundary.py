"""T5/T6 non-authorizing source evidence and schema migration boundary checks."""
import json
from pathlib import Path

from stegverse.structural_validator_candidate import (
    CONTRACT, canonical_bytes, check_schema,
)

ROOT = Path(__file__).resolve().parents[1]


def test_t5_candidate_never_claims_authenticated_authority():
    record = json.loads((ROOT / "evidence/validator-source-provenance-candidate-2026-10-13.json").read_text())
    assert record["authority_effect"] == "NONE"
    assert record["disposition"] == "FAIL_CLOSED"
    assert record["authenticated_tv_tvc_proof"] == "NOT_OBSERVED"
    assert record["manifest_bound_origin"] == "NOT_OBSERVED"
    assert record["organization_ledger_readback"] == "NOT_OBSERVED"
    assert record["failed_predicate"] == "AUTHENTICATED_TV_TVC_PROVENANCE_NOT_ESTABLISHED"
    assert all(len(a["git_blob_sha1"]) == 40 and all(c in "0123456789abcdef" for c in a["git_blob_sha1"]) for a in record["artifacts"])


def test_t6_universal_entry_schema_requires_reference_validator():
    # The SDK candidate does not implement arbitrary 2020-12 schema semantics.
    # This schema contains an unrestricted content subschema, so migration must
    # not be inferred from source-level compatibility or a passing fixture.
    schema = json.loads((ROOT / "schemas/universal-entry-envelope.schema.v0.1.json").read_text())
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["request"]["properties"]["content"] == {}
    assert CONTRACT["authority_effect"] == "NONE"
    assert "$ref" not in CONTRACT["supported_keywords"]
