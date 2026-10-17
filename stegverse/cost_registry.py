"""Versioned cost-component registry and the owner pricing invariant.

A registry declares the cost components that can apply to an action: what
quantity each consumes, which cited rate prices it, in which execution context
it applies (internal-first StegVerse execution or an externally billed
provider), whether the cost is direct or a shared cost allocated across
attributable outcomes, and which resource it covers so that no resource is
counted twice.

`estimate` prices one execution context against the registry and cited rate
cards. An applicable component whose quantity, rate or currency conversion is
unknown leaves the estimate INCOMPLETE; UNKNOWN is never priced as zero.

`pricing_basis` applies the owner invariant, for comparable scope, currency,
unit and cost-basis version:

    C_pricing = max(C_estimated, C_authentically_observed)

Both operands and the selected basis are preserved. With only one operand
available the result is a labelled PROVISIONAL_SCENARIO, never a final rate.
Cost calculation, commercial price and execution authority stay separate: no
result here approves a price, issues a TV/TVC entitlement or an InTr ALLOW.
Standard library only.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping, Sequence

REGISTRY_SCHEMA = "stegverse.cost-component-registry.v1"
RATE_CARD_SCHEMA = "stegverse.cost-rate-card.v1"
OBSERVATION_SCHEMA = "stegverse.cost-observation.v1"
ESTIMATE_SCHEMA = "stegverse.cost-estimate.v1"
BASIS_SCHEMA = "stegverse.pricing-cost-basis.v1"
UNKNOWN = "UNKNOWN"
EXECUTION_LOCI = ("INTERNAL", "EXTERNAL_PROVIDER")
ATTRIBUTIONS = ("DIRECT", "SHARED")
NO_AUTHORITY = {"final_price_approved": False, "entitlement_issued": False, "execution_authorized": False}


class CostInputError(ValueError):
    pass


def _number(value: Any, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise CostInputError(f"{field}: number required")
    try:
        result = Decimal(str(value))
    except ArithmeticError as exc:
        raise CostInputError(f"{field}: invalid number") from exc
    if not result.is_finite() or result < 0:
        raise CostInputError(f"{field}: nonnegative finite number required")
    return result


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CostInputError(f"{field}: non-empty string required")
    return value


def _cited(entry: Mapping[str, Any], field: str) -> None:
    if not str(entry.get("source", "")).startswith("https://"):
        raise CostInputError(f"{field}: https source required")
    _text(entry.get("observed_at"), f"{field}.observed_at")


def _schema(document: Any, expected: str, field: str) -> Mapping[str, Any]:
    if not isinstance(document, Mapping) or document.get("schema") != expected:
        raise CostInputError(f"{field}: schema {expected} required")
    return document


def validate_registry(registry: Any) -> Mapping[str, Any]:
    """Structural checks that do not depend on an execution context."""
    reg = _schema(registry, REGISTRY_SCHEMA, "registry")
    _text(reg.get("registry_version"), "registry.registry_version")
    _text(reg.get("currency"), "registry.currency")
    classes = reg.get("authentic_observation_classes")
    if not isinstance(classes, list) or not classes or not all(isinstance(c, str) and c for c in classes):
        raise CostInputError("registry.authentic_observation_classes: non-empty list required")
    components = reg.get("components")
    if not isinstance(components, list) or not components:
        raise CostInputError("registry.components: non-empty list required")
    seen = set()
    for index, component in enumerate(components):
        field = f"registry.components[{index}]"
        if not isinstance(component, Mapping):
            raise CostInputError(f"{field}: object required")
        cid = _text(component.get("component_id"), f"{field}.component_id")
        if cid in seen:
            raise CostInputError(f"{field}: duplicate component_id {cid}")
        seen.add(cid)
        for key in ("quantity_field", "rate_key", "covers"):
            _text(component.get(key), f"{field}.{key}")
        if "divisor" in component and _number(component["divisor"], f"{field}.divisor") == 0:
            raise CostInputError(f"{field}.divisor: must be positive")
        if component.get("attribution") not in ATTRIBUTIONS:
            raise CostInputError(f"{field}.attribution: one of {ATTRIBUTIONS}")
        if component["attribution"] == "SHARED":
            _text(component.get("allocation_basis"), f"{field}.allocation_basis")
        applies = component.get("applies_when", {})
        if not isinstance(applies, Mapping) or not all(
                isinstance(v, list) and v and all(isinstance(x, str) for x in v) for v in applies.values()):
            raise CostInputError(f"{field}.applies_when: map of non-empty string lists required")
        if any(locus not in EXECUTION_LOCI for locus in applies.get("execution_locus", [])):
            raise CostInputError(f"{field}.applies_when.execution_locus: values in {EXECUTION_LOCI}")
    return reg


def _rates(rate_cards: Sequence[Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    rates: dict[str, dict[str, Any]] = {}
    fx: dict[str, dict[str, Any]] = {}
    for index, card in enumerate(rate_cards):
        card = _schema(card, RATE_CARD_SCHEMA, f"rate_cards[{index}]")
        card_id = _text(card.get("rate_card_id"), f"rate_cards[{index}].rate_card_id")
        for key, entry in (card.get("rates") or {}).items():
            field = f"{card_id}.rates.{key}"
            if not isinstance(entry, Mapping):
                raise CostInputError(f"{field}: object required")
            _cited(entry, field)
            if key in rates:
                raise CostInputError(f"{field}: rate key defined by more than one rate card")
            rates[key] = {"amount": _number(entry.get("amount"), f"{field}.amount"),
                          "currency": _text(entry.get("currency"), f"{field}.currency"),
                          "source": entry["source"], "rate_card_id": card_id}
        for pair, entry in (card.get("fx") or {}).items():
            field = f"{card_id}.fx.{pair}"
            if not isinstance(entry, Mapping) or pair.count("->") != 1:
                raise CostInputError(f"{field}: 'FROM->TO' object required")
            _cited(entry, field)
            rate = _number(entry.get("rate"), f"{field}.rate")
            if rate == 0:
                raise CostInputError(f"{field}.rate: must be positive")
            fx[pair] = {"rate": rate, "source": entry["source"]}
    return rates, fx


def _applies(component: Mapping[str, Any], context: Mapping[str, Any]) -> bool:
    return all(context.get(key) in values for key, values in component.get("applies_when", {}).items())


def estimate(registry: Any, rate_cards: Sequence[Any], context: Any) -> dict[str, Any]:
    """Estimated cost of one action in one execution context (C_estimated)."""
    reg = validate_registry(registry)
    if not isinstance(context, Mapping):
        raise CostInputError("context: object required")
    _text(context.get("scope_id"), "context.scope_id")
    if context.get("execution_locus") not in EXECUTION_LOCI:
        raise CostInputError(f"context.execution_locus: one of {EXECUTION_LOCI}")
    quantities = context.get("quantities") or {}
    allocation = context.get("allocation") or {}
    if not isinstance(quantities, Mapping) or not isinstance(allocation, Mapping):
        raise CostInputError("context.quantities and context.allocation: objects required")
    rates, fx = _rates(rate_cards)
    applicable = [c for c in reg["components"] if _applies(c, context)]
    covered: dict[str, str] = {}
    for component in applicable:
        prior = covered.setdefault(component["covers"], component["component_id"])
        if prior != component["component_id"]:
            raise CostInputError(f"double counting: {prior} and {component['component_id']} "
                                 f"both cover {component['covers']} in this context")
    if context["execution_locus"] == "EXTERNAL_PROVIDER" and applicable:
        # Externally billed calls are attributed to a governed outcome, never silently omitted.
        _text(context.get("attributable_outcome_id"), "context.attributable_outcome_id (external provider cost)")
    currency = reg["currency"]
    lines, unknown, total = [], [], Decimal(0)
    for component in applicable:
        cid = component["component_id"]
        line = {"component_id": cid, "covers": component["covers"], "attribution": component["attribution"]}
        raw = quantities.get(component["quantity_field"], UNKNOWN)
        rate = rates.get(component["rate_key"])
        reason = None
        if raw == UNKNOWN:
            reason = f"quantity {component['quantity_field']} UNKNOWN"
        elif rate is None:
            reason = f"rate {component['rate_key']} not cited"
        if reason is None:
            amount = _number(raw, f"context.quantities.{component['quantity_field']}")
            amount = amount / _number(component.get("divisor", 1), f"{cid}.divisor") * rate["amount"]
            if rate["currency"] != currency:
                conversion = fx.get(f"{rate['currency']}->{currency}")
                if conversion is None:
                    reason = f"no cited fx {rate['currency']}->{currency}"
                else:
                    amount *= conversion["rate"]
                    line["fx_source"] = conversion["source"]
        if reason is None and component["attribution"] == "SHARED":
            share = allocation.get(component["allocation_basis"], UNKNOWN)
            if share == UNKNOWN or _number(share, f"context.allocation.{component['allocation_basis']}") == 0:
                reason = f"allocation basis {component['allocation_basis']} UNKNOWN"
            else:
                amount /= _number(share, f"context.allocation.{component['allocation_basis']}")
        if reason is None:
            line.update(amount=str(amount), rate_source=rate["source"], rate_card_id=rate["rate_card_id"])
            total += amount
        else:
            line.update(amount=UNKNOWN, reason=reason)
            unknown.append(cid)
        lines.append(line)
    return {
        "schema": ESTIMATE_SCHEMA,
        "scope_id": context["scope_id"],
        "execution_locus": context["execution_locus"],
        "attributable_outcome_id": context.get("attributable_outcome_id"),
        "cost_basis_version": reg["registry_version"],
        "currency": currency,
        "unit": reg.get("comparison_unit", "action"),
        "status": "INCOMPLETE" if unknown else "COMPLETE",
        "amount": UNKNOWN if unknown else str(total),
        "unknown_components": unknown,
        "components": lines,
        "authority": dict(NO_AUTHORITY),
    }


def observed(authentic_classes: Sequence[str], observation: Any) -> dict[str, Any]:
    """An authentically observed cost (C_authentically_observed), or UNKNOWN."""
    if observation is None:
        return {"amount": UNKNOWN, "reason": "no observation supplied"}
    obs = _schema(observation, OBSERVATION_SCHEMA, "observation")
    result = {key: obs.get(key) for key in ("scope_id", "currency", "unit", "cost_basis_version")}
    if obs.get("amount", UNKNOWN) == UNKNOWN:
        return {**result, "amount": UNKNOWN, "reason": "observation UNKNOWN_NOT_AUTHENTICALLY_OBSERVED"}
    if obs.get("observation_class") not in authentic_classes:
        raise CostInputError(f"observation.observation_class: not one of the authentic classes {list(authentic_classes)}")
    _text(obs.get("evidence_ref"), "observation.evidence_ref")
    digest = _text(obs.get("evidence_sha256"), "observation.evidence_sha256")
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise CostInputError("observation.evidence_sha256: 64 lowercase hex characters required")
    return {**result, "amount": str(_number(obs["amount"], "observation.amount")),
            "observation_class": obs["observation_class"], "evidence_ref": obs["evidence_ref"],
            "evidence_sha256": digest}


def pricing_basis(authentic_classes: Sequence[str], estimate_result: Mapping[str, Any],
                  observation: Any = None) -> dict[str, Any]:
    """C_pricing = max(C_estimated, C_authentically_observed), both operands preserved.

    `authentic_classes` is the registry's authentic_observation_classes.
    """
    if not authentic_classes:
        raise CostInputError("authentic observation classes required")
    estimated = {key: estimate_result.get(key) for key in ("scope_id", "currency", "unit", "cost_basis_version")}
    estimated["amount"] = estimate_result.get("amount", UNKNOWN)
    obs = observed(authentic_classes, observation)
    basis: dict[str, Any] = {"schema": BASIS_SCHEMA, "estimated": estimated, "observed": obs,
                             "invariant": "C_pricing = max(C_estimated, C_authentically_observed)",
                             "authority": dict(NO_AUTHORITY)}
    if obs["amount"] != UNKNOWN:
        mismatched = [key for key in ("scope_id", "currency", "unit", "cost_basis_version")
                      if obs.get(key) != estimated.get(key)]
        if mismatched:
            return {**basis, "status": "NOT_COMPARABLE", "mismatched": mismatched, "c_pricing": None,
                    "selected_basis": None, "final": False}
    known = {name: Decimal(op["amount"]) for name, op in (("ESTIMATED", estimated), ("OBSERVED", obs))
             if op["amount"] != UNKNOWN}
    if not known:
        return {**basis, "status": "INCOMPLETE", "c_pricing": None, "selected_basis": None, "final": False}
    if len(known) == 1:
        (name, amount), = known.items()
        return {**basis, "status": "PROVISIONAL_SCENARIO", "c_pricing": str(amount),
                "selected_basis": f"{name}_ONLY", "final": False}
    selected = ("EQUAL" if known["ESTIMATED"] == known["OBSERVED"]
                else max(known, key=known.__getitem__))
    return {**basis, "status": "COMPLETE_BASIS", "c_pricing": str(max(known.values())),
            "selected_basis": selected, "final": False}
