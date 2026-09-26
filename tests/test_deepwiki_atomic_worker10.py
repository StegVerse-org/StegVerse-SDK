"""Guard all ten original atomic-worker citation/source decisions."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DECISIONS=ROOT/"docs/deepwiki-review/ATOMIC_WORKER_10_SOURCE_DECISIONS.json"
GUIDE=ROOT/"docs/deepwiki-review/FIRST_PARTY_ATOMIC_WORKER_10.md"
EXPECTED={150,151,153,154,155,156,158,159,162,164}
PIN="2fdc9e7b98d87463d9183e5268a73eac37bb730e"

class AtomicWorkerSourceTenTests(unittest.TestCase):
    def test_current_witness_and_non_authorizing_disposition(self):
        rows=json.loads(DECISIONS.read_text(encoding="utf-8"))["records"]
        self.assertEqual(len(rows),10)
        self.assertEqual({x["index"] for x in rows},EXPECTED)
        self.assertEqual(sum(x["full_atomic_source_fact_verified"] for x in rows),5)
        for x in rows:
            with self.subTest(index=x["index"]):
                witness=(ROOT/x["witness_path"]).resolve()
                self.assertTrue(witness.is_relative_to(ROOT.resolve()))
                self.assertTrue(witness.is_file())
                self.assertIn(x["exact_literal"],witness.read_text(encoding="utf-8"))
                self.assertFalse(x["whole_generated_paragraph_approved"])
                self.assertFalse(x["third_party_republication_authorized"])
                self.assertFalse(x["authentic_execution_observed"])
    def test_first_party_reference_excludes_original_generated_pages(self):
        text=GUIDE.read_text(encoding="utf-8")
        rows=json.loads(DECISIONS.read_text(encoding="utf-8"))["records"]
        for x in rows:
            self.assertEqual(sum(
                line.startswith("| {} |".format(x["index"])) for line in text.splitlines()
            ),1)
            self.assertIn(x["narrow_fact"],text)
            self.assertIn(x["unsupported_extension"],text)
            self.assertIn(f"/blob/{PIN}/{x['witness_path']}",text)
        builder=(ROOT/"scripts/build_sdk_public_wiki.py").read_text(encoding="utf-8")
        self.assertNotIn("FIRST_PARTY_ATOMIC_WORKER_10.md",builder)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",builder)

if __name__=="__main__":
    unittest.main()
