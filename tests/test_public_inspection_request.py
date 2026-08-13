import json
import unittest
from pathlib import Path

from scripts.validate_public_inspection_request import validate


class PublicInspectionRequestTests(unittest.TestCase):
    def example(self):
        return {
            "schema_version": "1.0",
            "request_id": "case-001",
            "requester_label": "public-evaluator",
            "case_profile": "ordinary",
            "input": {"amount": 420, "currency": "USD"},
            "return_projection": "ALL",
            "manifest_labels": True,
            "authority_claim": False,
            "notes": "declarative request",
        }

    def test_example_file_is_valid(self):
        path = Path("inspection/examples/example-request.json")
        validate(json.loads(path.read_text(encoding="utf-8")))

    def test_personal_name_is_not_required(self):
        payload = self.example()
        payload.pop("requester_label")
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


if __name__ == "__main__":
    unittest.main()
