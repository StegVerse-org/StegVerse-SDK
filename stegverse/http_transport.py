"""Authenticated server-side HTTP transports for universal-entry integrations."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable, Mapping
from urllib import error, request


class HTTPTransportError(RuntimeError):
    """Raised when a governed transport cannot produce a valid bounded response."""


@dataclass(frozen=True)
class AuthenticatedJSONTransport:
    base_url: str
    bearer_token: str | None = None
    session_header: str | None = None
    timeout_seconds: float = 30.0
    opener: Callable[..., Any] = request.urlopen

    def __post_init__(self) -> None:
        if not self.base_url.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            raise HTTPTransportError("transport requires HTTPS except for local development")
        if not self.base_url.rstrip("/"):
            raise HTTPTransportError("base_url is required")
        if self.timeout_seconds <= 0 or self.timeout_seconds > 120:
            raise HTTPTransportError("timeout_seconds outside bounded range")

    def post(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if not path.startswith("/"):
            raise HTTPTransportError("path must be absolute")
        url = self.base_url.rstrip("/") + path
        body = json.dumps(dict(payload), separators=(",", ":")).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        if self.session_header:
            headers["X-SteGVerse-Session"] = self.session_header
        req = request.Request(url=url, data=body, headers=headers, method="POST")
        try:
            with self.opener(req, timeout=self.timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                raw = response.read()
        except error.HTTPError as exc:
            raise HTTPTransportError(f"HTTP_{exc.code}") from exc
        except error.URLError as exc:
            raise HTTPTransportError("TRANSPORT_UNAVAILABLE") from exc
        except TimeoutError as exc:
            raise HTTPTransportError("TRANSPORT_TIMEOUT") from exc
        if status < 200 or status >= 300:
            raise HTTPTransportError(f"HTTP_{status}")
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise HTTPTransportError("INVALID_JSON_RESPONSE") from exc
        if not isinstance(decoded, Mapping):
            raise HTTPTransportError("RESPONSE_MUST_BE_OBJECT")
        return dict(decoded)


@dataclass(frozen=True)
class LLMAdapterHTTPTransport:
    transport: AuthenticatedJSONTransport

    def __call__(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.transport.post("/api/ecosystem-chat", payload)
