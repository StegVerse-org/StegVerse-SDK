import json
import unittest
from pathlib import Path

from scripts.validate_public_inspection_request import validate
from stegverse.public_inspection import prepare_public_inspection_submission


class PublicInspectionRequestTests(unittest.TestCase):
    def example(self):
        return {
            "schema_version": "1.0",
            "request_id": "case-001",
            "requester_label": "public-evaluator",
            "case_profile": "ordinary",
            "evaluation_declaration": {
                "what": "Evaluate commit-time admissibility for the submitted candidate.",
                "how": "Use the published canonical route without runtime augmentation.",
                "why": "Test the declared proposition independently of evaluator identity.",
                "expected_observation": "Disposition follows current governing state.",
                "requested_capabilities": ["commit_time_admissibility", "master_records_custody"],
                "requested_evidence": ["governance_decision", "manifest_receipt", "exact_run_custody"],
            },
            "execution_provenance": {
                "lane_class": "PRODUCTION_VALIDATION",
                "routing_surface": "CANONICAL_PRODUCTION",
                "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
                "sandbox_required": False,
                "sandbox_tier": "NONE",
                "origin_surface": "StegVerse-org/StegVerse-SDK:public-inspection",
                "external_consequence_enabled": False,
            },
            "input": {"amount": 420, "currency": "USD"},
            "return_projection": "ALL",
            "manifest_labels": True,
            "authority_claim": False,
            "notes": "declarative request",
        }

    def test_example_file_is_valid(self):
        path = Path("inspection/examples/example-request.json")
        validate(json.loads(path.read_text(encoding="utf-8")))

    def test_governed_example_file_is_valid(self):
        path = Path("inspection/examples/governed-test-request.json")
        validate(json.loads(path.read_text(encoding="utf-8")))

    def test_personal_name_is_not_required(self):
        payload = self.example()
        payload.pop("requester_label")
        validate(payload)

    def test_evaluation_declaration_is_evidence_not_authority(self):
        payload = self.example()
        prepared = prepare_public_inspection_submission(payload)
        self.assertEqual(payload["evaluation_declaration"]["what"], prepared["evaluation_declaration"]["what"])
        self.assertTrue(prepared["testing_contract"]["configuration_not_augmentation"])
        self.assertFalse(prepared["testing_contract"]["route_augmentation_permitted"])
        self.assertFalse(prepared["testing_contract"]["evaluator_identity_is_decision_input"])
        self.assertFalse(prepared["testing_contract"]["declared_expected_observation_is_decision_input"])
        self.assertEqual("REJECT_BEFORE_EXECUTION", prepared["testing_contract"]["unsupported_capability_behavior"])

    def test_unsupported_capability_is_rejected_before_execution(self):
        payload = self.example()
        payload["evaluation_declaration"]["requested_capabilities"] = ["custom_hot_patch"]
        with self.assertRaises(ValueError):
            validate(payload)

    def test_declaration_requires_what_how_why_when_present(self):
        payload = self.example()
        payload["evaluation_declaration"].pop("why")
        with self.assertRaises(ValueError):
            validate(payload)

    def test_authority_claim_must_be_false(self):
        payload = self.example()
        payload["authority_claim"] = True
        with self.assertRaises(ValueError):
            validate(payload)

    def test_credential_like_fields_are_rejected(self):
        payload = self.example()
        payload["input"]["api_key"] = "not-allowed"
        with self.assertRaises(ValueError):
            validate(payload)

    def test_executable_fields_are_rejected(self):
        payload = self.example()
        payload["input"]["command"] = "echo hello"
        with self.assertRaises(ValueError):
            validate(payload)

    def test_execution_provenance_is_required(self):
        payload = self.example()
        payload.pop("execution_provenance")
        with self.assertRaises(ValueError):
            validate(payload)

    def test_demo_lane_must_be_repository_contained(self):
        payload = self.example()
        payload["execution_provenance"] = {
            "lane_class": "ENCLOSED_DEMO_TEST",
            "routing_surface": "DEMO_TEST_REPOSITORY",
            "containment": "DEMO_REPOSITORY_CONTAINED",
            "sandbox_required": True,
            "sandbox_tier": "StegGhost",
            "origin_surface": "StegVerse-org/StegGhost",
            "external_consequence_enabled": False,
        }
        validate(payload)

        payload["execution_provenance"]["routing_surface"] = "CANONICAL_PRODUCTION"
        with self.assertRaises(ValueError):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
