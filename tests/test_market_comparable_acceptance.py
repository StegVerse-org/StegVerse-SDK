"""Acceptance cases for the assessment market comparables (SDK#572 / #484, selection rule v2).

The eight cases proposed in the KV coordination worksheet (2026-10-28) for the #572 owner:
adjacent references never enter a governance statistic; STARTING_AT stays a lower bound; mixed
currency is refused; a missing source blocks eligibility; missing labor/token inputs stay UNKNOWN
with quote_ready false; two heterogeneous anchors never yield a quote-ready midpoint; the margin
is counted once; every scenario output stays provisional with no approval authority.
"""
import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path

from stegverse import tier_pricing

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "pricing" / "assessment"


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class MarketComparableAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.record = _load(D / "cost-basis.governance_assessment_engagement.candidate.json")
        self.card = _load(ROOT / "pricing" / "rate-card.candidate.json")
        self.policy = _load(D / "policy.candidate.json")
        self.market = _load(D / "market-comparables.candidate.json")

    def derive(self, market=None, policy=None):
        return tier_pricing.derive_pricing([self.record], self.card, policy or self.policy, market or self.market)

    def anchors(self):
        return [c for c in self.market["comparables"] if c["role"] == "GOVERNANCE_ANCHOR"]

    def test_1_adjacent_references_never_enter_the_governance_statistic(self):
        median = tier_pricing.market_median(self.market)
        self.assertEqual(median["adjacent_references"], 1)
        self.assertEqual(median["anchors"], len(self.anchors()))
        prices = sorted(Decimal(c["usd_per_action"]) for c in self.anchors())
        self.assertEqual(median["anchor_range"], (prices[0], prices[-1]))
        # The adjacent $1,499 STARTING_AT figure is below every anchor; it must not pull the median.
        self.assertGreater(median["at_least"], Decimal("1499"))

    def test_2_starting_at_remains_a_lower_bound(self):
        # Promote the STARTING_AT adjacent reference to an anchor: the median's at_least moves to
        # its bound side and the median stops being exact, so the figure never acts as a point.
        market = copy.deepcopy(self.market)
        anchors_only = tier_pricing.market_median(market)
        for c in market["comparables"]:
            c["role"] = "GOVERNANCE_ANCHOR"
        median = tier_pricing.market_median(market)
        self.assertFalse(median["exact"])
        self.assertEqual(median["anchors"], anchors_only["anchors"] + 1)
        self.assertLessEqual(median["at_least"], anchors_only["at_least"])
        single = {"schema": tier_pricing.MARKET_SCHEMA, "comparables": [
            {"name": "x", "usd_per_action": "1499", "price_basis": "STARTING_AT", "source": "https://x", "observed_at": "2026-10-29"}]}
        m = tier_pricing.market_median(single)
        self.assertEqual((m["at_least"], m["at_most"], m["exact"]), (Decimal("1499"), None, False))

    def test_2b_a_range_basis_bounds_the_median_on_both_sides(self):
        both = {"schema": tier_pricing.MARKET_SCHEMA, "comparables": [
            {"name": "r", "usd_per_action": "8000", "usd_per_action_high": "12000", "price_basis": "RANGE",
             "source": "https://r", "observed_at": "2026-10-29"}]}
        m = tier_pricing.market_median(both)
        self.assertEqual((m["at_least"], m["at_most"], m["exact"]), (Decimal("8000"), Decimal("12000"), False))
        both["comparables"][0]["usd_per_action_high"] = "7000"
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.market_median(both)
        del both["comparables"][0]["usd_per_action_high"]
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.market_median(both)

    def test_3_mixed_currency_is_refused(self):
        market = copy.deepcopy(self.market)
        market["comparables"][0]["currency"] = "CAD"
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.market_median(market)

    def test_4_missing_source_blocks_eligibility(self):
        market = copy.deepcopy(self.market)
        market["comparables"][0]["source"] = ""
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.market_median(market)

    def test_5_missing_labor_and_token_inputs_stay_unknown_and_not_quote_ready(self):
        report = self.derive()
        tier = report["tiers"][0]
        self.assertEqual(tier["cost_completeness"], "MACHINE_SUBTOTAL_ONLY")
        self.assertEqual(tier["unmodeled_cost_dimensions"], ["operator_seconds", "token_units"])
        self.assertFalse(tier["quote_ready"])

    def test_6_two_heterogeneous_anchors_never_yield_a_quote_ready_midpoint(self):
        # Drop one anchor to reproduce the two-anchor state: below the policy minimum the price is
        # the cost floor and the midpoint is reported as context only.
        market = copy.deepcopy(self.market)
        anchors = [c for c in market["comparables"] if c["role"] == "GOVERNANCE_ANCHOR"]
        market["comparables"].remove(anchors[-1])
        report = self.derive(market=market)
        tier = report["tiers"][0]
        self.assertEqual(report["market_anchors"], 2)
        self.assertEqual(report["minimum_market_anchors"], 3)
        self.assertEqual(tier["market_position"], "MARKET_ANCHORS_INSUFFICIENT")
        self.assertEqual(Decimal(tier["usd_per_action"]), Decimal(tier["cost_floor_usd_per_action"]))
        self.assertFalse(tier["quote_ready"])
        self.assertNotEqual(tier["usd_per_action"], report["market_median_range_usd_per_action"]["at_least"])
        # With enough anchors the median may set the price, positioned at its lower bound when
        # the median is a range; it is still never quote-ready while the basis is a subtotal.
        full = self.derive()["tiers"][0]
        self.assertEqual(full["market_position"], "AT_MARKET_MEDIAN_LOWER_BOUND")
        self.assertFalse(full["quote_ready"])

    def test_7_margin_is_counted_once(self):
        report = self.derive()
        tier = report["tiers"][0]
        margin = Decimal(report["target_gross_margin"])
        floor = Decimal(tier["unit_cost_usd"]) / (1 - margin)
        self.assertEqual(Decimal(tier["cost_floor_usd_per_action"]), floor)
        # The market price is never marked up again: it is the median bound itself.
        self.assertEqual(tier["usd_per_action"], report["market_median_range_usd_per_action"]["at_least"])

    def test_8_scenario_outputs_stay_provisional_with_no_approval_authority(self):
        report = self.derive()
        self.assertEqual(report["status"], "PROVISIONAL")
        self.assertTrue(all(t["status"] == "PROVISIONAL_SCENARIO" for t in report["tiers"]))
        self.assertFalse(any(report["authority"].values()))
        self.assertIn("CANDIDATE", self.market["status"])
        self.assertEqual(self.market["selection_rule_version"], "2026-10-29.v2")

    def test_every_comparable_declares_a_role_and_adjacent_ones_say_why(self):
        for c in self.market["comparables"]:
            self.assertIn(c["role"], tier_pricing.COMPARABLE_ROLES, c["source"])
            if c["role"] == "ADJACENT_REFERENCE":
                self.assertTrue(c.get("role_reason"), c["source"])

    def test_unknown_role_is_refused(self):
        market = copy.deepcopy(self.market)
        market["comparables"][0]["role"] = "MAYBE"
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.market_median(market)


if __name__ == "__main__":
    unittest.main()
