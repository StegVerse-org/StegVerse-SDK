#!/usr/bin/env python3
"""Local stdlib runner for the Ecosystem Chat SDK pipeline (event-bounded).

This runner is intended for local verification and deployment wrapping. It uses
only Python standard library modules. It is NOT a resident process: it handles
``--max-requests`` requests (default 1) via a bounded ``handle_request()`` loop
and then exits with a JSON receipt (.github #98, nonconformance 98-D3). Request
handling itself lives in ``stegverse.ecosystem_chat_pipeline_http``.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http

HOST = "127.0.0.1"
PORT = 8080
AUTHORITY_EFFECT = "NONE_LOCAL_VERIFICATION_ONLY"
UNBOUNDED_NOTICE = (
    "NOTICE: --max-requests 0 is a local-verification mode (unbounded until interrupted); "
    "this runner is not a resident service."
)


class EcosystemChatHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        status, response = handle_ecosystem_chat_pipeline_http("POST", self.path, body)
        self._send_json(status, response)

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        status, response = handle_ecosystem_chat_pipeline_http("GET", self.path, b"{}")
        self._send_json(status, response)

    def _send_json(self, status: int, response: dict) -> None:
        encoded = json.dumps(response, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - stdlib signature
        return


class BoundedServer(HTTPServer):
    """Synchronous server: each ``handle_request()`` completes one request, so the bound is exact."""

    def __init__(self, address: tuple[str, int], max_requests: int):
        super().__init__(address, EcosystemChatHandler)
        self.max_requests = max_requests
        self.handled_requests = 0


def build_server(host: str, port: int, max_requests: int) -> BoundedServer:
    return BoundedServer((host, port), max_requests)


def serve(server: BoundedServer) -> dict:
    """Handle at most ``server.max_requests`` requests (0 = unbounded), close, and return a receipt."""
    try:
        while not server.max_requests or server.handled_requests < server.max_requests:
            server.handle_request()
            server.handled_requests += 1
    finally:
        server.server_close()
    return {
        "requests_handled": server.handled_requests,
        "max_requests": server.max_requests,
        "resident_process": False,
        "authority_effect": AUTHORITY_EFFECT,
    }


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("--max-requests must be >= 0")
    return parsed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bounded local runner for the Ecosystem Chat SDK pipeline.")
    parser.add_argument("--bind", default=HOST, help=f"bind address (default {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"bind port; 0 = ephemeral (default {PORT})")
    parser.add_argument(
        "--max-requests",
        type=_non_negative_int,
        default=1,
        help="handle N requests then exit (default 1); 0 = unbounded local-verification mode",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    server = build_server(args.bind, args.port, args.max_requests)
    host, port = server.server_address[0], server.server_address[1]
    print(f"Ecosystem Chat SDK runner listening on http://{host}:{port}/api/ecosystem-chat")
    if args.max_requests == 0:
        print(UNBOUNDED_NOTICE)
    else:
        print(f"Handling at most {args.max_requests} request(s), then exiting.")
    receipt = serve(server)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
