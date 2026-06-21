"""WSGI app for Ecosystem Chat SDK pipeline."""

from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from .ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http

StartResponse = Callable[[str, list[tuple[str, str]]], None]


def application(environ: dict[str, Any], start_response: StartResponse) -> Iterable[bytes]:
    method = str(environ.get("REQUEST_METHOD", ""))
    path = str(environ.get("PATH_INFO", ""))
    body = _read_body(environ)

    status_code, result = handle_ecosystem_chat_pipeline_http(method, path, body)
    encoded = json.dumps(result, sort_keys=True).encode("utf-8")
    start_response(
        _status_line(status_code),
        [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(encoded))),
        ],
    )
    return [encoded]


def _read_body(environ: dict[str, Any]) -> bytes:
    try:
        length = int(environ.get("CONTENT_LENGTH") or "0")
    except ValueError:
        length = 0
    stream = environ.get("wsgi.input")
    if not stream or length <= 0:
        return b""
    return stream.read(length)


def _status_line(status_code: int) -> str:
    reason = {
        202: "Accepted",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        422: "Unprocessable Entity",
    }.get(status_code, "OK")
    return f"{status_code} {reason}"
