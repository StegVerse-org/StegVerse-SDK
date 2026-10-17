"""Cost-derived tier pricing for the StegVerse governance product.

Prices are derived from the ecosystem's existing task-class cost-basis records
(stegverse.worker-runtime-cost-basis/v0.1) converted to USD by a cited unit
rate card, then positioned against cited market comparables. Every USD figure
must carry an https source and an observation time (the same rule TV/TVC's
provider cost binding applies); a missing or uncited rate yields
UNKNOWN_RATE_NOT_SOURCED instead of an invented price.

Each task class's unit cost follows the owner pricing invariant
(stegverse/cost_registry.py): C_pricing = max(C_estimated,
C_authentically_observed), both operands preserved. A tier is PRICED only on a
complete basis; with one operand it is a labelled PROVISIONAL_SCENARIO, never a
final rate. No price is approved here.

Standard library only. The output is a pricing candidate: it grants no
entitlement, credential or execution authority (TV/TVC issues entitlements).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from typing import Any, Mapping, Sequence

COST_BASIS_SCHEMA = "stegverse.worker-runtime-cost-basis/v0.1"
RATE_CARD_SCHEMA = "stegverse.unit-rate-card.v1"
MARKET_SCHEMA = "stegverse.market-comparables.v1"
POLICY_SCHEMA = "stegverse.tier-pricing-policy.v1"
OBSERVATION_SET_SCHEMA = "stegverse.cost-observation-set.v1"
REPORT_SCHEMA = "stegverse.tier-pricing-candidate.v1"
GB = Decimal(10**9)
CENT = Decimal("0.01")
# cost_estimate field -> (rate card key, divisor). Recovery is priced as re-run compute.
COMPONENTS = {
    "compute_units": ("compute_unit", Decimal(1)),
    "failure_recovery_units": ("compute_unit", Decimal(1)),
    "recovery_actions": ("compute_unit", Decimal(1)),
    "storage_bytes": ("storage_gb", GB),
    "network_bytes": ("network_gb", GB),
}


class PricingInputError(ValueError):
    pass


def _cost_registry():
    """The sibling module, also when this file runs as a script with nothing installed."""
    try:
        from stegverse import cost_registry
        return cost_registry
    except ImportError:
        spec = importlib.util.spec_from_file_location(
            "stegverse_cost_registry", Path(__file__).resolve().with_name("cost_registry.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def _decimal(value: Any, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise PricingInputError(f"{field}: number required")
    try:
        result = Decimal(str(value))
    except ArithmeticError as exc:
        raise PricingInputError(f"{field}: invalid number") from exc
    if not result.is_finite() or result < 0:
        raise PricingInputError(f"{field}: nonnegative finite number required")
    return result


def _cited(entry: Mapping[str, Any], field: str) -> None:
    source, observed_at = entry.get("source"), entry.get("observed_at")
    if not isinstance(source, str) or not source.startswith("https://"):
        raise PricingInputError(f"{field}: https source required")
    if not isinstance(observed_at, str) or not observed_at:
        raise PricingInputError(f"{field}: observed_at required")


def _schema(document: Any, expected: str) -> Mapping[str, Any]:
    if not isinstance(document, Mapping) or document.get("schema") != expected:
        raise PricingInputError(f"schema {expected} required")
    return document


def rate_card_rates(rate_card: Any) -> dict[str, Decimal]:
    card = _schema(rate_card, RATE_CARD_SCHEMA)
    if not isinstance(card.get("compute_unit_definition"), str) or not card["compute_unit_definition"]:
        raise PricingInputError("compute_unit_definition required: the cost basis does not define a compute unit")
    rates = card.get("rates")
    if not isinstance(rates, Mapping):
        raise PricingInputError("rates object required")
    result = {}
    for key, entry in rates.items():
        if not isinstance(entry, Mapping):
            raise PricingInputError(f"rates.{key}: object required")
        _cited(entry, f"rates.{key}")
        result[key] = _decimal(entry.get("usd"), f"rates.{key}.usd")
    return result


def action_cost(record: Any, rates: Mapping[str, Decimal]) -> dict[str, Any]:
    """USD cost of one action of a task class, or UNKNOWN_RATE_NOT_SOURCED."""
    basis = _schema(record, COST_BASIS_SCHEMA)
    task_class = basis.get("task_class")
    if not isinstance(task_class, str) or not task_class:
        raise PricingInputError("task_class required")
    estimate = basis.get("cost_estimate")
    if not isinstance(estimate, Mapping):
        raise PricingInputError(f"{task_class}: cost_estimate required")
    total, missing = Decimal(0), set()
    for field, (rate_key, divisor) in COMPONENTS.items():
        value = estimate.get(field)
        if value is None:
            continue
        quantity = _decimal(value, f"{task_class}.{field}")
        if quantity == 0:
            continue
        if rate_key not in rates:
            missing.add(rate_key)
            continue
        total += quantity / divisor * rates[rate_key]
    if estimate.get("external_cost_usd") is not None:
        total += _decimal(estimate["external_cost_usd"], f"{task_class}.external_cost_usd")
    samples = basis.get("sample_count")
    return {
        "task_class": task_class,
        "status": "UNKNOWN_RATE_NOT_SOURCED" if missing else "PRICED",
        "missing_rates": sorted(missing),
        "usd_per_action": None if missing else str(total),
        # A sample_count of 0 (or absent) is a source-declared estimate, not an observed measurement.
        "evidence": "SAMPLED_COST_BASIS" if isinstance(samples, int) and samples > 0 else "PROVISIONAL_ESTIMATE",
    }


def market_median(market: Any) -> Decimal | None:
    if market is None:
        return None
    comparables = _schema(market, MARKET_SCHEMA).get("comparables")
    if not isinstance(comparables, list):
        raise PricingInputError("comparables list required")
    prices = []
    for index, entry in enumerate(comparables):
        if not isinstance(entry, Mapping):
            raise PricingInputError(f"comparables[{index}]: object required")
        _cited(entry, f"comparables[{index}]")
        prices.append(_decimal(entry.get("usd_per_action"), f"comparables[{index}].usd_per_action"))
    return statistics.median(prices) if prices else None


def _cents_up(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_CEILING))


def _observation_set(observations: Any) -> tuple[list[str], Mapping[str, Any]]:
    if observations is None:
        return ["NONE_SUPPLIED"], {}
    doc = _schema(observations, OBSERVATION_SET_SCHEMA)
    classes = doc.get("authentic_observation_classes")
    entries = doc.get("observations")
    if not isinstance(classes, list) or not classes or not isinstance(entries, Mapping):
        raise PricingInputError("observation set: authentic_observation_classes list and observations map required")
    return classes, entries


def derive_pricing(cost_basis: Sequence[Any], rate_card: Any, policy: Any, market: Any = None,
                   observations: Any = None) -> dict[str, Any]:
    rates = rate_card_rates(rate_card)
    policy = _schema(policy, POLICY_SCHEMA)
    version = policy.get("cost_basis_version")
    if not isinstance(version, str) or not version:
        raise PricingInputError("cost_basis_version required: estimates and observations compare only within one version")
    authentic, observed_by_class = _observation_set(observations)
    registry = _cost_registry()
    margin = _decimal(policy.get("target_gross_margin"), "target_gross_margin")
    if margin >= 1:
        raise PricingInputError("target_gross_margin must be below 1")
    plans = policy.get("plans")
    if not isinstance(plans, list) or not plans:
        raise PricingInputError("plans list required")
    referenced = {c for plan in plans if isinstance(plan, Mapping) and isinstance(plan.get("task_classes"), list)
                  for c in plan["task_classes"] if isinstance(c, str)}
    # Only records a plan prices are evaluated (and must be well formed); unrelated records are ignored.
    by_class: dict[str, list[Any]] = {}
    for record in cost_basis:
        if isinstance(record, Mapping) and record.get("task_class") in referenced:
            by_class.setdefault(record["task_class"], []).append(record)
    duplicated = sorted(c for c, records in by_class.items() if len(records) > 1)
    if duplicated:
        raise PricingInputError(f"duplicate cost basis for task classes {duplicated}")
    costs = {c: action_cost(records[0], rates) for c, records in by_class.items()}
    for task_class, cost in costs.items():
        estimate = {"scope_id": task_class, "currency": "USD", "unit": "action", "cost_basis_version": version,
                    "amount": cost["usd_per_action"] if cost["status"] == "PRICED" else "UNKNOWN"}
        try:
            cost["pricing_basis"] = registry.pricing_basis(authentic, estimate, observed_by_class.get(task_class))
        except registry.CostInputError as exc:
            raise PricingInputError(f"{task_class}: {exc}") from exc
    median = market_median(market)
    tiers = []
    for index, plan in enumerate(plans):
        if not isinstance(plan, Mapping) or not isinstance(plan.get("name"), str):
            raise PricingInputError(f"plans[{index}]: name required")
        included = _decimal(plan.get("included_actions"), f"plans[{index}].included_actions")
        classes = plan.get("task_classes")
        if not isinstance(classes, list) or not classes or not all(isinstance(c, str) for c in classes):
            raise PricingInputError(f"plans[{index}].task_classes: non-empty list of task classes required")
        absent = sorted(set(classes) - set(costs))
        unpriced = sorted(c for c in classes if c in costs
                          and costs[c]["pricing_basis"]["status"] not in ("COMPLETE_BASIS", "PROVISIONAL_SCENARIO"))
        tier = {"name": plan["name"], "included_actions": str(included), "task_classes": sorted(classes)}
        if absent or unpriced:
            tier.update(status="UNKNOWN_RATE_NOT_SOURCED" if unpriced and not absent else "UNKNOWN_COST_BASIS",
                        absent_cost_basis=absent, unpriced_task_classes=unpriced,
                        usd_per_action=None, usd_per_period=None, market_position="NOT_EVALUATED")
            tiers.append(tier)
            continue
        # Conservative: price every included action at the costliest class the plan admits.
        unit_cost = max(Decimal(costs[c]["pricing_basis"]["c_pricing"]) for c in classes)
        complete = all(costs[c]["pricing_basis"]["status"] == "COMPLETE_BASIS" for c in classes)
        floor = unit_cost / (1 - margin)
        if median is None:
            price, position = floor, "NO_MARKET_EVIDENCE"
        elif median >= floor:
            price, position = median, "AT_MARKET_MEDIAN"
        else:
            price, position = floor, "ABOVE_MARKET_COST_BOUND"
        tier.update(status="PRICED" if complete else "PROVISIONAL_SCENARIO", unit_cost_usd=str(unit_cost), cost_floor_usd_per_action=str(floor),
                    usd_per_action=str(price), usd_per_period=_cents_up(price * included),
                    market_position=position,
                    evidence="PROVISIONAL_ESTIMATE" if any(costs[c]["evidence"] != "SAMPLED_COST_BASIS" for c in classes)
                    else "SAMPLED_COST_BASIS")
        tiers.append(tier)
    statuses = {t["status"] for t in tiers}
    status = ("PRICED" if statuses == {"PRICED"}
              else "PROVISIONAL" if statuses <= {"PRICED", "PROVISIONAL_SCENARIO"} else "INCOMPLETE")
    extra = {}
    if status == "PROVISIONAL":
        unobserved = sorted(c for c, cost in costs.items() if cost["pricing_basis"]["status"] == "PROVISIONAL_SCENARIO")
        extra["actionable_disposition"] = _actionable(
            "PRICING_BASIS_PROVISIONAL",
            f"C_pricing = max(C_estimated, C_authentically_observed) has one operand UNKNOWN for {unobserved}",
            "supply an authentically observed cost (receipt-backed, same scope, currency, unit and cost_basis_version) "
            "and a complete estimate for each listed task class")
    elif status == "INCOMPLETE":
        unpriced = [t["name"] for t in tiers if t["status"] not in ("PRICED", "PROVISIONAL_SCENARIO")]
        missing = sorted({r for c in costs.values() for r in c["missing_rates"]})
        absent = sorted({c for t in tiers for c in t.get("absent_cost_basis", [])})
        extra["actionable_disposition"] = _actionable(
            "PRICING_INCOMPLETE",
            f"tiers {unpriced} lack a cited rate {missing}, a cost basis {absent} or a comparable observation",
            "add a cited rate card entry for each missing rate, a cost-basis record for each absent task class, "
            "or an observation in the same cost_basis_version")
    return {
        **extra,
        "schema": REPORT_SCHEMA,
        "status": status,
        "cost_basis_version": version,
        "compute_unit_definition": rate_card["compute_unit_definition"],
        "target_gross_margin": str(margin),
        "market_median_usd_per_action": None if median is None else str(median),
        "action_costs": [costs[k] for k in sorted(costs)],
        "tiers": tiers,
        "authority": {"final_price_approved": False, "entitlement_issued": False, "credential_issued": False,
                      "execution_authorized": False},
    }


def _actionable(code: str, predicate: str, repair: str) -> dict[str, str]:
    """The six fields every non-PRICED result carries (ecosystem disposition invariant)."""
    return {
        "failure_code": code,
        "failed_predicate": predicate,
        "required_evidence_or_repair": repair,
        "retry_entrypoint": "stegverse/tier_pricing.py::main",
        "owning_existing_goal": "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001",
        "next_attempt": "re-run with the corrected inputs; no price or tier is presumed until then",
    }


def _read(path: str | None):
    return None if path is None else json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stegverse-tier-pricing", description=__doc__.splitlines()[0])
    parser.add_argument("--cost-basis-dir", required=True, help="Directory of worker-runtime cost-basis JSON records")
    parser.add_argument("--rate-card", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--market", help="Cited market comparables (optional)")
    parser.add_argument("--observations", help="Authentically observed costs per task class (optional)")
    parser.add_argument("--output", help="Write the JSON report here (default: stdout)")
    args = parser.parse_args(argv)
    records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(args.cost_basis_dir).glob("*.json"))]
    try:
        report = derive_pricing(records, _read(args.rate_card), _read(args.policy), _read(args.market),
                                _read(args.observations))
    except PricingInputError as exc:
        report = {"schema": REPORT_SCHEMA, "status": "FAIL_CLOSED", "error": str(exc),
                  "actionable_disposition": _actionable("PRICING_INPUT_INVALID", str(exc),
                                                        "correct the named input; every USD figure needs an https source and observed_at")}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["status"] == "PRICED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
