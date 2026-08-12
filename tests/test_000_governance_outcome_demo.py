import unittest

from stegverse.governance_navigation import (
    GOVERNANCE_OUTCOME_STATES,
    demo_output_manifest_shape,
    guidance_for,
    validate_external_manifest,
)


class GovernanceOutcomeDemoTests(unittest.TestCase):
    def test_000_demo_prepends_exactly_one_example_of_each_active_outcome(self):
        output = demo_output_manifest_shape()
        self.assertEqual(next(iter(output)), "000_governance_outcome_dataset")
        dataset = output["000_governance_outcome_dataset"]
        examples = dataset["governance_outcome_examples"]
        states = [item["governance_state"] for item in examples]
        self.assertEqual(tuple(states), GOVERNANCE_OUTCOME_STATES)
        self.assertEqual(len(states), len(set(states)))

    def test_each_demo_outcome_is_labeled_non_authorizing_governance_evidence(self):
        examples = demo_output_manifest_shape()["000_governance_outcome_dataset"]["governance_outcome_examples"]
        for item in examples:
            self.assertEqual(item["transition_class"], "governance")
            self.assertEqual(item["receipt_class"], "governance-decision")
            self.assertFalse(item["consequence_implied"])
            self.assertFalse(item["authority_granted_by_example"])
            self.assertTrue(item["meaning"])

    def test_000_dataset_is_demo_only_and_precedes_example_transaction(self):
        dataset = demo_output_manifest_shape()["000_governance_outcome_dataset"]
        self.assertTrue(dataset["demo_only"])
        self.assertFalse(dataset["accepted_as_user_manifest"])
        self.assertIn("governance_outcome_examples", dataset)
        self.assertIn("demo_input", dataset)
        self.assertIn("prepended", dataset["notes"]["ordering"])

    def test_demo_dataset_cannot_be_submitted_as_ingress_manifest(self):
        dataset = demo_output_manifest_shape()["000_governance_outcome_dataset"]
        with self.assertRaises(ValueError):
            validate_external_manifest(dataset)

    def test_000_guidance_names_full_active_outcome_vocabulary(self):
        text = guidance_for("000")
        for state in GOVERNANCE_OUTCOME_STATES:
            self.assertIn(state, text)
        self.assertIn("strictly demo-only", text)


if __name__ == "__main__":
    unittest.main()
