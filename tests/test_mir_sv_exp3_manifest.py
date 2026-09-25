"""Acceptance checks for the *existing* SDK manifest and diagnostic route."""
import json
import unittest
from copy import deepcopy
from pathlib import Path
from scripts.build_mir_sv_exp3_manifest import HERE, build_exp3_manifest
from stegverse.manifest_contract import validate_ingress_manifest
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

    def test_same_payload_hash_and_sdk_lineage_stable(self):
        first=build_exp3_manifest()
        second=build_exp3_manifest()
        self.assertEqual(first,second)
        result=execute_local_diagnostic(first)
        self.assertTrue(validate_ingress_manifest(first)["canonical_manifest_sha256"])
        self.assertTrue(result["result_binding_hash"])
        self.assertTrue(first["completion"]["publisher"]["required"])
        self.assertTrue(first["completion"]["egress"]["far_side_transition_required"])

if __name__=="__main__": unittest.main()
