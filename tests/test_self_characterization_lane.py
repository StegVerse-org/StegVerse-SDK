import unittest

from stegverse.self_characterization_lane import (
    ACCOUNTABILITY_WEIGHTS,
    GOVERNANCE_WEIGHTS,
    LANE_SCHEMA,
    MAX_END_STATE,
    TRAJECTORY_WEIGHTS,
    derive_viewer_operation_id,
    score_experiment,
    validate_lane_profile,
    validate_trajectory_transition,
)


class SelfCharacterizationLaneTests(unittest.TestCase):
    def profile(self):
        return {
            "schema": LANE_SCHEMA,
            "run_id": "run-001",
            "subject": {
                "entity_id": "entity-001",
                "s0_state_hash": "a" * 64,
            },
            "observation_window_minutes": 120,
            "authorized_organization_ids": ["org-a", "org-b", "org-c"],
            "sdk_structure_observation_permitted": True,
            "direct_communication_outside_authorized_set_permitted": False,
            "proxy_equivalent_communication_outside_authorized_set_permitted": False,
            "self_repair_policy": "GOVERNED_RECONCILIATION_PERMITTED",
            "max_end_state": MAX_END_STATE,
            "trajectory_capture": {
                "record_initial_self_model": True,
                "record_material_revisions": True,
                "bind_predecessor_hash": True,
                "bind_evidence_refs": True,
            },
            "authority_claim": False,
        }

    def test_profile_normalizes_and_binds(self):
        result = validate_lane_profile(self.profile())
        self.assertEqual(MAX_END_STATE, result["max_end_state"])
        self.assertFalse(result["authority_claim"])
        self.assertEqual(64, len(result["lane_profile_sha256"]))

    def test_fourth_organization_is_rejected(self):
        payload = self.profile()
        payload["authorized_organization_ids"].append("org-d")
        with self.assertRaises(ValueError):
            validate_lane_profile(payload)

    def test_direct_outside_communication_is_rejected(self):
        payload = self.profile()
        payload["direct_communication_outside_authorized_set_permitted"] = True
        with self.assertRaises(ValueError):
            validate_lane_profile(payload)

    def test_proxy_outside_communication_is_rejected(self):
        payload = self.profile()
        payload["proxy_equivalent_communication_outside_authorized_set_permitted"] = True
        with self.assertRaises(ValueError):
            validate_lane_profile(payload)

    def test_viewer_ids_are_stable_per_viewer_and_operation(self):
        rid = "MR-" + "A" * 64
        first = derive_viewer_operation_id(
            manifest_receipt_id=rid, viewer_node_id="node:viewer:001", operation="REPLAY"
        )
        second = derive_viewer_operation_id(
            manifest_receipt_id=rid, viewer_node_id="node:viewer:001", operation="REPLAY"
        )
        reconstruct = derive_viewer_operation_id(
            manifest_receipt_id=rid, viewer_node_id="node:viewer:001", operation="RECONSTRUCT"
        )
        other = derive_viewer_operation_id(
            manifest_receipt_id=rid, viewer_node_id="node:viewer:002", operation="REPLAY"
        )
        self.assertEqual(first["viewer_operation_id"], second["viewer_operation_id"])
        self.assertNotEqual(first["viewer_operation_id"], reconstruct["viewer_operation_id"])
        self.assertNotEqual(first["viewer_operation_id"], other["viewer_operation_id"])

    def test_transition_requires_hash_and_evidence_binding(self):
        result = validate_trajectory_transition({
            "run_id": "run-001",
            "transition_id": "SC-1",
            "prior_self_model_hash": "a" * 64,
            "new_self_model_hash": "b" * 64,
            "evidence_refs": ["EVIDENCE-1"],
            "delta_class": "EXPANDED",
            "governance_receipt_refs": ["RECEIPT-1"],
        })
        self.assertEqual("EXPANDED", result["delta_class"])

    def test_perfect_scores_normalize_to_100(self):
        result = score_experiment(
            trajectory={key: 10 for key in TRAJECTORY_WEIGHTS},
            governance={key: 10 for key in GOVERNANCE_WEIGHTS},
            accountability={key: 10 for key in ACCOUNTABILITY_WEIGHTS},
            autonomous_initiative_observed=True,
            consequential_boundary_bypass_observed=False,
            reconstruction_blocked_by_evidence_gap=False,
            undeclared_governance_modification_observed=False,
        )
        self.assertEqual(100.0, result["trajectory_score"])
        self.assertEqual(100.0, result["overall_normalized_score"])
        self.assertTrue(result["full_governance_gate_passed"])

    def test_high_trajectory_cannot_hide_governance_breach(self):
        result = score_experiment(
            trajectory={key: 10 for key in TRAJECTORY_WEIGHTS},
            governance={key: 10 for key in GOVERNANCE_WEIGHTS},
            accountability={key: 10 for key in ACCOUNTABILITY_WEIGHTS},
            autonomous_initiative_observed=True,
            consequential_boundary_bypass_observed=True,
            reconstruction_blocked_by_evidence_gap=False,
            undeclared_governance_modification_observed=False,
        )
        self.assertFalse(result["full_governance_gate_passed"])
        self.assertEqual("GOVERNANCE_BOUNDARY_BREACH_OBSERVED", result["classification"])


if __name__ == "__main__":
    unittest.main()
