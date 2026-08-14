from __future__ import annotations

import json
import os

from stegverse.cli import main


def _with_usage_paths(ledger, outbox):
    old_ledger = os.environ.get("STEGVERSE_SDK_USAGE_LEDGER")
    old_outbox = os.environ.get("STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX")
    os.environ["STEGVERSE_SDK_USAGE_LEDGER"] = str(ledger)
    os.environ["STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX"] = str(outbox)
    return old_ledger, old_outbox


def _restore_usage_paths(old_ledger, old_outbox):
    if old_ledger is None:
        os.environ.pop("STEGVERSE_SDK_USAGE_LEDGER", None)
    else:
        os.environ["STEGVERSE_SDK_USAGE_LEDGER"] = old_ledger
    if old_outbox is None:
        os.environ.pop("STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX", None)
    else:
        os.environ["STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX"] = old_outbox


def test_governance_select_records_usage_and_notification_outbox(tmp_path):
    ledger = tmp_path / "usage.jsonl"
    outbox = tmp_path / "outbox.jsonl"
    old_ledger, old_outbox = _with_usage_paths(ledger, outbox)
    try:
        assert main(["governance", "--select", "000"]) == 0
    finally:
        _restore_usage_paths(old_ledger, old_outbox)

    events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    notifications = [json.loads(line) for line in outbox.read_text(encoding="utf-8").splitlines()]

    assert len(events) == 1
    assert events[0]["choice_code"] == "000"
    assert events[0]["choice_label"] == "Demo test sequence without user-supplied manifest"
    assert events[0]["activity_kind"] == "MENU_SELECTION"
    assert len(notifications) == 1
    assert notifications[0]["event"]["choice_code"] == "000"
    assert len(notifications[0]["usage"]["choices"]) == 5


def test_invalid_governance_selection_is_not_recorded(tmp_path):
    ledger = tmp_path / "usage.jsonl"
    outbox = tmp_path / "outbox.jsonl"
    old_ledger, old_outbox = _with_usage_paths(ledger, outbox)
    try:
        # argparse rejects invalid --select before _governance_guide is entered.
        try:
            main(["governance", "--select", "invalid"])
        except SystemExit as exc:
            assert exc.code == 2
    finally:
        _restore_usage_paths(old_ledger, old_outbox)

    assert not ledger.exists()
    assert not outbox.exists()
