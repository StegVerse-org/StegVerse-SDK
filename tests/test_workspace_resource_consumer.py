from __future__ import annotations

import unittest

from stegverse.external_interlock_ingress_binding import build_ingress_bound_interlock_request
from stegverse.manifest_builder import build_manifest
from stegverse.state_transition_evidence import attach_state_transition_evidence
from stegverse.workspace_resource_consumer import consume_workspace_resource


def governance_request():
    return {
        "candidate": {"actor_class": "external_entity", "action": "observe_external_document", "target": "shared-document", "scope": "bounded-ephemeral-projection", "parameters": {"external_side_effect": False}},
        "judgment": {"refusal_available": True, "operator_recoverability": "available", "workload_state": "supported", "time_pressure": "normal", "isolation_state": "supported", "evidence_refs": ["workspace:test:consumer"]},
        "signal": {"admitted_signal_refs": ["workspace:test:consumer"], "excluded_signal_refs": [], "transformations": [], "missing_inputs": [], "uncertainty_state": "bounded", "reference_state_hash": "a" * 64, "expected_reference_state_hash": "a" * 64, "reconstruction_available": True, "transformation_provenance_complete": True},
        "execution": {"actor_authority_current": True, "policy_current": True, "delegation_current": True, "evidence_current": True, "affected_entity_conditions_represented": True, "recoverability_profile": "recoverable", "validity_window_open": True, "policy_ref": "workspace:test-policy", "delegation_ref": "workspace:test-delegation", "evidence_refs": ["workspace:test:consumer"]},
        "capability": {"allowed": True}, "continuity": {"required": False}, "approval": {"required": False}, "permission_present": True,
    }


def request(*, unresolved=False):
    manifest = build_manifest(
        data={"resource_class": "external.collaborative-document.v1", "resource_ref": "provider-neutral:fixture", "observation": {"marker": "alpha"}},
        data_class="external.collaborative-document.v1",
        source_framework="provider-neutral-fixture",
        source_output_id="workspace-consumer-001",
        processor_request=governance_request(),
        created_at="2026-09-10T23:50:00Z",
    )
    manifest = attach_state_transition_evidence(manifest, {
        "profile": "stegverse.state-transition-evidence.v1",
        "transition_id": "workspace-consumer-transition-001",
        "state_domain": "external_document_projection",
        "prior_state_ref": "sha256:before",
        "new_state_ref": "sha256:after",
        "change_type": "REFRESHED",
        "applicable_predicates": [{"predicate_id": "authorization_current", "applicability": "APPLICABLE", "evidence_status": "UNRESOLVED" if unresolved else "SATISFIED"}],
        "ambiguities": [], "discovered_unknowns": [],
    })
    return build_ingress_bound_interlock_request(
        ingress_manifest=manifest,
        source_organization_id="Entity-A",
        target_organization_id="Entity-B",
        operation="OBSERVE_EXTERNAL_RESOURCE",
        authority_ref="TV/TVC:fixture",
        experiment_id="WORKSPACE-CONSUMER-001",
    )


class WorkspaceResourceConsumerTests(unittest.TestCase):
    def test_ready_materialization_produces_deterministic_non_authorizing_projection_state(self):
        state = consume_workspace_resource(request=request(), operation="MATERIALIZE", projection_id="projection-1")
        self.assertEqual(state["readiness"], "READY")
        self.assertTrue(state["projection_state_ref"].startswith("sha256:"))
        self.assertFalse(state["authority_transfer"])
        self.assertFalse(state["governance_authority"])
        self.assertFalse(state["intr_receipt_minted"])
        self.assertFalse(state["mir_custody_claimed"])
        self.assertFalse(state["master_records_custody_claimed"])

    def test_probe_required_blocks_materialize_and_refresh(self):
        for operation in ("MATERIALIZE", "REFRESH"):
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(ValueError, "requires READY state"):
                    consume_workspace_resource(request=request(unresolved=True), operation=operation, projection_id="projection-1")

    def test_probe_required_does_not_prevent_teardown(self):
        for operation in ("REVOKE", "EXPIRE", "DESTROY"):
            with self.subTest(operation=operation):
                state = consume_workspace_resource(request=request(unresolved=True), operation=operation, projection_id="projection-1", prior_projection_ref="sha256:prior")
                self.assertEqual(state["readiness"], "PROBE_REQUIRED")
                self.assertEqual(state["prior_projection_ref"], "sha256:prior")

    def test_provider_hook_is_evidence_only(self):
        def hook(operation, ingress):
            return {"provider_operation": operation, "resource_ref": ingress["payload"]["resource_ref"], "observed": True}

        state = consume_workspace_resource(request=request(), operation="OBSERVE", projection_id="projection-1", provider_hook=hook)
        self.assertTrue(state["provider_io_claimed"])
        self.assertTrue(state["provider_observation"]["observed"])
        self.assertFalse(state["governance_authority"])
        self.assertFalse(state["intr_receipt_minted"])

    def test_unsupported_operation_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported workspace operation"):
            consume_workspace_resource(request=request(), operation="PUBLISH", projection_id="projection-1")


if __name__ == "__main__":
    unittest.main()
