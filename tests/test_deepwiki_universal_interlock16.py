"""Exact-source checks for the 16 original universal-entry and interlock citations."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/"docs/deepwiki-review/UNIVERSAL_INTERLOCK_16_SOURCE_DECISIONS.json"
GUIDE=ROOT/"docs/deepwiki-review/FIRST_PARTY_UNIVERSAL_INTERLOCK_16.md"
INDICES={188,189,190,196,198,199,202,203,204,205,206,335,336,337,338,339}
PIN="e7498c18d57f80e83749ad86d85f9cfc91973f8c"

class UniversalInterlock16SourceReviewTests(unittest.TestCase):
    def test_all_sixteen_witnesses_are_present_and_bounded(self):
        records=json.loads(PACKET.read_text(encoding="utf-8"))["records"]
        self.assertEqual(len(records),16)
        self.assertEqual({r["index"] for r in records},INDICES)
        self.assertEqual(sum(r["full_atomic_source_fact_verified"] for r in records),9)
        for row in records:
            with self.subTest(index=row["index"]):
                witness=(ROOT/row["witness_path"]).resolve()
                self.assertTrue(witness.is_relative_to(ROOT.resolve()))
                self.assertTrue(witness.is_file(),str(witness))
                self.assertIn(row["exact_literal"],witness.read_text(encoding="utf-8"))
                self.assertTrue(row["narrow_fact"])
                self.assertTrue(row["unsupported_extension"])
                self.assertIs(row["whole_generated_paragraph_approved"],False)
                self.assertIs(row["generated_page_import_authorized"],False)
                self.assertIs(row["authentic_InTr_execution_observed"],False)

    def test_independently_authored_guide_does_not_change_public_builder(self):
        text=GUIDE.read_text(encoding="utf-8")
        records=json.loads(PACKET.read_text(encoding="utf-8"))["records"]
        for row in records:
            with self.subTest(index=row["index"]):
                self.assertEqual(sum(
                    line.startswith("| {} |".format(row["index"])) for line in text.splitlines()
                ),1)
                self.assertIn(row["narrow_fact"],text)
                self.assertIn(row["unsupported_extension"],text)
                self.assertIn(f"/blob/{PIN}/{row['witness_path']}",text)
        builder=(ROOT/"scripts/build_sdk_public_wiki.py").read_text(encoding="utf-8")
        self.assertNotIn("FIRST_PARTY_UNIVERSAL_INTERLOCK_16",builder)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",builder)

if __name__=="__main__":
    unittest.main()
