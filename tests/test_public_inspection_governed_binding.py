from __future__ import annotations

import unittest

from stegverse.public_inspection import PublicInspectionRequestError, prepare_public_inspection_submission, validate_public_inspection_request


class PublicInspectionGovernedBindingTests(unittest.TestCase):
    def request(self):
        return {
            "schema_version": "1.0",
            "request_id": "inspection-001",
            "case_profile": "ordinary",
            "input": {"candidate": {"action": "inspect"}, "value": 420},
            "return_projection": "ALL",
            "manifest_labels": True,
            "authority_claim": False,
        }

    def test_prepares_ordinary_0a_descriptor(self):
        result = prepare_public_inspection_submission(self.request())
        self.assertEqual(result["ordinary_governance_option"], "0A")
        self.assertEqual(result["submission_descriptor"]["ingress_mode"], "sdk_manifested_raw_data")
        self.assertEqual(result["runtime_processing_status"], "NOT_RUN")
        self.assertIsNone(result["manifest_receipt_id"])
        self.assertFalse(result["authority_claim"])

    def test_personal_name_not_required(self):
        normalized = validate_public_inspection_request(self.request())
        self.assertIsNone(normalized["requester_label"])

    def test_authority_escalation_rejected(self):
        request = self.request()
        request["authority_claim"] = True
        with self.assertRaises(PublicInspectionRequestError):
            validate_public_inspection_request(request)

    def test_unknown_top_level_field_rejected(self):
        request = self.request()
        request["extra"] = "no"
        with self.assertRaises(PublicInspectionRequestError):
            validate_public_inspection_request(request)


if __name__ == "__main__":
    unittest.main()
