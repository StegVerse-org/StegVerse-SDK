"""Frozen JSON Schema 2020-12 reference verdicts, replayed without jsonschema.

The differential tests compare the SDK structural validator with an independent
reference. That reference used to be jsonschema, installed through the [dev]
extra. LLM-adapter#368 Q6 option (b) freezes its answers instead: every query the
tests make is recorded once into tests/fixtures/structural_validator_reference/
verdicts.json by scripts/generate_structural_validator_reference_fixtures.py,
then replayed here with the standard library only.

A query the fixture does not hold fails the test (REFERENCE_FIXTURE_MISS): a new
case needs the generator, never a guessed verdict. With
STEGVERSE_REQUIRE_REFERENCE_VALIDATOR=1 the fixture must also match the pinned
digest below, so the gate cannot pass on an edited or missing fixture.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "structural_validator_reference" / "verdicts.json"
FIXTURE_SCHEMA = "stegverse.structural-validator-reference-verdicts.v1"
# Written by the generator; the fixture's sha256 must equal it when the reference is required.
PINNED_FIXTURE_SHA256 = "65b24b7024720da594a3ac3d9c185ed425d33aaf643bbd456dccaf42b8a36f43"
REQUIRE_REFERENCE = os.environ.get("STEGVERSE_REQUIRE_REFERENCE_VALIDATOR") == "1"
RECORD_TO = os.environ.get("STEGVERSE_RECORD_REFERENCE_VERDICTS")


def query_key(kind: str, schema, instance=None, formats: bool = False) -> str:
    """Stable key; json.dumps keeps 1, 1.0 and true distinct."""
    text = json.dumps([kind, schema, instance, formats], sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SchemaError(Exception):
    """The reference metaschema rejected a schema."""


class ValidationError(Exception):
    """The reference rejected an instance."""


class FormatChecker:
    """Marker: the reference asserts format (recorded under formats=True)."""


GENERATOR = "scripts/generate_structural_validator_reference_fixtures.py"
OWNING_GOAL = "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"


def refusal(failure_code: str, failed_predicate: str, detail: str) -> dict:
    """Six-field FAIL_CLOSED record for every way the frozen reference cannot answer."""
    return {
        "disposition": "FAIL_CLOSED",
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": f"{detail}; regenerate the verdicts with {GENERATOR} and commit the fixture",
        "retry_entrypoint": GENERATOR,
        "owning_existing_goal": OWNING_GOAL,
        "next_attempt": "rerun the tests after the regenerated fixture and its pinned digest are committed",
    }


class ReferenceFixtureMiss(AssertionError):
    """Raised with a six-field FAIL_CLOSED record (also available as .disposition)."""

    def __init__(self, failure_code: str, failed_predicate: str, detail: str):
        self.disposition = refusal(failure_code, failed_predicate, detail)
        super().__init__(json.dumps(self.disposition, sort_keys=True))


def _load(path: Path = FIXTURE):
    if not path.is_file():
        return None
    raw = path.read_bytes()
    data = json.loads(raw)
    if data.get("schema") != FIXTURE_SCHEMA:
        raise ReferenceFixtureMiss("REFERENCE_FIXTURE_SCHEMA_MISMATCH", "REFERENCE_FIXTURE_IS_VERDICT_DOCUMENT",
                                   f"{path} is not a {FIXTURE_SCHEMA} document")
    return hashlib.sha256(raw).hexdigest(), data


_LOADED = _load()


def fixture_status(path: Path = FIXTURE, require: bool = REQUIRE_REFERENCE) -> tuple[bool, str]:
    """(usable, reason). When required, the digest must equal PINNED_FIXTURE_SHA256."""
    loaded = _LOADED if path == FIXTURE else _load(path)
    if loaded is None:
        return False, json.dumps(refusal("REFERENCE_FIXTURE_MISSING", "REFERENCE_FIXTURE_PRESENT",
                                         f"reference fixture missing: {path}"), sort_keys=True)
    digest, _ = loaded
    if require and digest != PINNED_FIXTURE_SHA256:
        return False, json.dumps(refusal("REFERENCE_FIXTURE_DIGEST_MISMATCH", "REFERENCE_FIXTURE_MATCHES_PINNED_DIGEST",
                                         f"reference fixture digest {digest} != pinned {PINNED_FIXTURE_SHA256}"),
                                 sort_keys=True)
    return True, digest


def _answer(table: str, key: str, what: str):
    verdicts = _LOADED[1][table]
    if key not in verdicts:
        raise ReferenceFixtureMiss("REFERENCE_FIXTURE_MISS", "EVERY_REFERENCE_QUERY_IS_RECORDED",
                                   f"{what} is not in {FIXTURE.name}")
    return verdicts[key]


class _Recorder:
    """Real jsonschema behind the replay API; writes every answer it gives."""

    def __init__(self):
        import jsonschema  # generator only; never a test-time dependency
        self.jsonschema = jsonschema
        self.is_valid: dict[str, bool] = {}
        self.check_schema: dict[str, str | None] = {}

    def flush(self):
        path = Path(RECORD_TO)
        existing = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"is_valid": {}, "check_schema": {}}
        existing["is_valid"].update(self.is_valid)
        existing["check_schema"].update(self.check_schema)
        path.write_text(json.dumps(existing, sort_keys=True), encoding="utf-8")


_RECORDER = _Recorder() if RECORD_TO else None
if _RECORDER is not None:
    import atexit
    atexit.register(_RECORDER.flush)


class Draft202012Validator:
    """Replays jsonschema.Draft202012Validator answers for is_valid, validate and check_schema."""

    def __init__(self, schema, format_checker=None):
        self.schema = schema
        self.formats = format_checker is not None

    def is_valid(self, instance) -> bool:
        key = query_key("is_valid", self.schema, instance, self.formats)
        if _RECORDER is not None:
            checker = _RECORDER.jsonschema.FormatChecker() if self.formats else None
            verdict = _RECORDER.jsonschema.Draft202012Validator(self.schema, format_checker=checker).is_valid(instance)
            _RECORDER.is_valid[key] = verdict
            return verdict
        return _answer("is_valid", key, f"is_valid({instance!r}) against {self.schema!r}")

    def validate(self, instance) -> None:
        if not self.is_valid(instance):
            raise ValidationError(f"reference rejects {instance!r}")

    @classmethod
    def check_schema(cls, schema) -> None:
        key = query_key("check_schema", schema)
        if _RECORDER is not None:
            try:
                _RECORDER.jsonschema.Draft202012Validator.check_schema(schema)
                message = None
            except _RECORDER.jsonschema.exceptions.SchemaError as exc:
                message = exc.message
            _RECORDER.check_schema[key] = message
        else:
            message = _answer("check_schema", key, f"check_schema({schema!r})")
        if message is not None:
            raise SchemaError(message)


def reference_validator(fail, skip):
    """Return the replay validator, or fail (required) / skip (not required) when unusable."""
    if _RECORDER is not None:
        return Draft202012Validator
    usable, reason = fixture_status()
    if not usable:
        if REQUIRE_REFERENCE:
            fail(f"reference validator required (STEGVERSE_REQUIRE_REFERENCE_VALIDATOR=1): {reason}")
        skip(f"reference verdicts unavailable: {reason}")
    return Draft202012Validator
