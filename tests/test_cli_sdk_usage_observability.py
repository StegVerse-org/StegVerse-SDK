from __future__ import annotations

import json

from stegverse.cli import main


def test_governance_select_records_usage_and_notification_outbox(tmp_path, monkeypatch, capsys):
    ledger = tmp_path / "usage.jsonl"
    outbox = tmp_path / "outbox.jsonl"
    monkeypatch.setenv("STEGVERSE_SDK_USAGE_LEDGER", str(ledger))
    monkeypatch.setenv("STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX", str(outbox))

    assert main(["governance", "--select", "000"]) == 0
    capsys.readouterr()

    events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    notifications = [json.loads(line) for line in outbox.read_text(encoding="utf-8").splitlines()]

    assert len(events) == 1
    assert events[0]["choice_code"] == "000"
    assert events[0]["choice_label"] == "Demo test sequence without user-supplied manifest"
    assert events[0]["activity_kind"] == "MENU_SELECTION"
    assert len(notifications) == 1
    assert notifications[0]["event"]["choice_code"] == "000"
    assert len(notifications[0]["usage"]["choices"]) == 5


def test_invalid_governance_selection_is_not_recorded(tmp_path, monkeypatch, capsys):
    ledger = tmp_path / "usage.jsonl"
    outbox = tmp_path / "outbox.jsonl"
    monkeypatch.setenv("STEGVERSE_SDK_USAGE_LEDGER", str(ledger))
    monkeypatch.setenv("STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX", str(outbox))

    # argparse rejects invalid --select before _governance_guide is entered.
    try:
        main(["governance", "--select", "invalid"])
    except SystemExit as exc:
        assert exc.code == 2
    capsys.readouterr()

    assert not ledger.exists()
    assert not outbox.exists()
