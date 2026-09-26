"""No generated diagram import; six exact citations have bounded source findings."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"docs/deepwiki-review/GOVERNANCE_SIX_PRIORITY_DIAGRAM_CORRECTIONS.md"
PIN="1b255725e35c918b69efdf335d4843e791e44e46"
LINK=re.compile(r"https://github.com/StegVerse-org/StegVerse-SDK/blob/([0-9a-f]{40})/([\w./-]+)(?:#L(\d+)(?:-L(\d+))?)?")


class GovernanceSixDiagramTests(unittest.TestCase):
    def test_each_frozen_priority_context_has_separate_deny(self):
        text=DOC.read_text(encoding="utf-8")
        table=text.split("## Replacement first-party technical explanation",1)[0]
        for i in (56,57,58,59,61,62):
            with self.subTest(index=i):
                self.assertRegex(table,rf"(?m)^\| {i} ")
        self.assertEqual(sum(x.startswith("| ") and "`DENY:" in x for x in table.splitlines()),6)
        self.assertNotIn("]()",text)
        self.assertIn("None is an authentic InTr DENY",text)

    def test_pinned_sources_and_unimplemented_diagram_types(self):
        text=DOC.read_text(encoding="utf-8")
        links=LINK.findall(text)
        self.assertGreaterEqual(len(links),10)
        for sha,path,start,end in links:
            self.assertEqual(sha,PIN)
            source=ROOT/path
            self.assertTrue(source.is_file(),str(source))
            n=len(source.read_text(encoding="utf-8").splitlines())
            if start:
                self.assertGreaterEqual(int(start),1)
                self.assertLessEqual(int(end or start),n)
        cli=(ROOT/"stegverse/governance_ingress_cli.py").read_text()
        boundary=(ROOT/"stegverse/execution_boundary.py").read_text()
        self.assertIn("run_external_manifest",cli)
        self.assertIn("def _validate_transition_chain(",boundary)
        self.assertNotIn("def check_intervening_transitions(",boundary)
        self.assertNotIn("class TVTVCCredentialAuthority",cli)

    def test_not_in_public_pages_builder(self):
        builder=(ROOT/"scripts/build_sdk_public_wiki.py").read_text()
        self.assertNotIn("GOVERNANCE_SIX_PRIORITY_DIAGRAM_CORRECTIONS",builder)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",builder)


if __name__=="__main__":
    unittest.main()
