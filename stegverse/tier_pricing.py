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
# cost_estimate fields that are not costs; they never make a basis incomplete.
NON_COST_FIELDS = {"latency_ms"}
# A record may declare how each cost dimension stands. UNKNOWN on a required dimension, like a
# declared non-zero quantity the rate card does not model, keeps the basis a machine-only subtotal.
DIMENSION_DISPOSITIONS = ("MODELED", "NOT_APPLICABLE", "KNOWN_ZERO", "UNKNOWN")


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
    total, missing, unmodeled = Decimal(0), set(), []
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
    # A declared non-zero quantity the rate card does not model is cost the subtotal leaves out.
    for field in sorted(estimate):
        if field in COMPONENTS or field == "external_cost_usd" or field in NON_COST_FIELDS:
            continue
        value = estimate.get(field)
        if value is not None and _decimal(value, f"{task_class}.{field}") != 0:
            unmodeled.append(field)
    dispositions = basis.get("cost_dimension_dispositions") or {}
    if not isinstance(dispositions, Mapping):
        raise PricingInputError(f"{task_class}: cost_dimension_dispositions must be an object")
    for field, disposition in sorted(dispositions.items()):
        if disposition not in DIMENSION_DISPOSITIONS:
            raise PricingInputError(f"{task_class}.cost_dimension_dispositions.{field}: one of {list(DIMENSION_DISPOSITIONS)}")
        if disposition == "UNKNOWN" and field not in unmodeled:
            unmodeled.append(field)
        if disposition == "MODELED":
            # MODELED is a claim with two parts: the rate card maps this field to a cost, and a
            # quantity is present. A declared MODELED null, or MODELED on a field nothing prices,
            # is a contradiction, not a complete dimension.
            if field not in COMPONENTS and field != "external_cost_usd":
                raise PricingInputError(
                    f"{task_class}.cost_dimension_dispositions.{field}: MODELED but no cost mapping prices this field; "
                    "declare it UNKNOWN, NOT_APPLICABLE or KNOWN_ZERO")
            if estimate.get(field) is None:
                raise PricingInputError(
                    f"{task_class}.cost_dimension_dispositions.{field}: MODELED but the quantity is null; "
                    "supply the quantity, or declare NOT_APPLICABLE or KNOWN_ZERO")
        if disposition in ("KNOWN_ZERO", "NOT_APPLICABLE"):
            value = estimate.get(field)
            if value is not None and _decimal(value, f"{task_class}.{field}") != 0:
                raise PricingInputError(
                    f"{task_class}.cost_dimension_dispositions.{field}: declared {disposition} but the quantity is non-zero")
    samples = basis.get("sample_count")
    status = "UNKNOWN_RATE_NOT_SOURCED" if missing else "MACHINE_SUBTOTAL_ONLY" if unmodeled else "PRICED"
    return {
        "task_class": task_class,
        "status": status,
        "missing_rates": sorted(missing),
        # The modeled machine cost, kept apart from any complete cost claim.
        "machine_subtotal_usd_per_action": None if missing else str(total),
        "unmodeled_cost_dimensions": sorted(unmodeled),
        "usd_per_action": str(total) if status == "PRICED" else None,
        # A sample_count of 0 (or absent) is a source-declared estimate, not an observed measurement.
        "evidence": "SAMPLED_COST_BASIS" if isinstance(samples, int) and samples > 0 else "PROVISIONAL_ESTIMATE",
    }


# FLAT: a point price. STARTING_AT: a lower bound (the true price is at least p). RANGE: a published
# low and high (usd_per_action is the low, usd_per_action_high the high); the true price is within.
PRICE_BASES = ("FLAT", "STARTING_AT", "RANGE")
# A comparable's role. Only governance anchors enter the median; an adjacent reference is kept
# as context (its observation is preserved, its price is never a statistic).
COMPARABLE_ROLES = ("GOVERNANCE_ANCHOR", "ADJACENT_REFERENCE")
MARKET_CURRENCY = "USD"


