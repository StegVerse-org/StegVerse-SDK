from __future__ import annotations

import unittest

from stegverse.output_boundary_proof import evaluate_output_boundary_proof


class OutputBoundaryProofTests(unittest.TestCase):
    def candidate(self, deployment_class: str = "S"):
        return {
            "deployment_class": deployment_class,
            "provider": "openai",
            "model": "external-test-model",
            "prompt": "Summarize the bounded transition.",
            "output": "Candidate output generated outside StegVerse.",
            "declared_intent": "research_note",
            "consequence_level": "medium",
            "provider_api_key_transferred_to_stegverse": False,
        }

    def test_s_candidate_produces_credentialless_replay_and_reconstruction_proof(self):
        result = evaluate_output_boundary_proof(self.candidate("S"))
        self.assertEqual(result["deployment_class"], "S")
        self.assertFalse(result["provider_api_key_received_by_stegverse"])
        self.assertFalse(result["provider_api_key_required_by_proof_surface"])
        self.assertTrue(result["proof"]["candidate_bound"])
        self.assertTrue(result["proof"]["replay_match"])
        self.assertTrue(result["proof"]["semantic_reconstruction_match"])
        self.assertFalse(result["node_sovereign_membership_granted"])

    def test_ns_profile_never_self_grants_membership(self):
        result = evaluate_output_boundary_proof(self.candidate("NS"))
        self.assertEqual(result["deployment_class"], "NS")
        self.assertEqual(result["sovereign_mode"], "node_sovereign_profile")
        self.assertFalse(result["node_sovereign_membership_granted"])
        self.assertTrue(result["proof"]["replay_match"])
        self.assertTrue(result["proof"]["semantic_reconstruction_match"])

    def test_provider_key_transfer_is_rejected(self):
        candidate = self.candidate("S")
        candidate["provider_api_key_transferred_to_stegverse"] = True
        with self.assertRaisesRegex(ValueError, "must be false"):
            evaluate_output_boundary_proof(candidate)

    def test_unknown_deployment_class_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be S or NS"):
            evaluate_output_boundary_proof(self.candidate("UNKNOWN"))


if __name__ == "__main__":
    unittest.main()
