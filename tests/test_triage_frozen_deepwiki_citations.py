"""Frozen external-doc review never authorizes source-only candidates."""
import hashlib
import unittest
from unittest.mock import patch
from scripts import triage_frozen_deepwiki_citations as module


class FrozenDeepWikiTriageTests(unittest.TestCase):
    def sample(self):
        raw = b"frozen synthetic capture"
        digest = hashlib.sha256(raw).hexdigest()
        literals = module.NARROW_LITERAL
        ids = sorted(set(range(75)) - {14, 15, 16, 17, 18} | {75, 76, 77, 78, 79})
        # Real priority IDs are sparse; synthesize all reviewed and mismatch IDs.
        selected = sorted((set(range(75)) | set(literals) | module.MISMATCH))
        while len(selected) < 75:
            selected.append(max(selected) + 1)
        selected = selected[:75] if len(selected) == 75 else sorted(
            set(literals) | module.MISMATCH | set(range(800, 800 + 75 - len(literals) - len(module.MISMATCH))))
        rows = []
        for i in selected:
            snippet = literals.get(i, "some source excerpt")
            rows.append({"index": i, "page": "Test", "label": "demo.py:1",
                         "source_url": "https://example.org/source#L1",
                         "source_excerpt": snippet,
                         "claim_context": "GovernanceIntakeRequest" if i in module.MISMATCH else "A source claim",
                         "triage_signal": "LOW_LEXICAL_OVERLAP_REVIEW_FIRST"})
        claims = {"raw_sha256": digest, "source_revision": "a" * 40, "rows": rows}
        unresolved = {"original_sha256": digest,
                      "entries": [{"offset": i, "page": "Test", "label": str(i),
                                   "disposition": "NEEDS_REVIEW", "proposals": []} for i in range(27)],
                      "malformed_contextual_entries": [{"offset": i, "context": "x"} for i in range(19)]}
        return raw, digest, claims, unresolved

    def test_full_priority_and_defect_contract(self):
        raw, digest, claims, unresolved = self.sample()
        with patch.object(module, "CAPTURE_SHA256", digest):
            priority, defects = module.build(raw, claims, unresolved)
        self.assertEqual(len(priority), 75)
        self.assertEqual(len(defects), 46)
        self.assertEqual(sum(p["status"] == "CITATION_CONTEXT_MISMATCH" for p in priority), 2)
        self.assertEqual(sum(p["status"].startswith("NARROW_LITERAL_CONFIRMED") for p in priority), 27)
        self.assertFalse(any(p["full_claim_semantically_approved"] for p in priority))
        self.assertFalse(any(p["publication_approved"] for p in defects))

    def test_changed_raw_and_changed_literal_fail_closed(self):
        raw, digest, claims, unresolved = self.sample()
        with patch.object(module, "CAPTURE_SHA256", digest):
            with self.assertRaisesRegex(ValueError, "FROZEN_CAPTURE_HASH_MISMATCH"):
                module.build(raw + b"!", claims, unresolved)
            target = next(x for x in claims["rows"] if x["index"] == 19)
            target["source_excerpt"] = "wrong version"
            with self.assertRaisesRegex(ValueError, "SOURCE_LITERAL_CHANGED"):
                module.build(raw, claims, unresolved)


if __name__ == "__main__":
    unittest.main()
