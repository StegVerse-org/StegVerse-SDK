"""The manifest determines the destination, and nothing else may supply one.

This replaces the former transport-attachment boundary. That boundary asserted a
machine dependency: execute_manifest refused until an environment variable named
an HTTP ingress to POST to. Under the ecosystem standard - every action a
manifest-bound state transition, no external machine awaited - that ingress could
never be configured, so the SDK had no working path at all. The destination comes
from completion.egress instead, and an absent destination is a manifest defect
repairable in the manifest.
"""
import os
import unittest
from unittest.mock import patch

from stegverse.manifest_state_transition_runtime import (
    DESTINATION_RESOLUTION_SOURCE,
    RECEIVER_UNAVAILABLE_DISPOSITION,
    build_intr_handoff,
    execute_manifest,
    manifest_declared_destination,
)

REQUEST = {
    "request_sha256": "a" * 64,
    "wire_manifest_sha256": "b" * 64,
    "canonical_manifest_sha256": "c" * 64,
    "graph_id": "HOLD-T0",
    "canonical_task_id": "ELAN-PAPER-COAUTHOR-PUBLICATION-001",
    "processing_capability": "governance",
    "route_id": "stegverse.route.canonical-governed.v1",
}
DESTINATION = {
    "final_stegverse_transition_surface": "stegverse.publisher.evidence-report-package/v1",
    "transport": "INTERLOCK_INTR",
    "far_side_transition_required": True,
    "destination_profile": "GCAT-BCAT-Engine/Publisher",
    "destination_sha256": "d" * 64,
}


class ManifestDeclaredDestinationTest(unittest.TestCase):
    def test_destination_is_read_from_completion_egress(self):
        canonical = {
            "completion": {
                "egress": {
                    "final_stegverse_transition_surface": "surface.v1",
                    "transport": "INTERLOCK_INTR",
                    "far_side_transition_required": True,
                    "destination_profile": "GCAT-BCAT-Engine/Publisher",
                }
            }
        }
        destination = manifest_declared_destination(canonical)
        self.assertEqual(destination["final_stegverse_transition_surface"], "surface.v1")
        self.assertEqual(destination["transport"], "INTERLOCK_INTR")
        self.assertEqual(destination["destination_profile"], "GCAT-BCAT-Engine/Publisher")
        self.assertTrue(destination["far_side_transition_required"])
        self.assertEqual(len(destination["destination_sha256"]), 64)

    def test_a_manifest_without_completion_declares_no_destination(self):
        self.assertIsNone(manifest_declared_destination({}))
        self.assertIsNone(manifest_declared_destination({"completion": {}}))
        self.assertIsNone(manifest_declared_destination({"completion": {"egress": {}}}))

    def test_destination_profile_is_optional(self):
        canonical = {"completion": {"egress": {"final_stegverse_transition_surface": "surface.v1"}}}
        self.assertIsNone(manifest_declared_destination(canonical)["destination_profile"])


class HandoffTest(unittest.TestCase):
    def test_declared_destination_hands_off_without_contacting_anything(self):
        handoff = build_intr_handoff({**REQUEST, "manifest_declared_destination": DESTINATION})
        self.assertEqual(handoff["disposition"], "ALLOW")
        self.assertEqual(handoff["state"], "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF")
        self.assertEqual(handoff["destination"], DESTINATION)
        self.assertEqual(handoff["destination_resolution_source"], DESTINATION_RESOLUTION_SOURCE)
        self.assertEqual(handoff["destination_resolution_environment_inputs"], [])
        self.assertFalse(handoff["transport_performed_by_sdk"])
        self.assertFalse(handoff["transport_credential_supplied_by_sdk"])
        self.assertFalse(handoff["receiver_contacted"])
        self.assertFalse(handoff["receiver_availability_required"])
        self.assertFalse(handoff["awaits_external_machine"])
        self.assertEqual(handoff["receiver_unavailable_disposition"], RECEIVER_UNAVAILABLE_DISPOSITION)
        self.assertEqual(len(handoff["handoff_sha256"]), 64)

    def test_handoff_claims_no_far_side_observation(self):
        handoff = build_intr_handoff({**REQUEST, "manifest_declared_destination": DESTINATION})
        self.assertFalse(handoff["intr_admission_observed"])
        self.assertFalse(handoff["far_side_transition_observed"])
        self.assertFalse(handoff["organization_receipt_observed"])
        self.assertFalse(handoff["master_records_reconstruction_observed"])
        self.assertFalse(handoff["consequence_committed"])
        self.assertFalse(handoff["terminal"])
        self.assertEqual(handoff["transition_authority"], "INTERLOCK_INTR")
        self.assertEqual(handoff["next_transition_owner"], "INTERLOCK_INTR")
        self.assertEqual(handoff["authority_effect"], "NONE_MANIFEST_HANDOFF_ONLY")

    def test_a_receiver_that_is_not_listening_does_not_change_the_handoff(self):
        """Destination existence is sufficient; liveness is not a predicate."""
        with patch.dict(os.environ, {}, clear=True):
            bare = build_intr_handoff({**REQUEST, "manifest_declared_destination": DESTINATION})
        with patch.dict(os.environ, {"STEGVERSE_UNIVERSAL_INTR_INGRESS_URL": "https://example.invalid/x"}):
            with_env = build_intr_handoff({**REQUEST, "manifest_declared_destination": DESTINATION})
        self.assertEqual(bare, with_env)


