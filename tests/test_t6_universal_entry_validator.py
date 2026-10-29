"""T6 source-only universal entry validator regression."""
import json
from pathlib import Path

from scripts.verify_universal_entry_envelope import main


def test_invalid_packet_is_non_allow(tmp_path, monkeypatch, capsys):
    source = Path("examples/universal_entry/site_chat_good_morning.json")
    packet = json.loads(source.read_text(encoding="utf-8"))
    packet.pop("routing")
    candidate = tmp_path / "missing-routing.json"
    candidate.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(candidate)])
    assert main() == 1
    assert "FAIL_CLOSED: SCHEMA_INVALID" in capsys.readouterr().out


def test_valid_fixture_still_passes(monkeypatch, capsys):
    source = Path("examples/universal_entry/site_chat_good_morning.json")
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(source)])
    assert main() == 0
    assert "PASS:" in capsys.readouterr().out


def test_schema_failure_reports_non_allow_not_traceback(tmp_path, monkeypatch, capsys):
    packet = json.loads(Path("examples/universal_entry/site_chat_good_morning.json").read_text(encoding="utf-8"))
    packet["routing"] = "invalid"
    candidate = tmp_path / "invalid-routing.json"
    candidate.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(candidate)])
    assert main() == 1
    assert "FAIL_CLOSED: SCHEMA_INVALID routing:" in capsys.readouterr().out


def test_missing_packet_fails_closed(tmp_path, monkeypatch, capsys):
    missing = tmp_path / "absent.json"
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(missing)])
    assert main() == 1
    assert "FAIL_CLOSED: INPUT_OR_SCHEMA_INVALID FileNotFoundError" in capsys.readouterr().out


def test_malformed_json_fails_closed(tmp_path, monkeypatch, capsys):
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{bad-json", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(malformed)])
    assert main() == 1
    assert "FAIL_CLOSED: INPUT_OR_SCHEMA_INVALID JSONDecodeError" in capsys.readouterr().out


def test_missing_schema_fails_closed(tmp_path, monkeypatch, capsys):
    packet = Path("examples/universal_entry/site_chat_good_morning.json")
    missing_schema = tmp_path / "absent-schema.json"
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(packet), "--schema", str(missing_schema)])
    assert main() == 1
    assert "FAIL_CLOSED: INPUT_OR_SCHEMA_INVALID FileNotFoundError" in capsys.readouterr().out


def test_invalid_schema_fails_closed(tmp_path, monkeypatch, capsys):
    packet = Path("examples/universal_entry/site_chat_good_morning.json")
    invalid_schema = tmp_path / "invalid-schema.json"
    invalid_schema.write_text('{"type": "not-a-json-schema-type"}', encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(packet), "--schema", str(invalid_schema)])
    assert main() == 1
    assert "FAIL_CLOSED: INPUT_OR_SCHEMA_INVALID SchemaError" in capsys.readouterr().out


def test_non_object_packet_fails_closed(tmp_path, monkeypatch, capsys):
    candidate = tmp_path / "array-packet.json"
    candidate.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(candidate)])
    assert main() == 1
    assert "FAIL_CLOSED: INPUT_OR_SCHEMA_INVALID ValueError" in capsys.readouterr().out


def test_non_object_schema_fails_closed(tmp_path, monkeypatch, capsys):
    packet = Path("examples/universal_entry/site_chat_good_morning.json")
    schema = tmp_path / "array-schema.json"
    schema.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["verify_universal_entry_envelope", str(packet), "--schema", str(schema)])
    assert main() == 1
    assert "FAIL_CLOSED: INPUT_OR_SCHEMA_INVALID ValueError" in capsys.readouterr().out


def test_permissive_schema_missing_invariant_fields_fails_closed(tmp_path, monkeypatch, capsys):
    packet = json.loads(Path("examples/universal_entry/site_chat_good_morning.json").read_text(encoding="utf-8"))
    packet.pop("routing")
    candidate = tmp_path / "missing-routing.json"
    candidate.write_text(json.dumps(packet), encoding="utf-8")
    schema = tmp_path / "permissive-schema.json"
    schema.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "verify_universal_entry_envelope", str(candidate), "--schema", str(schema)
    ])
    assert main() == 1
    assert "FAIL_CLOSED: INVARIANT_INPUT_INVALID KeyError" in capsys.readouterr().out


def test_permissive_schema_invalid_invariant_type_fails_closed(tmp_path, monkeypatch, capsys):
    packet = json.loads(Path("examples/universal_entry/site_chat_good_morning.json").read_text(encoding="utf-8"))
    packet["routing"] = None
    candidate = tmp_path / "invalid-routing.json"
    candidate.write_text(json.dumps(packet), encoding="utf-8")
    schema = tmp_path / "permissive-schema.json"
    schema.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "verify_universal_entry_envelope", str(candidate), "--schema", str(schema)
    ])
    assert main() == 1
    assert "FAIL_CLOSED: INVARIANT_INPUT_INVALID TypeError" in capsys.readouterr().out


def test_permissive_schema_missing_output_origin_fails_closed(tmp_path, monkeypatch, capsys):
    packet = json.loads(Path("examples/universal_entry/site_chat_good_morning.json").read_text(encoding="utf-8"))
    packet.pop("origin")
    candidate = tmp_path / "missing-origin.json"
    candidate.write_text(json.dumps(packet), encoding="utf-8")
    schema = tmp_path / "permissive-schema.json"
    schema.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("sys.argv", [
        "verify_universal_entry_envelope", str(candidate), "--schema", str(schema)
    ])
    assert main() == 1
    output = capsys.readouterr().out
    assert "FAIL_CLOSED: OUTPUT_EVIDENCE_INVALID KeyError" in output
    assert "PASS:" not in output


def _envelope_mutations(good):
    import copy

    def paths(value, prefix=()):
        yield prefix
        if isinstance(value, dict):
            for key in value:
                yield from paths(value[key], prefix + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from paths(item, prefix + (index,))

    def replaced(path, new, delete=False):
        root = copy.deepcopy(good)
        target = root
        for key in path[:-1]:
            target = target[key]
        if delete:
            del target[path[-1]]
        else:
            target[path[-1]] = new
        return root

    values = [None, True, 0, 1, 1.5, -1, "", "x" * 600, [], ["x", "x"], {}, {"extra": 1}]
    cases = [good]
    for path in list(paths(good))[1:]:
        cases.append(replaced(path, None, delete=True))
        cases.extend(replaced(path, value) for value in values)
    return cases


def test_sdk_validator_agrees_with_reference_on_envelope_mutations():
    # The reference is frozen verdicts (tests/reference_oracle.py); no jsonschema at test time.
    import hashlib

    import pytest

    from tests import reference_oracle

    Draft202012Validator = reference_oracle.reference_validator(pytest.fail, pytest.skip)
    from scripts.verify_universal_entry_envelope import DEFAULT_SCHEMA, structural

    schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    digest = hashlib.sha256(structural.canonical_bytes(schema)).hexdigest()
    reference = Draft202012Validator(schema)
    good = json.loads(Path("examples/universal_entry/site_chat_good_morning.json").read_text(encoding="utf-8"))
    disagreements = [case for case in _envelope_mutations(good)
                     if structural.validate(case, schema, digest)["valid"] != reference.is_valid(case)]
    assert disagreements == []


def test_verifier_imports_only_the_standard_library():
    import ast
    import sys

    tree = ast.parse(Path("scripts/verify_universal_entry_envelope.py").read_text(encoding="utf-8"))
    imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    assert imported <= set(sys.stdlib_module_names) | {"__future__"}
