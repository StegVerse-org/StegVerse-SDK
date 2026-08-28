import copy
import json
import unittest
from pathlib import Path

from stegverse.public_inspection import (
    prepare_public_inspection_submission,
    validate_public_inspection_request,
)


class EvaluatorManifestMultilaneNonInterferenceTests(unittest.TestCase):
    def setUp(self):
        self.manifest_path = Path("inspection/examples/multilane-noninterference-request.json")
        self.r3_task_path = Path("tasks/SDK-EVALUATION-BOUNDARY-R3-RUN-002.json")

    def load_manifest(self):
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def load_r3_task(self):
        return json.loads(self.r3_task_path.read_text(encoding="utf-8"))

    def test_pending_r3_does_not_block_independent_manifest_preparation(self):
        r3 = self.load_r3_task()
        self.assertFalse(r3["current_state"]["governed_run_executed"])
        self.assertFalse(r3["current_state"]["r3_aggregate_receipt_observed"])

        manifest = self.load_manifest()
        validated = validate_public_inspection_request(manifest)
        prepared = prepare_public_inspection_submission(validated)

        self.assertEqual("multilane-noninterference-001", prepared["request_id"])
        self.assertEqual("0A", prepared["ordinary_governance_option"])
        self.assertTrue(prepared["testing_contract"]["configuration_not_augmentation"])
        self.assertFalse(prepared["testing_contract"]["route_augmentation_permitted"])
        self.assertFalse(prepared["testing_contract"]["evaluator_identity_is_decision_input"])
        self.assertFalse(prepared["testing_contract"]["declared_expected_observation_is_decision_input"])
        self.assertEqual("NOT_RUN", prepared["runtime_processing_status"])
        self.assertEqual("NOT_CLAIMED", prepared["master_records_custody_status"])

    def test_r3_task_state_is_not_an_input_to_independent_manifest_semantics(self):
        manifest = self.load_manifest()
        before = prepare_public_inspection_submission(manifest)

        r3 = self.load_r3_task()
        simulated_r3 = copy.deepcopy(r3)
        simulated_r3["current_state"]["governed_run_executed"] = True
        simulated_r3["current_state"]["r3_aggregate_receipt_observed"] = True
        simulated_r3["state"] = "SIMULATED_TERMINAL_STATE_FOR_NONINTERFERENCE_TEST"

        after = prepare_public_inspection_submission(manifest)

        self.assertEqual(before, after)
        self.assertNotIn(simulated_r3["task_id"], json.dumps(after["testing_contract"], sort_keys=True))
        self.assertNotIn(simulated_r3["state"], json.dumps(after, sort_keys=True))

    def test_two_evaluator_manifests_do_not_cross_contaminate(self):
        lane_a = self.load_manifest()
        lane_b = copy.deepcopy(lane_a)
        lane_b["request_id"] = "multilane-noninterference-002"
        lane_b["requester_label"] = "independent-evaluator-c"
        lane_b["evaluation_declaration"]["why"] = (
            "Verify a second evaluator declaration remains isolated from both the first manifest and R3."
        )
        lane_b["input"]["test_vector"] = "multilane-noninterference-second"

        prepared_a = prepare_public_inspection_submission(lane_a)
        prepared_b = prepare_public_inspection_submission(lane_b)

        self.assertNotEqual(prepared_a["request_id"], prepared_b["request_id"])
        self.assertNotEqual(prepared_a["payload"]["test_vector"], prepared_b["payload"]["test_vector"])
        self.assertEqual(prepared_a["testing_contract"], prepared_b["testing_contract"])
        self.assertEqual(prepared_a["execution_provenance"], prepared_b["execution_provenance"])
        self.assertFalse(prepared_a["authority_claim"])
        self.assertFalse(prepared_b["authority_claim"])
        self.assertIsNone(prepared_a["manifest_receipt_id"])
        self.assertIsNone(prepared_b["manifest_receipt_id"])


if __name__ == "__main__":
    unittest.main()
