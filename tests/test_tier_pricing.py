"""Cost-derived tier pricing: cited rates only, MAX(estimated, observed), fail closed on anything unsourced."""
import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from stegverse import tier_pricing as tp

ROOT = Path(__file__).resolve().parents[1]
SRC = "https://example.org/rates"
VERSION = "cost-basis-test-1"
DIGEST = "a" * 64


def _basis(task_class, samples=1, **cost):
    return {"schema": tp.COST_BASIS_SCHEMA, "task_class": task_class, "sample_count": samples, "cost_estimate": cost}


def _card(**rates):
    return {"schema": tp.RATE_CARD_SCHEMA, "compute_unit_definition": "one runner-minute",
            "rates": {k: {"usd": v, "source": SRC, "observed_at": "2026-10-14"} for k, v in rates.items()}}


def _policy(*plans, margin=0.5, version=VERSION):
    return {"schema": tp.POLICY_SCHEMA, "target_gross_margin": margin, "cost_basis_version": version,
            "plans": [{"name": n, "included_actions": a, "task_classes": c} for n, a, c in plans]}


def _market(*prices):
    return {"schema": tp.MARKET_SCHEMA,
            "comparables": [{"name": f"c{i}", "usd_per_action": p, "source": SRC, "observed_at": "2026-10-14"}
                            for i, p in enumerate(prices)]}


def _observations(version=VERSION, **amounts):
    return {"schema": tp.OBSERVATION_SET_SCHEMA, "authentic_observation_classes": ["ORGANIZATION_RECEIPT_MEASURED"],
            "observations": {c: {"schema": "stegverse.cost-observation.v1", "scope_id": c, "currency": "USD",
                                 "unit": "action", "cost_basis_version": version, "amount": a,
                                 "observation_class": "ORGANIZATION_RECEIPT_MEASURED",
                                 "evidence_ref": f"receipts/{c}.json", "evidence_sha256": DIGEST}
                             for c, a in amounts.items()}}


BASIS = [_basis("gate", compute_units=2, storage_bytes=10**9, failure_recovery_units=1),
         _basis("canary", samples=0, compute_units=1), {"task_class": None}]
CARD = dict(compute_unit="0.006", storage_gb="0.25")


def test_estimate_only_is_a_labelled_provisional_scenario_never_a_final_price():
    report = tp.derive_pricing(BASIS, _card(**CARD), _policy(("team", 1000, ["gate"])))
    assert report["status"] == "PROVISIONAL"
    gate = {c["task_class"]: c for c in report["action_costs"]}["gate"]
    # 3 units * 0.006 + 1 GB * 0.25 = 0.268
    assert tp.Decimal(gate["usd_per_action"]) == tp.Decimal("0.268")
    assert (gate["pricing_basis"]["status"], gate["pricing_basis"]["selected_basis"]) == (
        "PROVISIONAL_SCENARIO", "ESTIMATED_ONLY")
    assert gate["pricing_basis"]["observed"]["amount"] == "UNKNOWN"
    tier = report["tiers"][0]
    assert tier["status"] == "PROVISIONAL_SCENARIO"
    assert tp.Decimal(tier["cost_floor_usd_per_action"]) == tp.Decimal("0.536")
    assert (tier["usd_per_period"], tier["market_position"], tier["evidence"]) == (
        "536.00", "NO_MARKET_EVIDENCE", "SAMPLED_COST_BASIS")
    assert report["actionable_disposition"]["failure_code"] == "PRICING_BASIS_PROVISIONAL"
    assert not any(report["authority"].values())


def test_max_rule_selects_the_larger_operand_and_preserves_both():
    higher = tp.derive_pricing(BASIS, _card(**CARD), _policy(("team", 10, ["gate"])), observations=_observations(gate="0.5"))
    basis = higher["action_costs"][0]["pricing_basis"]
    assert (higher["status"], basis["status"], basis["selected_basis"], basis["c_pricing"]) == (
        "PRICED", "COMPLETE_BASIS", "OBSERVED", "0.5")
    assert (basis["estimated"]["amount"], basis["observed"]["amount"]) == ("0.268", "0.5")
    assert higher["tiers"][0]["usd_per_period"] == "10.00"  # 0.5 / (1 - 0.5) * 10
    lower = tp.derive_pricing(BASIS, _card(**CARD), _policy(("team", 10, ["gate"])), observations=_observations(gate="0.1"))
    assert lower["action_costs"][0]["pricing_basis"]["selected_basis"] == "ESTIMATED"
    assert lower["tiers"][0]["usd_per_period"] == "5.36"
    assert higher["authority"]["final_price_approved"] is False


