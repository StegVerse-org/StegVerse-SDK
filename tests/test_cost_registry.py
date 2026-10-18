"""Versioned cost-component registry and C_pricing = max(C_estimated, C_authentically_observed)."""
import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

from stegverse import cost_registry as cr

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "pricing" / "cost-component-registry.v1.json").read_text(encoding="utf-8"))
CARD = json.loads((ROOT / "pricing" / "rate-card.five-lane-declared.json").read_text(encoding="utf-8"))
AUTHENTIC = REGISTRY["authentic_observation_classes"]
DIGEST = "b" * 64


def _context(locus="EXTERNAL_PROVIDER", provider="openai", **quantities):
    base = {"storage_gb_month": 0, "governance_overhead_runner_minutes": 0}
    base.update(quantities)
    return {"scope_id": "SV-RECON-001", "execution_locus": locus, "provider": provider,
            "attributable_outcome_id": "sha256:155869ba", "quantities": base,
            "allocation": {"attributable_outcomes_in_period": 1}}


def _observation(amount, **overrides):
    obs = {"schema": cr.OBSERVATION_SCHEMA, "scope_id": "SV-RECON-001", "currency": "USD",
           "unit": "successful equivalent admissible outcome", "cost_basis_version": REGISTRY["registry_version"],
           "amount": amount, "observation_class": "EXACT_USAGE_PLUS_BOUND_VERSIONED_RATE_CARD",
           "evidence_ref": "five_lane_results.json#rows/0", "evidence_sha256": DIGEST}
    obs.update(overrides)
    return obs


@pytest.mark.parametrize("provider,tokens_in,tokens_out,expected", [
    ("openai", 307, 178, "0.006875"),      # five-lane openai-raw
    ("openai", 326, 175, "0.00688"),       # openai-governed
    ("anthropic", 362, 638, "0.010656"),   # anthropic-raw
    ("anthropic", 382, 398, "0.007116"),   # anthropic-governed
])
def test_reproduces_the_five_lane_provider_costs_from_retained_usage(provider, tokens_in, tokens_out, expected):
    result = cr.estimate(REGISTRY, [CARD], _context(provider=provider, input_tokens=tokens_in, output_tokens=tokens_out))
    assert result["status"] == "COMPLETE"
    assert Decimal(result["amount"]) == Decimal(expected)
    assert result["cost_basis_version"] == REGISTRY["registry_version"]
    assert {line["component_id"] for line in result["components"]} == {
        f"external.{provider}.input_tokens", f"external.{provider}.output_tokens",
        "internal.storage_gb_month", "shared.governance_overhead"}
    assert not any(result["authority"].values())


def test_context_selects_components_and_internal_execution_carries_no_provider_cost():
    internal = cr.estimate(REGISTRY, [CARD], _context(locus="INTERNAL", provider=None, runner_minutes=2,
                                                      input_tokens=999, output_tokens=999))
    ids = {line["component_id"] for line in internal["components"]}
    assert "internal.runner_minutes" in ids and not any(i.startswith("external.") for i in ids)
    assert Decimal(internal["amount"]) == Decimal("0.016")


def test_unknown_quantity_rate_or_allocation_is_never_priced_as_zero():
    missing_quantity = cr.estimate(REGISTRY, [CARD], _context(input_tokens=307))
    assert (missing_quantity["status"], missing_quantity["amount"]) == ("INCOMPLETE", "UNKNOWN")
    assert missing_quantity["unknown_components"] == ["external.openai.output_tokens"]
    card = copy.deepcopy(CARD)
    del card["rates"]["openai.output_usd_per_million"]
    assert cr.estimate(REGISTRY, [card], _context(input_tokens=1, output_tokens=1))["status"] == "INCOMPLETE"
    context = _context(input_tokens=1, output_tokens=1)
    context["allocation"] = {}
    assert "shared.governance_overhead" in cr.estimate(REGISTRY, [CARD], context)["unknown_components"]


def test_shared_cost_is_allocated_across_attributable_outcomes():
    context = _context(locus="INTERNAL", provider=None, runner_minutes=0, governance_overhead_runner_minutes=10)
    context["allocation"] = {"attributable_outcomes_in_period": 4}
    result = cr.estimate(REGISTRY, [CARD], context)
    shared = {line["component_id"]: line for line in result["components"]}["shared.governance_overhead"]
    assert Decimal(shared["amount"]) == Decimal("0.02")  # 10 min * 0.008 / 4 outcomes


