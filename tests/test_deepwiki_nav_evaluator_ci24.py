"""Assert exact current sources for the 24 newly reviewed original citations."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/"docs/deepwiki-review/NAV_EVALUATOR_CI_24_SOURCE_DECISIONS.json"
GUIDE=ROOT/"docs/deepwiki-review/FIRST_PARTY_NAV_EVALUATOR_CI_24.md"
EXPECTED={
    210,215,217,218,219,229,235,246,249,
    324,325,326,327,328,329,330,431,440,
    463,464,467,468,469,471
}
PIN="b92027db13d57e7738f30ce94a06c91d839ebd45"


class NavEvaluatorCI24Tests(unittest.TestCase):
    def test_all_original_rows_have_real_exact_source_witnesses(self):
        packet=json.loads(PACKET.read_text(encoding="utf-8"))
        rows=packet["records"]
        self.assertEqual(len(rows),24)
        self.assertEqual({x["index"] for x in rows},EXPECTED)
        self.assertEqual(sum(x["atomic_source_fact_verified"] for x in rows),6)
        for x in rows:
            with self.subTest(index=x["index"]):
                path=(ROOT/x["witness_path"]).resolve()
                self.assertTrue(path.is_relative_to(ROOT.resolve()))
                self.assertTrue(path.is_file(),x["witness_path"])
                self.assertIn(x["exact_literal"],path.read_text(encoding="utf-8"))
                self.assertFalse(x["generated_paragraph_approved"])
                self.assertFalse(x["generated_page_republication_authorized"])
                self.assertFalse(x["runtime_admission_observed"])

    def test_first_party_guide_is_independent_and_complete(self):
        guide=GUIDE.read_text(encoding="utf-8")
        rows=json.loads(PACKET.read_text(encoding="utf-8"))["records"]
        self.assertIn("not generated DeepWiki content",guide)
        self.assertIn("All 24 generated paragraphs remain non-ALLOW",guide)
        for x in rows:
            with self.subTest(index=x["index"]):
                self.assertEqual(
                    sum(line.startswith("| {} |".format(x["index"])) for line in guide.splitlines()),1
                )
                self.assertIn(x["narrow_fact"],guide)
                self.assertIn(x["unsupported_extension"],guide)
                self.assertIn(f"/blob/{PIN}/{x['witness_path']}",guide)
        public=(ROOT/"scripts/build_sdk_public_wiki.py").read_text(encoding="utf-8")
        self.assertNotIn("FIRST_PARTY_NAV_EVALUATOR_CI_24",public)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",public)


if __name__=="__main__":
    unittest.main()
