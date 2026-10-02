"""Outbound organization routing comes from canonical capability mapping, not completion.egress.

The canonical registry declares sdk-manifest-ingress / SDK:ManifestIngress and
its owner. Until that registry/overlay also resolves a concrete organization
.github ingress endpoint, run-manifest fails closed rather than promoting
LLM_ADAPTER, Publisher, or caller-authored completion metadata to routing authority.
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


class CompletionEgressIsNotDestinationTest(unittest.TestCase):
    def test_completion_egress_is_not_outbound_destination(self):
        canonical = {"completion": {"egress": {
            "final_stegverse_transition_surface": "LLM_ADAPTER",
            "transport": "INTERLOCK_INTR",
            "far_side_transition_required": True,
            "destination_profile": "GCAT-BCAT-Engine/Publisher",
        }}}
        self.assertIsNone(manifest_declared_destination(canonical))

    def test_a_manifest_without_completion_declares_no_destination(self):
        self.assertIsNone(manifest_declared_destination({}))
        self.assertIsNone(manifest_declared_destination({"completion": {}}))
        self.assertIsNone(manifest_declared_destination({"completion": {"egress": {}}}))

    def test_destination_profile_cannot_be_promoted_to_routing(self):
        canonical = {"completion": {"egress": {
            "final_stegverse_transition_surface": "surface.v1",
            "destination_profile": "GCAT-BCAT-Engine/Publisher",
        }}}
        self.assertIsNone(manifest_declared_destination(canonical))


class HandoffTest(unittest.TestCase):
    def test_unresolved_canonical_endpoint_fails_closed(self):
        result = build_intr_handoff({**REQUEST, "manifest_declared_destination": None})
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["evaluation_boundary"], "SDK_ORGANIZATION_DESTINATION_RESOLUTION")
        self.assertEqual(result["failure_code"], "CANONICAL_ORGANIZATION_INGRESS_ENDPOINT_NOT_RESOLVED")
        self.assertEqual(result["connector_profile_id"], "sdk-manifest-ingress")
        self.assertEqual(result["connector_destination_subsystem"], "SDK:ManifestIngress")
        self.assertFalse(result["completion_egress_controls_outbound_organization_routing"])
        self.assertFalse(result["llm_adapter_is_outbound_organization_destination"])
        self.assertFalse(result["publisher_is_outbound_organization_destination"])


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
        self.assertEqual(result["evaluation_boundary"], "SDK_ORGANIZATION_DESTINATION_RESOLUTION")
        self.assertEqual(result["failure_code"], "CANONICAL_ORGANIZATION_INGRESS_ENDPOINT_NOT_RESOLVED")
        self.assertEqual(result["failed_predicate"], "REGISTERED_CAPABILITY_RESOLVES_TO_CANONICAL_ORGANIZATION_GITHUB_INGRESS_ENDPOINT")
        self.assertEqual(result["next_attempt"], "RETRY_AFTER_CANONICAL_ORGANIZATION_ENDPOINT_MAPPING_IS_AVAILABLE")
        self.assertIn("sdk-manifest-ingress", result["required_evidence_or_repair"])
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
        for forbidden in ("host", "reachable", "device", "machine prerequisite", "attach"):
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
