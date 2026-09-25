"""Source-only exact-head validation for eight broadened priority claims."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"docs/deepwiki-review/EIGHT_CROSS_BOUNDARY_PRIORITY_CORRECTIONS.md"
PIN="44d9b130b7e1f1dd374e71ad0a31b35e731d4f9b"
LINK=re.compile(r"https://github.com/StegVerse-org/StegVerse-SDK/blob/([a-f0-9]{40})/([\w./-]+)#L(\d+)(?:-L(\d+))?")


class EightPriorityReviewTests(unittest.TestCase):
    def test_all_eight_are_distinct_nonallow_and_source_exact(self):
        text=DOC.read_text(encoding="utf-8")
        table=text.split("## First-party correction",1)[0]
        for i in (78,100,152,307,394,499,501,502):
            with self.subTest(index=i):
                self.assertRegex(table,rf"(?m)^\| {i} ")
        self.assertEqual(sum(row.startswith("| ") and "`DENY:" in row for row in table.splitlines()),8)
        links=LINK.findall(text)
        self.assertGreaterEqual(len(links),10)
        for sha,rel,start,end in links:
            self.assertEqual(sha,PIN)
            file=ROOT/rel
            self.assertTrue(file.is_file(),rel)
            length=len(file.read_text(encoding="utf-8").splitlines())
            self.assertGreaterEqual(int(start),1)
            self.assertLessEqual(int(end or start),length)

    def test_declared_source_facts_and_nonpublication(self):
        builder=(ROOT/"stegverse/manifest_builder.py").read_text()
        worker=(ROOT/"stegverse/atomic_task_worker_processor.py").read_text()
        status=(ROOT/"evidence/system-boundary-downstream-status.v0.1.json").read_text()
        self.assertIn("does not synthesize governance evidence",builder)
        self.assertIn('"adapter_executes_lifecycle": False',worker)
        self.assertIn('"status_only": true',status)
        pub=(ROOT/"scripts/build_sdk_public_wiki.py").read_text()
        self.assertNotIn("EIGHT_CROSS_BOUNDARY_PRIORITY_CORRECTIONS.md",pub)
        self.assertNotIn("GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION",pub)


if __name__=="__main__":
    unittest.main()
