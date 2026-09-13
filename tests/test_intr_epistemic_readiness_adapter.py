import unittest

from stegverse.intr_epistemic_readiness_adapter import readiness_predicate_from_epistemic_ack
from stegverse.readiness import evaluate_readiness


class InTrEpistemicReadinessAdapterTests(unittest.TestCase):
    def test_received_only_cannot_satisfy_high_consequence_readiness(self):
        predicate = readiness_predicate_from_epistemic_ack(
            {"item_id": "p1", "level": "RECEIVED", "incorporation_state": "INCORPORATED"},
            required_acknowledgement_level="INCORPORATED",
        )
        self.assertEqual(predicate.state, "UNKNOWN")
        self.assertEqual(evaluate_readiness([predicate]).state, "PROBE_REQUIRED")

    def test_incorporated_ack_satisfies_matching_requirement(self):
        predicate = readiness_predicate_from_epistemic_ack(
            {"item_id": "p2", "incorporated_predicate_id": "p2", "level": "INCORPORATED", "incorporation_state": "INCORPORATED"},
            required_acknowledgement_level="INCORPORATED",
        )
        self.assertEqual(predicate.state, "SATISFIED")
        self.assertEqual(evaluate_readiness([predicate]).state, "READY")

    def test_dispute_forces_probe_required(self):
        predicate = readiness_predicate_from_epistemic_ack(
            {"item_id": "p3", "level": "RECEIVED", "incorporation_state": "DISPUTED"},
            required_acknowledgement_level="RECEIVED",
        )
        self.assertEqual(evaluate_readiness([predicate]).state, "PROBE_REQUIRED")

    def test_not_applicable_is_not_promoted_to_satisfied(self):
        predicate = readiness_predicate_from_epistemic_ack(
            {"item_id": "p4", "level": "APPLICABILITY_RESOLVED", "incorporation_state": "NOT_APPLICABLE"},
            required_acknowledgement_level="APPLICABILITY_RESOLVED",
        )
        self.assertFalse(predicate.applicable)
        self.assertEqual(predicate.state, "NOT_APPLICABLE")


if __name__ == "__main__":
    unittest.main()
