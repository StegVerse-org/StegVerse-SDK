"""The committed assessment pricing candidate must equal what the established formula derives.

StegVerse-Labs/.github#3370 / #3368 owner ruling: price = exactly the established formula
(stegverse/tier_pricing.py, C_pricing = max(C_estimated, C_authentically_observed), margin inside).
Re-derive from the committed candidate inputs so the number cannot drift from the formula.
"""
import json
import unittest
from pathlib import Path

from stegverse import tier_pricing

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "pricing" / "assessment"


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class AssessmentPricingCandidateTests(unittest.TestCase):
    def setUp(self):
        self.record = _load(D / "cost-basis.governance_assessment_engagement.candidate.json")
        self.rates = _load(ROOT / "pricing" / "rate-card.candidate.json")
        self.policy = _load(D / "policy.candidate.json")
        self.market = _load(D / "market-comparables.candidate.json")

    def test_committed_report_is_exactly_the_formula_output(self):
        derived = tier_pricing.derive_pricing([self.record], self.rates, self.policy, self.market)
        committed = _load(D / "candidate-report.json")
        self.assertEqual(json.loads(json.dumps(derived, sort_keys=True)), committed)

    def test_candidate_stays_provisional_and_non_authorizing(self):
        report = _load(D / "candidate-report.json")
        self.assertEqual(report["status"], "PROVISIONAL")
        self.assertTrue(all(t["status"] == "PROVISIONAL_SCENARIO" for t in report["tiers"]))
        self.assertIn("CANDIDATE", self.policy["status"])
        self.assertIn("CANDIDATE", self.market["status"])

    def test_every_comparable_is_cited(self):
        # Form only: whether each page shows the cited price is checked by hand
        # on observed_at (see the file's citation_check); this cannot catch a miscitation.
        self.assertGreaterEqual(len(self.market["comparables"]), 3)
        for entry in self.market["comparables"]:
            self.assertTrue(entry["source"].startswith("https://"), entry)
            self.assertRegex(entry["observed_at"], r"^\d{4}-\d{2}-\d{2}$")

    def test_without_market_the_formula_alone_prices_only_machine_cost(self):
        derived = tier_pricing.derive_pricing([self.record], self.rates, self.policy)
        # Labor (operator_seconds) and LLM tokens (token_units) carry no rate in the engine.
        self.assertLess(float(derived["tiers"][0]["usd_per_action"]), 10)

    def test_every_comparable_states_vendor_currency_scope_and_basis(self):
        scope_keys = {"authority_map", "risk_matrix", "prioritized_remediations", "thirty_day_plan"}
        for entry in self.market["comparables"]:
            self.assertEqual(entry["currency"], "USD", entry["source"])
            self.assertIn(entry["price_basis"], tier_pricing.PRICE_BASES, entry["source"])
            self.assertTrue(entry["vendor"] and entry["price_text"] and entry["deliverables"], entry["source"])
            self.assertEqual(set(entry["scope_match"]), scope_keys, entry["source"])
            for value in entry["scope_match"].values():
                self.assertRegex(value, r"^(YES|NO|PARTIAL|UNKNOWN)( \(.+\))?$")
            self.assertRegex(entry["verified_on_vendor_page_at"], r"^\d{4}-\d{2}-\d{2}$")

    def test_a_non_usd_or_unknown_basis_comparable_is_refused_by_the_engine(self):
        bad = json.loads(json.dumps(self.market))
        bad["comparables"][0]["price_basis"] = "TYPICAL_VALUE"
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.derive_pricing([self.record], self.rates, self.policy, bad)


if __name__ == "__main__":
    unittest.main()
