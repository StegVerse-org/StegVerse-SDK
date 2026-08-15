from __future__ import annotations

import unittest
from unittest.mock import patch

from stegverse.governance_fallback import GovernanceFallbackError, execute_fallback


class FakeSovereignValidationError(RuntimeError):
    pass


class GovernanceFallbackTests(unittest.TestCase):
    def test_run_returns_canonical_result_unchanged(self):
        request = {"request_id": "r-1"}
        expected = {
            "governance_state": "DENY",
            "manifest_receipt_id": "MR-ABCDEF0123456789",
            "chain_verified": True,
        }

        runtime = (
            FakeSovereignValidationError,
            lambda target: request,
            lambda loaded, **kwargs: expected if loaded is request else None,
            lambda *args, **kwargs: None,
            lambda *args, **kwargs: None,
        )
        with patch("stegverse.governance_fallback._runtime", return_value=runtime):
            result = execute_fallback("run", "request.json")

        self.assertIs(result, expected)
        self.assertEqual(result["governance_state"], "DENY")

    def test_replay_dispatches_to_canonical_runtime(self):
        expected = {"replay_disposition": "ALLOW", "consequence_reexecuted": False}
        runtime = (
            FakeSovereignValidationError,
            lambda target: None,
            lambda *args, **kwargs: None,
            lambda receipt_id, **kwargs: expected if receipt_id == "MR-ABCDEF0123456789" else None,
            lambda *args, **kwargs: None,
        )
        with patch("stegverse.governance_fallback._runtime", return_value=runtime):
            result = execute_fallback("replay", "MR-ABCDEF0123456789")

        self.assertIs(result, expected)
        self.assertFalse(result["consequence_reexecuted"])

    def test_invalid_operation_fails_before_runtime(self):
        with self.assertRaises(GovernanceFallbackError) as ctx:
            execute_fallback("replace-governance", "anything")
        self.assertEqual(ctx.exception.code, "INVALID_REQUEST")

    def test_missing_canonical_components_are_distinct_from_governance_result(self):
        def fail_run(*args, **kwargs):
            raise FakeSovereignValidationError(
                "Canonical StegCore, Core-Lite and Master Records packages are required; no parallel evaluator is provided."
            )

        runtime = (
            FakeSovereignValidationError,
            lambda target: {"request_id": "r-1"},
            fail_run,
            lambda *args, **kwargs: None,
            lambda *args, **kwargs: None,
        )
        with patch("stegverse.governance_fallback._runtime", return_value=runtime):
            with self.assertRaises(GovernanceFallbackError) as ctx:
                execute_fallback("run", "request.json")

        self.assertEqual(ctx.exception.code, "RUNTIME_COMPONENT_UNAVAILABLE")
        self.assertNotIn(ctx.exception.code, {"ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"})


if __name__ == "__main__":
    unittest.main()
