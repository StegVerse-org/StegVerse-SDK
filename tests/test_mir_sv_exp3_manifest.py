"""Acceptance checks for the *existing* SDK manifest and diagnostic route."""
import json
import unittest
from unittest.mock import patch
from copy import deepcopy
from pathlib import Path
from scripts.build_mir_sv_exp3_manifest import HERE, build_exp3_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request, execute_manifest, validate_runtime_result
from stegverse.manifest_builder import correct_manifest_binding_deny
from stegverse.route_resolution import canonical_sha256
from stegverse.ecosystem_diagnostic_runtime import execute_manifest as execute_local_diagnostic

class MIRSVExp3ManifestTests(unittest.TestCase):
    def setUp(self):
        self.m=build_exp3_manifest()
        self.payload=self.m["payload"]

    def test_exact_registered_goal_and_cosv(self):
        self.assertEqual(self.payload["goal_task_id"],"MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003")
        self.assertEqual(self.payload["cosv"],"50000000100000")
        self.assertEqual(self.m["processing"]["capability"],"ecosystem_diagnostic")
        self.assertEqual(self.m["processing"]["route_id"],"stegverse.route.ecosystem-diagnostic.v1")

    def test_four_capabilities_limits_and_checks_are_copresent(self):
        rows=self.payload["dimensions"]
        self.assertEqual({x["key"] for x in rows},{"observe","demonstrate","retain","reconstruct"})
        for row in rows:
            for key in ("capability","limit","verification"):
                self.assertTrue(row[key])
        self.assertEqual(len(self.payload["four_questions"]),4)

    def test_missing_capability_limitation_cannot_be_replaced_post_hoc(self):
        raw=json.loads((HERE/"assessment-input.json").read_text())
        row=raw["dimensions"][0]
        row["limit"]=""
        self.assertFalse(all(row.get(x) for x in ("capability","limit","verification")))
        bad=deepcopy(self.m)
        bad["payload"]=raw
        with self.assertRaises(ValueError):
            validate_ingress_manifest(bad)

    def test_diagnostic_does_not_upgrade_unobserved_runtime(self):
        res=execute_local_diagnostic(self.m)
        current=[x for x in res["results"] if x["test_id"].endswith("_current_runtime")]
        self.assertEqual(len(current),4)
        self.assertTrue(all(x["observation_state"]=="NOT_OBSERVED" for x in current))
        source=[x for x in res["results"] if x["test_id"].endswith("_source_contract")]
        self.assertTrue(all(x["observation_state"]=="PASS" and x["evidence_refs"] for x in source))
        self.assertFalse(res["mutation_performed"])
        self.assertEqual(res["authority_effect"],"NONE_DIAGNOSTIC_ONLY")

    def test_no_independent_physical_work_or_shared_coverage_invented(self):
        res=execute_local_diagnostic(self.m)
        for key in ("physical_work","coverage_completeness","dissent_preservation","matched_master_records"):
            self.assertEqual(next(x for x in res["results"] if x["test_id"]==key)["observation_state"],"NOT_OBSERVED")
        self.assertEqual(self.payload["coverage"]["activity_side_sampling"],"NOT_PERFORMED")
        self.assertTrue(self.payload["disagreement_policy"]["retain_unknowns_first_class"])

    def test_frozen_wire_manifest_is_not_modified_and_has_distinct_digest_bindings(self):
        original=deepcopy(self.m)
        request=derive_execution_request(self.m)
        self.assertEqual(self.m,original)
        self.assertNotIn("canonical_manifest_sha256",self.m)
        self.assertEqual(request["canonical_manifest"],original)
        self.assertEqual(request["wire_manifest_sha256"],
                         "ad9b8b8aab2beeea04bff2aac34fd2e7bfa5915133bcaef9209c16de7d9bea68")
        self.assertEqual(request["wire_manifest_sha256"],canonical_sha256(original))
        self.assertEqual(request["canonical_manifest_sha256"],
                         canonical_sha256(request["canonical_manifest_projection"]))
        self.assertEqual(request["state_graph"]["canonical_task_id"],None)
        self.assertFalse(request["requires_workercoordinator_claim_fence"])
        self.assertTrue(original["completion"]["publisher"]["required"])

    def test_same_payload_hash_and_sdk_lineage_stable(self):
        first=build_exp3_manifest()
        second=build_exp3_manifest()
        self.assertEqual(first,second)
        result=execute_local_diagnostic(first)
        self.assertTrue(validate_ingress_manifest(first)["canonical_manifest_sha256"])
        self.assertTrue(result["result_binding_hash"])
        self.assertTrue(first["completion"]["publisher"]["required"])
        self.assertTrue(first["completion"]["egress"]["far_side_transition_required"])

    def test_existing_builder_repairs_historical_hash_deny_without_changing_frozen_manifest(self):
        frozen = deepcopy(self.m)
        current = derive_execution_request(frozen)
        historical = deepcopy(current)
        historical.pop("wire_manifest_sha256")
        historical.pop("canonical_manifest_projection")
        historical["canonical_manifest_sha256"] = canonical_sha256(frozen)
        historical.pop("request_sha256")
        historical["request_sha256"] = canonical_sha256(historical)
        denial = {
            "schema": "stegverse.sdk.manifest-profile-disposition/v1",
            "state": "DENY", "terminal": False,
            "transition_id": "SDK_MANIFEST_BINDING",
            "reason_code": "canonical_manifest_sha256_binding_mismatch",
            "retry_condition": "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT",
            "original_wire_manifest_sha256": canonical_sha256(frozen),
            "original_request_sha256": canonical_sha256(historical),
        }
        corrected = correct_manifest_binding_deny(frozen, historical, denial)
        self.assertEqual(corrected, current)
        self.assertNotEqual(corrected["request_sha256"], historical["request_sha256"])
        self.assertEqual(frozen, self.m)
        self.assertTrue(frozen["completion"]["publisher"]["required"])
        with self.assertRaisesRegex(ValueError, "terminal_or_non_deny"):
            correct_manifest_binding_deny(frozen, historical, {**denial, "state": "FAIL_CLOSED", "terminal": True})
        with self.assertRaisesRegex(ValueError, "unchanged_request"):
            correct_manifest_binding_deny(frozen, current, {**denial, "original_request_sha256": canonical_sha256(current)})

    def test_exact_source_profile_deny_not_blindly_retried_by_current_builder(self):
        original = deepcopy(self.m)
        current = derive_execution_request(original)
        # This mock claims a historical digest mismatch on an already-correct
        # envelope. An unchanged derived request is not a new governed attempt.
        denial = {
            "schema": "stegverse.sdk.manifest-profile-disposition/v1",
            "state": "DENY", "disposition": "DENY", "terminal": False,
            "automatic_retry_permitted": False,
            "retry_condition": "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT",
            "evaluation_boundary": "SDK_MANIFEST_PROFILE", "transport_validated": True,
            "authentic_intr_admission_observed": False,
            "organization_master_records_closure_observed": False,
            "transition_id": "SDK_MANIFEST_BINDING",
            "repair_owner": "StegVerse-org/StegVerse-SDK:stegverse/manifest_builder.py",
            "authority_effect": "NONE_MANIFEST_PROFILE_DENY_ONLY",
            "reason_code": "canonical_manifest_sha256_binding_mismatch",
            "failed_predicate": "canonical_manifest_sha256_binding_mismatch",
            "original_request_sha256": canonical_sha256(current),
            "claimed_request_sha256": current["request_sha256"],
            "original_wire_manifest_sha256": canonical_sha256(original),
            "graph_id": current["graph_id"],
            "processing_capability": "ecosystem_diagnostic",
            "source_disposition_ref": "mock-evaluating-profile-path-not-sovereign-custody",
        }
        with patch("stegverse.manifest_state_transition_runtime._post_existing_intr", return_value=denial) as post:
            self.assertEqual(execute_manifest(original)["disposition"], "DENY")
            self.assertEqual(post.call_count, 1)
        self.assertEqual(original, self.m)
        altered = deepcopy(denial)
        altered["authentic_intr_admission_observed"] = True
        with self.assertRaisesRegex(ValueError, "MANIFEST_BINDING_DENY_CONTRACT_MISMATCH"):
            validate_runtime_result(altered, current)


if __name__=="__main__": unittest.main()
