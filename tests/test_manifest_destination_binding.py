"""Outbound organization routing comes from canonical capability mapping, not completion.egress.

The canonical registry declares sdk-manifest-ingress / SDK:ManifestIngress and
its owner. Until that registry/overlay also resolves a concrete organization
.github ingress endpoint, run-manifest fails closed rather than promoting
LLM_ADAPTER, Publisher, or caller-authored completion metadata to routing authority.
"""
import os
import json
import unittest
from pathlib import Path
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


# Exact content of StegVerse-Labs/.github:org-runtime/interlock-intr.json at the
# pinned canonical ref (aa2f89ac877e6a84bedb81a8b4efb30f4910d5f4).
BOUNDARY_FIXTURE = Path(__file__).parent / "fixtures" / "stegverse-labs-interlock-intr-boundary.aa2f89ac.json"
ORGANIZATION_BOUNDARY = json.loads(BOUNDARY_FIXTURE.read_text(encoding="utf-8"))
PINNED_BOUNDARY_REF = "aa2f89ac877e6a84bedb81a8b4efb30f4910d5f4"


class CanonicalOrganizationDestinationTest(unittest.TestCase):
    def test_consumes_organization_owned_binding_without_environment_or_authority(self):
        resolved = canonical_organization_destination(ORGANIZATION_BOUNDARY)
        self.assertEqual(resolved["owner_repository"], "StegVerse-Labs/.github")
        self.assertEqual(resolved["receiving_operation"]["operation_id"], "ORGANIZATION_SDK_MANIFEST_INGRESS")
        self.assertEqual(resolved["environment_inputs"], [])
        self.assertEqual(resolved["authority_effect"], "NONE_BINDING_ONLY")
        self.assertFalse(resolved["grants_routing_authority"])
        self.assertFalse(resolved["grants_admission_authority"])
        self.assertFalse(resolved["grants_execution_authority"])

    def test_completion_metadata_cannot_override_organization_binding(self):
        canonical = {"completion": {"egress": {"final_stegverse_transition_surface": "LLM_ADAPTER", "destination_profile": "GCAT-BCAT-Engine/Publisher"}}}
        self.assertIsNone(manifest_declared_destination(canonical))
        self.assertEqual(canonical_organization_destination(ORGANIZATION_BOUNDARY)["receiving_operation"]["operation_id"], "ORGANIZATION_SDK_MANIFEST_INGRESS")



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
            PINNED_BOUNDARY_REF,
        )])

    def test_caller_cannot_select_repository_path_ref_or_endpoint(self):
        import inspect
        signature = inspect.signature(_canonical_organization_boundary)
        self.assertEqual(set(signature.parameters), {"fetcher"})
        self.assertEqual(
            canonical_organization_destination(ORGANIZATION_BOUNDARY)["receiving_operation"]["operation_id"],
            "ORGANIZATION_SDK_MANIFEST_INGRESS",
        )


class PinnedCanonicalBoundaryRegressionTest(unittest.TestCase):
    """The pinned ref resolves SDK manifest ingress to the organization-owned operation."""

    def test_sdk_pins_the_current_organization_boundary_ref(self):
        from stegverse import manifest_execution
        self.assertEqual(manifest_execution._CANONICAL_ORGANIZATION_BOUNDARY_REF, PINNED_BOUNDARY_REF)

    def test_pinned_boundary_resolves_organization_sdk_manifest_ingress(self):
        def fetch(binding):
            self.assertEqual(binding.ref, PINNED_BOUNDARY_REF)
            return {"text": BOUNDARY_FIXTURE.read_text(encoding="utf-8"), "repository": binding.repository,
                    "path": binding.path, "ref": binding.ref, "sha": "fixture-blob"}
        resolved = canonical_organization_destination(_canonical_organization_boundary(fetcher=fetch))
        self.assertEqual(resolved["profile_id"], "sdk-manifest-ingress")
        self.assertEqual(resolved["operation"], "SUBMIT_MANIFEST")
        self.assertEqual(resolved["owner_repository"], "StegVerse-Labs/.github")
        operation = resolved["receiving_operation"]
        self.assertEqual(operation["operation_id"], "ORGANIZATION_SDK_MANIFEST_INGRESS")
        self.assertEqual(operation["owner_repository"], "StegVerse-Labs/.github")
        self.assertEqual(operation["operation"], "resident-runtime/organization_manifest_ingress.py")
        self.assertEqual(operation["address_resolution"], "org-boundary/runtime/capability_ingress.py::receive")
        self.assertEqual(operation["admission"], "resident-runtime/sdk_manifest_crossing.py::cross")
        self.assertEqual(operation["emits"], "stegverse.organization-transition-receipt/v1")
        self.assertEqual(operation["transport"], "INTERLOCK_INTR")
        self.assertNotIn("path", operation)
        self.assertNotIn("method", operation)
        self.assertEqual(resolved["environment_inputs"], [])
        self.assertEqual(resolved["authority_effect"], "NONE_BINDING_ONLY")

    def test_pinned_boundary_binding_is_non_authorizing(self):
        bindings = [b for b in ORGANIZATION_BOUNDARY["ingress"]["capability_endpoint_bindings"]
                    if b.get("profile_id") == "sdk-manifest-ingress" and b.get("operation") == "SUBMIT_MANIFEST"]
        self.assertEqual(len(bindings), 1)
        for flag in ("grants_routing_authority", "grants_admission_authority",
                     "grants_execution_authority", "environment_selected_ingress"):
            self.assertIs(bindings[0][flag], False, flag)


class HandoffTest(unittest.TestCase):
    def test_resolved_canonical_endpoint_produces_non_authorizing_handoff(self):
        result = build_intr_handoff({**REQUEST, "manifest_declared_destination": canonical_organization_destination(ORGANIZATION_BOUNDARY)})
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertEqual(result["destination"]["owner_repository"], "StegVerse-Labs/.github")
        self.assertEqual(result["destination"]["receiving_operation"]["operation_id"], "ORGANIZATION_SDK_MANIFEST_INGRESS")
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
