"""Verify 30 candidate sources at exact HEAD and preserve original classifications."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/"docs/deepwiki-review/MANIFEST_30_ATOMIC_SOURCE_DECISIONS.json"
INDEX={18,74,75,76,77,80,81,83,85,95,97,98,99,105,106,107,108,
       109,110,111,113,114,115,116,117,118,119,120,122,128}


class ManifestClaimReviewTests(unittest.TestCase):
    def test_all_30_source_witnesses_and_bounded_classification(self):
        data=json.loads(PACKET.read_text())
        self.assertEqual(data["input_capture_sha256"],
                         "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087")
        rows=data["records"]
        self.assertEqual(len(rows),30)
        self.assertEqual({r["index"] for r in rows},INDEX)
        self.assertEqual(sum(r["full_atomic_source_claim_approved"] for r in rows),13)
        for r in rows:
            with self.subTest(index=r["index"]):
                file=(ROOT/r["witness_path"]).resolve()
                self.assertTrue(file.is_relative_to(ROOT.resolve()))
                self.assertTrue(file.is_file(),str(file))
                self.assertIn(r["exact_source_predicate"],file.read_text())
                self.assertTrue(r["narrow_fact"])
                self.assertTrue(r["unsupported_extension"])
                self.assertIs(r["whole_generated_context_approved"],False)
                self.assertIs(r["generated_prose_republication_allowed"],False)
                self.assertIs(r["actual_InTr_disposition_observed"],False)
                self.assertEqual(r["full_atomic_source_claim_approved"],
                                 r["source_review_disposition"]=="FULL_ATOMIC_SOURCE_CLAIM_VERIFIED")

    def test_old_drift_is_identified_and_public_builder_unchanged(self):
        data=json.loads(PACKET.read_text())
        records={r["index"]:r for r in data["records"]}
        self.assertEqual(records[98]["source_review_disposition"],
                         "DENY_ORIGINAL_CITATION_LINE_DRIFT_REPAIRED")
        self.assertEqual(records[99]["source_review_disposition"],
                         "DENY_ORIGINAL_CITATION_LINE_DRIFT_REPAIRED")
        builder=(ROOT/"scripts/build_sdk_public_wiki.py").read_text()
        self.assertNotIn("MANIFEST_30_ATOMIC_SOURCE_DECISIONS",builder)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",builder)


if __name__=="__main__":
    unittest.main()
