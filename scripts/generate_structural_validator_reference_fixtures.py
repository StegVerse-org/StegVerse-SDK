"""Record the JSON Schema 2020-12 reference verdicts the differential tests use.

LLM-adapter#368 Q6 option (b): the differential tests replay frozen reference
answers (tests/reference_oracle.py) instead of importing jsonschema. This script
is the only place jsonschema is used. Run it once, in an environment that has
jsonschema installed, whenever a differential test adds a query:

    python3 scripts/generate_structural_validator_reference_fixtures.py

It runs the tests that consult the reference with recording on, writes
tests/fixtures/structural_validator_reference/verdicts.json (sorted, so a rerun
over the same tests is byte-identical) and pins its sha256 in
tests/reference_oracle.py. Commit both. jsonschema is not a repository
dependency: nothing at test time imports it.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORACLE = ROOT / "tests" / "reference_oracle.py"
FIXTURE = ROOT / "tests" / "fixtures" / "structural_validator_reference" / "verdicts.json"
TESTS = (
    "tests/test_structural_validator_candidate.py",
    "tests/test_t6_universal_entry_validator.py",
    "tests/test_mhia_module_manifest_schema.py",
)


def main() -> int:
    import jsonschema  # noqa: F401  the reference being frozen; required only here

    with tempfile.TemporaryDirectory() as tmp:
        record = Path(tmp) / "verdicts.json"
        env = dict(os.environ, STEGVERSE_RECORD_REFERENCE_VERDICTS=str(record))
        env.pop("STEGVERSE_REQUIRE_REFERENCE_VALIDATOR", None)
        # -P keeps the root off sys.path, so the installed pytest runs, not the vendored pytest/ shim.
        proc = subprocess.run([sys.executable, "-P", "-m", "pytest", "-q", "-p", "no:cacheprovider", *TESTS],
                              cwd=ROOT, env=env)
        if proc.returncode != 0:
            print("REFERENCE_FIXTURE_NOT_GENERATED: the recorded test run failed", file=sys.stderr)
            return 1
        recorded = json.loads(record.read_text(encoding="utf-8"))
    document = {
        "schema": "stegverse.structural-validator-reference-verdicts.v1",
        "reference": {"implementation": "jsonschema.Draft202012Validator", "version": importlib.metadata.version("jsonschema")},
        "generated_by": "scripts/generate_structural_validator_reference_fixtures.py",
        "recorded_from": list(TESTS),
        "authority_effect": "NONE",
        "is_valid": dict(sorted(recorded["is_valid"].items())),
        "check_schema": dict(sorted(recorded["check_schema"].items())),
    }
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(document, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    text = ORACLE.read_text(encoding="utf-8")
    ORACLE.write_text(re.sub(r'PINNED_FIXTURE_SHA256 = "[0-9a-f]{64}"', f'PINNED_FIXTURE_SHA256 = "{digest}"', text),
                      encoding="utf-8")
    print(f"REFERENCE_FIXTURE_WRITTEN is_valid={len(document['is_valid'])} "
          f"check_schema={len(document['check_schema'])} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