def market_median(market: Any) -> dict[str, Any] | None:
    """Bounds on the market median. A STARTING_AT price p means the true price is at least p; a
    RANGE [p, q] means it is within. at_least is the median with every bounded price at its low,
    at_most the median at every high (None when unbounded); exact only when the two agree.
    """
    if market is None:
        return None
    comparables = _schema(market, MARKET_SCHEMA).get("comparables")
    if not isinstance(comparables, list):
        raise PricingInputError("comparables list required")
    low, high, adjacent = [], [], 0
    for index, entry in enumerate(comparables):
        if not isinstance(entry, Mapping):
            raise PricingInputError(f"comparables[{index}]: object required")
        _cited(entry, f"comparables[{index}]")
        price = _decimal(entry.get("usd_per_action"), f"comparables[{index}].usd_per_action")
        basis = entry.get("price_basis", "FLAT")
        if basis not in PRICE_BASES:
            raise PricingInputError(f"comparables[{index}].price_basis must be one of {list(PRICE_BASES)}")
        # usd_per_action is a USD figure by name; a comparable declaring another currency, with
        # no authorized conversion provenance in scope, cannot enter the statistic.
        if entry.get("currency", MARKET_CURRENCY) != MARKET_CURRENCY:
            raise PricingInputError(f"comparables[{index}].currency must be {MARKET_CURRENCY}")
        role = entry.get("role", "GOVERNANCE_ANCHOR")
        if role not in COMPARABLE_ROLES:
            raise PricingInputError(f"comparables[{index}].role must be one of {list(COMPARABLE_ROLES)}")
        if role == "ADJACENT_REFERENCE":
            adjacent += 1
            continue
        if basis == "RANGE":
            upper = _decimal(entry.get("usd_per_action_high"), f"comparables[{index}].usd_per_action_high")
            if upper < price:
                raise PricingInputError(f"comparables[{index}]: usd_per_action_high must be at least usd_per_action")
        low.append(price)
        high.append(Decimal("Infinity") if basis == "STARTING_AT" else upper if basis == "RANGE" else price)
    if not low:
        return {"at_least": None, "at_most": None, "exact": False, "anchors": 0,
                "adjacent_references": adjacent, "anchor_range": None}
    at_least, at_most = statistics.median(low), statistics.median(high)
    return {"at_least": at_least, "at_most": None if at_most.is_infinite() else at_most,
            "exact": at_least == at_most, "anchors": len(low), "adjacent_references": adjacent,
            "anchor_range": (min(low), max(low))}


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
    # How many governance anchors a market median needs before it may set a price. Below it the
    # anchors are context only, and the cost floor is the only figure the formula establishes.
    minimum_anchors = policy.get("minimum_market_anchors", 1)
    if not isinstance(minimum_anchors, int) or minimum_anchors < 1:
        raise PricingInputError("minimum_market_anchors must be a positive integer")
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
                    # A machine-only subtotal is a lower bound on the estimate, never a complete cost.
                    "amount": cost["usd_per_action"] if cost["status"] == "PRICED"
                    else cost["machine_subtotal_usd_per_action"] if cost["status"] == "MACHINE_SUBTOTAL_ONLY"
                    else "UNKNOWN"}
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
                        usd_per_action=None, usd_per_period=None, market_position="NOT_EVALUATED", quote_ready=False)
            tiers.append(tier)
            continue
        # Conservative: price every included action at the costliest class the plan admits.
        unit_cost = max(Decimal(costs[c]["pricing_basis"]["c_pricing"]) for c in classes)
        unmodeled = sorted({d for c in classes for d in costs[c]["unmodeled_cost_dimensions"]})
        # A basis with unmodeled cost dimensions is never complete, whatever was observed.
        complete = not unmodeled and all(costs[c]["pricing_basis"]["status"] == "COMPLETE_BASIS" for c in classes)
        floor = unit_cost / (1 - margin)
        # A lower-bound median is never an exact match, and never caps the quote: the floor is
        # above the market only when it exceeds the median's upper bound.
        if median is None or median["anchors"] == 0:
            price, position = floor, "NO_MARKET_EVIDENCE"
        elif median["anchors"] < minimum_anchors:
            price, position = floor, "MARKET_ANCHORS_INSUFFICIENT"
        elif median["at_least"] >= floor:
            price = median["at_least"]
            position = "AT_MARKET_MEDIAN" if median["exact"] else "AT_MARKET_MEDIAN_LOWER_BOUND"
        elif median["at_most"] is not None and median["at_most"] < floor:
            price, position = floor, "ABOVE_MARKET_COST_BOUND"
        else:
            price, position = floor, "WITHIN_MARKET_MEDIAN_RANGE"
        tier.update(status="PRICED" if complete else "PROVISIONAL_SCENARIO", unit_cost_usd=str(unit_cost), cost_floor_usd_per_action=str(floor),
                    usd_per_action=str(price), usd_per_period=_cents_up(price * included),
                    market_position=position,
                    cost_completeness="MACHINE_SUBTOTAL_ONLY" if unmodeled else "ALL_DECLARED_DIMENSIONS_MODELED",
                    unmodeled_cost_dimensions=unmodeled,
                    # A figure is quote-ready only when the basis is complete and any market
                    # statistic it rests on has enough governance anchors.
                    quote_ready=bool(complete and position != "MARKET_ANCHORS_INSUFFICIENT"),
                    evidence="PROVISIONAL_ESTIMATE" if any(costs[c]["evidence"] != "SAMPLED_COST_BASIS" for c in classes)
                    else "SAMPLED_COST_BASIS")
        tiers.append(tier)
    statuses = {t["status"] for t in tiers}
    status = ("PRICED" if statuses == {"PRICED"}
              else "PROVISIONAL" if statuses <= {"PRICED", "PROVISIONAL_SCENARIO"} else "INCOMPLETE")
    extra = {}
    if status == "PROVISIONAL":
        unobserved = sorted(c for c, cost in costs.items() if cost["pricing_basis"]["status"] == "PROVISIONAL_SCENARIO")
        unmodeled = {c: cost["unmodeled_cost_dimensions"] for c, cost in costs.items() if cost["unmodeled_cost_dimensions"]}
        extra["actionable_disposition"] = _actionable(
            "PRICING_BASIS_PROVISIONAL",
            f"C_pricing = max(C_estimated, C_authentically_observed) has one operand UNKNOWN for {unobserved}"
            + (f"; the estimate is a machine-only subtotal, unmodeled cost dimensions {unmodeled}" if unmodeled else ""),
            "supply an authentically observed cost (receipt-backed, same scope, currency, unit and cost_basis_version) "
            "and a complete estimate for each listed task class"
            + ("; model or cite a rate for each unmodeled dimension, or declare it NOT_APPLICABLE or KNOWN_ZERO" if unmodeled else ""))
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
        "market_median_usd_per_action": str(median["at_least"]) if median and median["exact"] else None,
        "market_median_range_usd_per_action": None if median is None or median["anchors"] == 0 else {
            "at_least": str(median["at_least"]),
            "at_most": None if median["at_most"] is None else str(median["at_most"]),
            "exact": median["exact"]},
        "market_anchors": None if median is None else median["anchors"],
        "market_adjacent_references": None if median is None else median["adjacent_references"],
        "market_anchor_range_usd_per_action": None if median is None or median["anchor_range"] is None else
            {"min": str(median["anchor_range"][0]), "max": str(median["anchor_range"][1])},
        "minimum_market_anchors": minimum_anchors,
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
        "owning_existing_goal": "SDK-COST-DERIVED-TIER-PRICING-001",
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
