"""Fail-closed source-only curation checks. No raw/generated prose committed."""
import hashlib
import unittest
from unittest.mock import patch
from scripts.curate_frozen_deepwiki_review import curate,ORIGINAL_PRIORITY_REASON,MISMATCH

class FrozenReviewTests(unittest.TestCase):
    def fixture(self):
        raw = ("# Page: Test\n" + " ".join(f"[s{i}.py:1]()" for i in range(640))
               + " " + " ".join(f"`e{i}.py:1]()" for i in range(19))).encode()
        s=raw.decode()
        positions=[s.index(f"[s{i}.py:1]()") for i in range(640)]
        mpos=[s.index(f"`e{i}.py:1]()")+len(f"`e{i}.py:1") for i in range(19)]
        prior={"input_sha256":hashlib.sha256(raw).hexdigest(),
               "source_revision":"a"*40,"entries":[{"offset":o,"page":"Test",
               "label":f"s{i}.py:1","candidate_url":None if i<27 else "https://example.org/file#L1"}
               for i,o in enumerate(positions)]}
        claims={"raw_sha256":prior["input_sha256"],"rows":[{"offset":o,
                "claim_context":f"claim {i}","source_excerpt":f"source {i}"}
                for i,o in enumerate(positions)]}
        unresolved={"original_sha256":prior["input_sha256"],
                    "entries":[{"offset":positions[i]} for i in range(27)],
                    "malformed_contextual_entries":[{"offset":o,"context":"malformed source"}
                    for o in mpos]}
        original_priority=[{"occurrence_index":i,
                            "status":"FULL_CLAIM_REVIEW_PENDING"}
                           for i in ORIGINAL_PRIORITY_REASON]
        original_priority += [{"occurrence_index":i,"status":"CITATION_CONTEXT_MISMATCH"}
                              for i in MISMATCH]
        # Synthetic priority remaining 27 are disjoint from broad+diagram.
        other=[i for i in range(640) if i not in ORIGINAL_PRIORITY_REASON and i not in MISMATCH][:27]
        original_priority += [{"occurrence_index":i,
                               "status":"NARROW_LITERAL_CONFIRMED_CONTEXT_NOT_FULLY_APPROVED"}
                              for i in other]
        return raw,prior,claims,unresolved,original_priority

    def test_expected_set_exact_and_no_approved_links(self):
        self.assertEqual(len(ORIGINAL_PRIORITY_REASON),46)
        self.assertTrue(MISMATCH.isdisjoint(ORIGINAL_PRIORITY_REASON))
        raw,prior,claims,unresolved,priority=self.fixture()
        # Three source-drift labels are checked against historical original offsets.
        for i,label in [(98,"stegverse/manifest_builder.py:75-95"),
                        (99,"stegverse/manifest_builder.py:98-111"),
                        (439,"tests/test_mir_sv_exp3_manifest.py:39-48")]:
            prior["entries"][i]["label"]=label
        # The test intentionally needs to recompute all fixture offsets after
        # label changes; this keeps original raw/offset agreement strict.
        s=raw.decode()
        for i,label in [(439,"tests/test_mir_sv_exp3_manifest.py:39-48"),
                        (99,"stegverse/manifest_builder.py:98-111"),
                        (98,"stegverse/manifest_builder.py:75-95")]:
            o=prior["entries"][i]["offset"]
            old=f"[s{i}.py:1]()"
            s=s[:o]+"["+label+"]()"+s[o+len(old):]
        raw=s.encode()
        import re
        for i,e in enumerate(prior["entries"]):
            e["offset"]=s.index("["+e["label"]+"]()")
            claims["rows"][i]["offset"]=e["offset"]
        for x in unresolved["entries"]:
            x["offset"]=prior["entries"][int(x["offset"] and
                    next(i for i,p in enumerate(self.fixture()[1]["entries"]) if p["offset"]==x["offset"]))]["offset"]
        for j,z in enumerate(unresolved["malformed_contextual_entries"]):
            z["offset"]=s.index(f"`e{j}.py:1]()")+len(f"`e{j}.py:1")
        prior["input_sha256"]=claims["raw_sha256"]=unresolved["original_sha256"]=hashlib.sha256(raw).hexdigest()
        with patch("scripts.curate_frozen_deepwiki_review.RAW_SHA",prior["input_sha256"]):
            result,report,rows=curate(raw,prior,claims,unresolved,priority)
            self.assertEqual(report["claim_rows"],659)
            self.assertEqual(report["full_semantic_approvals"],0)
            self.assertEqual(report["priority_broader_contexts_reviewed_nonallow"],46)
            self.assertNotIn(b"]()",result)
            self.assertFalse(any(x["semantic_approval"] for x in rows))
            with self.assertRaisesRegex(ValueError,"FROZEN_CAPTURE"):
                curate(raw+b"x",prior,claims,unresolved,priority)

if __name__=="__main__":
    unittest.main()
