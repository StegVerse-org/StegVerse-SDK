"""A cost basis with unmodeled cost dimensions is a machine-only subtotal, never a complete cost.

Regressions for the five exact-head reproductions on StegVerse-org/StegVerse-SDK#572
(comment 6485872438): declared operator_seconds / token_units were silently dropped and the
basis reported PRICED with no missing rates.
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


class CostCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.record = _load(D / "cost-basis.governance_assessment_engagement.candidate.json")
        self.rates = tier_pricing.rate_card_rates(_load(ROOT / "pricing" / "rate-card.candidate.json"))
        self.policy = _load(D / "policy.candidate.json")
        self.card = _load(ROOT / "pricing" / "rate-card.candidate.json")

    def cost(self, **estimate):
        record = copy.deepcopy(self.record)
        record["cost_estimate"].update(estimate)
        return tier_pricing.action_cost(record, self.rates)

    def test_committed_candidate_is_a_machine_subtotal_not_a_price(self):
        cost = self.cost()
        self.assertEqual(cost["status"], "MACHINE_SUBTOTAL_ONLY")
        self.assertEqual(cost["machine_subtotal_usd_per_action"], "0.926214400")
        self.assertIsNone(cost["usd_per_action"])
        self.assertEqual(cost["unmodeled_cost_dimensions"], ["operator_seconds", "token_units"])
        self.assertEqual(cost["missing_rates"], [])

    def test_zeroed_labor_and_tokens_still_unknown_by_declaration(self):
        # The quantities are zero, but the record declares the dimensions UNKNOWN, not KNOWN_ZERO.
        cost = self.cost(operator_seconds=0, token_units=0)
        self.assertEqual(cost["status"], "MACHINE_SUBTOTAL_ONLY")
        self.assertEqual(cost["unmodeled_cost_dimensions"], ["operator_seconds", "token_units"])

    def test_tenfold_labor_and_tokens_change_no_subtotal_but_stay_unmodeled(self):
        cost = self.cost(operator_seconds=720000, token_units=20000000)
        self.assertEqual(cost["machine_subtotal_usd_per_action"], "0.926214400")
        self.assertEqual(cost["status"], "MACHINE_SUBTOTAL_ONLY")

    def test_null_compute_lowers_the_subtotal_and_stays_unmodeled(self):
        # An undeclared optional null is allowed; a null on a field declared MODELED is refused
        # (see test_modeled_with_a_null_quantity_is_a_contradiction).
        record = copy.deepcopy(self.record)
        record["cost_estimate"]["compute_units"] = None
        del record["cost_dimension_dispositions"]["compute_units"]
        cost = tier_pricing.action_cost(record, self.rates)
        self.assertEqual(cost["machine_subtotal_usd_per_action"], "0.206214400")
        self.assertEqual(cost["status"], "MACHINE_SUBTOTAL_ONLY")

    def test_all_machine_quantities_null_gives_a_zero_subtotal_not_a_price(self):
        record = copy.deepcopy(self.record)
        for field in ("compute_units", "failure_recovery_units", "recovery_actions", "storage_bytes",
                      "network_bytes", "external_cost_usd"):
            record["cost_estimate"][field] = None
            record["cost_dimension_dispositions"].pop(field, None)
        cost = tier_pricing.action_cost(record, self.rates)
        self.assertEqual(cost["machine_subtotal_usd_per_action"], "0")
        self.assertIsNone(cost["usd_per_action"])
        self.assertEqual(cost["status"], "MACHINE_SUBTOTAL_ONLY")

    def test_known_zero_and_not_applicable_declarations_are_complete(self):
        record = copy.deepcopy(self.record)
        record["cost_estimate"].update(operator_seconds=0, token_units=0)
        record["cost_dimension_dispositions"].update(operator_seconds="KNOWN_ZERO", token_units="NOT_APPLICABLE")
        cost = tier_pricing.action_cost(record, self.rates)
        self.assertEqual(cost["status"], "PRICED")
        self.assertEqual(cost["usd_per_action"], "0.926214400")
        self.assertEqual(cost["unmodeled_cost_dimensions"], [])

    def test_a_declared_quantity_on_an_unmodeled_field_is_unmodeled_without_any_declaration(self):
        record = copy.deepcopy(self.record)
        del record["cost_dimension_dispositions"]
        cost = tier_pricing.action_cost(record, self.rates)
        self.assertEqual(cost["status"], "MACHINE_SUBTOTAL_ONLY")
        self.assertEqual(cost["unmodeled_cost_dimensions"], ["operator_seconds", "token_units"])

    def test_optional_machine_nulls_without_declaration_do_not_break_a_machine_task(self):
        record = {"schema": tier_pricing.COST_BASIS_SCHEMA, "task_class": "gate", "sample_count": 0,
                  "cost_estimate": {"compute_units": 1, "storage_bytes": None, "network_bytes": None, "latency_ms": 500}}
        cost = tier_pricing.action_cost(record, self.rates)
        self.assertEqual((cost["status"], cost["usd_per_action"]), ("PRICED", "0.006"))

    def test_unknown_disposition_value_fails_closed(self):
        record = copy.deepcopy(self.record)
        record["cost_dimension_dispositions"]["token_units"] = "MAYBE"
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.action_cost(record, self.rates)

    def test_tier_never_reports_priced_while_a_dimension_is_unmodeled_even_when_observed(self):
        c = self.record["task_class"]
        obs = {"schema": tier_pricing.OBSERVATION_SET_SCHEMA,
               "authentic_observation_classes": ["ORGANIZATION_RECEIPT_MEASURED"],
               "observations": {c: {"schema": "stegverse.cost-observation.v1", "scope_id": c, "currency": "USD",
                                    "unit": "action", "cost_basis_version": self.policy["cost_basis_version"],
                                    "amount": "5", "observation_class": "ORGANIZATION_RECEIPT_MEASURED",
                                    "evidence_ref": f"receipts/{c}.json", "evidence_sha256": "a" * 64}}}
        report = tier_pricing.derive_pricing([self.record], self.card, self.policy, None, obs)
        tier = report["tiers"][0]
        self.assertEqual(report["action_costs"][0]["pricing_basis"]["status"], "COMPLETE_BASIS")
        self.assertNotEqual(tier["status"], "PRICED")
        self.assertEqual(tier["cost_completeness"], "MACHINE_SUBTOTAL_ONLY")
        self.assertEqual(report["status"], "PROVISIONAL")

    def test_report_keeps_the_subtotal_as_the_floor_operand_and_names_the_repair(self):
        report = tier_pricing.derive_pricing([self.record], self.card, self.policy, _load(D / "market-comparables.candidate.json"))
        tier = report["tiers"][0]
        self.assertEqual(report["status"], "PROVISIONAL")
        self.assertEqual(tier["cost_completeness"], "MACHINE_SUBTOTAL_ONLY")
        self.assertEqual(Decimal(tier["unit_cost_usd"]), Decimal("0.926214400"))
        self.assertIn("unmodeled cost dimensions", report["actionable_disposition"]["failed_predicate"])
        self.assertIn("NOT_APPLICABLE or KNOWN_ZERO", report["actionable_disposition"]["required_evidence_or_repair"])
        self.assertFalse(report["authority"]["final_price_approved"])

    # Residual cases from the second verification (comment 6486545783): MODELED must mean a
    # present quantity on a field the rate card prices.
    def test_modeled_with_a_null_quantity_is_a_contradiction(self):
        record = copy.deepcopy(self.record)
        record["cost_estimate"].update(operator_seconds=0, token_units=0, compute_units=None)
        record["cost_dimension_dispositions"].update(operator_seconds="KNOWN_ZERO", token_units="KNOWN_ZERO",
                                                     compute_units="MODELED")
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.action_cost(record, self.rates)

    def test_modeled_on_a_field_nothing_prices_is_a_contradiction(self):
        record = copy.deepcopy(self.record)
        record["cost_estimate"].update(operator_seconds=None, token_units=0)
        record["cost_dimension_dispositions"].update(operator_seconds="MODELED", token_units="KNOWN_ZERO")
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.action_cost(record, self.rates)

    def test_modeled_on_a_field_nothing_prices_is_refused_even_with_a_quantity(self):
        record = copy.deepcopy(self.record)
        record["cost_dimension_dispositions"]["operator_seconds"] = "MODELED"  # quantity 72000 is present
        with self.assertRaisesRegex(tier_pricing.PricingInputError, "no cost mapping"):
            tier_pricing.action_cost(record, self.rates)

    def test_known_zero_with_a_non_zero_quantity_is_a_contradiction(self):
        record = copy.deepcopy(self.record)
        record["cost_dimension_dispositions"]["token_units"] = "KNOWN_ZERO"
        with self.assertRaises(tier_pricing.PricingInputError):
            tier_pricing.action_cost(record, self.rates)

    def test_modeled_with_a_present_quantity_on_a_priced_field_is_complete(self):
        record = copy.deepcopy(self.record)
        record["cost_estimate"].update(operator_seconds=0, token_units=0)
        record["cost_dimension_dispositions"].update(operator_seconds="KNOWN_ZERO", token_units="NOT_APPLICABLE")
        cost = tier_pricing.action_cost(record, self.rates)
        self.assertEqual((cost["status"], cost["usd_per_action"]), ("PRICED", "0.926214400"))


if __name__ == "__main__":
    unittest.main()
