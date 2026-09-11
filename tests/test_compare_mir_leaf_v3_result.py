from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.compare_mir_leaf_v3_result import compare

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "fixtures" / "mir_leaf_v3_conformance_expected_result_v1.json"


class MirLeafV3CounterpartComparisonTests(unittest.TestCase):
    def expected(self):
        return json.loads(EXPECTED.read_text(encoding="utf-8"))

    def test_exact_counterpart_result_matches(self):
        expected = self.expected()
        result = compare(expected, copy.deepcopy(expected))
        self.assertTrue(result["exact_match"])
        self.assertEqual(result["missing_fields"], [])
        self.assertEqual(result["mismatched_fields"], [])

    def test_leaf_mismatch_fails(self):
        expected = self.expected()
        observed = copy.deepcopy(expected)
        observed["leaf_hashes"][2] = "sha256:" + "00" * 32
        result = compare(expected, observed)
        self.assertFalse(result["exact_match"])
        self.assertIn("leaf_hashes", result["mismatched_fields"])

    def test_missing_checkpoint_tip_fails(self):
        expected = self.expected()
        observed = copy.deepcopy(expected)
        observed.pop("checkpoint_tip")
        result = compare(expected, observed)
        self.assertFalse(result["exact_match"])
        self.assertIn("checkpoint_tip", result["missing_fields"])

    def test_premature_proof_claim_fails(self):
        expected = self.expected()
        observed = copy.deepcopy(expected)
        observed["proof_status"] = "PROVIDED"
        result = compare(expected, observed)
        self.assertFalse(result["exact_match"])
        self.assertIn("proof_status", result["mismatched_fields"])

    def test_witness_claim_fails(self):
        expected = self.expected()
        observed = copy.deepcopy(expected)
        observed["witnesses"] = [{"witnessId": "unexpected"}]
        result = compare(expected, observed)
        self.assertFalse(result["exact_match"])
        self.assertIn("witnesses", result["mismatched_fields"])


if __name__ == "__main__":
    unittest.main()
