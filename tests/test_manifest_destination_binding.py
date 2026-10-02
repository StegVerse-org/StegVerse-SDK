"""Outbound organization routing comes from canonical capability mapping, not completion.egress.

The canonical registry declares sdk-manifest-ingress / SDK:ManifestIngress and
its owner. Until that registry/overlay also resolves a concrete organization
.github ingress endpoint, run-manifest fails closed rather than promoting
LLM_ADAPTER, Publisher, or caller-authored completion metadata to routing authority.
"""
import os
import json
import unittest
from unittest.mock import patch

from stegverse.manifest_execution import _canonical_organization_boundary
from stegverse.manifest_state_transition_runtime import (
    DESTINATION_RESOLUTION_SOURCE,
    RECEIVER_UNAVAILABLE_DISPOSITION,
    build_intr_handoff,
    execute_manifest,
    manifest_declared_destination,
    canonical_organization_destination,
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


ORGANIZATION_BOUNDARY = {
    "schema": "stegverse.organization-interlock-intr-boundary/v1",
    "organization": "StegVerse-Labs", "owner_repository": "StegVerse-Labs/.github",
    "ingress": {"capability_endpoint_bindings": [{
        "profile_id": "sdk-manifest-ingress", "profile_name": "SDK:ManifestIngress", "operation": "SUBMIT_MANIFEST",
        "receiving_operation": {"method": "POST", "path": "/intr/materialization", "owner_repository": "StegVerse-Labs/.github", "source": "workers/universal_intr_profiled_ingress.py", "delegate": "workers/manifest_state_transition_intr_ingress.py::admit"},
        "binding_role": "ORGANIZATION_RECEIVING_OPERATION_RESOLUTION", "authority_effect": "NONE_BINDING_ONLY",
        "grants_routing_authority": False, "grants_admission_authority": False, "grants_execution_authority": False, "environment_selected_ingress": False,
    }]},
}


class CanonicalOrganizationDestinationTest(unittest.TestCase):
    def test_consumes_organization_owned_binding_without_environment_or_authority(self):
        resolved = canonical_organization_destination(ORGANIZATION_BOUNDARY)
        self.assertEqual(resolved["owner_repository"], "StegVerse-Labs/.github")
        self.assertEqual(resolved["receiving_operation"]["path"], "/intr/materialization")
        self.assertEqual(resolved["environment_inputs"], [])
        self.assertEqual(resolved["authority_effect"], "NONE_BINDING_ONLY")
        self.assertFalse(resolved["grants_routing_authority"])
        self.assertFalse(resolved["grants_admission_authority"])
        self.assertFalse(resolved["grants_execution_authority"])

    def test_completion_metadata_cannot_override_organization_binding(self):
        canonical = {"completion": {"egress": {"final_stegverse_transition_surface": "LLM_ADAPTER", "destination_profile": "GCAT-BCAT-Engine/Publisher"}}}
        self.assertIsNone(manifest_declared_destination(canonical))
        self.assertEqual(canonical_organization_destination(ORGANIZATION_BOUNDARY)["receiving_operation"]["path"], "/intr/materialization")



class PublicRunManifestCanonicalSourceTest(unittest.TestCase):
    def test_existing_source_reader_binds_fixed_organization_contract(self):
        calls = []
        def fetch(binding):
            calls.append((binding.repository, binding.path, binding.ref))
            return {
                "text": json.dumps(ORGANIZATION_BOUNDARY),
                "repository": binding.repository,
                "path": binding.path,
                "ref": binding.ref,
                "sha": "fixture-blob",
            }
        boundary = _canonical_organization_boundary(fetcher=fetch)
        self.assertEqual(boundary, ORGANIZATION_BOUNDARY)
        self.assertEqual(calls, [(
            "StegVerse-Labs/.github",
            "org-runtime/interlock-intr.json",
            "75d68c83e28178af053b8af097de4c8ca7e5017e",
        )])

    def test_caller_cannot_select_repository_path_ref_or_endpoint(self):
        import inspect
        signature = inspect.signature(_canonical_organization_boundary)
        self.assertEqual(set(signature.parameters), {"fetcher"})
        self.assertEqual(
            canonical_organization_destination(ORGANIZATION_BOUNDARY)["receiving_operation"]["path"],
            "/intr/materialization",
        )


class HandoffTest(unittest.TestCase):
    def test_resolved_canonical_endpoint_produces_non_authorizing_handoff(self):
        result = build_intr_handoff({**REQUEST, "manifest_declared_destination": canonical_organization_destination(ORGANIZATION_BOUNDARY)})
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertEqual(result["destination"]["owner_repository"], "StegVerse-Labs/.github")
        self.assertEqual(result["destination"]["receiving_operation"]["path"], "/intr/materialization")
        self.assertFalse(result["transport_performed_by_sdk"])
        self.assertFalse(result["receiver_contacted"])
        self.assertFalse(result["intr_admission_observed"])

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
        self.assertEqual(result["evidence_class"], "SDK_LOCAL_CAPABILITY_DESTINATION_RESOLUTION")
        self.assertEqual(result["authority_effect"], "NONE")
        repair = result["required_evidence_or_repair"]
        self.assertIn("sdk-manifest-ingress / SDK:ManifestIngress", repair)
        self.assertIn(".github ingress endpoint", repair)
        self.assertIn("Do not substitute", repair)


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
