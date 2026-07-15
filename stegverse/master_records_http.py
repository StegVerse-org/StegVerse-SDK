"""Concrete server-side HTTP transport for Master-Records custody and reconstruction.

Credentials are resolved at call time through an injected resolver and are never stored
in returned evidence. This module performs transport only; it does not itself validate
custody or reconstructability. Pair it with MasterRecordsCustodyClient.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable, Mapping
from urllib.parse import quote, urlparse


class MasterRecordsHTTPError(RuntimeError):
    """Raised when Master-Records HTTP transport cannot satisfy its contract."""


TokenResolver = Callable[[str], str]
HTTPExecutor = Callable[[str, str, Mapping[str, str], bytes | None, float], Mapping[str, Any]]


def _validate_base_url(value: str, *, allow_localhost_http: bool) -> str:
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        raise MasterRecordsHTTPError("base_url must be an absolute URL")
    localhost = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (
        allow_localhost_http and localhost and parsed.scheme == "http"
    ):
        raise MasterRecordsHTTPError("remote Master-Records endpoints must use HTTPS")
    if parsed.username or parsed.password:
        raise MasterRecordsHTTPError("base_url must not contain credentials")
    return value.rstrip("/")


def _json_object(value: Mapping[str, Any] | Any, *, operation: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise MasterRecordsHTTPError(f"{operation} response must be a JSON object")
    return dict(value)


@dataclass(frozen=True)
class MasterRecordsHTTPTransport:
    """Server-side HTTP adapter for Master-Records custody routes."""

    base_url: str
    credential_ref: str
    token_resolver: TokenResolver
    executor: HTTPExecutor
    timeout_seconds: float = 15.0
    submit_path: str = "/api/custody/universal-entry"
    reconstruction_path_template: str = "/api/custody/universal-entry/receipts/{receipt_id}/reconstruction"
    allow_localhost_http: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "base_url",
            _validate_base_url(
                self.base_url, allow_localhost_http=self.allow_localhost_http
            ),
        )
        if not self.credential_ref.strip():
            raise MasterRecordsHTTPError("credential_ref is required")
        if self.timeout_seconds <= 0:
            raise MasterRecordsHTTPError("timeout_seconds must be positive")
        if not self.submit_path.startswith("/"):
            raise MasterRecordsHTTPError("submit_path must be an absolute path")
        if "{receipt_id}" not in self.reconstruction_path_template:
            raise MasterRecordsHTTPError(
                "reconstruction_path_template must include {receipt_id}"
            )

    def _headers(self, *, session_id: str | None = None) -> dict[str, str]:
        token = str(self.token_resolver(self.credential_ref)).strip()
        if not token:
            raise MasterRecordsHTTPError("credential resolver returned no token")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "StegVerse-SDK-MasterRecords/0.1",
        }
        if session_id:
            headers["X-SteGVerse-Session"] = session_id
        return headers

    def submit(self, submission: Mapping[str, Any]) -> dict[str, Any]:
        session_id = str(submission.get("session_id", "")).strip()
        if not session_id:
            raise MasterRecordsHTTPError("custody submission session_id is required")
        body = json.dumps(
            dict(submission), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        response = self.executor(
            "POST",
            self.base_url + self.submit_path,
            self._headers(session_id=session_id),
            body,
            self.timeout_seconds,
        )
        return _json_object(response, operation="custody submission")

    def reconstruct(self, receipt_id: str) -> dict[str, Any]:
        receipt_id = receipt_id.strip()
        if not receipt_id:
            raise MasterRecordsHTTPError("receipt_id is required")
        path = self.reconstruction_path_template.format(
            receipt_id=quote(receipt_id, safe="")
        )
        response = self.executor(
            "GET",
            self.base_url + path,
            self._headers(),
            None,
            self.timeout_seconds,
        )
        return _json_object(response, operation="reconstruction")

    def as_custody_client(self):
        """Return the transport-neutral custody client bound to these HTTP methods."""
        from .master_records_custody import MasterRecordsCustodyClient

        return MasterRecordsCustodyClient(
            submit_transport=self.submit,
            reconstruct_transport=self.reconstruct,
        )


__all__ = ["MasterRecordsHTTPError", "MasterRecordsHTTPTransport"]
