"""Validate new MIR/SV capability documents without modifying the frozen original."""
import unittest
from copy import deepcopy
from scripts.build_mir_sv_exp3_capability_documents import build, markdown
from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from stegverse.route_resolution import canonical_sha256

class MIRCapabilityDocumentsTests(unittest.TestCase):
    def test_primary_manifest_reports_source_checks_not_runtime(self):
        m, result, source = build("primary")
        self.assertEqual([x["key"] for x in source["sections"]],
            ["observe", "demonstrate", "retain", "reconstruct"])
        self.assertEqual(len(source["questions"]), 4)
        self.assertEqual(m["processing"]["capability"], "ecosystem_diagnostic")
        self.assertEqual([x["observation_state"] for x in result["results"]].count("PASS"), 4)
        self.assertEqual([x["observation_state"] for x in result["results"]].count("NOT_OBSERVED"), 4)
        self.assertIn("Equal-weight limit", markdown(source, "primary"))

    def test_addendum_is_separate_and_not_delivered(self):
        m, result, source = build("addendum")
        self.assertNotEqual(m["payload"]["schema"], build("primary")[0]["payload"]["schema"])
        self.assertFalse(m["completion"]["publisher"]["required"])
        self.assertTrue(m["completion"]["egress"]["far_side_transition_required"])
        self.assertEqual(sum(x["observation_state"] == "NOT_OBSERVED" for x in result["results"]), 4)
        self.assertIn("MIR ingress", " ".join(source["required_runtime_evidence"]))

    def test_source_declared_outcome_cannot_be_promoted_to_runtime(self):
        _, _, source = build("primary")
        for row in source["sections"]:
            row["current_exp3_runtime"] = "NOT_OBSERVED"
        self.assertEqual(len(source["sections"]), 4)

    def test_frozen_original_manifest_remains_unchanged(self):
        self.assertEqual(canonical_sha256(build_exp3_manifest()),
            "ad9b8b8aab2beeea04bff2aac34fd2e7bfa5915133bcaef9209c16de7d9bea68")

if __name__ == "__main__":
    unittest.main()
