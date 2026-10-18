"""Governed-DENY (Experiment 3) negative-conformance fixture, StegVerse-Labs/.github#3183 Workstream A.

Owner SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001 / COSV 71000000101000. A correct
DENY/FAIL_CLOSED is a negative-conformance pass, never an experiment FAILED.
Source-only: no runtime, receipt or authority is observed or minted here.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from stegverse import manifest_state_transition_runtime as runtime
from stegverse.ecosystem_diagnostic_runtime import execute_manifest as run_diagnostic
from stegverse.manifest_builder import build_manifest
from stegverse.negative_conformance import PASS, classify_governed_deny_fixture, diagnostic_request
from stegverse.organization_ledger_evidence import REFUSAL_FIELDS
from stegverse.route_resolution import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "conformance" / "governed_deny_experiment3.json"
SDK = "StegVerse-org/StegVerse-SDK"


def load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def receipt(fixture: dict, receipt_id: str) -> dict:
    return next(r for r in fixture["bound_receipts"] if r["receipt_id"] == receipt_id)


class GovernedDenyNegativeConformanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = load()

    def test_sdk_held_original_receipts_are_byte_bound(self):
        local = [r for r in self.fixture["bound_receipts"] if r["repository"] == SDK]
        self.assertTrue(local)
        for row in local:
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            self.assertEqual(digest, row["sha256"], row["path"])

    def test_frozen_original_manifest_regenerates_exact_bytes(self):
        frozen = self.fixture["frozen_original"]
        manifest = build_exp3_manifest()
        raw = (json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), frozen["manifest_file_sha256"])
        self.assertEqual(canonical_sha256(manifest), frozen["wire_manifest_sha256"])

    def test_live_sdk_handoff_awaits_no_machine_and_returns_via_admit_runtime_result(self):
        boundary_row = receipt(self.fixture, self.fixture["sdk_handoff"]["organization_boundary_receipt_id"])
        boundary = json.loads((ROOT / boundary_row["path"]).read_text(encoding="utf-8"))
        handoff = runtime.execute_manifest(build_exp3_manifest(), boundary)
        for key, expected in self.fixture["sdk_handoff"]["expected"].items():
            self.assertEqual(handoff.get(key), expected, key)
        module, _, name = handoff["return_entrypoint"].rpartition(".")
        self.assertEqual(module, runtime.__name__)
        self.assertTrue(callable(getattr(runtime, name)))

    def test_correct_refusal_classifies_as_negative_conformance_pass(self):
        result = classify_governed_deny_fixture(self.fixture)
        self.assertEqual(result["classification"], PASS)
        self.assertEqual(result["governance_disposition"], "FAIL_CLOSED")
        self.assertEqual(result["experiment_outcome"], "NOT_FAILED")
        self.assertFalse(result["refusal_counted_as_experiment_failure"])
        self.assertFalse(result["awaits_external_machine"])
        self.assertEqual(result["current_non_allow_entry_ids"], ["exp3-organization-receipt-not-appended"])
        self.assertEqual(len(result["bound_receipt_refs"]), len(self.fixture["bound_receipts"]))

    def test_installed_diagnostic_processor_keeps_unobserved_effects_not_observed(self):
        result = classify_governed_deny_fixture(self.fixture)
        manifest = build_manifest(
            data={"fixture_id": self.fixture["fixture_id"], "classification": result["classification"]},
            source_framework="stegverse_sdk_session",
            source_output_id=self.fixture["fixture_id"],
            processor_request=diagnostic_request(self.fixture, result),
            process="ecosystem_diagnostic",
            created_at="2026-10-17T00:00:00Z",
        )
        out = run_diagnostic(manifest)
        states = {row["test_id"]: row["observation_state"] for row in out["results"]}
        self.assertEqual(states["governed_refusal_carries_six_fields"], "PASS")
        self.assertEqual(states["refusal_is_not_experiment_failure"], "PASS")
        self.assertEqual(states["sdk_handoff_awaits_no_external_machine"], "PASS")
        for effect in self.fixture["unobserved_effects"]:
            self.assertEqual(states["unobserved:" + effect["effect"]], "NOT_OBSERVED")
        self.assertFalse(out["mutation_performed"])
        self.assertEqual(out["authority_effect"], "NONE_DIAGNOSTIC_ONLY")

    def test_missing_six_field_entry_is_rejected(self):
        for field in REFUSAL_FIELDS:
            for index in range(len(self.fixture["non_allow_entries"])):
                bad = deepcopy(self.fixture)
                del bad["non_allow_entries"][index][field]
                with self.subTest(field=field, index=index):
                    with self.assertRaisesRegex(ValueError, "NON_ALLOW_SIX_FIELD_ENTRY_MISSING:.*:" + field):
                        classify_governed_deny_fixture(bad)

    def test_experiment_failed_solely_from_the_refusal_is_rejected(self):
        bad = deepcopy(self.fixture)
        bad["experiment_outcome"] = "FAILED"
        bad.pop("expected_classification")
        with self.assertRaisesRegex(ValueError, "EXPERIMENT_FAILED_INFERRED_FROM_GOVERNANCE_REFUSAL"):
            classify_governed_deny_fixture(bad)
        bad["experiment_failure_bases"] = [{"basis": "GOVERNANCE_FAIL_CLOSED",
                                            "source_receipt_ids": ["labs-organization-manifest-ingress"]}]
        with self.assertRaisesRegex(ValueError, "EXPERIMENT_FAILED_INFERRED_FROM_GOVERNANCE_REFUSAL"):
            classify_governed_deny_fixture(bad)

    def test_awaiting_an_external_machine_or_liveness_gate_is_rejected(self):
        for path, value, code in (
            (("sdk_handoff", "expected", "awaits_external_machine"), True, "SDK_HANDOFF_AWAITS_EXTERNAL_MACHINE"),
            (("registry_invariants", "external_machine_awaiting_allowed"), True, "REGISTRY_INVARIANT_VIOLATED"),
            (("registry_invariants", "destination_liveness_is_transition_predicate"), True,
             "REGISTRY_INVARIANT_VIOLATED"),
        ):
            bad = deepcopy(self.fixture)
            node = bad
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, code):
                classify_governed_deny_fixture(bad)

    def test_unobserved_effect_requires_marker_and_reconciliation_entrypoint(self):
        bad = deepcopy(self.fixture)
        bad["unobserved_effects"][0]["consequence_observation"] = "OBSERVED"
        with self.assertRaisesRegex(ValueError, "UNOBSERVED_EFFECT_MISCLASSIFIED"):
            classify_governed_deny_fixture(bad)
        bad = deepcopy(self.fixture)
        del bad["unobserved_effects"][0]["reconciliation_entrypoint"]
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_ENTRYPOINT_REQUIRED"):
            classify_governed_deny_fixture(bad)


if __name__ == "__main__":
    unittest.main()
