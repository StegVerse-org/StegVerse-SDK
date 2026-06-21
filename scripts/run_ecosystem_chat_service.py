#!/usr/bin/env python3
"""Local stdlib service runner for Ecosystem Chat SDK pipeline.

This runner is intended for local verification and deployment wrapping. It uses
only Python standard library modules.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http

HOST = "127.0.0.1"
PORT = 8080


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


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), EcosystemChatHandler)
    print(f"Ecosystem Chat SDK service listening on http://{HOST}:{PORT}/api/ecosystem-chat")
    server.serve_forever()


if __name__ == "__main__":
    main()
