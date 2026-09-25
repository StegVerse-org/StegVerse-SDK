"""Fail-closed source-only curation checks. No raw/generated prose committed."""
import hashlib
import unittest
from unittest.mock import patch
from scripts.curate_frozen_deepwiki_review import curate,ORIGINAL_PRIORITY_REASON,MISMATCH

class FrozenReviewTests(unittest.TestCase):
    def fixture(self):
        raw = ("# Page: Test\n" + " ".join(f"[s{i}.py:1]()" for i in range(640))
               + " " + " ".join(f"`e{i}.py:1]()" for i in range(19))).encode()
        s = raw.decode()
        for i, label in [(98, "stegverse/manifest_builder.py:75-95"),
                         (99, "stegverse/manifest_builder.py:98-111"),
                         (439, "tests/test_mir_sv_exp3_manifest.py:39-48")]:
            s = s.replace(f"[s{i}.py:1]()", "[" + label + "]()", 1)
        raw = s.encode()
        for i,e in enumerate(prior["entries"]):
            e["offset"] = s.index("[" + e["label"] + "]()")
            claims["rows"][i]["offset"] = e["offset"]
        for i,e in enumerate(unresolved["entries"]):
            e["offset"] = prior["entries"][i]["offset"]
        for j,e in enumerate(unresolved["malformed_contextual_entries"]):
            e["offset"] = s.index(f"`e{j}.py:1]()") + len(f"`e{j}.py:1")
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
