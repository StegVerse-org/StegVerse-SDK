"""A declared adapter's liveness never gates the connection (task-registry invariants)."""
from __future__ import annotations

import argparse
import unittest
from unittest.mock import patch

from stegverse.llm_connect_cli import _connection_result
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


if __name__ == "__main__":
    unittest.main()
