"""Roadmap benchmark S4_COST evaluator over cost inputs supplied by reference.

S4_COST (StegVerse-Labs/Site:data/economy/public-release-benchmarks.v1.json) requires an
"authenticated operating-cost sample plus free-to-paid sensitivity and contingency
reserve". This evaluator composes the registered cost-derived pricing goal
(SDK-COST-DERIVED-TIER-PRICING-001, StegVerse-org/StegVerse-SDK#484) instead of repeating
it: the cost basis is ``stegverse.cost_registry.pricing_basis``, so
``C_pricing = max(C_estimated, C_authentically_observed)`` and UNKNOWN is never zero.

Inputs are named in a manifest (schema ``stegverse.s4-cost-benchmark-inputs.v1``) by
reference, ``owner/repo:path@<40-hex revision>`` plus ``sha256``, and the caller supplies
the bytes. Nothing is fetched. Each supplied byte string must hash to its declared digest.
Required inputs: ``cost_component_registry``, ``rate_card``, ``execution_context``,
``cost_observation`` and ``economics_policy``.

Predicates, all evaluated on exact fractions:

* ``AUTHENTICATED_OPERATING_COST_SAMPLE``: the pricing basis is ``COMPLETE_BASIS``, i.e. an
  authentic observation was supplied and is comparable with the estimate;
* ``FREE_TO_PAID_SENSITIVITY``: for every declared conversion rate, period revenue and
  cost are computed; at least one declared rate reaches break-even;
* ``CONTINGENCY_RESERVE``: the declared available reserve covers ``reserve_periods`` of
  period operating cost.

Dispositions: ``ALLOW`` (all three hold), ``DENY`` (inputs complete, a predicate fails,
named), ``FAIL_CLOSED`` (an input is missing, ``INPUT_NOT_SUPPLIED`` naming it, or does not
verify). Every non-ALLOW carries the six fields. ALLOW is research evidence: it grants no
benchmark completion, price approval, entitlement or execution authority; realism needs
owner-accepted inputs and completion stays a Publisher-governed Master Records closure.
Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

MANIFEST_SCHEMA = "stegverse.s4-cost-benchmark-inputs.v1"
POLICY_SCHEMA = "stegverse.s4-cost-economics-policy.v1"
RESULT_SCHEMA = "stegverse.s4-cost-benchmark-result.v1"
BENCHMARK_ID = "S4_COST"
GOAL = "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
PRICING_GOAL = "SDK-COST-DERIVED-TIER-PRICING-001"
RETRY = "python3 -m stegverse.s4_cost_benchmark <manifest.json> --input NAME=PATH ..."
REQUIRED_INPUTS = ("cost_component_registry", "rate_card", "execution_context", "cost_observation", "economics_policy")
PREDICATES = ("AUTHENTICATED_OPERATING_COST_SAMPLE", "FREE_TO_PAID_SENSITIVITY", "CONTINGENCY_RESERVE")
_REF = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+:[^@\s]+@[0-9a-f]{40}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
NO_AUTHORITY = {"benchmark_completion_granted": False, "final_price_approved": False,
                "entitlement_issued": False, "execution_authorized": False}


def _cost_registry():
    try:
        from stegverse import cost_registry
        return cost_registry
    except ImportError:
        spec = importlib.util.spec_from_file_location(
            "stegverse_cost_registry", Path(__file__).resolve().with_name("cost_registry.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def _six(disposition: str, code: str, predicate: str, repair: str, next_attempt: str, **evidence: Any) -> dict[str, Any]:
    return {"schema": RESULT_SCHEMA, "benchmark_id": BENCHMARK_ID, "disposition": disposition,
            "failure_code": code, "failed_predicate": predicate, "required_evidence_or_repair": repair,
            "retry_entrypoint": RETRY, "owning_existing_goal": GOAL, "next_attempt": next_attempt,
            "evidence": evidence, "authority": dict(NO_AUTHORITY)}


class Refused(Exception):
    def __init__(self, result: dict[str, Any]) -> None:
        super().__init__(result["failure_code"])
        self.result = result


def _fail(code: str, predicate: str, repair: str, **evidence: Any) -> Refused:
    return Refused(_six("FAIL_CLOSED", code, predicate, repair, "after the named input is supplied or corrected", **evidence))


def verified_inputs(manifest: Any, supplied: Mapping[str, bytes]) -> dict[str, Any]:
    """Parse each required input from caller-supplied bytes that match the manifest digest."""
    if not isinstance(manifest, Mapping) or manifest.get("schema") != MANIFEST_SCHEMA:
        raise _fail("INPUT_MANIFEST_SCHEMA", f"manifest schema == {MANIFEST_SCHEMA}", "supply an input manifest")
    if manifest.get("benchmark_id") != BENCHMARK_ID:
        raise _fail("INPUT_MANIFEST_BENCHMARK", f"manifest benchmark_id == {BENCHMARK_ID}", "bind the manifest to S4_COST")
    declared = manifest.get("inputs") if isinstance(manifest.get("inputs"), Mapping) else {}
    parsed: dict[str, Any] = {}
    for name in REQUIRED_INPUTS:
        entry = declared.get(name)
        if not isinstance(entry, Mapping):
            raise _fail("INPUT_NOT_SUPPLIED", f"manifest declares input {name}",
                        f"declare {name} as owner/repo:path@revision with its sha256", input=name)
        ref, digest = entry.get("ref"), entry.get("sha256")
        if not (isinstance(ref, str) and _REF.match(ref) and isinstance(digest, str) and _SHA.match(digest)):
            raise _fail("INPUT_REFERENCE_MALFORMED", f"{name} is owner/repo:path@<40-hex revision> with a 64-hex sha256",
                        f"pin {name} to an exact revision and digest", input=name)
        if name not in supplied:
            raise _fail("INPUT_NOT_SUPPLIED", f"caller supplies the bytes of {name} ({ref})",
                        f"pass --input {name}=<path to the bytes of {ref}>", input=name, ref=ref)
        actual = hashlib.sha256(supplied[name]).hexdigest()
        if actual != digest:
            raise _fail("INPUT_DIGEST_MISMATCH", f"sha256({name}) == declared {digest}",
                        f"supply the exact bytes of {ref}", input=name, actual_sha256=actual)
        try:
            parsed[name] = json.loads(supplied[name].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise _fail("INPUT_NOT_JSON", f"{name} is UTF-8 JSON", f"supply {name} as JSON", input=name) from None
    return parsed


def _fraction(value: Any, field: str, *, upper: Fraction | None = None) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise _fail("INPUT_VALUE_INVALID", f"{field} is an integer or decimal string", "write it exactly", field=field)
    try:
        number = Fraction(Decimal(value)) if isinstance(value, str) else Fraction(value)
    except (ArithmeticError, ValueError):
        raise _fail("INPUT_VALUE_INVALID", f"{field} parses exactly", "fix the number", field=field) from None
    if number < 0 or (upper is not None and number > upper):
        raise _fail("INPUT_VALUE_INVALID", f"{field} is within range", "correct the value", field=field)
    return number


def _text(fraction: Fraction) -> str:
    return str(Decimal(fraction.numerator) / Decimal(fraction.denominator)) if fraction.denominator != 1 else str(fraction.numerator)


def evaluate(manifest: Any, supplied: Mapping[str, bytes]) -> dict[str, Any]:
    inputs = verified_inputs(manifest, supplied)
    cr = _cost_registry()
    try:
        registry = inputs["cost_component_registry"]
        estimate = cr.estimate(registry, [inputs["rate_card"]], inputs["execution_context"])
        basis = cr.pricing_basis(registry.get("authentic_observation_classes") or [], estimate, inputs["cost_observation"])
    except cr.CostInputError as exc:
        raise _fail("COST_INPUT_INVALID", "the cost inputs satisfy stegverse.cost_registry", str(exc)) from None
    policy = inputs["economics_policy"]
    if not isinstance(policy, Mapping) or policy.get("schema") != POLICY_SCHEMA:
        raise _fail("INPUT_VALUE_INVALID", f"economics_policy schema == {POLICY_SCHEMA}", "supply the economics policy",
                    input="economics_policy")
    users = _fraction(policy.get("users_per_period"), "users_per_period")
    actions = _fraction(policy.get("actions_per_user_per_period"), "actions_per_user_per_period")
    price = _fraction(policy.get("paid_price_per_user_per_period"), "paid_price_per_user_per_period")
    reserve_periods = _fraction(policy.get("reserve_periods"), "reserve_periods")
    reserve_available = _fraction(policy.get("reserve_available"), "reserve_available")
    rates = policy.get("conversion_rates")
    if not isinstance(rates, list) or not rates:
        raise _fail("INPUT_VALUE_INVALID", "conversion_rates is a non-empty list", "declare conversion scenarios",
                    field="conversion_rates")
    conversions = [_fraction(r, "conversion_rates[]", upper=Fraction(1)) for r in rates]

    checks: dict[str, Any] = {}
    sample_ok = basis.get("status") == "COMPLETE_BASIS"
    checks["AUTHENTICATED_OPERATING_COST_SAMPLE"] = {"holds": sample_ok, "pricing_basis_status": basis.get("status"),
                                                     "selected_basis": basis.get("selected_basis")}
    if basis.get("c_pricing") is None:
        unit_cost = None
    else:
        unit_cost = Fraction(Decimal(basis["c_pricing"]))
    sensitivity, breakeven = [], None
    if unit_cost is not None:
        period_cost = users * actions * unit_cost
        if users and price:
            breakeven = period_cost / (users * price)
        for conversion in conversions:
            revenue = users * conversion * price
            sensitivity.append({"conversion_rate": _text(conversion), "revenue": _text(revenue),
                                "cost": _text(period_cost), "margin": _text(revenue - period_cost),
                                "breaks_even": revenue >= period_cost})
        reserve_needed = period_cost * reserve_periods
        checks["CONTINGENCY_RESERVE"] = {"holds": reserve_available >= reserve_needed,
                                         "reserve_needed": _text(reserve_needed), "reserve_available": _text(reserve_available)}
    else:
        checks["CONTINGENCY_RESERVE"] = {"holds": False, "reason": "no cost basis"}
    checks["FREE_TO_PAID_SENSITIVITY"] = {"holds": any(row["breaks_even"] for row in sensitivity),
                                          "breakeven_conversion": None if breakeven is None else _text(breakeven),
                                          "scenarios": sensitivity}
    failed = [name for name in PREDICATES if not checks[name]["holds"]]
    body = {"pricing_goal": PRICING_GOAL, "pricing_basis": basis, "predicates": checks,
            "evidence_class": "SOURCE_IMPLEMENTED", "realism_owner_accepted": False,
            "inputs": {name: dict(manifest["inputs"][name]) for name in REQUIRED_INPUTS}}
    if failed:
        result = _six("DENY", f"S4_COST_{failed[0]}_NOT_MET", failed[0],
                      "supply inputs under which the named predicate holds; the evaluator never relaxes a predicate",
                      "after the owner supplies new accepted inputs", failed_predicates=failed)
        result.update(body)
        return result
    return {"schema": RESULT_SCHEMA, "benchmark_id": BENCHMARK_ID, "disposition": "ALLOW",
            "authority": dict(NO_AUTHORITY), **body}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--input", action="append", default=[], metavar="NAME=PATH",
                        help="caller-supplied bytes for a declared input; nothing is fetched")
    args = parser.parse_args(argv)
    try:
        supplied: dict[str, bytes] = {}
        for item in args.input:
            name, sep, path = item.partition("=")
            if not sep:
                raise _fail("INPUT_ARGUMENT_MALFORMED", "--input is NAME=PATH", "pass --input NAME=PATH", value=item)
            supplied[name] = Path(path).read_bytes()
        result = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")), supplied)
    except Refused as refusal:
        result = refusal.result
    except (OSError, ValueError) as exc:
        result = _fail("INPUT_MANIFEST_SCHEMA", "manifest and inputs are readable", "supply readable files",
                       detail=f"{type(exc).__name__}: {exc}").result
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"ALLOW": 0, "DENY": 2}.get(result["disposition"], 1)


if __name__ == "__main__":
    sys.exit(main())
