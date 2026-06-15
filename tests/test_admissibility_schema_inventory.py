from __future__ import annotations

import json
from pathlib import Path


EXPECTED_SCHEMA_FILES = {
    "tester-output.schema.json": "stegverse.governed_admissibility.tester_output.v1",
    "dynamic-demo-result.schema.json": "stegverse.governed_admissibility.dynamic_demo_result.v1",
    "llm-bridge-result.schema.json": "stegverse.llm_admissibility.bridge_result.v1",
    "math-bridge-result.schema.json": "stegverse.math_admissibility.bridge_result.v1",
    "bridge-registry.schema.json": None,
    "admissibility-bundle.schema.json": "stegverse.admissibility.bundle.v1",
    "replay-result.schema.json": "stegverse.admissibility.replay_result.v1",
    "gax-exchange.schema.json": "stegverse.admissibility.gax_exchange.v1",
}


def _schema_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "admissibility"


def test_expected_dynamic_admissibility_schema_files_exist():
    schema_dir = _schema_dir()

    for filename in EXPECTED_SCHEMA_FILES:
        assert (schema_dir / filename).exists(), f"missing schema: {filename}"


def test_expected_dynamic_admissibility_schema_constants():
    schema_dir = _schema_dir()

    for filename, expected_const in EXPECTED_SCHEMA_FILES.items():
        schema = json.loads((schema_dir / filename).read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"].endswith(f"/schemas/admissibility/{filename}")
        if expected_const is not None:
            assert schema["properties"]["schema"]["const"] == expected_const


def test_schema_inventory_has_no_untracked_schema_files():
    schema_dir = _schema_dir()
    actual = {path.name for path in schema_dir.glob("*.schema.json")}

    assert actual == set(EXPECTED_SCHEMA_FILES)
