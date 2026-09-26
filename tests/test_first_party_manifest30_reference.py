"""Review independent first-party guide against the 30 original source decisions."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=(ROOT/"docs/deepwiki-review/FIRST_PARTY_MANIFEST_30_SOURCE_REFERENCE.md")
DECISIONS=(ROOT/"docs/deepwiki-review/MANIFEST_30_ATOMIC_SOURCE_DECISIONS.json")
PIN="e1dae308f23b126bc84bd3c606c4e378aa73907b"


class FirstPartyManifest30Tests(unittest.TestCase):
    def test_every_current_reference_is_source_bound_and_separate(self):
        markdown=DOC.read_text(encoding="utf-8")
        records=json.loads(DECISIONS.read_text(encoding="utf-8"))["records"]
        self.assertEqual(len(records),30)
        self.assertEqual(sum(r["full_atomic_source_claim_approved"] for r in records),13)
        for row in records:
            with self.subTest(index=row["index"]):
                self.assertEqual(
                    len(re.findall(rf"(?m)^\| {row['index']} \|",markdown)),1
                )
                self.assertIn(row["narrow_fact"],markdown)
                self.assertIn(row["unsupported_extension"],markdown)
                source=ROOT/row["witness_path"]
                self.assertTrue(source.is_file())
                self.assertIn(row["exact_source_predicate"],source.read_text())
                self.assertIn(f"/blob/{PIN}/{row['witness_path']}",markdown)

    def test_no_unauthorized_page_import_or_generated_paragraph_approval(self):
        markdown=DOC.read_text()
        self.assertIn("zero whole generated paragraphs or page imports approved",markdown)
        self.assertIn("existing six-source SDK public Pages builder is unchanged",markdown)
        builder=(ROOT/"scripts/build_sdk_public_wiki.py").read_text()
        self.assertNotIn("FIRST_PARTY_MANIFEST_30_SOURCE_REFERENCE.md",builder)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",builder)
        self.assertNotIn("]()",markdown)


if __name__=="__main__":
    unittest.main()
