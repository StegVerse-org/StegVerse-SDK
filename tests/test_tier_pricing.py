"""Cost-derived tier pricing: cited rates only, fail closed on anything unsourced."""
import ast
import json
import sys
from pathlib import Path

import pytest

from stegverse import tier_pricing as tp

ROOT = Path(__file__).resolve().parents[1]
SRC = "https://example.org/rates"


def _basis(task_class, samples=1, **cost):
    return {"schema": tp.COST_BASIS_SCHEMA, "task_class": task_class, "sample_count": samples, "cost_estimate": cost}


def _card(**rates):
    return {"schema": tp.RATE_CARD_SCHEMA, "compute_unit_definition": "one runner-minute",
            "rates": {k: {"usd": v, "source": SRC, "observed_at": "2026-10-14"} for k, v in rates.items()}}


def _policy(*plans, margin=0.5):
    return {"schema": tp.POLICY_SCHEMA, "target_gross_margin": margin,
            "plans": [{"name": n, "included_actions": a, "task_classes": c} for n, a, c in plans]}


def _market(*prices):
    return {"schema": tp.MARKET_SCHEMA,
            "comparables": [{"name": f"c{i}", "usd_per_action": p, "source": SRC, "observed_at": "2026-10-14"}
                            for i, p in enumerate(prices)]}


BASIS = [_basis("gate", compute_units=2, storage_bytes=10**9, failure_recovery_units=1),
         _basis("canary", samples=0, compute_units=1), {"task_class": None}]


def test_cost_is_units_times_cited_rates_and_floor_applies_margin():
    report = tp.derive_pricing(BASIS, _card(compute_unit="0.006", storage_gb="0.25"),
                               _policy(("team", 1000, ["gate"])))
    assert report["status"] == "PRICED"
    gate = {c["task_class"]: c for c in report["action_costs"]}["gate"]
    # 3 units * 0.006 + 1 GB * 0.25 = 0.268
    assert tp.Decimal(gate["usd_per_action"]) == tp.Decimal("0.268")
    tier = report["tiers"][0]
    assert tp.Decimal(tier["cost_floor_usd_per_action"]) == tp.Decimal("0.536")
    assert (tier["usd_per_period"], tier["market_position"], tier["evidence"]) == ("536.00", "NO_MARKET_EVIDENCE", "OBSERVED")
    assert not any(report["authority"].values())


def test_market_median_sets_price_only_above_the_cost_floor():
    card, policy = _card(compute_unit="0.006", storage_gb="0.25"), _policy(("team", 10, ["gate"]))
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
    assert (starter["status"], starter["evidence"]) == ("PRICED", "PROVISIONAL_ESTIMATE")
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
    lambda card, policy, market: policy["plans"][0].update(task_classes=[]),
    lambda card, policy, market: market["comparables"][0].pop("source"),
])
def test_malformed_inputs_fail_closed(mutate):
    card, policy, market = _card(compute_unit="0.006"), _policy(("starter", 1, ["canary"])), _market("1")
    mutate(card, policy, market)
    with pytest.raises(tp.PricingInputError):
        tp.derive_pricing(BASIS, card, policy, market)


def test_duplicate_referenced_basis_fails_closed_and_cli_reports_it(tmp_path):
    with pytest.raises(tp.PricingInputError, match="duplicate"):
        tp.derive_pricing(BASIS + [_basis("canary", compute_units=9)], _card(compute_unit="1"),
                          _policy(("s", 1, ["canary"])))
    basis_dir = tmp_path / "basis"
    basis_dir.mkdir()
    for i, record in enumerate(BASIS):
        (basis_dir / f"{i}.json").write_text(json.dumps(record))
    files = {"card": _card(compute_unit="0.006"), "policy": _policy(("s", 100, ["canary"]))}
    for name, doc in files.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(doc))
    args = ["--cost-basis-dir", str(basis_dir), "--rate-card", str(tmp_path / "card.json"),
            "--policy", str(tmp_path / "policy.json"), "--output", str(tmp_path / "out.json")]
    assert tp.main(args) == 0
    assert json.loads((tmp_path / "out.json").read_text())["tiers"][0]["usd_per_period"] == "1.20"
    (tmp_path / "card.json").write_text(json.dumps({"schema": "wrong"}))
    assert tp.main(args) == 1
    assert json.loads((tmp_path / "out.json").read_text())["status"] == "FAIL_CLOSED"


def test_imports_only_the_standard_library():
    tree = ast.parse((ROOT / "stegverse" / "tier_pricing.py").read_text(encoding="utf-8"))
    modules = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    modules |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.level == 0}
    assert modules <= set(sys.stdlib_module_names) | {"__future__"}


def test_non_priced_results_carry_the_six_actionable_fields(tmp_path):
    fields = {"failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
              "owning_existing_goal", "next_attempt"}
    incomplete = tp.derive_pricing(BASIS, _card(compute_unit="0.006"), _policy(("team", 10, ["gate"])))
    assert set(incomplete["actionable_disposition"]) == fields
    assert "storage_gb" in incomplete["actionable_disposition"]["failed_predicate"]
    priced = tp.derive_pricing(BASIS, _card(compute_unit="0.006"), _policy(("s", 1, ["canary"])))
    assert "actionable_disposition" not in priced
    (tmp_path / "card.json").write_text(json.dumps({"schema": "wrong"}))
    (tmp_path / "policy.json").write_text(json.dumps(_policy(("s", 1, ["canary"]))))
    (tmp_path / "basis").mkdir()
    out = tmp_path / "out.json"
    assert tp.main(["--cost-basis-dir", str(tmp_path / "basis"), "--rate-card", str(tmp_path / "card.json"),
                    "--policy", str(tmp_path / "policy.json"), "--output", str(out)]) == 1
    assert set(json.loads(out.read_text())["actionable_disposition"]) == fields