class UndeclaredDestinationTest(unittest.TestCase):
    def _result(self):
        with patch(
            "stegverse.manifest_state_transition_runtime.derive_execution_request",
            return_value={**REQUEST, "manifest_declared_destination": None},
        ):
            return execute_manifest({})

    def test_undeclared_destination_is_a_repairable_manifest_defect(self):
        result = self._result()
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["evaluation_boundary"], "SDK_MANIFEST_DESTINATION_BINDING")
        self.assertEqual(result["failure_code"], "MANIFEST_DECLARES_NO_EGRESS_DESTINATION")
        self.assertEqual(result["failed_predicate"], "MANIFEST_COMPLETION_EGRESS_DECLARES_A_DESTINATION")
        self.assertEqual(result["next_attempt"], "RE_MANIFEST_WITH_A_DECLARED_EGRESS_DESTINATION")
        self.assertIn("completion.egress", result["required_evidence_or_repair"])
        self.assertEqual(result["request_sha256"], REQUEST["request_sha256"])

    def test_the_repair_names_no_machine_and_consults_no_receiver(self):
        result = self._result()
        self.assertFalse(result["machine_dependency_introduced"])
        self.assertFalse(result["external_machine_required"])
        self.assertFalse(result["receiver_availability_consulted"])
        self.assertFalse(result["consequence_committed"])
        self.assertEqual(result["evidence_class"], "SDK_LOCAL_MANIFEST_BINDING")
        self.assertEqual(result["authority_effect"], "NONE")
        repair = result["required_evidence_or_repair"]
        for forbidden in ("ingress", "URL", "host", "reachable", "device", "machine", "attach"):
            self.assertNotIn(forbidden.lower(), repair.lower())


class ReturnLegTest(unittest.TestCase):
    """A correctable binding DENY re-manifests; it never re-transports."""

    def test_correctable_deny_produces_a_new_handoff_not_a_second_send(self):
        from stegverse.manifest_state_transition_runtime import admit_runtime_result

        request = {**REQUEST, "manifest_declared_destination": DESTINATION}
        repaired = {**request, "request_sha256": "e" * 64}
        denial = {"disposition": "DENY", "evaluation_boundary": "SDK_MANIFEST_PROFILE"}
        with patch(
            "stegverse.manifest_state_transition_runtime.validate_runtime_result",
            return_value=denial,
        ), patch(
            "stegverse.manifest_builder.correct_manifest_binding_deny",
            return_value=repaired,
        ):
            out = admit_runtime_result({}, request, denial)
        self.assertEqual(out["state"], "REMANIFESTED_AFTER_CORRECTABLE_BINDING_DENY")
        self.assertEqual(out["corrected_from_request_sha256"], REQUEST["request_sha256"])
        # The repair produces a fresh handoff carrying the new request's identity.
        self.assertEqual(out["handoff"]["request_sha256"], "e" * 64)
        self.assertFalse(out["handoff"]["receiver_contacted"])
        self.assertFalse(out["handoff"]["intr_admission_observed"])

    def test_an_unchanged_request_retains_the_exact_deny(self):
        from stegverse.manifest_state_transition_runtime import admit_runtime_result

        request = {**REQUEST, "manifest_declared_destination": DESTINATION}
        denial = {"disposition": "DENY", "evaluation_boundary": "SDK_MANIFEST_PROFILE"}
        with patch(
            "stegverse.manifest_state_transition_runtime.validate_runtime_result",
            return_value=denial,
        ), patch(
            "stegverse.manifest_builder.correct_manifest_binding_deny",
            side_effect=ValueError("manifest_binding_repair_produced_unchanged_request"),
        ):
            out = admit_runtime_result({}, request, denial)
        self.assertEqual(out, denial)

    def test_a_non_deny_result_passes_through_validation_unchanged(self):
        from stegverse.manifest_state_transition_runtime import admit_runtime_result

        checked = {"disposition": "ALLOW", "evaluation_boundary": "SOMEWHERE_ELSE"}
        with patch(
            "stegverse.manifest_state_transition_runtime.validate_runtime_result",
            return_value=checked,
        ):
            self.assertEqual(admit_runtime_result({}, REQUEST, {}), checked)


class NoTransportRemainsTest(unittest.TestCase):
    def test_the_module_holds_no_transport_client(self):
        import inspect

        from stegverse import manifest_state_transition_runtime as module

        source = inspect.getsource(module)
        for symbol in ("urlopen", "urllib", "_post_existing_intr",
                       "STEGVERSE_UNIVERSAL_INTR_INGRESS_URL",
                       "STEGVERSE_TVC_RELAY_AUTHORIZATION_ID"):
            self.assertNotIn(symbol, source, f"transport client symbol survived: {symbol}")
        self.assertFalse(hasattr(module, "INGRESS_URL_ENV"))
        self.assertFalse(hasattr(module, "TRANSPORT_AUTHORIZATION_ENV"))


if __name__ == "__main__":
    unittest.main()
