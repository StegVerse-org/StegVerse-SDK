from __future__ import annotations

import copy
import unittest

from stegverse.evaluation_boundary_verifier import (
    canonical_sha256,
    verify_evaluation_boundary_result,
)
from stegverse.public_inspection import (
    PublicInspectionRequestError,
    validate_public_inspection_request,
)
from stegverse.sovereign_validation_runtime import _canonical_sha256 as runtime_sha256


PROVENANCE = {
    "lane_class": "PRODUCTION_VALIDATION",
    "routing_surface": "CANONICAL_PRODUCTION",
    "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
    "sandbox_required": False,
    "sandbox_tier": "NONE",
    "origin_surface": "StegVerse-org/StegVerse-SDK:public-inspection",
    "external_consequence_enabled": False,
}


class EvaluationBoundaryContractTests(unittest.TestCase):
    def manifest(self):
        return {
            "schema_version": "1.0",
            "request_id": "oda3-boundary-001",
            "requester_label": "evaluator-a",
            "case_profile": "ordinary",
            "evaluation_declaration": {
                "what": "Evaluate the fixed published route.",
                "how": "Use published capabilities only.",
                "why": "Test evaluator non-interference.",
                "expected_observation": "A governed disposition is retained.",
                "requested_capabilities": [
                    "commit_time_admissibility",
                    "master_records_custody",
                ],
                "requested_evidence": [
                    "governance_decision",
                    "manifest_receipt",
                    "exact_run_custody",
                ],
            },
            "execution_provenance": dict(PROVENANCE),
            "input": {
                "steggate_request": {
                    "candidate": {"action": "inspect"},
                }
            },
            "return_projection": "ALL",
            "manifest_labels": True,
            "authority_claim": False,
        }

    def bound_result(self, normalized_manifest, governance_request):
        body = {
            "schema": "stegverse.sovereign-production-validation-result.v1",
            "request_id": normalized_manifest["request_id"],
            "governance_state": "ALLOW",
            "submitted_manifest_hash": canonical_sha256(normalized_manifest),
            "governance_request_hash": canonical_sha256(governance_request),
            "manifest_receipt_id": "MR-" + "A" * 64,
            "route_manifest_id": "MF-" + "B" * 64,
            "transaction_id": "TX-ODA3-BOUNDARY",
            "master_records_custody_status": "RECORDED",
            "configuration_not_augmentation": True,
            "route_augmentation_permitted": False,
        }
        body["result_binding_hash"] = canonical_sha256(body)
        return body

    def test_01_valid_published_capability_manifest_is_accepted(self):
        normalized = validate_public_inspection_request(self.manifest())
        self.assertEqual("oda3-boundary-001", normalized["request_id"])

    def test_02_evaluator_metadata_changes_do_not_change_governance_request(self):
        first = validate_public_inspection_request(self.manifest())
        second_raw = self.manifest()
        second_raw["requester_label"] = "evaluator-b"
        second_raw["evaluation_declaration"]["why"] = "Independent alternate rationale."
        second_raw["evaluation_declaration"]["expected_observation"] = "No favorable result presumed."
        second = validate_public_inspection_request(second_raw)

        first_governance = first["input"]["steggate_request"]
        second_governance = second["input"]["steggate_request"]
        self.assertEqual(canonical_sha256(first_governance), canonical_sha256(second_governance))
        self.assertNotEqual(canonical_sha256(first), canonical_sha256(second))

    def test_03_unavailable_capability_is_rejected(self):
        raw = self.manifest()
        raw["evaluation_declaration"]["requested_capabilities"] = ["oda3_private_hot_patch"]
        with self.assertRaises(PublicInspectionRequestError):
            validate_public_inspection_request(raw)

    def test_04_route_or_semantic_override_is_rejected(self):
        for field in ("canonical_route", "steggate_semantics", "ordinary_governance_option"):
            raw = self.manifest()
            raw[field] = "evaluator-override"
            with self.subTest(field=field):
                with self.assertRaises(PublicInspectionRequestError):
                    validate_public_inspection_request(raw)

    def test_05_alternate_execution_path_is_rejected(self):
        raw = self.manifest()
        raw["execution_provenance"]["routing_surface"] = "EVALUATOR_PRIVATE_ROUTE"
        with self.assertRaises(PublicInspectionRequestError):
            validate_public_inspection_request(raw)

    def test_06_post_normalization_manifest_modification_is_detected(self):
        normalized = validate_public_inspection_request(self.manifest())
        governance = normalized["input"]["steggate_request"]
        result = self.bound_result(normalized, governance)
        modified = copy.deepcopy(normalized)
        modified["notes"] = "modified after binding"
        report = verify_evaluation_boundary_result(
            result,
            normalized_manifest=modified,
            governance_request=governance,
        )
        self.assertEqual("FAIL", report["checks"]["submitted_manifest_binding"]["status"])
        self.assertFalse(report["verified"])

    def test_07_governance_request_or_returned_result_modification_is_detected(self):
        normalized = validate_public_inspection_request(self.manifest())
        governance = normalized["input"]["steggate_request"]
        result = self.bound_result(normalized, governance)

        changed_governance = copy.deepcopy(governance)
        changed_governance["candidate"]["action"] = "altered"
        request_report = verify_evaluation_boundary_result(
            result,
            normalized_manifest=normalized,
            governance_request=changed_governance,
        )
        self.assertEqual("FAIL", request_report["checks"]["governance_request_binding"]["status"])

        changed_result = copy.deepcopy(result)
        changed_result["governance_state"] = "DENY"
        result_report = verify_evaluation_boundary_result(
            changed_result,
            normalized_manifest=normalized,
            governance_request=governance,
        )
        self.assertEqual("FAIL", result_report["checks"]["result_binding"]["status"])

    def test_08_independent_verifier_reports_complete_pass(self):
        normalized = validate_public_inspection_request(self.manifest())
        governance = normalized["input"]["steggate_request"]
        result = self.bound_result(normalized, governance)
        report = verify_evaluation_boundary_result(
            result,
            normalized_manifest=normalized,
            governance_request=governance,
        )
        self.assertTrue(report["verification_complete"])
        self.assertTrue(report["verified"])
        self.assertFalse(report["authority_granted"])
        self.assertEqual(
            {"PASS"},
            {entry["status"] for entry in report["checks"].values()},
        )

    def test_verifier_hash_profile_matches_sovereign_runtime(self):
        value = {"unicode": "StegVerse Ω", "nested": {"b": 2, "a": 1}}
        self.assertEqual(runtime_sha256(value), canonical_sha256(value))


if __name__ == "__main__":
    unittest.main()