def test_other_currency_needs_a_cited_fx_rate():
    card = copy.deepcopy(CARD)
    card["rates"]["openai.output_usd_per_million"]["currency"] = "EUR"
    assert cr.estimate(REGISTRY, [card], _context(input_tokens=0, output_tokens=1000000))["status"] == "INCOMPLETE"
    card["fx"] = {"EUR->USD": {"rate": "1.1", "source": "https://example.org/fx", "observed_at": "2026-10-17"}}
    result = cr.estimate(REGISTRY, [card], _context(input_tokens=0, output_tokens=1000000))
    assert Decimal(result["amount"]) == Decimal("33.0")


def test_external_provider_cost_must_be_attributed_to_a_governed_outcome():
    context = _context(input_tokens=1, output_tokens=1)
    del context["attributable_outcome_id"]
    with pytest.raises(cr.CostInputError, match="attributable_outcome_id"):
        cr.estimate(REGISTRY, [CARD], context)


def test_double_counting_one_resource_fails_closed():
    registry = copy.deepcopy(REGISTRY)
    duplicate = dict(registry["components"][0], component_id="external.openai.input_tokens.again")
    registry["components"].append(duplicate)
    with pytest.raises(cr.CostInputError, match="double counting"):
        cr.estimate(registry, [CARD], _context(input_tokens=1, output_tokens=1))
    registry["components"][-1]["component_id"] = registry["components"][0]["component_id"]
    with pytest.raises(cr.CostInputError, match="duplicate component_id"):
        cr.validate_registry(registry)
    second_card = dict(copy.deepcopy(CARD), rate_card_id="other")
    with pytest.raises(cr.CostInputError, match="more than one rate card"):
        cr.estimate(REGISTRY, [CARD, second_card], _context(input_tokens=1, output_tokens=1))


@pytest.mark.parametrize("estimated_amount,observed_amount,status,selected,c_pricing", [
    ("0.006875", "0.007", "COMPLETE_BASIS", "OBSERVED", "0.007"),
    ("0.006875", "0.001", "COMPLETE_BASIS", "ESTIMATED", "0.006875"),
    ("0.006875", "0.006875", "COMPLETE_BASIS", "EQUAL", "0.006875"),
    ("0.006875", "UNKNOWN", "PROVISIONAL_SCENARIO", "ESTIMATED_ONLY", "0.006875"),
    ("UNKNOWN", "0.007", "PROVISIONAL_SCENARIO", "OBSERVED_ONLY", "0.007"),
    ("UNKNOWN", "UNKNOWN", "INCOMPLETE", None, None),
])
def test_pricing_basis_is_the_max_of_both_operands(estimated_amount, observed_amount, status, selected, c_pricing):
    estimate = {"scope_id": "SV-RECON-001", "currency": "USD", "unit": "successful equivalent admissible outcome",
                "cost_basis_version": REGISTRY["registry_version"], "amount": estimated_amount}
    basis = cr.pricing_basis(AUTHENTIC, estimate, _observation(observed_amount))
    assert (basis["status"], basis["selected_basis"], basis["c_pricing"]) == (status, selected, c_pricing)
    assert (basis["estimated"]["amount"], basis["observed"]["amount"]) == (estimated_amount, observed_amount)
    assert basis["final"] is False and not any(basis["authority"].values())


def test_incomparable_or_unauthentic_observation_is_refused():
    estimate = cr.estimate(REGISTRY, [CARD], _context(input_tokens=307, output_tokens=178))
    estimate = dict(estimate, unit="successful equivalent admissible outcome")
    for key, value in (("currency", "EUR"), ("scope_id", "OTHER"), ("cost_basis_version", "older"), ("unit", "token")):
        basis = cr.pricing_basis(AUTHENTIC, estimate, _observation("0.007", **{key: value}))
        assert (basis["status"], basis["mismatched"], basis["c_pricing"]) == ("NOT_COMPARABLE", [key], None)
    for key, value in (("observation_class", "SELF_REPORTED"), ("evidence_sha256", "xyz"), ("evidence_ref", "")):
        with pytest.raises(cr.CostInputError):
            cr.pricing_basis(AUTHENTIC, estimate, _observation("0.007", **{key: value}))
    assert cr.pricing_basis(AUTHENTIC, estimate)["status"] == "PROVISIONAL_SCENARIO"


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(schema="wrong"),
    lambda r: r.pop("registry_version"),
    lambda r: r.update(authentic_observation_classes=[]),
    lambda r: r["components"][0].update(attribution="SOMETIMES"),
    lambda r: r["components"][-1].pop("allocation_basis"),
    lambda r: r["components"][0].update(divisor=0),
    lambda r: r["components"][0].update(applies_when={"execution_locus": ["ON_A_LAPTOP"]}),
    lambda r: r["components"][0].pop("covers"),
])
def test_malformed_registry_fails_closed(mutate):
    registry = copy.deepcopy(REGISTRY)
    mutate(registry)
    with pytest.raises(cr.CostInputError):
        cr.validate_registry(registry)
