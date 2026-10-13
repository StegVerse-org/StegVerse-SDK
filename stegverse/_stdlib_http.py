"""Minimal JSON-over-HTTP client on the standard library.

The SDK's runtime dependency on the third-party ``requests`` package existed
for three call sites that POST or GET JSON. Reduction of framework
dependencies is required, so they use this module instead: one attempt, an
explicit timeout, no retries, no session state. A response with any HTTP
status is returned as a response (as ``requests`` did); only a transport
failure raises ``HttpTransportError``.
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Optional
from urllib import error as urlerror
from urllib import request as urlrequest

MAX_RESPONSE_BYTES = 16 * 1024 * 1024


class HttpTransportError(OSError):
    """The request did not reach a server, or the response could not be read."""


class Response:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.content = body

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.content.decode("utf-8"))


def request(method: str, url: str, *, headers: Optional[Mapping[str, str]] = None,
            json_body: Any = None, timeout: float = 30) -> Response:
    if not url.startswith(("http://", "https://")):
        raise HttpTransportError("url must use http:// or https://")
    data = None
    all_headers = dict(headers or {})
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        all_headers.setdefault("Content-Type", "application/json")
    req = urlrequest.Request(url, data=data, method=method, headers=all_headers)
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            return Response(response.status, response.read(MAX_RESPONSE_BYTES))
    except urlerror.HTTPError as exc:
        return Response(exc.code, exc.read(MAX_RESPONSE_BYTES))
    except (urlerror.URLError, OSError, ValueError) as exc:
        raise HttpTransportError(str(exc)) from exc


def post(url: str, *, json: Any = None, headers: Optional[Mapping[str, str]] = None,  # noqa: A002
         timeout: float = 30) -> Response:
    return request("POST", url, headers=headers, json_body=json, timeout=timeout)


def get(url: str, *, headers: Optional[Mapping[str, str]] = None, timeout: float = 30) -> Response:
    return request("GET", url, headers=headers, timeout=timeout)


__all__ = ["HttpTransportError", "Response", "request", "post", "get"]
