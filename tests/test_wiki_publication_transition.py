from __future__ import annotations

from copy import deepcopy
import unittest

from stegverse.governance_navigation import canonical_sha256
from stegverse.security_posture_request import build_security_posture_request
from stegverse.wiki_publication_transition import (
    prepare_wiki_publication_manifest,
    publication_governance_candidate,
)


def transition(decision: str = "ALLOW_PUBLICATION_CANDIDATE") -> dict:
    return {
        "schema_version": "1.0.0",
        "transition_type": "external_framework_wiki_publication_transition",
        "package_id": "external-review-package:sha256:" + "1" * 64,
        "correction_receipt_id": "external-framework-correction-receipt:hmac-sha256:" + "2" * 64,
        "publisher_ref": "publisher:external-frameworks:test",
        "target_path": "docs/external-frameworks/reports/test-framework.compatibility.json",
        "decision": decision,
        "source_commit_ref": "commit:reviewed-source",
        "evidence_references": ["external:test:compatibility", "external:test:review"],
        "publication_executed": False,
        "boundary": {
            "transition_is_not_repository_write": True,
            "transition_is_not_certification": True,
            "transition_creates_no_standing": True,
            "separate_repository_mutation_required": True,
        },
    }


def governance_request(value: dict) -> dict:
    return {
        "candidate": publication_governance_candidate(value),
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": list(value["evidence_references"]),
        },
        "signal": {
            "admitted_signal_refs": list(value["evidence_references"]),
            "excluded_signal_refs": [],
            "transformations": [],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": canonical_sha256(value),
            "expected_reference_state_hash": canonical_sha256(value),
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": False,
            "policy_current": False,
            "delegation_current": False,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "publication-policy:requires-runtime-resolution",
            "delegation_ref": "publication-delegation:requires-runtime-resolution",
            "evidence_refs": list(value["evidence_references"]),
        },
        "capability": {"allowed": True},
        "continuity": {"required": True},
        "approval": {"required": True},
        "permission_present": False,
    }


def posture_request() -> dict:
    return build_security_posture_request(
        task_id="GOVERNED-WIKI-PUBLICATION-TRANSITION-001",
        selection_present=False,
        organization_minimum_tier="SECURE",
        data_class="stegverse.external-framework-wiki-publication-transition.v1",
        channel="wiki-publication",
    )


class WikiPublicationTransitionTests(unittest.TestCase):
    def test_allow_candidate_is_exactly_bound_without_authority_grant(self):
        value = transition()
        manifest = prepare_wiki_publication_manifest(
            transition=value,
            governance_request=governance_request(value),
            security_posture_request=posture_request(),
            created_at="2026-09-21T20:00:00Z",
        )
        self.assertEqual(manifest["payload"], value)
        self.assertEqual(manifest["hashes"]["payload_sha256"], canonical_sha256(value))
        params = manifest["candidate"]["parameters"]
        self.assertEqual(params["publication_transition_sha256"], canonical_sha256(value))
        self.assertEqual(params["package_id"], value["package_id"])
        self.assertEqual(params["correction_receipt_id"], value["correction_receipt_id"])
        self.assertEqual(params["source_commit_ref"], value["source_commit_ref"])
        self.assertEqual(params["publisher_ref"], value["publisher_ref"])
        self.assertEqual(params["target_repository"], "StegVerse-Labs/admissibility-wiki")
        self.assertEqual(params["target_path"], value["target_path"])
        self.assertEqual(params["decision"], "ALLOW_PUBLICATION_CANDIDATE")
        self.assertEqual(params["evidence_references"], value["evidence_references"])
        self.assertFalse(params["publication_executed"])
        self.assertTrue(manifest["completion"]["publisher"]["required"])

    def test_converter_does_not_synthesize_governance_candidate(self):
        value = transition()
        request = governance_request(value)
        request["candidate"]["parameters"]["publisher_ref"] = "publisher:tampered"
        with self.assertRaisesRegex(ValueError, "exactly bind publication transition"):
            prepare_wiki_publication_manifest(
                transition=value,
                governance_request=request,
                security_posture_request=posture_request(),
                created_at="2026-09-21T20:00:00Z",
            )

    def test_publication_executed_true_is_rejected(self):
        value = transition()
        value["publication_executed"] = True
        with self.assertRaisesRegex(ValueError, "publication_executed=false"):
            publication_governance_candidate(value)

    def test_non_allow_is_manifestable_but_cannot_require_publisher(self):
        for decision in ("DENY_PUBLICATION", "REVIEW_REQUIRED"):
            with self.subTest(decision=decision):
                value = transition(decision)
                manifest = prepare_wiki_publication_manifest(
                    transition=value,
                    governance_request=governance_request(value),
                    security_posture_request=posture_request(),
                    created_at="2026-09-21T20:00:00Z",
                )
                self.assertEqual(manifest["candidate"]["parameters"]["decision"], decision)
                self.assertFalse(manifest["candidate"]["parameters"]["external_side_effect"])
                self.assertFalse(manifest["completion"]["publisher"]["required"])
                self.assertIn("zero repository mutation", manifest["requested_consequence"])

    def test_manifest_requires_authoritative_intr_posture_request(self):
        value = transition()
        manifest = prepare_wiki_publication_manifest(
            transition=value,
            governance_request=governance_request(value),
            security_posture_request=posture_request(),
            created_at="2026-09-21T20:00:00Z",
        )
        posture = manifest["extensions"]["security_posture_request"]
        self.assertEqual(posture["task_id"], "GOVERNED-WIKI-PUBLICATION-TRANSITION-001")
        self.assertEqual(posture["authority_effect"], "NONE_REQUEST_INPUT_ONLY")
        self.assertEqual(manifest["completion"]["egress"]["transport"], "INTERLOCK_INTR")

    def test_wrong_posture_task_binding_fails_closed(self):
        value = transition()
        bad = posture_request()
        bad["task_id"] = "OTHER-TASK"
        with self.assertRaisesRegex(ValueError, "must bind governed wiki publication task"):
            prepare_wiki_publication_manifest(
                transition=value,
                governance_request=governance_request(value),
                security_posture_request=bad,
                created_at="2026-09-21T20:00:00Z",
            )

    def test_reserved_targets_are_not_enabled_by_default(self):
        value = transition()
        with self.assertRaisesRegex(ValueError, "reserved but not enabled"):
            publication_governance_candidate(value, target_profile="stegguardian")


if __name__ == "__main__":
    unittest.main()
