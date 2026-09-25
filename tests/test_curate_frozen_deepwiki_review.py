"""Offset-complete 659-citation curation must never publish generated text."""
import hashlib
import unittest
from unittest.mock import patch
from scripts.curate_frozen_deepwiki_review import curate,ORIGINAL_PRIORITY_REASON,MISMATCH

class FrozenReviewTests(unittest.TestCase):
    def fixture(self):
        labels=[f"s{i}.py:1" for i in range(640)]
        labels[98]="stegverse/manifest_builder.py:75-95"
        labels[99]="stegverse/manifest_builder.py:98-111"
        labels[439]="tests/test_mir_sv_exp3_manifest.py:39-48"
        s="# Page: Test\n"+" ".join("["+label+"]()" for label in labels)
        s+=" "+" ".join(f"`e{i}.py:1]()" for i in range(19))
        raw=s.encode()
        digest=hashlib.sha256(raw).hexdigest()
        entries=[]
        claimrows=[]
        for i,label in enumerate(labels):
            o=s.index("["+label+"]()")
            entries.append({"offset":o,"page":"Test","label":label,
                "candidate_url":None if i<27 else "https://example.org/source#L1"})
            claimrows.append({"offset":o,"claim_context":f"claim {i}","source_excerpt":f"source {i}"})
        prior={"input_sha256":digest,"source_revision":"a"*40,"entries":entries}
        claims={"raw_sha256":digest,"rows":claimrows}
        unresolved={"original_sha256":digest,
          "entries":[{"offset":entries[i]["offset"]} for i in range(27)],
          "malformed_contextual_entries":[{"offset":s.index(f"`e{j}.py:1]()")+len(f"`e{j}.py:1"),
                                          "context":"malformed source"} for j in range(19)]}
        priority=[{"occurrence_index":i,"status":"FULL_CLAIM_REVIEW_PENDING"} for i in ORIGINAL_PRIORITY_REASON]
        priority += [{"occurrence_index":i,"status":"CITATION_CONTEXT_MISMATCH"} for i in MISMATCH]
        other=[i for i in range(640) if i not in ORIGINAL_PRIORITY_REASON and i not in MISMATCH][:27]
        priority += [{"occurrence_index":i,"status":"NARROW_LITERAL_CONFIRMED_CONTEXT_NOT_FULLY_APPROVED"} for i in other]
        return raw,prior,claims,unresolved,priority

    def test_all_659_are_omitted_with_separate_nonallow_receipts(self):
        self.assertEqual(len(ORIGINAL_PRIORITY_REASON),46)
        self.assertTrue(MISMATCH.isdisjoint(ORIGINAL_PRIORITY_REASON))
        raw,prior,claims,unresolved,priority=self.fixture()
        with patch("scripts.curate_frozen_deepwiki_review.RAW_SHA",prior["input_sha256"]):
            sanitized,report,rows=curate(raw,prior,claims,unresolved,priority)
            self.assertEqual(report["claim_rows"],659)
            self.assertEqual(report["full_semantic_approvals"],0)
            self.assertEqual(report["priority_broader_contexts_reviewed_nonallow"],46)
            self.assertEqual(report["simple_candidates_downgraded_to_nonlinks"],613)
            self.assertEqual(report["broken_simple_citations_omitted"],27)
            self.assertEqual(report["malformed_citations_omitted"],19)
            self.assertNotIn(b"]()",sanitized)
            self.assertFalse(any(x["semantic_approval"] for x in rows))
            with self.assertRaisesRegex(ValueError,"FROZEN_CAPTURE"):
                curate(raw+b"x",prior,claims,unresolved,priority)

if __name__=="__main__":
    unittest.main()