def test_unknown_observation_is_never_zero_and_mismatched_version_is_not_comparable():
    unknown = tp.derive_pricing(BASIS, _card(**CARD), _policy(("team", 10, ["gate"])),
                                observations=_observations(gate="UNKNOWN"))
    assert unknown["action_costs"][0]["pricing_basis"]["status"] == "PROVISIONAL_SCENARIO"
    assert unknown["tiers"][0]["usd_per_period"] == "5.36"
    stale = tp.derive_pricing(BASIS, _card(**CARD), _policy(("team", 10, ["gate"])),
                              observations=_observations(version="older", gate="0.5"))
    basis = stale["action_costs"][0]["pricing_basis"]
    assert (basis["status"], basis["mismatched"], basis["c_pricing"]) == ("NOT_COMPARABLE", ["cost_basis_version"], None)
    assert (stale["status"], stale["tiers"][0]["status"]) == ("INCOMPLETE", "UNKNOWN_RATE_NOT_SOURCED")


def test_observation_without_an_authentic_class_or_receipt_digest_fails_closed():
    for field, value in (("observation_class", "SELF_REPORTED"), ("evidence_sha256", "abc"), ("evidence_ref", "")):
        observations = _observations(gate="0.5")
        observations["observations"]["gate"][field] = value
        with pytest.raises(tp.PricingInputError):
            tp.derive_pricing(BASIS, _card(**CARD), _policy(("team", 10, ["gate"])), observations=observations)


def test_market_median_sets_price_only_above_the_cost_floor():
    card, policy = _card(**CARD), _policy(("team", 10, ["gate"]))
    at = tp.derive_pricing(BASIS, card, policy, _market("0.5", "1.0", "2.0"))["tiers"][0]
    assert (at["usd_per_action"], at["market_position"], at["usd_per_period"]) == ("1.0", "AT_MARKET_MEDIAN", "10.00")
    below = tp.derive_pricing(BASIS, card, policy, _market("0.1"))["tiers"][0]
    assert (below["market_position"], below["usd_per_period"]) == ("ABOVE_MARKET_COST_BOUND", "5.36")


def test_unsourced_or_missing_rate_is_unknown_not_invented():
    report = tp.derive_pricing(BASIS, _card(compute_unit="0.006"),
                               _policy(("team", 10, ["gate"]), ("starter", 10, ["canary"]), ("ghost", 1, ["nope"])))
    assert report["status"] == "INCOMPLETE"
    team, starter, ghost = report["tiers"]
    assert (team["status"], team["unpriced_task_classes"], team["usd_per_period"]) == ("UNKNOWN_RATE_NOT_SOURCED", ["gate"], None)
    assert (starter["status"], starter["evidence"]) == ("PROVISIONAL_SCENARIO", "PROVISIONAL_ESTIMATE")
    assert (ghost["status"], ghost["absent_cost_basis"]) == ("UNKNOWN_COST_BASIS", ["nope"])


@pytest.mark.parametrize("mutate", [
    lambda card, policy, market: card.pop("compute_unit_definition"),
    lambda card, policy, market: card["rates"]["compute_unit"].update(source="http://insecure"),
    lambda card, policy, market: card["rates"]["compute_unit"].pop("observed_at"),
    lambda card, policy, market: card["rates"]["compute_unit"].update(usd=-1),
    lambda card, policy, market: card["rates"]["compute_unit"].update(usd=True),
    lambda card, policy, market: card["rates"]["compute_unit"].update(usd="NaN"),
    lambda card, policy, market: policy.update(target_gross_margin=1),
    lambda card, policy, market: policy.update(plans=[]),
    lambda card, policy, market: policy.pop("cost_basis_version"),
    lambda card, policy, market: policy["plans"][0].update(task_classes=[]),
    lambda card, policy, market: market["comparables"][0].pop("source"),
])
def test_malformed_inputs_fail_closed(mutate):
    card, policy, market = _card(compute_unit="0.006"), _policy(("starter", 1, ["canary"])), _market("1")
    mutate(card, policy, market)
    with pytest.raises(tp.PricingInputError):
        tp.derive_pricing(BASIS, card, policy, market)


