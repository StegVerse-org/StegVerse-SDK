"""Authoritative ecosystem record validation and retrieval.

The universal-entry ecosystem lane consumes records, not repository credentials.
This module validates a bounded record catalog, rejects stale/superseded/non-authoritative
entries, and returns deterministic query matches with source provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Iterable, Mapping, Sequence


class EcosystemRecordError(ValueError):
    """Raised when an ecosystem record violates the retrieval contract."""


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class EcosystemRecord:
    record_id: str
    repository: str
    source: str
    record_type: str
    title: str
    text: str
    authoritative: bool
    lifecycle_state: str
    observed_at: str
    supersedes: Sequence[str]
    tags: Sequence[str]
    receipt_ref: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "EcosystemRecord":
        required = ("record_id", "repository", "source", "record_type", "title", "text", "observed_at")
        missing = [name for name in required if not str(value.get(name, "")).strip()]
        if missing:
            raise EcosystemRecordError(f"missing record fields: {', '.join(missing)}")
        lifecycle = str(value.get("lifecycle_state", "CURRENT")).upper()
        if lifecycle not in {"CURRENT", "SUPERSEDED", "DEPRECATED", "QUARANTINED"}:
            raise EcosystemRecordError(f"invalid lifecycle_state: {lifecycle}")
        _parse_time(str(value["observed_at"]))
        return cls(
            record_id=str(value["record_id"]),
            repository=str(value["repository"]),
            source=str(value["source"]),
            record_type=str(value["record_type"]),
            title=str(value["title"]),
            text=str(value["text"]),
            authoritative=value.get("authoritative") is True,
            lifecycle_state=lifecycle,
            observed_at=str(value["observed_at"]),
            supersedes=tuple(str(item) for item in value.get("supersedes", [])),
            tags=tuple(str(item).casefold() for item in value.get("tags", [])),
            receipt_ref=(str(value["receipt_ref"]) if value.get("receipt_ref") else None),
        )

    def to_result(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "repository": self.repository,
            "source": self.source,
            "record_type": self.record_type,
            "title": self.title,
            "text": self.text,
            "observed_at": self.observed_at,
            "receipt_ref": self.receipt_ref,
            "authoritative": True,
        }


def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9][a-z0-9_.-]+", value.casefold()) if len(token) > 2}


@dataclass(frozen=True)
class AuthoritativeEcosystemRetriever:
    records: Sequence[EcosystemRecord]
    max_age_days: int | None = None
    max_results: int = 5

    @classmethod
    def from_mappings(
        cls,
        records: Iterable[Mapping[str, Any]],
        *,
        max_age_days: int | None = None,
        max_results: int = 5,
    ) -> "AuthoritativeEcosystemRetriever":
        parsed = tuple(EcosystemRecord.from_mapping(item) for item in records)
        identifiers = [record.record_id for record in parsed]
        if len(identifiers) != len(set(identifiers)):
            raise EcosystemRecordError("duplicate record_id")
        return cls(parsed, max_age_days=max_age_days, max_results=max_results)

    def __call__(self, query: str, context: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
        now_value = context.get("now")
        now = _parse_time(str(now_value)) if now_value else datetime.now(timezone.utc)
        superseded_ids = {
            old_id
            for record in self.records
            if record.lifecycle_state == "CURRENT"
            for old_id in record.supersedes
        }
        query_tokens = _tokens(query)
        scored: list[tuple[int, datetime, EcosystemRecord]] = []
        for record in self.records:
            if not record.authoritative:
                continue
            if record.lifecycle_state != "CURRENT" or record.record_id in superseded_ids:
                continue
            observed = _parse_time(record.observed_at)
            if self.max_age_days is not None and (now - observed).days > self.max_age_days:
                continue
            corpus = " ".join((record.title, record.text, record.repository, record.record_type, *record.tags))
            score = len(query_tokens & _tokens(corpus))
            if score == 0 and query_tokens:
                continue
            scored.append((score, observed, record))
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [record.to_result() for _, _, record in scored[: self.max_results]]
