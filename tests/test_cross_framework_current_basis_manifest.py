import json
import unittest
from pathlib import Path


MANIFEST_PATH = Path("inspection/examples/cross-framework-current-basis-request.draft.json")


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _data():
    return _manifest()["input"]["comparison_input"]


class CrossFrameworkCurrentBasisManifestTests(unittest.TestCase):
    def test_v04_common_input_does_not_preassert_native_currentness(self):
        manifest = _manifest()
        data = _data()
        self.assertEqual(data["vector_schema"], "stegverse.cross-framework-current-basis-vector.v0.4")
        self.assertNotIn("steggate_request", manifest["input"])
        self.assertTrue(data["architecture_native_derivation"]["required"])
        self.assertFalse(data["architecture_native_derivation"]["common_artifact_contains_native_currentness_booleans"])
        self.assertTrue(data["comparison_boundary"]["common_input_does_not_assert_native_currentness"])
        serialized = json.dumps(manifest["input"], sort_keys=True)
        for forbidden in (
            "actor_authority_current",
            "policy_current",
            "delegation_current",
            "evidence_current",
            "validity_window_open",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_s0_is_not_transition_receipt_bearing_before_s1_observation(self):
        data = _data()
        self.assertEqual(data["initial_state"]["state_id"], "S0")
        self.assertEqual(data["initial_state"]["receipt_state"], "NOT_RECEIPT_BEARING_PRE_OBSERVATION")
        self.assertNotIn("prior_receipt_ref", data["initial_state"])

    def test_transition_receipt_is_post_observation_output_not_freeze_input(self):
        data = _data()
        self.assertEqual(
            data["transition"]["receipt_semantics"],
            "S0_TO_S1_RECEIPT_IS_POST_OBSERVATION_EVIDENCE",
        )
        self.assertTrue(data["comparison_boundary"]["transition_receipt_is_not_a_pre_execution_input"])
        self.assertIn(
            "do not require or assert an S0-to-S1 transition receipt before S1 is observed",
            data["pre_freeze_requirements"],
        )
        self.assertIn(
            "only after that observation bind the S0-to-S1 transition receipt",
            data["post_observation_requirements"],
        )

    def test_successor_current_basis_remains_architecture_output(self):
        data = _data()
        self.assertEqual(
            data["successor_state_determination"]["current_basis_status"],
            "TO_BE_DETERMINED_BY_EACH_ARCHITECTURE",
        )
        self.assertTrue(data["comparison_boundary"]["current_standing_is_independently_determined"])
        rule = data["architecture_native_derivation"]["rule"]
        self.assertIn("independently derives", rule)
        self.assertIn("not common pre-established conclusions", rule)

    def test_known_invalidation_control_separates_preexisting_input_evidence_from_transition_receipt(self):
        data = _data()
        controls = {item["control_id"]: item for item in data["controls"]}
        known = controls["KNOWN_INVALIDATION_CONTROL"]
        self.assertTrue(known["prior_invalidation_established"])
        self.assertIn("independently pre-existing evidence", known["freeze_requirement"])
        self.assertIn("receipt is minted after observation", known["freeze_requirement"])

    def test_manifest_remains_pre_freeze_snapshot_after_v04_correction(self):
        manifest = _manifest()
        data = _data()
        self.assertEqual(data["freeze_state"], "DRAFT_PRE_FREEZE")
        self.assertFalse(manifest["authority_claim"])
        self.assertIn("revision v0.4", manifest["notes"])


if __name__ == "__main__":
    unittest.main()
