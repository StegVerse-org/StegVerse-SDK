"""Historical exact-source successor must not mutate earlier audit conclusions."""
import unittest
from copy import deepcopy
from unittest.mock import patch

from scripts.assess_deepwiki_atomic_claims import assess
from scripts.reconcile_historical_deepwiki_literals import reconcile
from tests.test_assess_deepwiki_atomic_claims import AtomicClaimReviewTests


class HistoricalNarrowReviewTests(unittest.TestCase):
    def fixture(self):
        raw, claims, curations, priority, report, sha = AtomicClaimReviewTests().fixture()
        with patch("scripts.assess_deepwiki_atomic_claims.ORIGINAL_SHA256", sha):
            latest = assess(raw, claims, curations, priority, report)["records"]
        historical=deepcopy(claims)
        later=deepcopy(claims)
        historical["source_revision"]="a"*40
        later["source_revision"]="b"*40
        return historical,later,latest,sha

    def test_proven_historical_literal_is_not_full_generated_claim(self):
        historical,later,latest,sha=self.fixture()
        with patch("scripts.reconcile_historical_deepwiki_literals.CAPTURE_SHA256",sha), patch(
             "scripts.reconcile_historical_deepwiki_literals.HISTORICAL_REVISION","a"*40):
            result=reconcile(historical,later,latest,{100:"sample_handler"})
        self.assertEqual(result["historical_narrow_facts_revalidated"],1)
        self.assertEqual(result["full_generated_claim_semantic_approvals"],0)
        self.assertFalse(result["source_reconciliations"][0]["republication_allowed"])
        self.assertEqual(result["source_reconciliations"][0]["predecessor_disposition"],
                         latest[100]["disposition"])

    def test_mutated_historic_evidence_fails_closed(self):
        historical,later,latest,sha=self.fixture()
        historical["rows"][100]["source_excerpt"]="different"
        with patch("scripts.reconcile_historical_deepwiki_literals.CAPTURE_SHA256",sha), patch(
             "scripts.reconcile_historical_deepwiki_literals.HISTORICAL_REVISION","a"*40):
            with self.assertRaisesRegex(ValueError,"ORIGINAL_NARROW_LITERAL_NOT_FOUND"):
                reconcile(historical,later,latest,{100:"sample_handler"})
            historical["raw_sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"CAPTURE_PROVENANCE_CHANGED"):
                reconcile(historical,later,latest,{100:"sample_handler"})


if __name__=="__main__":
    unittest.main()
