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
