from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from stegverse.external_framework_runner import (
    EVALUATION_DECLARATION_EXTENSION,
    prepare_external_framework_manifest,
    run_external_framework,
)


ROOT = Path(__file__).resolve().parents[1]


def governance_request():
    return {
        "candidate": {
            "actor_class": "external_framework",
            "action": "evaluate_relational_state",
            "target": "source-native-object",
            "scope": "test",
            "parameters": {"external_side_effect": False},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["external:test:1"],
        },
        "signal": {
            "admitted_signal_refs": ["external:test:1"],
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
            "policy_ref": "external:test-policy",
            "delegation_ref": "external:test-delegation",
            "evidence_refs": ["external:test:1"],
        },
        "capability": {"allowed": True},
        "continuity": {"required": False},
        "approval": {"required": False},
        "permission_present": True,
    }


class ExternalFrameworkRunnerTests(unittest.TestCase):
    def test_preregistration_is_retained_outside_governance_request(self):
        declaration = {
            "what": "ELAN boundary test",
            "expected_observation": "relational and governance outputs may differ",
            "requested_evidence": ["governance_decision", "manifest_receipt"],
        }
        request = governance_request()
        manifest = prepare_external_framework_manifest(
            data={"silence_observed": True, "response_withheld": True},
            data_class="elan.relational-state.v1",
            source_framework="ELAN",
            source_output_id="elan-test-001",
            processor_request=request,
            evaluation_declaration=declaration,
            return_depth="full-trace",
            created_at="2026-09-08T20:00:00Z",
        )

        self.assertEqual(
            manifest["extensions"][EVALUATION_DECLARATION_EXTENSION], declaration
        )
        self.assertNotIn(
            EVALUATION_DECLARATION_EXTENSION,
            manifest["extensions"]["stegverse_governance_request"],
        )
        self.assertEqual(manifest["payload"]["silence_observed"], True)
        self.assertEqual(manifest["return_projection"]["mode"], "ALL")

    def test_public_elan_fixtures_build_without_semantic_repacking(self):
        source = json.loads(
            (ROOT / "inspection/examples/elan-relational-state-test1.json").read_text(
                encoding="utf-8"
            )
        )
        request = json.loads(
            (ROOT / "inspection/examples/elan-governance-request.example.json").read_text(
                encoding="utf-8"
            )
        )
        declaration = json.loads(
            (ROOT / "inspection/examples/elan-evaluation-declaration-test1.json").read_text(
                encoding="utf-8"
            )
        )
        manifest = prepare_external_framework_manifest(
            data=source,
            source_framework="ELAN",
            source_output_id="elan-emotional-ambiguity-silence-test-001",
            processor_request=request,
            evaluation_declaration=declaration,
            data_class="elan.relational-state.v1",
            return_depth="full-trace",
            created_at="2026-09-08T20:00:00Z",
        )
        self.assertEqual(manifest["payload"], source)
        self.assertEqual(manifest["extensions"]["source_data_class"], "elan.relational-state.v1")
        self.assertEqual(
            manifest["extensions"][EVALUATION_DECLARATION_EXTENSION], declaration
        )
        self.assertEqual(manifest["return_projection"]["mode"], "ALL")

    @patch("stegverse.sovereign_validation_runtime.reconstruct_sovereign")
    @patch("stegverse.sovereign_validation_runtime.replay_sovereign")
    @patch("stegverse.governance_ingress_runtime.run_external_manifest")
    def test_one_call_runs_receipt_replay_and_reconstruction(
        self, run_manifest, replay, reconstruct
    ):
        run_manifest.return_value = {
            "manifest_receipt_id": "MR-TEST-001",
            "governance_state": "ADMIT",
            "master_records_custody_status": "RECORDED",
        }
        replay.return_value = {"manifest_receipt_id": "MR-TEST-001", "replayed": True}
        reconstruct.return_value = {
            "manifest_receipt_id": "MR-TEST-001",
            "reconstructed": True,
        }

        result = run_external_framework(
            data={"native_semantics": ["presence", "restraint"]},
            data_class="elan.relational-state.v1",
            source_framework="ELAN",
            source_output_id="elan-test-001",
            processor_request=governance_request(),
            evaluation_declaration={"what": "fixed test"},
            return_depth="result+evidence",
            created_at="2026-09-08T20:00:00Z",
            custody_db="/tmp/sdk-completion-test.db",
        )

        self.assertEqual(result["manifest_receipt_id"], "MR-TEST-001")
        self.assertEqual(result["governed_result"]["master_records_custody_status"], "RECORDED")
        self.assertTrue(result["replay"]["replayed"])
        self.assertTrue(result["reconstruction"]["reconstructed"])
        run_manifest.assert_called_once()
        replay.assert_called_once_with("MR-TEST-001", custody_db="/tmp/sdk-completion-test.db")
        reconstruct.assert_called_once_with("MR-TEST-001", custody_db="/tmp/sdk-completion-test.db")

    @patch("stegverse.governance_ingress_runtime.run_external_manifest")
    def test_missing_manifest_receipt_fails_closed(self, run_manifest):
        run_manifest.return_value = {"governance_state": "ADMIT"}
        with self.assertRaisesRegex(RuntimeError, "manifest_receipt_id"):
            run_external_framework(
                data={"value": 1},
                source_framework="fixture",
                source_output_id="fixture-001",
                processor_request=governance_request(),
                replay=False,
                reconstruct=False,
            )


if __name__ == "__main__":
    unittest.main()
