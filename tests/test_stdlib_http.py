"""JSON-over-HTTP on the standard library, which replaced the requests dependency."""
from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from stegverse import _stdlib_http as http
from stegverse.comparison_transport import ComparisonTransportError, submit_comparison

ROOT = Path(__file__).resolve().parents[1]


class _Handler(BaseHTTPRequestHandler):
    seen: list = []

    def _reply(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        type(self).seen.append({"path": self.path, "body": raw, "headers": dict(self.headers)})
        if self.path == "/fail":
            self._reply(503, b'{"detail":"unavailable"}')
        elif self.path == "/notjson":
            self._reply(200, b"not json")
        else:
            self._reply(201, json.dumps({"echo": json.loads(raw)}).encode())

    def do_GET(self):
        self._reply(200, b'{"ok":true}')

    def log_message(self, *_args):
        return


class StdlibHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_post_json_and_read_response(self):
        response = http.post(self.base + "/x", json={"a": 1}, headers={"X-Test": "1"}, timeout=5)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"echo": {"a": 1}})
        sent = _Handler.seen[-1]
        self.assertEqual(json.loads(sent["body"]), {"a": 1})
        self.assertEqual(sent["headers"]["Content-Type"], "application/json")
        self.assertEqual(sent["headers"]["X-Test"], "1")

    def test_http_error_status_is_a_response_not_an_exception(self):
        response = http.post(self.base + "/fail", json={}, timeout=5)
        self.assertEqual(response.status_code, 503)
        self.assertIn("unavailable", response.text)

    def test_get(self):
        self.assertEqual(http.get(self.base + "/y", timeout=5).json(), {"ok": True})

    def test_transport_failure_raises_transport_error(self):
        with self.assertRaises(http.HttpTransportError):
            http.post("http://127.0.0.1:1/unreachable", json={}, timeout=2)
        with self.assertRaises(http.HttpTransportError):
            http.get("file:///etc/passwd")

    def test_comparison_transport_maps_http_failures_to_its_error(self):
        from tests.test_comparison_transport import _request

        with self.assertRaisesRegex(ComparisonTransportError, "comparison transport failed: HTTP 503"):
            submit_comparison(_request(), self.base + "/fail", timeout_seconds=5)
        with self.assertRaisesRegex(ComparisonTransportError, "invalid JSON"):
            submit_comparison(_request(), self.base + "/notjson", timeout_seconds=5)
        with self.assertRaisesRegex(ComparisonTransportError, "comparison transport failed"):
            submit_comparison(_request(), "http://127.0.0.1:1/unreachable", timeout_seconds=2)
        # The envelope reached the endpoint as JSON.
        self.assertEqual(_Handler.seen[-1]["path"], "/notjson")
        json.loads(_Handler.seen[-1]["body"])

    def test_package_declares_no_third_party_runtime_dependency(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        block = text.split("dependencies = [", 1)[1].split("]", 1)[0]
        self.assertEqual([l for l in block.splitlines() if l.strip() and not l.strip().startswith("#")], [])
        for path in sorted((ROOT / "stegverse").rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("\nimport requests", source, str(path))
            self.assertNotIn("\nfrom requests", source, str(path))


if __name__ == "__main__":
    unittest.main()
