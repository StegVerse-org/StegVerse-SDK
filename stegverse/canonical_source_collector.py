"""Collect explicitly authorized canonical ecosystem sources.

The collector is transport-neutral. It accepts a source inventory and a dependency-
injected reader, verifies that every source is allowlisted and explicitly canonical,
and converts retrieved content into projection inputs. Repository credentials remain
outside this module and outside browser entry adapters.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Iterable, Mapping, Sequence

from .ecosystem_projection import project_records
from .ecosystem_records import EcosystemRecord


class CanonicalSourceCollectorError(ValueError):
    """Raised when a source inventory or retrieved source violates the contract."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CanonicalSourceSpec:
    source_id: str
    repository: str
    path: str
    record_type: str
    title: str
    observed_at: str
    canonical: bool
    authoritative: bool
    enabled: bool = True
    lifecycle_state: str = "CURRENT"
    receipt_ref: str | None = None
    tags: Sequence[str] = ()
    supersedes: Sequence[str] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CanonicalSourceSpec":
        required = ("source_id", "repository", "path", "record_type", "title", "observed_at")
        missing = [name for name in required if not str(raw.get(name, "")).strip()]
        if missing:
            raise CanonicalSourceCollectorError(
                f"missing canonical source fields: {', '.join(missing)}"
            )
        if raw.get("canonical") is not True or raw.get("authoritative") is not True:
            raise CanonicalSourceCollectorError(
                "canonical sources require canonical=true and authoritative=true"
            )
        return cls(
            source_id=str(raw["source_id"]),
            repository=str(raw["repository"]),
            path=str(raw["path"]),
            record_type=str(raw["record_type"]),
            title=str(raw["title"]),
            observed_at=str(raw["observed_at"]),
            canonical=True,
            authoritative=True,
            enabled=raw.get("enabled", True) is True,
            lifecycle_state=str(raw.get("lifecycle_state", "CURRENT")),
            receipt_ref=(str(raw["receipt_ref"]) if raw.get("receipt_ref") else None),
            tags=tuple(str(value) for value in raw.get("tags", [])),
            supersedes=tuple(str(value) for value in raw.get("supersedes", [])),
        )


SourceReader = Callable[[CanonicalSourceSpec], Mapping[str, Any] | str]


@dataclass(frozen=True)
class CanonicalSourceCollector:
    specs: Sequence[CanonicalSourceSpec]
    reader: SourceReader

    @classmethod
    def from_inventory(
        cls,
        inventory: Iterable[Mapping[str, Any]],
        *,
        reader: SourceReader,
    ) -> "CanonicalSourceCollector":
        specs = tuple(CanonicalSourceSpec.from_mapping(raw) for raw in inventory)
        identities = [spec.source_id for spec in specs]
        locations = [(spec.repository, spec.path) for spec in specs]
        if len(identities) != len(set(identities)):
            raise CanonicalSourceCollectorError("duplicate source_id")
        if len(locations) != len(set(locations)):
            raise CanonicalSourceCollectorError("duplicate repository/path source")
        return cls(specs=specs, reader=reader)

    def collect(self) -> dict[str, Any]:
        """Read enabled sources and return deterministic projections plus evidence."""
        sources: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        for spec in self.specs:
            if not spec.enabled:
                continue
            retrieved = self.reader(spec)
            if isinstance(retrieved, str):
                text = retrieved
                metadata: Mapping[str, Any] = {}
            elif isinstance(retrieved, Mapping):
                text = str(retrieved.get("text", retrieved.get("content", "")))
                metadata = retrieved
            else:
                raise CanonicalSourceCollectorError(
                    f"reader returned unsupported value for {spec.source_id}"
                )
            if not text.strip():
                raise CanonicalSourceCollectorError(
                    f"canonical source returned empty content: {spec.source_id}"
                )
            returned_repository = metadata.get("repository")
            returned_path = metadata.get("path") or metadata.get("source")
            if returned_repository is not None and str(returned_repository) != spec.repository:
                raise CanonicalSourceCollectorError(
                    f"repository identity mismatch: {spec.source_id}"
                )
            if returned_path is not None and str(returned_path) != spec.path:
                raise CanonicalSourceCollectorError(
                    f"source path identity mismatch: {spec.source_id}"
                )
            content_digest = _digest({"text": text})
            expected_digest = metadata.get("content_digest")
            if expected_digest is not None and str(expected_digest) != content_digest:
                raise CanonicalSourceCollectorError(
                    f"content digest mismatch: {spec.source_id}"
                )
            sources.append(
                {
                    "canonical": True,
                    "authoritative": True,
                    "repository": spec.repository,
                    "source": spec.path,
                    "record_type": spec.record_type,
                    "title": spec.title,
                    "text": text,
                    "observed_at": spec.observed_at,
                    "lifecycle_state": spec.lifecycle_state,
                    "receipt_ref": spec.receipt_ref,
                    "tags": list(spec.tags),
                    "supersedes": list(spec.supersedes),
                }
            )
            evidence.append(
                {
                    "source_id": spec.source_id,
                    "repository": spec.repository,
                    "path": spec.path,
                    "content_digest": content_digest,
                    "reader_receipt_ref": metadata.get("receipt_ref"),
                }
            )
        projected = project_records(sources)
        body = {
            "schema": "stegverse.canonical_source_collection.v0.1",
            "authorizing": False,
            "custody_transferred": False,
            "source_count": len(evidence),
            "projection_count": len(projected),
            "evidence": sorted(evidence, key=lambda item: item["source_id"]),
            "projections": projected,
        }
        body["collection_id"] = _digest(body)
        return body


def validate_collection(collection: Mapping[str, Any]) -> dict[str, Any]:
    if collection.get("schema") != "stegverse.canonical_source_collection.v0.1":
        raise CanonicalSourceCollectorError("unsupported collection schema")
    if collection.get("authorizing") is not False or collection.get("custody_transferred") is not False:
        raise CanonicalSourceCollectorError("collection attempted authority or custody escalation")
    evidence = collection.get("evidence")
    projections = collection.get("projections")
    if not isinstance(evidence, list) or not isinstance(projections, list):
        raise CanonicalSourceCollectorError("collection evidence and projections must be lists")
    if collection.get("source_count") != len(evidence):
        raise CanonicalSourceCollectorError("collection source count mismatch")
    if collection.get("projection_count") != len(projections):
        raise CanonicalSourceCollectorError("collection projection count mismatch")
    expected = dict(collection)
    collection_id = expected.pop("collection_id", None)
    if collection_id != _digest(expected):
        raise CanonicalSourceCollectorError("collection digest mismatch")
    seen: set[str] = set()
    for raw in projections:
        if raw.get("canonical_source_declared") is not True:
            raise CanonicalSourceCollectorError("projection lacks canonical-source declaration")
        if not str(raw.get("projection_source_digest", "")).startswith("sha256:"):
            raise CanonicalSourceCollectorError("projection lacks source digest")
        record = EcosystemRecord.from_mapping(raw)
        if record.record_id in seen:
            raise CanonicalSourceCollectorError("duplicate projected record_id")
        seen.add(record.record_id)
    return dict(collection)
