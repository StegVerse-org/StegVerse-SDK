from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

import pytest

from stegverse.sdk_usage_observability import (
    CHOICE_CODES,
    CHOICE_LABELS,
    SDKUsageLedger,
)


NOW = datetime(2026, 8, 14, 20, 0, tzinfo=timezone.utc)


def test_all_five_canonical_choices_are_counted(tmp_path):
    ledger = SDKUsageLedger(tmp_path / "usage.jsonl")
    for index, code in enumerate(CHOICE_CODES):
        ledger.record(code, occurred_at=NOW - timedelta(days=index))

    summary = ledger.summary(now=NOW)
    rows = {row["choice_code"]: row for row in summary["choices"]}

    assert tuple(rows) == CHOICE_CODES
    assert summary["lifetime_all_menu_invocations"] == 5
    assert summary["trailing_30_day_all_menu_invocations"] == 5
    assert summary["lifetime_core_governed_invocations"] == 3
    for code in CHOICE_CODES:
        assert rows[code]["choice_label"] == CHOICE_LABELS[code]
        assert rows[code]["lifetime_invocations"] == 1
        assert rows[code]["trailing_30_day_invocations"] == 1
        assert rows[code]["percent_of_total"] == 20.0
        assert rows[code]["menu_selections"] == 1


def test_observed_since_does_not_claim_unrecorded_inception(tmp_path):
    ledger = SDKUsageLedger(tmp_path / "usage.jsonl")
    ledger.record("000", occurred_at=NOW - timedelta(days=45))
    ledger.record("000", occurred_at=NOW - timedelta(days=1))

    summary = ledger.summary(now=NOW)
    row = next(row for row in summary["choices"] if row["choice_code"] == "000")

    assert summary["historical_coverage"] == "OBSERVED_ONLY"
    assert summary["observed_since"] == (NOW - timedelta(days=45)).isoformat()
    assert row["lifetime_invocations"] == 2
    assert row["trailing_30_day_invocations"] == 1


def test_menu_selection_and_governed_operation_remain_distinguishable(tmp_path):
    ledger = SDKUsageLedger(tmp_path / "usage.jsonl")
    ledger.record("1", occurred_at=NOW, activity_kind="MENU_SELECTION")
    ledger.record(
        "1",
        occurred_at=NOW + timedelta(seconds=1),
        activity_kind="GOVERNED_OPERATION",
        manifest_receipt_id="MR-ABCDEF0123456789",
    )

    row = next(row for row in ledger.summary(now=NOW + timedelta(seconds=2))["choices"] if row["choice_code"] == "1")
    assert row["lifetime_invocations"] == 2
    assert row["menu_selections"] == 1
    assert row["governed_operations"] == 1


def test_governed_replay_and_reconstruct_require_receipt_id(tmp_path):
    ledger = SDKUsageLedger(tmp_path / "usage.jsonl")
    for code in ("1", "2"):
        with pytest.raises(ValueError, match="manifest_receipt_id"):
            ledger.record(code, activity_kind="GOVERNED_OPERATION")


def test_reconstruct_cannot_claim_consequence_reexecution(tmp_path):
    ledger = SDKUsageLedger(tmp_path / "usage.jsonl")
    with pytest.raises(ValueError, match="consequence re-execution"):
        ledger.record(
            "2",
            activity_kind="GOVERNED_OPERATION",
            manifest_receipt_id="MR-ABCDEF0123456789",
            consequence_reexecuted=True,
        )


def test_notification_projection_contains_usage_but_no_payload_or_authority(tmp_path):
    ledger = SDKUsageLedger(tmp_path / "usage.jsonl")
    event = ledger.record("00", occurred_at=NOW)
    projection = ledger.notification_projection(event, now=NOW)

    assert projection["schema_version"] == "stegcore.sdk_usage_notification.v1.1"
    assert projection["payload_disclosed"] is False
    assert projection["notification_grants_authority"] is False
    assert "payload" not in projection["event"]
    assert projection["event"]["activity_kind"] == "MENU_SELECTION"
    assert len(projection["usage"]["choices"]) == 5


def test_outbox_contains_safe_projection(tmp_path):
    ledger = SDKUsageLedger(tmp_path / "usage.jsonl")
    event = ledger.record("0", occurred_at=NOW)
    outbox = ledger.enqueue_notification(event, outbox_path=tmp_path / "outbox.jsonl")

    rows = [json.loads(line) for line in outbox.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["event"]["choice_code"] == "0"
    assert rows[0]["payload_disclosed"] is False


def test_ledger_detects_tampering(tmp_path):
    path = tmp_path / "usage.jsonl"
    ledger = SDKUsageLedger(path)
    ledger.record("000", occurred_at=NOW)
    row = json.loads(path.read_text(encoding="utf-8"))
    row["choice_code"] = "2"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="choice label|integrity"):
        SDKUsageLedger(path).events()
