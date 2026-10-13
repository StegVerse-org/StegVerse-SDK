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
