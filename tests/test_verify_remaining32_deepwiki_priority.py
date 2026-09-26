"""The remaining 32 first-party judgments must stay complete and non-authorizing."""
import json
import unittest
from pathlib import Path

from scripts.verify_remaining32_deepwiki_priority import (
    EARLIER_14, REMAINING_32, RAW_SHA256,
)

ROOT=Path(__file__).resolve().parents[1]
DECISIONS=ROOT/"docs/deepwiki-review/REMAINING_32_PRIORITY_SOURCE_DECISIONS.json"


class RemainingPriorityTests(unittest.TestCase):
    def test_complete_partition_and_source_witnesses(self):
        self.assertEqual(len(EARLIER_14),14)
        self.assertEqual(len(REMAINING_32),32)
        self.assertFalse(EARLIER_14 & REMAINING_32)
        data=json.loads(DECISIONS.read_text(encoding="utf-8"))
        self.assertEqual(data["original_capture_sha256"], RAW_SHA256)
        self.assertEqual(data["full_generated_claim_approvals"],0)
        self.assertEqual(data["generated_page_imports_authorized"],0)
        rows=data["records"]
        self.assertEqual(len(rows),32)
        self.assertEqual({r["index"] for r in rows},REMAINING_32)
        for row in rows:
            with self.subTest(index=row["index"]):
                self.assertTrue(row["disposition"].startswith("DENY:"))
                self.assertIs(row["full_generated_claim_semantically_approved"],False)
                self.assertIs(row["publication_authorized"],False)
                self.assertTrue(row["narrow_fact"])
                self.assertTrue(row["unsupported"])
                source=(ROOT/row["witness_path"]).resolve()
                self.assertTrue(source.is_relative_to(ROOT.resolve()))
                self.assertTrue(source.is_file(), row["witness_path"])
                self.assertIn(row["exact_literal"],source.read_text(encoding="utf-8"))

    def test_original_generated_text_never_enters_public_builder(self):
        builder=(ROOT/"scripts/build_sdk_public_wiki.py").read_text(encoding="utf-8")
        self.assertNotIn("REMAINING_32_PRIORITY_SOURCE_DECISIONS.json",builder)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",builder)


if __name__=="__main__":
    unittest.main()
