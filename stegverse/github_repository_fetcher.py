"""Authenticated GitHub file fetcher for allowlisted canonical sources.

Credentials are resolved at call time through a dependency-injected resolver. Tokens are
never stored in source bindings, integration packets, returned metadata, or browser state.
The fetcher uses GitHub's contents API, validates repository/path/ref identity, decodes UTF-8
file content, and returns immutable blob and read-receipt evidence to the existing
AllowlistedRepositorySourceReader.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .repository_source_reader import RepositorySourceBinding


class GitHubRepositoryFetcherError(RuntimeError):
    """Raised when GitHub source retrieval cannot be verified."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


TokenResolver = Callable[[str | None], str | None]
HTTPExecutor = Callable[[Request, float], Mapping[str, Any]]


def _default_http_executor(request: Request, timeout_seconds: float) -> Mapping[str, Any]:
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # nosec B310 - fixed HTTPS API base
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubRepositoryFetcherError(
            f"GitHub contents request failed with HTTP {exc.code}: {detail[:300]}"
        ) from exc
    except URLError as exc:
        raise GitHubRepositoryFetcherError(
            f"GitHub contents request failed: {exc.reason}"
        ) from exc
    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise GitHubRepositoryFetcherError("GitHub contents response was not valid JSON") from exc
    if not isinstance(decoded, Mapping):
        raise GitHubRepositoryFetcherError("GitHub contents response must be an object")
    return decoded


@dataclass(frozen=True)
class GitHubRepositoryFetcher:
    """Read one allowlisted GitHub file at an explicit ref."""

    credential_ref: str | None = None
    token_resolver: TokenResolver | None = None
    http_executor: HTTPExecutor = _default_http_executor
    api_base: str = "https://api.github.com"
    timeout_seconds: float = 15.0
    user_agent: str = "StegVerse-SDK-Universal-Entry/0.1"

    def _token(self) -> str | None:
        if self.credential_ref and self.token_resolver is None:
            raise GitHubRepositoryFetcherError(
                "credential_ref configured without a token resolver"
            )
        token = self.token_resolver(self.credential_ref) if self.token_resolver else None
        if token is not None and not str(token).strip():
            raise GitHubRepositoryFetcherError("token resolver returned an empty token")
        return str(token).strip() if token is not None else None

    def __call__(self, binding: RepositorySourceBinding) -> Mapping[str, Any]:
        if self.api_base.rstrip("/") != "https://api.github.com":
            raise GitHubRepositoryFetcherError("GitHub API base must be https://api.github.com")
        if "/" not in binding.repository:
            raise GitHubRepositoryFetcherError("repository must use owner/name form")
        owner, repo = binding.repository.split("/", 1)
        if not owner or not repo:
            raise GitHubRepositoryFetcherError("repository must use owner/name form")
        encoded_path = "/".join(quote(segment, safe="") for segment in binding.path.split("/"))
        encoded_ref = quote(binding.ref, safe="")
        url = (
            f"{self.api_base.rstrip('/')}/repos/{quote(owner, safe='')}/"
            f"{quote(repo, safe='')}/contents/{encoded_path}?ref={encoded_ref}"
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": self.user_agent,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = self._token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(url, headers=headers, method="GET")
        response = self.http_executor(request, self.timeout_seconds)

        response_type = response.get("type")
        if response_type not in (None, "file"):
            raise GitHubRepositoryFetcherError("GitHub source path did not resolve to a file")
        returned_path = str(response.get("path", ""))
        if returned_path != binding.path:
            raise GitHubRepositoryFetcherError("GitHub response path mismatch")
        blob_sha = str(response.get("sha", ""))
        if not blob_sha:
            raise GitHubRepositoryFetcherError("GitHub response omitted blob sha")
        if binding.expected_blob_sha and blob_sha != binding.expected_blob_sha:
            raise GitHubRepositoryFetcherError("GitHub response blob sha mismatch")
        if response.get("encoding") != "base64":
            raise GitHubRepositoryFetcherError("GitHub file response must use base64 encoding")
        encoded_content = response.get("content")
        if not isinstance(encoded_content, str) or not encoded_content.strip():
            raise GitHubRepositoryFetcherError("GitHub response omitted file content")
        try:
            content_bytes = base64.b64decode(encoded_content, validate=False)
            text = content_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise GitHubRepositoryFetcherError(
                "GitHub file content was not valid UTF-8 base64"
            ) from exc
        if not text.strip():
            raise GitHubRepositoryFetcherError("GitHub source returned empty content")

        content_digest = _digest({"text": text})
        if binding.expected_content_digest and content_digest != binding.expected_content_digest:
            raise GitHubRepositoryFetcherError("GitHub content digest mismatch")
        receipt_body = {
            "schema": "stegverse.github_repository_read_receipt.v0.1",
            "repository": binding.repository,
            "path": binding.path,
            "ref": binding.ref,
            "blob_sha": blob_sha,
            "content_digest": content_digest,
            "read_only": True,
            "authorizing": False,
            "custody_transferred": False,
        }
        receipt_id = _digest(receipt_body)
        return {
            "text": text,
            "repository": binding.repository,
            "path": binding.path,
            "ref": binding.ref,
            "blob_sha": blob_sha,
            "content_digest": content_digest,
            "receipt_ref": receipt_id,
            "read_receipt": {**receipt_body, "receipt_id": receipt_id},
            "read_only": True,
            "authorizing": False,
            "custody_transferred": False,
            "credentials_exposed": False,
        }


__all__ = ["GitHubRepositoryFetcher", "GitHubRepositoryFetcherError"]
