"""SDK transport attachment is an actionable local transition, not an InTr verdict."""
import os
import unittest
from unittest.mock import patch

from stegverse.manifest_state_transition_runtime import execute_manifest

REQUEST = {
    "request_sha256": "a" * 64,
    "wire_manifest_sha256": "b" * 64,
    "canonical_manifest_sha256": "c" * 64,
    "graph_id": "HOLD-T0",
    "canonical_task_id": "ELAN-PAPER-COAUTHOR-PUBLICATION-001",
    "processing_capability": "governance",
    "route_id": "stegverse.route.canonical-governed.v1",
}


class ManifestAttachmentBoundaryTest(unittest.TestCase):
    def test_missing_transport_attachment_is_local_nonallow(self):
        with patch("stegverse.manifest_state_transition_runtime.derive_execution_request", return_value=REQUEST):
            with patch.dict(os.environ, {"STEGVERSE_UNIVERSAL_INTR_INGRESS_URL": ""}):
                result = execute_manifest({})
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["evaluation_boundary"], "SDK_MANIFEST_TRANSPORT_ATTACHMENT")
        self.assertEqual(result["failed_predicate"], "UNIVERSAL_INTR_INGRESS_NOT_CONFIGURED")
        self.assertFalse(result["authentic_governance_disposition_observed"])
        self.assertFalse(result["organization_receipt_observed"])
        self.assertFalse(result["consequence_committed"])
        self.assertEqual(result["request_sha256"], REQUEST["request_sha256"])

    def test_missing_tvc_authorization_is_distinct(self):
        with patch("stegverse.manifest_state_transition_runtime.derive_execution_request", return_value=REQUEST):
            with patch.dict(os.environ, {"STEGVERSE_UNIVERSAL_INTR_INGRESS_URL": "https://example.invalid/ingress",
                                        "STEGVERSE_TVC_RELAY_AUTHORIZATION_ID": ""}):
                result = execute_manifest({})
        self.assertEqual(result["failed_predicate"], "TV_TVC_RELAY_AUTHORIZATION_REQUIRED")
        self.assertFalse(result["master_records_reconstruction_observed"])

    def test_other_errors_are_not_reclassified(self):
        with patch("stegverse.manifest_state_transition_runtime.derive_execution_request", return_value=REQUEST):
            with patch("stegverse.manifest_state_transition_runtime._post_existing_intr",
                       side_effect=ValueError("UNIVERSAL_INTR_HTTP_ERROR:403:denied")):
                with self.assertRaisesRegex(ValueError, "UNIVERSAL_INTR_HTTP_ERROR"):
                    execute_manifest({})


if __name__ == "__main__":
    unittest.main()
