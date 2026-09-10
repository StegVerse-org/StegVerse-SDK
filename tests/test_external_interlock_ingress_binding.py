from __future__ import annotations

import copy
import unittest

from stegverse.external_interlock_ingress_binding import (
    BINDING_PROFILE,
    build_ingress_bound_interlock_request,
    validate_ingress_bound_interlock_request,
)
from stegverse.manifest_builder import build_manifest
from stegverse.state_transition_evidence import attach_state_transition_evidence


def governance_request():
    return {
        "candidate": {
            "actor_class": "external_entity",
            "action": "observe_external_document",
            "target": "shared-document",
            "scope": "bounded-ephemeral-projection",
            "parameters": {"external_side_effect": False},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["workspace:test:1"],
        },
        "signal": {
            "admitted_signal_refs": ["workspace:test:1"],
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
            "policy_ref": "workspace:test-policy",
            "delegation_ref": "workspace:test-delegation",
            "evidence_refs": ["workspace:test:1"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }


def ingress_manifest(*, unresolved: bool = False):
    manifest = build_manifest(
        data={
            "resource_class": "external.collaborative-document.v1",
            "resource_ref": "shared-docs:fixture-document",
            "observation": {"marker": "alpha", "content_sha256": "b" * 64},
        },
        data_class="external.collaborative-document.v1",
        source_framework="shared-docs-fixture",
        source_output_id="workspace-observation-001",
        processor_request=governance_request(),
        created_at="2026-09-10T21:30:00Z",
    )
    transition = {
        "profile": "stegverse.state-transition-evidence.v1",
        "transition_id": "workspace-transition-001",
        "state_domain": "external_document_projection",
        "prior_state_ref": None,
        "new_state_ref": "shared-docs:fixture-document:alpha",
        "change_type": "MATERIALIZED",
        "applicable_predicates": [
            {
                "predicate_id": "authorization_current",
                "applicability": "APPLICABLE",
                "evidence_status": "UNRESOLVED" if unresolved else "SATISFIED",
            },
            {
                "predicate_id": "projection_scope_bounded",
                "applicability": "APPLICABLE",
                "evidence_status": "SATISFIED",
            },
        ],
        "ambiguities": [],
        "discovered_unknowns": [],
    }
    return attach_state_transition_evidence(manifest, transition)


class ExternalInterlockIngressBindingTests(unittest.TestCase):
    def build_request(self, *, unresolved: bool = False):
        return build_ingress_bound_interlock_request(
            ingress_manifest=ingress_manifest(unresolved=unresolved),
            source_organization_id="Entity-A",
            target_organization_id="Entity-B",
            operation="OBSERVE_EXTERNAL_RESOURCE",
            authority_ref="TV/TVC:fixture",
            experiment_id="WORKSPACE-GENERIC-INTR-001",
        )

    def test_canonical_ingress_remains_universal_payload_inside_transport_control(self):
        request = self.build_request()
        interaction = request["payload"]["manifest"]
        nested = interaction["payload"]["canonical_ingress_manifest"]
        self.assertEqual(interaction["schema"], "stegverse.external_organization.interaction_manifest.v1")
        self.assertEqual(interaction["payload"]["binding_profile"], BINDING_PROFILE)
        self.assertEqual(nested["manifest_profile"], "stegverse.ingress-manifest.v1")
        self.assertEqual(nested["extensions"]["stegverse_state_transition"]["readiness"], "READY")
        self.assertFalse(request["canonical_ingress_grants_transport_authority"])
        self.assertFalse(request["sdk_mints_intr_receipt"])
        self.assertFalse(request["sdk_claims_delivery"])
        validate_ingress_bound_interlock_request(request)

    def test_probe_required_state_survives_transport_binding_without_becoming_ready(self):
        request = self.build_request(unresolved=True)
        state = request["payload"]["manifest"]["payload"]["canonical_ingress_manifest"]["extensions"]["stegverse_state_transition"]
        self.assertEqual(state["readiness"], "PROBE_REQUIRED")
        self.assertIn("predicate:authorization_current:evidence_unresolved", state["probe_reasons"])
        validate_ingress_bound_interlock_request(request)

    def test_nested_ingress_tamper_fails_before_transport_acceptance(self):
        bad = copy.deepcopy(self.build_request())
        bad["payload"]["manifest"]["payload"]["canonical_ingress_manifest"]["payload"]["observation"]["marker"] = "tampered"
        with self.assertRaises(ValueError):
            validate_ingress_bound_interlock_request(bad)

    def test_binding_hash_tamper_fails_even_when_nested_manifest_is_unchanged(self):
        bad = copy.deepcopy(self.build_request())
        bad["bindings"]["canonical_ingress_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bindings.canonical_ingress_sha256"):
            validate_ingress_bound_interlock_request(bad)

    def test_transport_control_tamper_fails_without_invoking_runtime(self):
        bad = copy.deepcopy(self.build_request())
        bad["sdk_claims_delivery"] = True
        with self.assertRaisesRegex(ValueError, "sdk_claims_delivery mismatch"):
            validate_ingress_bound_interlock_request(bad)


if __name__ == "__main__":
    unittest.main()
