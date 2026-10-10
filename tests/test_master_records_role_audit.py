"""The Master Records role audit inventory stays internally consistent (LLMA-DECLARED-PATH-CONFORMANCE-368)."""
from __future__ import annotations

import collections
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "master-records-role-audit.json"
CLASSES = {"PROPER", "IMPROPER_CODE", "IMPROPER_DOC", "HISTORICAL_EVIDENCE", "NAMING_ONLY"}


class MasterRecordsRoleAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_every_row_has_a_known_classification_and_reason(self):
        for rows in (self.audit["rows"], self.audit["before_rows"]):
            for row in rows:
                self.assertIn(row["classification"], CLASSES, row)
                self.assertTrue(row["path"] and row["line"] > 0, row)
        for row in self.audit["rows"]:
            self.assertTrue(row["reason"], row)

    def test_summary_matches_rows(self):
        for state, rows in (("after", self.audit["rows"]), ("before", self.audit["before_rows"])):
            counts = collections.Counter(row["classification"] for row in rows)
            summary = dict(self.audit["summary"][state])
            self.assertEqual(summary.pop("total"), len(rows))
            self.assertEqual(summary, dict(counts))

    def test_no_improper_row_remains_without_an_exact_blocked_reason(self):
        improper = [row for row in self.audit["rows"] if row["classification"].startswith("IMPROPER")]
        for row in improper:
            self.assertEqual(row.get("status"), "BLOCKED", row)
            self.assertEqual(row.get("owning_existing_goal"), "LLMA-DECLARED-PATH-CONFORMANCE-368", row)
            self.assertTrue(row.get("blocked_reason"), row)
        self.assertEqual(self.audit["summary"]["after_improper_unblocked"], 0)
        self.assertEqual(self.audit["summary"]["after_improper_blocked"], len(improper))
        self.assertEqual(sorted({row["path"] for row in improper}), self.audit["blocked"]["files"])

    def test_no_improper_doc_remains(self):
        self.assertFalse([row for row in self.audit["rows"] if row["classification"] == "IMPROPER_DOC"])

    def test_inventoried_paths_exist(self):
        for path in {row["path"] for row in self.audit["rows"]}:
            self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
