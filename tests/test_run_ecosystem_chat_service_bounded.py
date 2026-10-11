"""The local Ecosystem Chat runner is event-bounded, not a resident process (.github #98, 98-D3).

Mirrors the Labs ``handle_request()`` / ``--max-requests`` pattern: the runner
handles N requests (default 1) and exits with a JSON receipt. Stdlib only.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from tests.test_ecosystem_chat_intake_minimal import payload

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_ecosystem_chat_service.py"

_spec = importlib.util.spec_from_file_location("run_ecosystem_chat_service", SCRIPT)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)


def _last_json(text: str) -> dict:
    lines = [line for line in text.splitlines() if line.strip()]
    return json.loads(lines[-1])


def _post(port: int, body: dict) -> int:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/ecosystem-chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


class BoundedServeTests(unittest.TestCase):
    def _serve_in_thread(self, max_requests: int):
        server = runner.build_server("127.0.0.1", 0, max_requests)
        port = server.server_address[1]
        result: dict = {}

        def target() -> None:
            result["receipt"] = runner.serve(server)

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        return port, thread, result

    def test_source_has_no_resident_listener(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("serve_forever", text)
        self.assertIn("handle_request", text)
        self.assertIn("--max-requests", text)

    def test_stops_after_exact_request_bound_and_emits_receipt(self):
        port, thread, result = self._serve_in_thread(2)
        self.assertEqual(_post(port, payload()), 202)
        self.assertEqual(_post(port, {}), 422)
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive(), "runner must exit after max_requests")
        self.assertEqual(
            result["receipt"],
            {
                "requests_handled": 2,
                "max_requests": 2,
                "resident_process": False,
                "authority_effect": "NONE_LOCAL_VERIFICATION_ONLY",
            },
        )
        with self.assertRaises(urllib.error.URLError):
            _post(port, {})

    def test_default_bound_is_one_request(self):
        self.assertEqual(runner.parse_args([]).max_requests, 1)
        port, thread, result = self._serve_in_thread(runner.parse_args([]).max_requests)
        self.assertEqual(_post(port, payload()), 202)
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(result["receipt"]["requests_handled"], 1)
        self.assertEqual(result["receipt"]["max_requests"], 1)
        self.assertIs(result["receipt"]["resident_process"], False)

    def test_main_default_is_bounded_and_prints_receipt(self):
        receipt = {
            "requests_handled": 1,
            "max_requests": 1,
            "resident_process": False,
            "authority_effect": "NONE_LOCAL_VERIFICATION_ONLY",
        }
        out = io.StringIO()
        with patch.object(runner, "serve", return_value=receipt) as serve, contextlib.redirect_stdout(out):
            rc = runner.main(["--port", "0"])
        self.assertEqual(rc, 0)
        self.assertEqual(serve.call_args.args[0].max_requests, 1)
        text = out.getvalue()
        self.assertNotIn(runner.UNBOUNDED_NOTICE, text)
        self.assertEqual(_last_json(text), receipt)

    def test_main_unbounded_requires_explicit_zero_and_prints_notice(self):
        out = io.StringIO()
        with patch.object(runner, "serve", return_value={}) as serve, contextlib.redirect_stdout(out):
            runner.main(["--max-requests", "0", "--port", "0"])
        self.assertEqual(serve.call_args.args[0].max_requests, 0)
        text = out.getvalue()
        self.assertIn(runner.UNBOUNDED_NOTICE, text)
        self.assertIn("local-verification mode", runner.UNBOUNDED_NOTICE)
        self.assertIn("not a resident service", runner.UNBOUNDED_NOTICE)

    def test_negative_bound_is_refused(self):
        with self.assertRaises(SystemExit):
            runner.parse_args(["--max-requests", "-1"])


if __name__ == "__main__":
    unittest.main()
