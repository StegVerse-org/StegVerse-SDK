"""All fixtures here are SDK-local diagnostics, never sovereign runtime proof."""
import unittest
from unittest.mock import patch

from stegverse.transition_disposition import attempt_manifest_transition

MANIFEST = {"schema": "illustrative", "payload": {"x": 1}}
REQUEST = {
    "canonical_manifest_sha256": "a" * 64,
    "canonical_task_id": "TASK-1",
    "graph_id": "GRAPH-1",
    "processing_capability": "ecosystem_diagnostic",
    "route_id": "stegverse.route.ecosystem-diagnostic.v1",
}


class TestActionableBoundary(unittest.TestCase):
    @patch("stegverse.transition_disposition.derive_execution_request")
    def test_invalid_manifest_is_admission_deny(self, derive):
        derive.side_effect = ValueError("invalid route")
        value = attempt_manifest_transition(MANIFEST)
        self.assertEqual(value["boundary"], "SDK_MANIFEST_ADMISSION")
        self.assertEqual(value["disposition"], "DENY")
        self.assertFalse(value["consequence_committed"])
        self.assertFalse(value["is_intr_receipt"])

    @patch("stegverse.transition_disposition._post_existing_intr")
    @patch("stegverse.transition_disposition.derive_execution_request")
    def test_missing_existing_intr_url_is_actionable(self, derive, post):
        derive.return_value = REQUEST
        post.side_effect = ValueError("UNIVERSAL_INTR_INGRESS_NOT_CONFIGURED")
        value = attempt_manifest_transition(MANIFEST)
        self.assertEqual(value["failed_predicate"], "intr.endpoint.configured/v1")
        self.assertEqual(value["disposition"], "DENY")
        self.assertFalse(value["is_master_records_receipt"])

    @patch("stegverse.transition_disposition._post_existing_intr")
    @patch("stegverse.transition_disposition.derive_execution_request")
    def test_missing_tvc_authorization_is_actionable(self, derive, post):
        derive.return_value = REQUEST
        post.side_effect = ValueError("TV_TVC_RELAY_AUTHORIZATION_REQUIRED")
        value = attempt_manifest_transition(MANIFEST)
        self.assertEqual(value["failure_code"], "TV_TVC_RELAY_AUTHORIZATION_REQUIRED")
        self.assertIn("TV/TVC", value["required_evidence_or_repair"])

    @patch("stegverse.transition_disposition._post_existing_intr")
    @patch("stegverse.transition_disposition.derive_execution_request")
    def test_transport_failure_stays_local(self, derive, post):
        derive.return_value = REQUEST
        post.side_effect = ValueError("UNIVERSAL_INTR_UNREACHABLE:refused")
        value = attempt_manifest_transition(MANIFEST)
        self.assertEqual(value["disposition"], "FAIL_CLOSED")
        self.assertEqual(value["boundary"], "SDK_TO_INTR_TRANSPORT")
        self.assertFalse(value["is_intr_receipt"])

    @patch("stegverse.transition_disposition.validate_runtime_result")
    @patch("stegverse.transition_disposition._post_existing_intr")
    @patch("stegverse.transition_disposition.derive_execution_request")
    def test_unverifiable_response_does_not_become_runtime_deny(self, derive, post, validate):
        derive.return_value = REQUEST
        post.return_value = {"state": "NOT_COMPLETE", "blocker": "unknown"}
        validate.side_effect = ValueError("UNIVERSAL_INTR_RUNTIME_NOT_COMPLETE:unknown")
        value = attempt_manifest_transition(MANIFEST)
        self.assertEqual(value["boundary"], "SDK_INTR_RESULT_ACCEPTANCE")
        self.assertEqual(value["disposition"], "FAIL_CLOSED")
        self.assertEqual(len(value["response_sha256"]), 64)
        self.assertFalse(value["is_intr_receipt"])

    @patch("stegverse.transition_disposition.validate_runtime_result")
    @patch("stegverse.transition_disposition._post_existing_intr")
    @patch("stegverse.transition_disposition.derive_execution_request")
    def test_validated_success_passes_through(self, derive, post, validate):
        derive.return_value = REQUEST
        post.return_value = {"schema": "example"}
        validate.return_value = {"schema": "validated-existing-result", "state": "COMPLETE"}
        self.assertEqual(attempt_manifest_transition(MANIFEST), validate.return_value)


if __name__ == "__main__":
    unittest.main()
