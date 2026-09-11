from __future__ import annotations

import unittest

from stegverse.active_probe_execution import ACTIVE_PROBE_RESULT_PROFILE, execute_active_probes
from stegverse.workspace_resource_consumer import consume_workspace_resource
from tests.test_workspace_resource_consumer import request


def satisfied(reason, _ingress):
    result = {
        "profile": ACTIVE_PROBE_RESULT_PROFILE,
        "reason": reason,
        "outcome": "SATISFIED",
        "observed_at": "2026-09-11T00:30:00Z",
        "evidence_ref": "provider-native:probe:current",
        "source": "provider-neutral-test-probe",
        "authority_effect": "NONE",
    }
    if reason.endswith(":applicability_unknown"):
        result["applicability"] = "APPLICABLE"
    return result


class ActiveProbeExecutionTests(unittest.TestCase):
    def test_probe_required_materialize_becomes_ready_only_after_runtime_probe(self):
        state = consume_workspace_resource(
            request=request(unresolved=True),
            operation="MATERIALIZE",
            projection_id="projection-1",
            probe_executor=satisfied,
        )
        self.assertEqual(state["readiness_before_probe"], "PROBE_REQUIRED")
        self.assertEqual(state["readiness"], "READY")
        self.assertTrue(state["active_probe_executed"])
        self.assertEqual(len(state["active_probe_evidence"]), 1)
        self.assertFalse(state["authority_transfer"])
        self.assertFalse(state["intr_receipt_minted"])

    def test_unresolved_probe_result_remains_fail_closed(self):
        def unresolved(reason, _ingress):
            return {
                "profile": ACTIVE_PROBE_RESULT_PROFILE,
                "reason": reason,
                "outcome": "UNRESOLVED",
                "observed_at": "2026-09-11T00:30:00Z",
                "evidence_ref": "provider-native:probe:unresolved",
                "source": "provider-neutral-test-probe",
                "authority_effect": "NONE",
            }

        with self.assertRaisesRegex(ValueError, "requires READY state"):
            consume_workspace_resource(
                request=request(unresolved=True),
                operation="REFRESH",
                projection_id="projection-1",
                probe_executor=unresolved,
            )

    def test_probe_cannot_claim_authority(self):
        def bad(reason, _ingress):
            return {
                "profile": ACTIVE_PROBE_RESULT_PROFILE,
                "reason": reason,
                "outcome": "SATISFIED",
                "observed_at": "2026-09-11T00:30:00Z",
                "evidence_ref": "provider-native:probe:bad",
                "source": "provider-neutral-test-probe",
                "authority_effect": "GRANT",
            }

        with self.assertRaisesRegex(ValueError, "authority_effect NONE"):
            consume_workspace_resource(
                request=request(unresolved=True),
                operation="MATERIALIZE",
                projection_id="projection-1",
                probe_executor=bad,
            )

    def test_probe_reason_must_match_exact_derived_reason(self):
        def mismatch(_reason, _ingress):
            return {
                "profile": ACTIVE_PROBE_RESULT_PROFILE,
                "reason": "predicate:other:evidence_unresolved",
                "outcome": "SATISFIED",
                "observed_at": "2026-09-11T00:30:00Z",
                "evidence_ref": "provider-native:probe:mismatch",
                "source": "provider-neutral-test-probe",
                "authority_effect": "NONE",
            }

        with self.assertRaisesRegex(ValueError, "reason mismatch"):
            consume_workspace_resource(
                request=request(unresolved=True),
                operation="MATERIALIZE",
                projection_id="projection-1",
                probe_executor=mismatch,
            )

    def test_ready_transition_executes_no_probe(self):
        calls = []
        def should_not_run(reason, ingress):
            calls.append((reason, ingress))
            return satisfied(reason, ingress)

        state = consume_workspace_resource(
            request=request(),
            operation="MATERIALIZE",
            projection_id="projection-1",
            probe_executor=should_not_run,
        )
        self.assertEqual(state["readiness_before_probe"], "READY")
        self.assertEqual(state["readiness"], "READY")
        self.assertFalse(state["active_probe_executed"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
