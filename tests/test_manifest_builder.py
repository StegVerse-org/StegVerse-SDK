from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from stegverse.governance_navigation import canonical_sha256
from stegverse.manifest_builder import (
    RETURN_DEPTHS,
    available_processors,
    build_manifest,
    main,
)
from stegverse.manifest_contract import validate_ingress_manifest


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


class ManifestBuilderTests(unittest.TestCase):
    def test_build_preserves_source_native_payload_and_separates_candidate(self):
        payload = {
            "class": "elan.relational-state.v1",
            "state": {"silence_observed": True, "response_withheld": True},
            "native_semantics": ["presence", "restraint"],
        }
        request = governance_request()
        manifest = build_manifest(
            data=payload,
            data_class="elan.relational-state.v1",
            source_framework="ELAN",
            source_output_id="elan-test-001",
            processor_request=request,
            created_at="2026-09-08T20:00:00Z",
        )

        self.assertEqual(manifest["payload"], payload)
        self.assertIsNot(manifest["payload"], payload)
        self.assertEqual(manifest["processing"]["capability"], "governance")
        self.assertEqual(
            manifest["processing"]["route_id"],
            manifest["extensions"]["stegverse_route"]["route_id"],
        )
        self.assertEqual(manifest["candidate"], request["candidate"])
        self.assertNotEqual(manifest["payload"], manifest["candidate"])
        self.assertEqual(manifest["extensions"]["source_data_class"], "elan.relational-state.v1")
        self.assertEqual(manifest["extensions"]["manifest_builder"]["source_semantic_custody"], "EXTERNAL")
        self.assertFalse(manifest["extensions"]["manifest_builder"]["builder_grants_authority"])
        self.assertEqual(manifest["hashes"]["payload_sha256"], canonical_sha256(payload))
        self.assertEqual(manifest["hashes"]["candidate_sha256"], canonical_sha256(request["candidate"]))
        validate_ingress_manifest(manifest)

    def test_return_depth_aliases_map_deterministically(self):
        request = governance_request()
        for name, expected in RETURN_DEPTHS.items():
            with self.subTest(name=name):
                manifest = build_manifest(
                    data={"value": 1},
                    source_framework="fixture",
                    source_output_id=name,
                    processor_request=request,
                    return_depth=name,
                    created_at="2026-09-08T20:00:00Z",
                )
                self.assertEqual(manifest["return_projection"], expected)

    def test_missing_governance_evidence_fails_closed(self):
        request = governance_request()
        request.pop("signal")
        with self.assertRaisesRegex(ValueError, "missing required governance fields: signal"):
            build_manifest(
                data={"value": 1},
                source_framework="fixture",
                source_output_id="missing-signal",
                processor_request=request,
            )

    def test_current_processor_registry_exposes_governance_only(self):
        self.assertEqual(available_processors(), ("governance",))

    def test_cli_build_writes_submission_ready_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            request_path = root / "governance.json"
            output = root / "manifest.json"
            source.write_text(json.dumps({"native": [1, 2, 3]}), encoding="utf-8")
            request_path.write_text(json.dumps(governance_request()), encoding="utf-8")

            rc = main([
                "build",
                "--input", str(source),
                "--governance-request", str(request_path),
                "--source-framework", "fixture-framework",
                "--source-output-id", "fixture-output",
                "--data-class", "fixture.native.v1",
                "--return-depth", "full-trace",
                "--created-at", "2026-09-08T20:00:00Z",
                "--output", str(output),
            ])
            self.assertEqual(rc, 0)
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["processing"]["capability"], "governance")
            self.assertEqual(manifest["return_projection"]["mode"], "ALL")
            validate_ingress_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
