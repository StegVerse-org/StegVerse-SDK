from __future__ import annotations

import unittest

from stegverse.active_probe_execution import execute_active_probes
from stegverse.tvc_provider_probe_bridge import google_drive_probe_result_from_tvc
from tests.test_workspace_resource_consumer import request


def tvc_result():
    return {
        "schema": "stegverse.tvc.personal-kv-google-drive-materialization-result/v1",
        "request_id": "request-1234567890abcdef",
        "request_sha256": "sha256:" + "a" * 64,
        "binding_id": "kvpb_workspace_test",
        "provider": "GOOGLE_DRIVE",
        "broker_response": {"decision": "ALLOW_OPERATION_RESULT", "result_ref": "provider-result:test"},
        "lease_receipt_sha256": "sha256:" + "b" * 64,
        "credential_authority": "TV/TVC",
        "credential_material_exported": False,
        "provider_operation_authority_transferred": False,
        "runtime_activation_claimed": False,
        "authority_effect": "NONE_RESULT_EVIDENCE_ONLY",
    }


class TvcProviderProbeBridgeTests(unittest.TestCase):
    def test_secret_free_tvc_result_projects_to_non_authorizing_active_probe(self):
        probe = google_drive_probe_result_from_tvc(
            reason="predicate:authorization_current:evidence_unresolved",
            tvc_result=tvc_result(),
            observed_at="2026-09-11T00:40:00Z",
        )
        self.assertEqual(probe["outcome"], "SATISFIED")
        self.assertEqual(probe["credential_authority"], "TV/TVC")
        self.assertFalse(probe["credential_material_exported"])
        self.assertFalse(probe["provider_operation_authority_transferred"])
        self.assertEqual(probe["authority_effect"], "NONE")

    def test_bridge_output_is_accepted_by_canonical_active_probe_execution(self):
        req = request(unresolved=True)
        ingress = req["payload"]["manifest"]["payload"]["canonical_ingress_manifest"]
        transition = ingress["extensions"]["stegverse_state_transition"]

        def executor(reason, _manifest):
            return google_drive_probe_result_from_tvc(
                reason=reason,
                tvc_result=tvc_result(),
                observed_at="2026-09-11T00:40:00Z",
            )

        resolved = execute_active_probes(
            state_transition=transition,
            ingress_manifest=ingress,
            executor=executor,
        )
        self.assertEqual(resolved["readiness_before_probe"], "PROBE_REQUIRED")
        self.assertEqual(resolved["readiness_after_probe"], "READY")

    def test_credential_material_is_rejected(self):
        bad = tvc_result()
        bad["broker_response"]["access_token"] = "ya29.must-not-cross"
        with self.assertRaisesRegex(ValueError, "protected TVC result"):
            google_drive_probe_result_from_tvc(
                reason="predicate:authorization_current:evidence_unresolved",
                tvc_result=bad,
                observed_at="2026-09-11T00:40:00Z",
            )

    def test_authority_transfer_is_rejected(self):
        bad = tvc_result()
        bad["provider_operation_authority_transferred"] = True
        with self.assertRaisesRegex(ValueError, "authority transfer prohibited"):
            google_drive_probe_result_from_tvc(
                reason="predicate:authorization_current:evidence_unresolved",
                tvc_result=bad,
                observed_at="2026-09-11T00:40:00Z",
            )

    def test_wrong_tvc_schema_is_rejected(self):
        bad = tvc_result()
        bad["schema"] = "other"
        with self.assertRaisesRegex(ValueError, "unsupported TVC Google Drive result schema"):
            google_drive_probe_result_from_tvc(
                reason="predicate:authorization_current:evidence_unresolved",
                tvc_result=bad,
                observed_at="2026-09-11T00:40:00Z",
            )


if __name__ == "__main__":
    unittest.main()
