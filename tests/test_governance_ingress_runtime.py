from __future__ import annotations

import unittest
from unittest.mock import patch

from stegverse.governance_ingress_runtime import (
    GOVERNANCE_REQUEST_EXTENSION,
    build_000_public_request,
    external_manifest_to_public_request,
    run_000_demo,
)
from stegverse.governance_navigation import canonical_sha256, demo_output_manifest_shape
from stegverse.route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    ROUTE_DECLARATION_EXTENSION,
    governance_state_hash,
)


def governance_request(candidate):
    return {
        "candidate": dict(candidate),
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["fixture:judgment"],
        },
        "signal": {
            "admitted_signal_refs": ["fixture:signal"],
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": "a" * 64,
            "expected_reference_state_hash": "a" * 64,
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": True,
            "policy_current": True,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "fixture:policy",
            "delegation_ref": "fixture:delegation",
            "evidence_refs": ["fixture:execution"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
        "declared_context": {"fixture": True},
    }


def production_route():
    return {
        "route_id": CANONICAL_PRODUCTION_ROUTE_ID,
        "lane_class": "PRODUCTION_VALIDATION",
        "routing_surface": "CANONICAL_PRODUCTION",
        "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
        "sandbox_required": False,
        "external_consequence_enabled": False,
    }


def external_manifest(*, include_governance=True, include_route=True, mismatched=False, route=None):
    payload = {"value": 1}
    candidate = {
        "actor_class": "external_system",
        "action": "inspect",
        "target": "fixture",
        "scope": "test",
        "parameters": {},
    }
    request_candidate = dict(candidate)
    if mismatched:
        request_candidate["target"] = "different-fixture"
    extensions = {}
    if include_governance:
        extensions[GOVERNANCE_REQUEST_EXTENSION] = governance_request(request_candidate)
    if include_route:
        extensions[ROUTE_DECLARATION_EXTENSION] = dict(route or production_route())
    return {
        "manifest_profile": "stegverse.ingress-manifest.v1",
        "manifest_profile_version": "1",
        "source_framework": "fixture-framework",
        "source_instance": "fixture-instance",
        "source_output_id": "fixture-output-1",
        "created_at": "2026-08-15T00:00:00Z",
        "freshness": {"status": "fresh"},
        "payload": payload,
        "candidate": candidate,
        "declared_intent": "inspect fixture",
        "requested_consequence": "none",
        "context_refs": [],
        "canonicalization_profile": "steggate.jcs.v1",
        "hashes": {
            "payload_sha256": canonical_sha256(payload),
            "candidate_sha256": canonical_sha256(candidate),
        },
        "attestation": None,
        "extensions": extensions,
        "return_projection": {"mode": "ALL", "transition_classes": []},
        "manifest_labels": {"mode": "ALL"},
    }


class Tests(unittest.TestCase):
    def test_0b_requires_complete_governance_request(self):
        with self.assertRaisesRegex(ValueError, "complete canonical StegGate request"):
            external_manifest_to_public_request(external_manifest(include_governance=False))

    def test_0b_requires_explicit_published_route(self):
        with self.assertRaisesRegex(ValueError, "declaring a published route"):
            external_manifest_to_public_request(external_manifest(include_route=False))

    def test_0b_rejects_unknown_route_instead_of_substituting_default(self):
        bad = production_route()
        bad["route_id"] = "stegverse.route.unknown.v1"
        with self.assertRaisesRegex(ValueError, "unsupported manifest route"):
            external_manifest_to_public_request(external_manifest(route=bad))

    def test_0b_rejects_route_tuple_conflict(self):
        bad = production_route()
        bad["routing_surface"] = "DEMO_TEST_REPOSITORY"
        with self.assertRaisesRegex(ValueError, "conflicts with published routing_surface"):
            external_manifest_to_public_request(external_manifest(route=bad))

    def test_0b_fails_closed_on_candidate_identity_mismatch(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            external_manifest_to_public_request(external_manifest(mismatched=True))

    def test_0b_preserves_manifest_identity_route_and_state_binding_without_granting_authority(self):
        manifest = external_manifest()
        original_state = manifest["extensions"][GOVERNANCE_REQUEST_EXTENSION]
        request = external_manifest_to_public_request(manifest)
        self.assertFalse(request["authority_claim"])
        provenance = request["execution_provenance"]
        self.assertFalse(provenance["external_consequence_enabled"])
        self.assertEqual(CANONICAL_PRODUCTION_ROUTE_ID, provenance["route_id"])
        self.assertEqual(governance_state_hash(original_state), provenance["state_binding_hash"])
        identity = request["input"]["ingress_manifest_identity"]
        self.assertEqual("stegverse.ingress-manifest.v1", identity["manifest_profile"])
        self.assertEqual("fixture-framework", identity["source_framework"])
        self.assertEqual("external_manifest", identity["ingress_mode"])
        self.assertEqual("NONE", identity["authority_effect"])
        self.assertEqual(
            identity,
            request["input"]["steggate_request"]["declared_context"]["sdk_ingress_manifest_identity"],
        )
        route_binding = request["input"]["route_binding"]
        self.assertEqual(CANONICAL_PRODUCTION_ROUTE_ID, route_binding["route_id"])
        self.assertEqual(provenance["route_declaration_hash"], route_binding["route_declaration_hash"])
        self.assertEqual(provenance["state_binding_hash"], route_binding["state_binding_hash"])
        self.assertFalse(route_binding["route_substitution_permitted"])

    def test_000_builds_complete_bounded_canonical_request(self):
        request = build_000_public_request()
        gate = request["input"]["steggate_request"]
        self.assertEqual("sdk_demo", gate["candidate"]["actor_class"])
        self.assertEqual("evaluate_demo", gate["candidate"]["action"])
        self.assertTrue(gate["judgment"]["refusal_available"])
        self.assertEqual("bounded", gate["signal"]["uncertainty_state"])
        self.assertTrue(gate["execution"]["policy_current"])
        self.assertFalse(gate["continuity"]["required"])
        self.assertFalse(gate["approval"]["required"])
        self.assertFalse(request["execution_provenance"]["external_consequence_enabled"])
        self.assertEqual(CANONICAL_PRODUCTION_ROUTE_ID, request["execution_provenance"]["route_id"])
        self.assertFalse(request["authority_claim"])

    @patch("stegverse.sovereign_validation_runtime.run_sovereign_validation")
    def test_000_replaces_pending_only_after_canonical_runtime_result(self, run):
        run.return_value = {
            "manifest_receipt_id": "MR-" + "A" * 64,
            "route_receipt_chain_head": "B" * 64,
            "governance_state": "ALLOW",
            "chain_verified": True,
            "master_records_custody_status": "RECORDED",
            "external_side_effect": False,
            "third_party_host_required": False,
        }
        result = run_000_demo(custody_db=":memory:")
        processing = result["demo_dataset_processing"]
        self.assertEqual("PROCESSED_CANONICAL_RUNTIME", processing["canonical_processing_status"])
        self.assertTrue(processing["chain_verified"])
        self.assertEqual("RECORDED", processing["master_records_custody_status"])
        self.assertFalse(processing["external_side_effect"])
        self.assertFalse(processing["do_not_claim_processed_until_receipts_exist"])
        self.assertTrue(run.called)

    def test_static_demo_shape_remains_pending_without_runtime(self):
        result = demo_output_manifest_shape()
        self.assertEqual("PENDING_RUNTIME_BINDING", result["demo_dataset_processing"]["canonical_processing_status"])


if __name__ == "__main__":
    unittest.main()
