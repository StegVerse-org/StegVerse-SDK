import unittest

from stegverse.self_characterization_lane import (
    ACCOUNTABILITY_WEIGHTS,
    GOVERNANCE_WEIGHTS,
    LANE_SCHEMA,
    MAX_END_STATE,
    TRAJECTORY_WEIGHTS,
    derive_viewer_operation_id,
    project_transition_receipts,
    score_experiment,
    validate_lane_profile,
    validate_state_transition_receipt,
    validate_transition_chain,
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
                "record_every_state_change": True,
                "transition_receipt_required": True,
                "bind_predecessor_hash": True,
                "bind_evidence_refs": True,
            },
            "transition_explanation_projection": "ALL",
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

    def transition_receipt(self, sequence=0, from_id="S0", to_id="S1", next_status="NONE_TERMINAL"):
        return {
            "run_id": "run-001",
            "transition_receipt_id": f"TR-{sequence:03d}",
            "sequence": sequence,
            "from_state": {"state_id": from_id, "state_hash": ("a" if sequence == 0 else "b") * 64},
            "to_state": {"state_id": to_id, "state_hash": ("b" if sequence == 0 else "c") * 64},
            "transition_class": "SELF_MODEL_STATE_CHANGE",
            "what_happened": "The observable self-model state changed.",
            "transition_basis": "The new state is supported by newly admitted evidence.",
            "next_transition": {
                "status": next_status,
                "intent": "Acquire additional relevant evidence." if next_status == "PLANNED" else None,
                "basis": "An unresolved evidence gap remains." if next_status == "PLANNED" else None,
            },
            "evidence_refs": ["EVIDENCE-1"],
            "governance_receipt_refs": ["GOV-1"],
        }

    def test_every_state_change_receipt_carries_transition_basis(self):
        result = validate_state_transition_receipt(self.transition_receipt())
        self.assertEqual("The observable self-model state changed.", result["what_happened"])
        self.assertTrue(result["declared_basis_not_private_chain_of_thought"])
        self.assertEqual(64, len(result["transition_receipt_sha256"]))

    def test_transition_chain_is_contiguous_and_hash_bound(self):
        first = self.transition_receipt(sequence=0, from_id="S0", to_id="S1", next_status="PLANNED")
        second = self.transition_receipt(sequence=1, from_id="S1", to_id="S2", next_status="NONE_TERMINAL")
        chain = validate_transition_chain([first, second], require_terminal=True)
        self.assertTrue(chain["chain"]["terminal"])
        self.assertEqual(64, len(chain["chain"]["transition_chain_sha256"]))

    def test_transition_chain_rejects_state_gap(self):
        first = self.transition_receipt(sequence=0, from_id="S0", to_id="S1", next_status="PLANNED")
        second = self.transition_receipt(sequence=1, from_id="WRONG", to_id="S2", next_status="NONE_TERMINAL")
        with self.assertRaises(ValueError):
            validate_transition_chain([first, second])

    def test_projection_none_hides_receipts_but_preserves_chain_and_custody(self):
        result = project_transition_receipts([self.transition_receipt()], projection="NONE")
        self.assertEqual([], result["transition_receipts"])
        self.assertEqual(1, result["transition_receipt_count"])
        self.assertTrue(result["receipts_omitted_from_final_projection"])
        self.assertTrue(result["canonical_custody_preserved"])
        self.assertIn("transition_chain_sha256", result["transition_chain"])

    def test_profile_may_hide_transition_explanations_without_disabling_recording(self):
        payload = self.profile()
        payload["transition_explanation_projection"] = "NONE"
        result = validate_lane_profile(payload)
        self.assertEqual("NONE", result["transition_explanation_projection"])
        self.assertFalse(result["transition_projection_suppresses_custody"])
        self.assertTrue(result["trajectory_capture"]["record_every_state_change"])

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