def test_cli_exit_codes_and_isolated_run(tmp_path):
    with pytest.raises(tp.PricingInputError, match="duplicate"):
        tp.derive_pricing(BASIS + [_basis("canary", compute_units=9)], _card(compute_unit="1"),
                          _policy(("s", 1, ["canary"])))
    basis_dir = tmp_path / "basis"
    basis_dir.mkdir()
    for i, record in enumerate(BASIS):
        (basis_dir / f"{i}.json").write_text(json.dumps(record))
    files = {"card": _card(compute_unit="0.006"), "policy": _policy(("s", 100, ["canary"])),
             "obs": _observations(canary="0.006")}
    for name, doc in files.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(doc))
    args = ["--cost-basis-dir", str(basis_dir), "--rate-card", str(tmp_path / "card.json"),
            "--policy", str(tmp_path / "policy.json"), "--output", str(tmp_path / "out.json")]
    assert tp.main(args) == 1  # estimate only: provisional, not a final price
    assert json.loads((tmp_path / "out.json").read_text())["tiers"][0]["usd_per_period"] == "1.20"
    assert tp.main(args + ["--observations", str(tmp_path / "obs.json")]) == 0
    # Isolated mode: the sibling cost_registry module is loaded by path, nothing installed.
    result = subprocess.run([sys.executable, "-I", str(ROOT / "stegverse" / "tier_pricing.py"), *args[:-2],
                             "--observations", str(tmp_path / "obs.json")], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "PRICED"
    (tmp_path / "card.json").write_text(json.dumps({"schema": "wrong"}))
    assert tp.main(args) == 1
    assert json.loads((tmp_path / "out.json").read_text())["status"] == "FAIL_CLOSED"


def test_imports_only_the_standard_library():
    for name in ("tier_pricing", "cost_registry"):
        tree = ast.parse((ROOT / "stegverse" / f"{name}.py").read_text(encoding="utf-8"))
        modules = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        modules |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.level == 0}
        # "stegverse" is the sibling cost_registry module, with a by-path fallback.
        assert modules <= set(sys.stdlib_module_names) | {"__future__", "stegverse"}, (name, modules)


def test_non_priced_results_carry_the_six_actionable_fields(tmp_path):
    fields = {"failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
              "owning_existing_goal", "next_attempt"}
    incomplete = tp.derive_pricing(BASIS, _card(compute_unit="0.006"), _policy(("team", 10, ["gate"])))
    assert set(incomplete["actionable_disposition"]) == fields
    assert incomplete["actionable_disposition"]["owning_existing_goal"] == "SDK-COST-DERIVED-TIER-PRICING-001"
    assert "storage_gb" in incomplete["actionable_disposition"]["failed_predicate"]
    priced = tp.derive_pricing(BASIS, _card(compute_unit="0.006"), _policy(("s", 1, ["canary"])),
                               observations=_observations(canary="0.006"))
    assert "actionable_disposition" not in priced
    (tmp_path / "card.json").write_text(json.dumps({"schema": "wrong"}))
    (tmp_path / "policy.json").write_text(json.dumps(_policy(("s", 1, ["canary"]))))
    (tmp_path / "basis").mkdir()
    out = tmp_path / "out.json"
    assert tp.main(["--cost-basis-dir", str(tmp_path / "basis"), "--rate-card", str(tmp_path / "card.json"),
                    "--policy", str(tmp_path / "policy.json"), "--output", str(out)]) == 1
    assert set(json.loads(out.read_text())["actionable_disposition"]) == fields
