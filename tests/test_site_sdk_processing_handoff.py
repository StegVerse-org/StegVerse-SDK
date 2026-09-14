from __future__ import annotations

import unittest
from unittest.mock import patch

from stegverse.governance_navigation import canonical_sha256
from stegverse.manifest_builder import build_manifest
from stegverse.site_sdk_processing_handoff import (
    NEXT_TRANSITION,
    SITE_SDK_PROCESSING_HANDOFF_SCHEMA,
    SiteSdkProcessingHandoffError,
    execute_site_sdk_processing_handoff,
    validate_site_sdk_processing_handoff,
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
            "evidence_refs": ["mir-site-handoff:judgment"],
        },
        "signal": {
            "admitted_signal_refs": ["mir-site-handoff:signal"],
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
            "policy_ref": "mir-site-handoff:policy",
            "delegation_ref": "mir-site-handoff:delegation",
            "evidence_refs": ["mir-site-handoff:execution"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
        "declared_context": {"fixture": "site-sdk-processing-handoff"},
    }


def admitted_manifest():
    candidate = {
        "actor_class": "external_framework",
        "action": "process_mir_return",
        "target": "retained-mir-node-mirror-return",
        "scope": "MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001",
        "parameters": {"external_side_effect": False},
    }
    return build_manifest(
        data={"schema": "stegverse.mir.source-native-result/v1", "event_count": 2},
        source_framework="MIR_NODE_MIRROR",
        source_instance="StegVerse-Labs/Site#1319",
        source_output_id="mir-retained-return-001",
        processor_request=governance_request(candidate),
        process="governance",
        return_depth="result+evidence",
        created_at="2026-09-14T17:45:00Z",
        context_refs=[
            "StegVerse-Labs/Site#1319",
            "StegVerse-Labs/Site@7c2d19649a8ad52520e45a76b4a0009a22f2e0df",
        ],
        declared_intent="Process the admitted retained MIR return through the manifest-selected SDK route.",
        requested_consequence="Execute SDK-owned manifest-selected processing without creating MIR-specific transport or authority.",
        initiator_class="site_sdk_processing_handoff",
        initiator_ref="StegVerse-Labs/Site#1319",
        publisher_required=False,
    )


def site_handoff():
    manifest = admitted_manifest()
    manifest_hash = canonical_sha256(manifest)
    response_to = "mir-node-mirror-runtime-return-001"
    return {
        "schema": SITE_SDK_PROCESSING_HANDOFF_SCHEMA,
        "manifest": manifest,
        "manifest_hash": "sha256:" + manifest_hash,
        "response_to": response_to,
        "retained_packet_sha256": "sha256:" + "b" * 64,
        "retained_packet_schema": "stegverse.canonical-runtime-exact-return-packet/v1",
        "stegverse_return_exit_receipt": {
            "transition_class": "STEGVERSE_RETURN_EXIT",
            "response_to": response_to,
            "manifest_sha256": "sha256:" + manifest_hash,
            "authority_effect": "NONE_ADMISSION_ONLY",
        },
        "sdk_evaluator_ingress_state": "SDK_EVALUATOR_INGRESS_ADMITTED",
        "node_transition_receipt": {
            "schema": "stegos.node_capability_receipt.v1",
            "transition": "EXTERNAL_COUNTERPART_RETURN_ADMITTED",
            "capability": "external-counterpart-return",
            "authority_effect": "NONE",
        },
        "next_required_transition": NEXT_TRANSITION,
        "authority_effect": "NONE",
    }


class Tests(unittest.TestCase):
    def test_validates_site_handoff_without_authority_expansion(self):
        handoff = validate_site_sdk_processing_handoff(site_handoff())
        self.assertEqual(NEXT_TRANSITION, handoff["next_required_transition"])
        self.assertEqual("NONE", handoff["authority_effect"])
        self.assertEqual("governance", handoff["manifest"]["processing"]["capability"])
        self.assertEqual("SDK_EVALUATOR_INGRESS_ADMITTED", handoff["sdk_evaluator_ingress_state"])

    def test_rejects_manifest_hash_mismatch(self):
        handoff = site_handoff()
        handoff["manifest_hash"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(SiteSdkProcessingHandoffError, "manifest_hash"):
            validate_site_sdk_processing_handoff(handoff)

    def test_rejects_return_exit_correlation_mismatch(self):
        handoff = site_handoff()
        handoff["stegverse_return_exit_receipt"]["response_to"] = "different"
        with self.assertRaisesRegex(SiteSdkProcessingHandoffError, "response_to mismatch"):
            validate_site_sdk_processing_handoff(handoff)

    def test_rejects_wrong_next_transition(self):
        handoff = site_handoff()
        handoff["next_required_transition"] = "EXECUTE_PUBLISHER_FIRST"
        with self.assertRaisesRegex(SiteSdkProcessingHandoffError, "manifest-selected"):
            validate_site_sdk_processing_handoff(handoff)

    @patch("stegverse.sovereign_validation_runtime.run_sovereign_validation")
    def test_executes_manifest_selected_sdk_processor_and_preserves_downstream_boundary(self, run):
        run.return_value = {
            "manifest_receipt_id": "MR-" + "C" * 64,
            "route_receipt_chain_head": "d" * 64,
            "governance_state": "ALLOW",
            "chain_verified": True,
            "master_records_custody_status": "RECORDED",
            "external_side_effect": False,
            "third_party_host_required": False,
        }
        result = execute_site_sdk_processing_handoff(site_handoff(), custody_db=":memory:")
        self.assertEqual("SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED", result["state"])
        self.assertEqual(NEXT_TRANSITION, result["transition_class"])
        self.assertEqual("governance", result["processing_capability"])
        self.assertEqual("SDK_EVALUATOR_INGRESS_ADMITTED", result["sdk_evaluator_ingress_state"])
        self.assertEqual("sha256:" + "b" * 64, "sha256:" + result["retained_packet_sha256"])
        self.assertTrue(result["processor_result_observed"])
        self.assertFalse(result["publisher_transition_observed"])
        self.assertFalse(result["sdk_return_binding_observed"])
        self.assertFalse(result["final_stegverse_side_egress_transition_observed"])
        self.assertFalse(result["far_side_transition_observed"])
        self.assertFalse(result["communication_complete"])
        self.assertTrue(run.called)


if __name__ == "__main__":
    unittest.main()
