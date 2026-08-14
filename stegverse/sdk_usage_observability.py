"""Disclosure-safe usage observation for the canonical SDK governance menu.

This module is an observation surface only. It does not evaluate governance,
grant authority, persist user payloads, or replace Master Records. It records
which canonical governance menu option was selected so option usefulness can be
measured over time, and it can render a safe projection for a TV/TVC-owned
notification bridge.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping
import uuid


CHOICE_CODES = ("000", "00", "0", "1", "2")
CHOICE_LABELS = {
    "000": "Demo test sequence without user-supplied manifest",
    "00": "User-defined run parameters",
    "0": "Submit data for governance",
    "1": "Replay previously run set",
    "2": "Reconstruct previously run set",
}
DEFAULT_RUNTIME_IDENTITY = "stegverse-sdk:governance-navigation:v1"
ENV_LEDGER_PATH = "STEGVERSE_SDK_USAGE_LEDGER"
ENV_NOTIFICATION_OUTBOX = "STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def default_ledger_path() -> Path:
    configured = os.environ.get(ENV_LEDGER_PATH)
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".stegverse" / "sdk-usage-events.jsonl"


def default_outbox_path() -> Path:
    configured = os.environ.get(ENV_NOTIFICATION_OUTBOX)
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".stegverse" / "sdk-usage-notification-outbox.jsonl"


@dataclass(frozen=True)
class UsageEvent:
    event_id: str
    invocation_id: str
    occurred_at: str
    choice_code: str
    choice_label: str
    phase: str
    activity_kind: str
    canonical_runtime_identity: str
    source: str
    manifest_receipt_id: str | None
    transaction_id: str | None
    receipt_chain_head: str | None
    consequence_reexecuted: bool | None
    payload_disclosed: bool
    observation_grants_authority: bool
    event_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "invocation_id": self.invocation_id,
            "occurred_at": self.occurred_at,
            "choice_code": self.choice_code,
            "choice_label": self.choice_label,
            "phase": self.phase,
            "activity_kind": self.activity_kind,
            "canonical_runtime_identity": self.canonical_runtime_identity,
            "source": self.source,
            "manifest_receipt_id": self.manifest_receipt_id,
            "transaction_id": self.transaction_id,
            "receipt_chain_head": self.receipt_chain_head,
            "consequence_reexecuted": self.consequence_reexecuted,
            "payload_disclosed": self.payload_disclosed,
            "observation_grants_authority": self.observation_grants_authority,
            "event_hash": self.event_hash,
        }


def _validate_choice(choice_code: str) -> str:
    code = str(choice_code).strip()
    if code not in CHOICE_CODES:
        raise ValueError("choice_code must be 000, 00, 0, 1, or 2")
    return code


def _event_from_mapping(value: Mapping[str, Any]) -> UsageEvent:
    event = UsageEvent(
        event_id=str(value["event_id"]),
        invocation_id=str(value["invocation_id"]),
        occurred_at=str(value["occurred_at"]),
        choice_code=_validate_choice(str(value["choice_code"])),
        choice_label=str(value["choice_label"]),
        phase=str(value["phase"]),
        activity_kind=str(value.get("activity_kind") or "MENU_SELECTION"),
        canonical_runtime_identity=str(value["canonical_runtime_identity"]),
        source=str(value["source"]),
        manifest_receipt_id=(None if value.get("manifest_receipt_id") is None else str(value["manifest_receipt_id"])),
        transaction_id=(None if value.get("transaction_id") is None else str(value["transaction_id"])),
        receipt_chain_head=(None if value.get("receipt_chain_head") is None else str(value["receipt_chain_head"])),
        consequence_reexecuted=value.get("consequence_reexecuted"),
        payload_disclosed=bool(value.get("payload_disclosed", False)),
        observation_grants_authority=bool(value.get("observation_grants_authority", False)),
        event_hash=str(value["event_hash"]),
    )
    if event.choice_label != CHOICE_LABELS[event.choice_code]:
        raise ValueError("choice label does not match canonical SDK navigation")
    if event.phase not in {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}:
        raise ValueError("unsupported usage event phase")
    if event.activity_kind not in {"MENU_SELECTION", "GOVERNED_OPERATION"}:
        raise ValueError("unsupported usage activity kind")
    if event.payload_disclosed or event.observation_grants_authority:
        raise ValueError("usage observation cannot disclose payload or grant authority")
    if event.consequence_reexecuted is not None and not isinstance(event.consequence_reexecuted, bool):
        raise ValueError("consequence_reexecuted must be boolean or null")
    body = event.to_dict()
    body.pop("event_id")
    body.pop("event_hash")
    expected = _sha256(body)
    if event.event_hash != expected or event.event_id != f"SDK-EVT-{expected.upper()}":
        raise ValueError("usage event integrity mismatch")
    return event


class SDKUsageLedger:
    """Append-only local usage ledger with observed-only historical semantics."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path).expanduser() if path is not None else default_ledger_path()

    def _load(self) -> list[UsageEvent]:
        if not self.path.exists():
            return []
        events: list[UsageEvent] = []
        seen: set[str] = set()
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, Mapping):
                raise ValueError("usage ledger row must be a JSON object")
            event = _event_from_mapping(value)
            if event.event_id in seen:
                raise ValueError("duplicate usage event identity")
            seen.add(event.event_id)
            events.append(event)
        return events

    def events(self) -> list[UsageEvent]:
        return self._load()

    def record(
        self,
        choice_code: str,
        *,
        phase: str = "COMPLETED",
        activity_kind: str = "MENU_SELECTION",
        occurred_at: datetime | None = None,
        canonical_runtime_identity: str = DEFAULT_RUNTIME_IDENTITY,
        source: str = "sdk-governance-navigation",
        invocation_id: str | None = None,
        manifest_receipt_id: str | None = None,
        transaction_id: str | None = None,
        receipt_chain_head: str | None = None,
        consequence_reexecuted: bool | None = None,
    ) -> UsageEvent:
        code = _validate_choice(choice_code)
        if phase not in {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}:
            raise ValueError("unsupported usage event phase")
        if activity_kind not in {"MENU_SELECTION", "GOVERNED_OPERATION"}:
            raise ValueError("unsupported usage activity kind")
        if activity_kind == "GOVERNED_OPERATION" and code in {"1", "2"} and not manifest_receipt_id:
            raise ValueError("governed replay/reconstruct observation requires manifest_receipt_id")
        if code == "2" and consequence_reexecuted is True:
            raise ValueError("reconstruction observation cannot claim consequence re-execution")
        body = {
            "invocation_id": invocation_id or f"SDK-INV-{uuid.uuid4()}",
            "occurred_at": _iso(occurred_at or _utc_now()),
            "choice_code": code,
            "choice_label": CHOICE_LABELS[code],
            "phase": phase,
            "activity_kind": activity_kind,
            "canonical_runtime_identity": canonical_runtime_identity,
            "source": source,
            "manifest_receipt_id": manifest_receipt_id,
            "transaction_id": transaction_id,
            "receipt_chain_head": receipt_chain_head,
            "consequence_reexecuted": consequence_reexecuted,
            "payload_disclosed": False,
            "observation_grants_authority": False,
        }
        event_hash = _sha256(body)
        event = _event_from_mapping({
            **body,
            "event_id": f"SDK-EVT-{event_hash.upper()}",
            "event_hash": event_hash,
        })
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical_json(event.to_dict()) + "\n")
        return event

    def summary(self, *, now: datetime | None = None, trailing_days: int = 30) -> dict[str, Any]:
        if trailing_days <= 0:
            raise ValueError("trailing_days must be positive")
        reference = now or _utc_now()
        if reference.tzinfo is None:
            reference = reference.replace(tzinfo=timezone.utc)
        reference = reference.astimezone(timezone.utc)
        cutoff = reference - timedelta(days=trailing_days)
        events = self._load()
        total = len(events)
        recent = [event for event in events if _parse_iso(event.occurred_at) >= cutoff]
        observed_since = min((_parse_iso(event.occurred_at) for event in events), default=None)
        rows: list[dict[str, Any]] = []
        for code in CHOICE_CODES:
            selected = [event for event in events if event.choice_code == code]
            selected_recent = [event for event in selected if _parse_iso(event.occurred_at) >= cutoff]
            last_used = max((_parse_iso(event.occurred_at) for event in selected), default=None)
            rows.append({
                "choice_code": code,
                "choice_label": CHOICE_LABELS[code],
                "lifetime_invocations": len(selected),
                "trailing_30_day_invocations": len(selected_recent),
                "percent_of_total": (len(selected) / total * 100.0) if total else 0.0,
                "last_used_at": _iso(last_used) if last_used is not None else None,
                "unique_runtime_identities": len({event.canonical_runtime_identity for event in selected}),
                "completed": sum(event.phase == "COMPLETED" for event in selected),
                "failed": sum(event.phase == "FAILED" for event in selected),
                "cancelled": sum(event.phase == "CANCELLED" for event in selected),
                "in_progress": sum(event.phase == "STARTED" for event in selected),
                "menu_selections": sum(event.activity_kind == "MENU_SELECTION" for event in selected),
                "governed_operations": sum(event.activity_kind == "GOVERNED_OPERATION" for event in selected),
            })
        core = [event for event in events if event.choice_code in {"0", "1", "2"}]
        core_recent = [event for event in core if _parse_iso(event.occurred_at) >= cutoff]
        return {
            "artifact_type": "stegverse.sdk_usage_summary",
            "schema_version": "1.1",
            "generated_at": _iso(reference),
            "observed_since": _iso(observed_since) if observed_since else None,
            "historical_coverage": "OBSERVED_ONLY",
            "lifetime_all_menu_invocations": total,
            "trailing_30_day_all_menu_invocations": len(recent),
            "lifetime_core_governed_invocations": len(core),
            "trailing_30_day_core_governed_invocations": len(core_recent),
            "choices": rows,
            "payload_disclosed": False,
            "observation_grants_authority": False,
        }

    def notification_projection(self, event: UsageEvent, *, now: datetime | None = None) -> dict[str, Any]:
        _event_from_mapping(event.to_dict())
        event_projection = event.to_dict()
        event_projection.pop("payload_disclosed")
        event_projection.pop("observation_grants_authority")
        event_projection.pop("event_hash")
        return {
            "schema_version": "stegcore.sdk_usage_notification.v1.1",
            "event": event_projection,
            "usage": self.summary(now=now),
            "payload_disclosed": False,
            "notification_grants_authority": False,
        }

    def enqueue_notification(self, event: UsageEvent, *, outbox_path: str | Path | None = None) -> Path:
        path = Path(outbox_path).expanduser() if outbox_path is not None else default_outbox_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical_json(self.notification_projection(event)) + "\n")
        return path


def record_navigation_selection(choice_code: str) -> UsageEvent:
    """Record one canonical governance-menu selection and queue its safe projection."""
    ledger = SDKUsageLedger()
    event = ledger.record(choice_code, activity_kind="MENU_SELECTION")
    ledger.enqueue_notification(event)
    return event


def record_governed_operation(
    choice_code: str,
    *,
    phase: str = "COMPLETED",
    manifest_receipt_id: str | None = None,
    transaction_id: str | None = None,
    receipt_chain_head: str | None = None,
    consequence_reexecuted: bool | None = None,
    source: str = "sdk-governed-operation",
) -> UsageEvent:
    """Record an actual governed option-0/1/2 operation and queue notification data."""
    code = _validate_choice(choice_code)
    if code not in {"0", "1", "2"}:
        raise ValueError("governed operations are only valid for options 0, 1, or 2")
    ledger = SDKUsageLedger()
    event = ledger.record(
        code,
        phase=phase,
        activity_kind="GOVERNED_OPERATION",
        source=source,
        manifest_receipt_id=manifest_receipt_id,
        transaction_id=transaction_id,
        receipt_chain_head=receipt_chain_head,
        consequence_reexecuted=consequence_reexecuted,
    )
    ledger.enqueue_notification(event)
    return event
