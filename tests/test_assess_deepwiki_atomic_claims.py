"""Atomic citation assessor must review every original candidate without importing it."""
import hashlib
import unittest
from unittest.mock import patch

from scripts.assess_deepwiki_atomic_claims import assess, narrow_observations


class AtomicClaimReviewTests(unittest.TestCase):
    def fixture(self):
        labels = ["stegverse/example.py:1" for _ in range(640)]
        raw_text = "".join(
            f"The source declares sample_handler and describes source validation. [{label}]()\n\n"
            for label in labels
        )
        raw = raw_text.encode()
        sha = hashlib.sha256(raw).hexdigest()
        entries, claims, curations = [], [], []
        at = 0
        priority = []
        for i, label in enumerate(labels):
            reference = "[" + label + "]()"
            position = raw_text.find(reference, at)
            self.assertGreaterEqual(position, at)
            at = position + len(reference)
            url = None if i < 27 else f"https://example.org/blob/abc/example.py#L1"
            entries.append({"offset": position, "label": label, "page": "Test",
                            "candidate_path": "stegverse/example.py", "candidate_url": url})
            claims.append({"index": i, "offset": position, "label": label, "page": "Test",
                           "source_excerpt": "def sample_handler(value):\n    return value",
                           "claim_context": "Source declares sample_handler."})
            status = "DENY:UNRESOLVED_SOURCE_LABEL_OMITTED" if i < 27 else (
                "DENY:PENDING_CLAIM_SPECIFIC_SEMANTIC_REVIEW"
            )
            if 100 <= i < 127:
                status = "DENY:FULL_CLAIM_UNREVIEWED_NARROW_LITERAL_ONLY"
                priority.append({"occurrence_index": i,
                                 "status": "NARROW_LITERAL_CONFIRMED_CONTEXT_NOT_FULLY_APPROVED"})
            if 127 <= i < 129:
                status = "DENY:CITATION_CONTEXT_MISMATCH"
                priority.append({"occurrence_index": i, "status": "CITATION_CONTEXT_MISMATCH"})
            if 129 <= i < 175:
                status = "DENY:REVIEWED_INSUFFICIENT_EVIDENCE"
                priority.append({"occurrence_index": i, "status": "FULL_CLAIM_REVIEW_PENDING"})
            curations.append({"index": i, "offset": position, "disposition": status})
        curations += [{"disposition":"DENY:MALFORMED_CITATION_OMITTED"} for _ in range(19)]
        claim_packet = {"raw_sha256": sha, "source_revision": "a"*40,
                        "candidate_total": 613, "rows": claims}
        report = {"input_sha256": sha, "entries": entries}
        return raw, claim_packet, curations, priority, report, sha

    def test_exhaustive_non_authorizing_review_and_exact_atomic_fact(self):
        raw, claims, curations, priority, report, sha = self.fixture()
        with patch("scripts.assess_deepwiki_atomic_claims.ORIGINAL_SHA256", sha):
            result = assess(raw, claims, curations, priority, report)
            summary = result["summary"]
            self.assertEqual(summary["reviewed_simple_occurrences"], 640)
            self.assertEqual(summary["reviewed_original_candidates"], 613)
            self.assertEqual(summary["pending538_reassessed"], 538)
            self.assertEqual(summary["original_priority75_reassessed"], 75)
            self.assertEqual(summary["full_claim_semantically_approved"], 0)
            self.assertGreater(summary["narrow_source_observations"], 0)
            self.assertTrue(all(not r["publication_allowed"] for r in result["records"]))
            self.assertTrue(all(not r["full_semantic_approval"] for r in result["records"]))

    def test_original_hash_or_predecessor_mismatch_denied(self):
        raw, claims, curations, priority, report, sha = self.fixture()
        with patch("scripts.assess_deepwiki_atomic_claims.ORIGINAL_SHA256", sha):
            with self.assertRaisesRegex(ValueError, "FROZEN_CAPTURE"):
                assess(raw+b"x", claims, curations, priority, report)
            claims["rows"][0]["offset"] += 1
            with self.assertRaisesRegex(ValueError, "PREDECESSOR_OCCURRENCE"):
                assess(raw, claims, curations, priority, report)

    def test_literal_code_symbol_does_not_prove_a_live_task(self):
        evidence = narrow_observations(
            "The live worker has called sample_handler", "def sample_handler(x):\n    return x",
            "stegverse/example.py")
        self.assertTrue(evidence)
        self.assertTrue(all(e["scope"] == "SOURCE_ONLY_NOT_FULL_CLAIM" for e in evidence))


if __name__ == "__main__":
    unittest.main()
