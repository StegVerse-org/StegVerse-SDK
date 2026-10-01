"""A route's surface must state what its transport requires, not leave a bare guard.

The transport ingress is a resident loopback listener. The SDK may say what the
surface requires; it may not discover the endpoint, start the listener, mint the
credential, or accept an endpoint a manifest named for itself.
"""
import os
import unittest
from unittest.mock import patch

from stegverse.manifest_state_transition_runtime import (
    UNIVERSAL_RUNTIME_BINDING,
    execute_manifest,
)
from stegverse.route_resolution import PUBLISHED_ROUTES
from stegverse.transport_ingress_profile import (
    AUTHORITY_BOUNDARY,
    MISMATCH_NON_LOOPBACK_PLAINTEXT,
    MISMATCH_PATH,
    PROFILE_MISMATCH,
    SURFACE_UNKNOWN,
    ingress_repair_instruction,
    resolve_ingress_profile,
    validate_ingress_instance,
)

RESIDENT_INGRESS = "http://127.0.0.1:51221/intr/materialization"

REQUEST = {
    "request_sha256": "a" * 64,
    "wire_manifest_sha256": "b" * 64,
    "canonical_manifest_sha256": "c" * 64,
    "graph_id": "HOLD-T0",
    "canonical_task_id": "SDK-TRANSPORT-INGRESS-PROFILE-001",
    "processing_capability": "governance",
    "route_id": "stegverse.route.canonical-governed.v1",
}


class SurfaceCoverageTest(unittest.TestCase):
    def test_every_published_route_surface_has_a_profile(self):
        for route_id, route in PUBLISHED_ROUTES.items():
            with self.subTest(route_id=route_id):
                profile = resolve_ingress_profile(route["routing_surface"])
                self.assertTrue(profile["resolved"], route["routing_surface"])

    def test_universal_runtime_routes_require_transport(self):
        transported = [r for r in PUBLISHED_ROUTES.values()
                       if r.get("runtime_binding") == UNIVERSAL_RUNTIME_BINDING]
        self.assertGreater(len(transported), 0)
        for route in transported:
            with self.subTest(route_id=route["route_id"]):
                profile = resolve_ingress_profile(route["routing_surface"])
                self.assertTrue(profile["transport_required"])
                self.assertEqual(profile["transport"], "INTERLOCK_INTR")
                self.assertEqual(profile["credential_authority"], "TV/TVC")
                self.assertFalse(profile["reachable_from_hosted_ci"])

    def test_routes_with_their_own_runtime_require_no_transport(self):
        local = [r for r in PUBLISHED_ROUTES.values()
                 if r.get("runtime_binding") != UNIVERSAL_RUNTIME_BINDING]
        self.assertGreater(len(local), 0)
        for route in local:
            with self.subTest(route_id=route["route_id"]):
                profile = resolve_ingress_profile(route["routing_surface"])
                self.assertFalse(profile["transport_required"])

    def test_unknown_surface_is_not_defaulted_to_a_transport(self):
        profile = resolve_ingress_profile("SOME_UNPUBLISHED_SURFACE")
        self.assertFalse(profile["resolved"])
        self.assertEqual(profile["failed_predicate"], SURFACE_UNKNOWN)
        self.assertNotIn("transport_required", profile)


class InstanceRecognitionTest(unittest.TestCase):
    def setUp(self):
        self.profile = resolve_ingress_profile("EXISTING_UNIVERSAL_INTR")

    def test_resident_loopback_materialization_endpoint_matches(self):
        self.assertTrue(validate_ingress_instance(self.profile, RESIDENT_INGRESS)["matched"])

    def test_non_loopback_plaintext_is_named_not_silently_accepted(self):
        outcome = validate_ingress_instance(self.profile, "http://ingress.invalid/intr/materialization")
        self.assertFalse(outcome["matched"])
        self.assertEqual(outcome["mismatch_reason"], MISMATCH_NON_LOOPBACK_PLAINTEXT)

    def test_wrong_path_is_rejected(self):
        outcome = validate_ingress_instance(self.profile, "http://127.0.0.1:51221/ingress")
        self.assertFalse(outcome["matched"])
        self.assertEqual(outcome["mismatch_reason"], MISMATCH_PATH)

    def test_non_loopback_with_tls_is_permitted_as_the_listener_permits_it(self):
        outcome = validate_ingress_instance(self.profile, "https://relay.example/intr/materialization")
        self.assertTrue(outcome["matched"])

    def test_recognition_grants_nothing(self):
        outcome = validate_ingress_instance(self.profile, RESIDENT_INGRESS)
        self.assertEqual(outcome["authority_boundary"], AUTHORITY_BOUNDARY)
        for claim in AUTHORITY_BOUNDARY.values():
            self.assertFalse(claim)


class RepairInstructionTest(unittest.TestCase):
    def test_unconfigured_ingress_repair_names_the_listener_and_the_binding(self):
        profile = resolve_ingress_profile("EXISTING_UNIVERSAL_INTR")
        repair = ingress_repair_instruction(profile, "UNIVERSAL_INTR_INGRESS_NOT_CONFIGURED")
        self.assertIn("serve_hil_intr_materialization_ingress.py", repair)
        self.assertIn("STEGVERSE_UNIVERSAL_INTR_INGRESS_URL", repair)
        self.assertIn("/intr/materialization", repair)
        self.assertIn("not reachable from hosted CI", repair)

    def test_credential_repair_does_not_claim_the_sdk_can_supply_it(self):
        profile = resolve_ingress_profile("EXISTING_UNIVERSAL_INTR")
        repair = ingress_repair_instruction(profile, "TV_TVC_RELAY_AUTHORIZATION_REQUIRED")
        self.assertIn("TV/TVC issues it", repair)
        self.assertIn("neither mints nor discovers", repair)


class AttachmentRecordTest(unittest.TestCase):
    def _attempt(self, env):
        with patch("stegverse.manifest_state_transition_runtime.derive_execution_request",
                   return_value=REQUEST):
            with patch.dict(os.environ, env):
                return execute_manifest({})

    def test_fail_closed_record_carries_the_resolved_profile(self):
        result = self._attempt({"STEGVERSE_UNIVERSAL_INTR_INGRESS_URL": ""})
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        profile = result["transport_ingress_profile"]
        self.assertTrue(profile["resolved"])
        self.assertEqual(profile["routing_surface"], "CANONICAL_PRODUCTION")
        self.assertIn("serve_hil_intr_materialization_ingress.py",
                      result["required_evidence_or_repair"])

    def test_mismatched_endpoint_fails_closed_without_posting(self):
        with patch("stegverse.manifest_state_transition_runtime.urllib.request.urlopen") as opened:
            result = self._attempt({
                "STEGVERSE_UNIVERSAL_INTR_INGRESS_URL": "http://ingress.invalid/materialize",
                "STEGVERSE_TVC_RELAY_AUTHORIZATION_ID": "tvc-relay-0001",
            })
        opened.assert_not_called()
        self.assertEqual(result["failed_predicate"], PROFILE_MISMATCH)
        self.assertFalse(result["consequence_committed"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_record_still_claims_no_downstream_observation(self):
        result = self._attempt({"STEGVERSE_UNIVERSAL_INTR_INGRESS_URL": ""})
        self.assertFalse(result["authentic_governance_disposition_observed"])
        self.assertFalse(result["organization_receipt_observed"])
        self.assertFalse(result["master_records_reconstruction_observed"])


if __name__ == "__main__":
    unittest.main()
