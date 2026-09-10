import unittest

from stegverse.readiness import (
    ProbeEvidence,
    ReadinessPredicate,
    evaluate_readiness,
    resolve_with_probe,
)


class ReadinessDisciplineTests(unittest.TestCase):
    def test_narrow_success_cannot_imply_end_to_end_ready(self):
        decision = evaluate_readiness([
            ReadinessPredicate("sdk_source_governance", "SATISFIED"),
            ReadinessPredicate("runtime_route", "UNKNOWN"),
        ])
        self.assertEqual(decision.state, "PROBE_REQUIRED")
        self.assertEqual(decision.probes_required, ("runtime_route",))

    def test_unsatisfied_predicate_dominates_probe_required(self):
        decision = evaluate_readiness([
            ReadinessPredicate("sdk_source_governance", "SATISFIED"),
            ReadinessPredicate("public_distribution", "UNSATISFIED"),
            ReadinessPredicate("runtime_route", "UNKNOWN"),
        ])
        self.assertEqual(decision.state, "BLOCKED")
        self.assertEqual(decision.blockers, ("public_distribution",))

    def test_ambiguity_affecting_readiness_forces_probe(self):
        decision = evaluate_readiness([
            ReadinessPredicate(
                "downstream_applicability",
                "SATISFIED",
                ambiguity_affects_readiness=True,
            )
        ])
        self.assertEqual(decision.state, "PROBE_REQUIRED")

    def test_probe_evidence_allows_reclassification(self):
        predicate = ReadinessPredicate("runtime_route", "UNKNOWN")
        resolved = resolve_with_probe(
            predicate,
            resolved_state="SATISFIED",
            evidence=ProbeEvidence(
                evidence_ref="receipt:runtime-route-001",
                observed_at="2026-09-10T12:05:00-05:00",
                observation="canonical route accepted and produced durable receipt",
            ),
        )
        decision = evaluate_readiness([resolved])
        self.assertEqual(decision.state, "READY")
        self.assertEqual(resolved.probe_evidence.evidence_ref, "receipt:runtime-route-001")

    def test_empty_inventory_is_not_ready(self):
        decision = evaluate_readiness([])
        self.assertEqual(decision.state, "PROBE_REQUIRED")
        self.assertIn("readiness_predicate_inventory", decision.probes_required)

    def test_discovered_predicate_changes_prior_ready_to_probe_required(self):
        prior = evaluate_readiness([
            ReadinessPredicate("sdk_source_governance", "SATISFIED"),
        ])
        self.assertEqual(prior.state, "READY")
        after_discovery = evaluate_readiness([
            ReadinessPredicate("sdk_source_governance", "SATISFIED"),
            ReadinessPredicate("newly_discovered_runtime_predicate", "UNKNOWN"),
        ])
        self.assertEqual(after_discovery.state, "PROBE_REQUIRED")


if __name__ == "__main__":
    unittest.main()
