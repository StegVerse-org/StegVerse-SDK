from __future__ import annotations

import unittest

from stegverse.manifest_builder import build_manifest
from stegverse.state_transition_evidence import (
    READINESS_PROBE_REQUIRED,
    READINESS_READY,
    STATE_TRANSITION_PROFILE,
    attach_state_transition_evidence,
    normalize_state_transition_evidence,
)


def governance_request():
    return {
        "candidate": {
            "actor_class": "external_framework",
            "action": "project_workspace_state",
            "target": "external-shared-document",
            "scope": "test",
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


def transition(**overrides):
    value = {
        "profile": STATE_TRANSITION_PROFILE,
        "transition_id": "workspace-transition-002",
        "state_domain": "external_document_projection",
        "prior_state_ref": "sha256:before",
        "new_state_ref": "sha256:after",
        "change_type": "LIVE_EDIT",
        "applicable_predicates": [
            {
                "predicate_id": "session_admitted",
                "applicability": "APPLICABLE",
                "evidence_status": "SATISFIED",
                "evidence_refs": ["workspace:session:admitted"],
            },
            {
                "predicate_id": "projection_scope_current",
                "applicability": "APPLICABLE",
                "evidence_status": "SATISFIED",
                "evidence_refs": ["workspace:scope:current"],
            },
        ],
        "ambiguities": [],
        "discovered_unknowns": [],
    }
    value.update(overrides)
    return value


class StateTransitionEvidenceTests(unittest.TestCase):
    def test_all_known_applicable_predicates_satisfied_is_ready(self):
        result = normalize_state_transition_evidence(transition())
        self.assertEqual(result["readiness"], READINESS_READY)
        self.assertEqual(result["probe_reasons"], [])
        self.assertFalse(result["evidence_grants_authority"])

    def test_unknown_applicability_forces_probe_required(self):
        value = transition()
        value["applicable_predicates"].append(
            {
                "predicate_id": "external_owner_policy",
                "applicability": "UNKNOWN",
                "evidence_status": "UNRESOLVED",
            }
        )
        result = normalize_state_transition_evidence(value)
        self.assertEqual(result["readiness"], READINESS_PROBE_REQUIRED)
        self.assertIn(
            "predicate:external_owner_policy:applicability_unknown", result["probe_reasons"]
        )

    def test_open_ambiguity_forces_probe_required(self):
        result = normalize_state_transition_evidence(
            transition(
                ambiguities=[{"ambiguity_id": "which-document-revision", "status": "OPEN"}]
            )
        )
        self.assertEqual(result["readiness"], READINESS_PROBE_REQUIRED)

    def test_discovered_unknown_forces_probe_until_resolved(self):
        value = transition(
            discovered_unknowns=[
                {"unknown_id": "provider-lease-epoch", "status": "OPEN", "discovered_by": "probe-17"}
            ]
        )
        self.assertEqual(
            normalize_state_transition_evidence(value)["readiness"], READINESS_PROBE_REQUIRED
        )
        value["discovered_unknowns"][0]["status"] = "RESOLVED"
        self.assertEqual(normalize_state_transition_evidence(value)["readiness"], READINESS_READY)

    def test_false_ready_claim_is_rejected(self):
        value = transition(
            readiness=READINESS_READY,
            ambiguities=[{"ambiguity_id": "current-editor-identity", "status": "OPEN"}],
        )
        with self.assertRaisesRegex(ValueError, "contradicts derived readiness PROBE_REQUIRED"):
            normalize_state_transition_evidence(value)

    def test_not_applicable_predicate_requires_not_required_evidence(self):
        value = transition(
            applicable_predicates=[
                {
                    "predicate_id": "second-device-present",
                    "applicability": "NOT_APPLICABLE",
                    "evidence_status": "SATISFIED",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "must use NOT_REQUIRED"):
            normalize_state_transition_evidence(value)

    def test_attach_preserves_generic_manifest_and_source_payload(self):
        payload = {
            "provider": "external-shared-docs",
            "document_ref": "doc-001",
            "observed_revision": "rev-002",
            "content_binding": "b" * 64,
        }
        manifest = build_manifest(
            data=payload,
            data_class="external.collaborative-document-observation.v1",
            source_framework="shared-docs-test-adapter",
            source_output_id="shared-docs-rev-002",
            processor_request=governance_request(),
            created_at="2026-09-10T20:00:00Z",
        )
        result = attach_state_transition_evidence(manifest, transition())
        self.assertEqual(result["manifest_profile"], "stegverse.ingress-manifest.v1")
        self.assertEqual(result["payload"], payload)
        self.assertEqual(
            result["extensions"]["stegverse_state_transition"]["readiness"], READINESS_READY
        )
        self.assertFalse(
            result["extensions"]["stegverse_state_transition"]["evidence_grants_authority"]
        )

    def test_initial_materialization_allows_null_prior_state(self):
        result = normalize_state_transition_evidence(
            transition(
                transition_id="workspace-transition-001",
                prior_state_ref=None,
                new_state_ref="sha256:first-projection",
                change_type="MATERIALIZED",
            )
        )
        self.assertIsNone(result["prior_state_ref"])
        self.assertEqual(result["readiness"], READINESS_READY)


if __name__ == "__main__":
    unittest.main()
