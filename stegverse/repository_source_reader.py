"""Allowlisted server-side repository reader for canonical ecosystem sources.

This adapter owns no connector credentials. A deployment supplies a fetcher callable
that can read repository files. The adapter verifies that each requested canonical
source matches an explicit repository/path/ref binding and that returned content
matches any configured blob or content digest.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Mapping

from .canonical_source_collector import CanonicalSourceSpec


class RepositorySourceReaderError(ValueError):
    """Raised when repository source identity or integrity cannot be verified."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RepositorySourceBinding:
    source_id: str
    repository: str
    path: str
    ref: str
    expected_blob_sha: str | None = None
    expected_content_digest: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "RepositorySourceBinding":
        required = ("source_id", "repository", "path", "ref")
        missing = [name for name in required if not str(raw.get(name, "")).strip()]
        if missing:
            raise RepositorySourceReaderError(
                f"missing repository binding fields: {', '.join(missing)}"
            )
        return cls(
            source_id=str(raw["source_id"]),
            repository=str(raw["repository"]),
            path=str(raw["path"]),
            ref=str(raw["ref"]),
            expected_blob_sha=(
                str(raw["expected_blob_sha"]) if raw.get("expected_blob_sha") else None
            ),
            expected_content_digest=(
                str(raw["expected_content_digest"])
                if raw.get("expected_content_digest")
                else None
            ),
        )


RepositoryFetcher = Callable[[RepositorySourceBinding], Mapping[str, Any] | str]


@dataclass(frozen=True)
class AllowlistedRepositorySourceReader:
    bindings: Mapping[str, RepositorySourceBinding]
    fetcher: RepositoryFetcher

    @classmethod
    def from_bindings(
        cls,
        bindings: list[Mapping[str, Any]],
        *,
        fetcher: RepositoryFetcher,
    ) -> "AllowlistedRepositorySourceReader":
        parsed = [RepositorySourceBinding.from_mapping(raw) for raw in bindings]
        identities = [binding.source_id for binding in parsed]
        locations = [
            (binding.repository, binding.path, binding.ref) for binding in parsed
        ]
        if len(identities) != len(set(identities)):
            raise RepositorySourceReaderError("duplicate repository binding source_id")
        if len(locations) != len(set(locations)):
            raise RepositorySourceReaderError("duplicate repository/path/ref binding")
        return cls({binding.source_id: binding for binding in parsed}, fetcher)

    def __call__(self, spec: CanonicalSourceSpec) -> Mapping[str, Any]:
        binding = self.bindings.get(spec.source_id)
        if binding is None:
            raise RepositorySourceReaderError(
                f"canonical source is not allowlisted: {spec.source_id}"
            )
        if binding.repository != spec.repository or binding.path != spec.path:
            raise RepositorySourceReaderError(
                f"canonical source does not match repository binding: {spec.source_id}"
            )

        raw = self.fetcher(binding)
        if isinstance(raw, str):
            content = raw
            metadata: Mapping[str, Any] = {}
        elif isinstance(raw, Mapping):
            content = str(raw.get("text", raw.get("content", "")))
            metadata = raw
        else:
            raise RepositorySourceReaderError(
                f"fetcher returned unsupported value: {spec.source_id}"
            )
        if not content.strip():
            raise RepositorySourceReaderError(
                f"repository source returned empty content: {spec.source_id}"
            )

        returned_repository = metadata.get("repository")
        returned_path = metadata.get("path") or metadata.get("source")
        returned_ref = metadata.get("ref")
        if returned_repository is not None and str(returned_repository) != binding.repository:
            raise RepositorySourceReaderError("repository identity mismatch")
        if returned_path is not None and str(returned_path) != binding.path:
            raise RepositorySourceReaderError("repository path mismatch")
        if returned_ref is not None and str(returned_ref) != binding.ref:
            raise RepositorySourceReaderError("repository ref mismatch")

        content_digest = _digest({"text": content})
        returned_digest = metadata.get("content_digest")
        if returned_digest is not None and str(returned_digest) != content_digest:
            raise RepositorySourceReaderError("returned content digest mismatch")
        if (
            binding.expected_content_digest is not None
            and binding.expected_content_digest != content_digest
        ):
            raise RepositorySourceReaderError("expected content digest mismatch")

        returned_blob_sha = metadata.get("blob_sha") or metadata.get("sha")
        if (
            binding.expected_blob_sha is not None
            and str(returned_blob_sha or "") != binding.expected_blob_sha
        ):
            raise RepositorySourceReaderError("expected blob sha mismatch")

        return {
            "text": content,
            "repository": binding.repository,
            "path": binding.path,
            "ref": binding.ref,
            "blob_sha": returned_blob_sha,
            "content_digest": content_digest,
            "receipt_ref": metadata.get("receipt_ref"),
            "read_only": True,
            "authorizing": False,
            "custody_transferred": False,
        }
