"""Verify all fourteen purpose-worker citation judgments against exact local source."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT/"docs/deepwiki-review/PURPOSE_WORKER_14_SOURCE_DECISIONS.json"
EXPECTED = {130,132,133,134,136,139,140,141,142,143,145,146,147,148}

class PurposeWorker14SourceTests(unittest.TestCase):
    def test_exact_current_literals_and_non_authorizing_dispositions(self):
        data = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = data["records"]
        self.assertEqual(len(rows),14)
        self.assertEqual({r["index"] for r in rows}, EXPECTED)
        self.assertEqual(sum(r["full_atomic_source_fact_verified"] for r in rows),10)
        for r in rows:
            with self.subTest(index=r["index"]):
                path=(ROOT/r["witness_path"]).resolve()
                self.assertTrue(path.is_relative_to(ROOT.resolve()))
                self.assertTrue(path.is_file(),str(path))
                self.assertIn(r["exact_literal"],path.read_text(encoding="utf-8"))
                self.assertTrue(r["narrow_fact"] and r["unsupported_extension"])
                self.assertIs(r["complete_generated_paragraph_approved"],False)
                self.assertIs(r["external_generated_content_republication_authorized"],False)
                self.assertIs(r["authentic_runtime_transition_observed"],False)

    def test_local_records_are_not_authentic_custody(self):
        worker=(ROOT/"stegverse/purpose_bound_worker.py").read_text(encoding="utf-8")
        self.assertIn('"runtime_binding_state": "LOCAL_SEMANTIC_DEMONSTRATION_ONLY"',worker)
        self.assertIn('"live_runtime_receipt_refs": []',worker)
        public=(ROOT/"scripts/build_sdk_public_wiki.py").read_text(encoding="utf-8")
        self.assertNotIn("PURPOSE_WORKER_14_SOURCE_DECISIONS",public)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",public)

if __name__ == "__main__":
    unittest.main()
