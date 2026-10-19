"""A declared adapter's liveness never gates the connection (task-registry invariants)."""
from __future__ import annotations

import argparse
import unittest
from unittest.mock import patch

import io
import json
from contextlib import redirect_stdout

from stegverse.llm_connect_cli import _connection_result, connection_refusal, main
from stegverse.llm_connection import AdapterProbe, LLMConnectionError


def _args(**overrides):
    values = dict(adapter_url="http://127.0.0.1:8080", user_id="u", llm_id="l", provider="p",
                  model="m", scope=[], connection_id=None, output_dir=".unused", no_save=True)
    values.update(overrides)
    return argparse.Namespace(**values)


def _probe(state):
    return AdapterProbe(base_url="http://127.0.0.1:8080", state=state, health={}, readiness={},
                        capabilities={}, activation={})


class DeclaredAdapterTests(unittest.TestCase):
    def test_unreachable_declared_adapter_still_yields_a_descriptor(self):
        with patch("stegverse.llm_connect_cli.probe_adapter",
                   side_effect=LLMConnectionError("adapter_unreachable:URLError")):
            out = _connection_result(_args())
        self.assertEqual(out["state"], "CONNECTED")
        self.assertEqual(out["connection"]["adapter_base_url"], "http://127.0.0.1:8080")
        self.assertEqual(out["adapter_probe"]["state"], "NOT_OBSERVED")
        self.assertIs(out["adapter_probe"]["gates_connection"], False)
        self.assertIs(out["destination_liveness_gates_connection"], False)

    def test_deferred_or_unhealthy_adapter_does_not_gate(self):
        for state in ("DEFERRED", "UNHEALTHY"):
            with patch("stegverse.llm_connect_cli.probe_adapter", return_value=_probe(state)):
                out = _connection_result(_args())
            self.assertEqual(out["state"], "CONNECTED")
            self.assertEqual(out["adapter_probe"]["state"], state)

    def test_observed_authority_escalation_is_still_refused(self):
        with patch("stegverse.llm_connect_cli.probe_adapter",
                   return_value=_probe("REJECTED_AUTHORITY_ESCALATION")):
            with self.assertRaisesRegex(LLMConnectionError, "adapter_authority_escalation_observed"):
                _connection_result(_args())

    def test_discovery_without_a_declared_destination_still_requires_an_answer(self):
        with patch("stegverse.llm_connect_cli.discover_adapter", return_value=_probe("DEFERRED")):
            with self.assertRaisesRegex(LLMConnectionError, "adapter_not_connected"):
                _connection_result(_args(adapter_url=None))


SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
              "owning_existing_goal", "next_attempt")


class RefusalTests(unittest.TestCase):
    def test_every_cli_refusal_is_a_six_field_record_and_never_a_wait(self):
        cases = {
            LLMConnectionError("adapter_not_connected:state=DEFERRED"): "ADAPTER_DESTINATION_NOT_DECLARED",
            LLMConnectionError("adapter_not_discovered:http://127.0.0.1:8080:adapter_unreachable:URLError"):
                "ADAPTER_DESTINATION_NOT_DECLARED",
            LLMConnectionError("adapter_authority_escalation_observed"): "ADAPTER_AUTHORITY_ESCALATION_OBSERVED",
            EOFError(): "INTERACTIVE_INPUT_UNAVAILABLE",
            LLMConnectionError("endpoint_mismatch:submit"): "LLM_CONNECTION_INPUT_INVALID",
        }
        for exc, code in cases.items():
            record = connection_refusal(exc)
            self.assertEqual((record["disposition"], record["failure_code"]), ("FAIL_CLOSED", code))
            self.assertTrue(all(isinstance(record[f], str) and record[f] for f in SIX_FIELDS), record)
            self.assertNotIn("retry until", record["next_attempt"].lower())

    def test_undeclared_unanswered_discovery_exits_2_with_the_record(self):
        with patch("stegverse.llm_connect_cli.discover_adapter",
                   side_effect=LLMConnectionError("adapter_not_discovered:none")):
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["--json", "--no-save", "--user-id", "u", "--llm-id", "l",
                             "--provider", "p", "--model", "m"])
        self.assertEqual(code, 2)
        record = json.loads(out.getvalue())
        self.assertEqual(record["failure_code"], "ADAPTER_DESTINATION_NOT_DECLARED")
        self.assertIn("--adapter-url", record["required_evidence_or_repair"])


if __name__ == "__main__":
    unittest.main()
