"""S4_COST evaluator: inputs by reference, composed pricing basis, sensitivity and reserve.

Every input below is SYNTHETIC and NON-AUTHORITATIVE: it exercises the evaluator, it is
not an owner-accepted cost sample and proves nothing about real StegVerse economics.
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stegverse import s4_cost_benchmark as s4  # noqa: E402

REGISTRY = json.loads((ROOT / "pricing" / "cost-component-registry.v1.json").read_text(encoding="utf-8"))
CARD = json.loads((ROOT / "pricing" / "rate-card.five-lane-declared.json").read_text(encoding="utf-8"))
REV = "0" * 40


def context():
    return {"scope_id": "SV-RECON-001", "execution_locus": "EXTERNAL_PROVIDER", "provider": "openai",
            "attributable_outcome_id": "sha256:155869ba",
            "quantities": {"storage_gb_month": 0, "governance_overhead_runner_minutes": 0,
                           "input_tokens": 307, "output_tokens": 178},  # five-lane openai-raw: 0.006875
            "allocation": {"attributable_outcomes_in_period": 1}}


def observation(amount="0.007"):
    return {"schema": "stegverse.cost-observation.v1", "scope_id": "SV-RECON-001", "currency": "USD",
            "unit": "successful equivalent admissible outcome", "cost_basis_version": REGISTRY["registry_version"],
            "amount": amount, "observation_class": "EXACT_USAGE_PLUS_BOUND_VERSIONED_RATE_CARD",
            "evidence_ref": "SYNTHETIC-NON-AUTHORITATIVE", "evidence_sha256": "b" * 64}


def policy(**overrides):
    value = {"schema": s4.POLICY_SCHEMA, "users_per_period": 1000, "actions_per_user_per_period": 100,
             "paid_price_per_user_per_period": "5", "conversion_rates": ["0.01", "0.05", "0.2"],
             "reserve_periods": 3, "reserve_available": "2100", "note": "SYNTHETIC NON-AUTHORITATIVE"}
    value.update(overrides)
    return value


def bundle(**docs):
    values = {"cost_component_registry": REGISTRY, "rate_card": CARD, "execution_context": context(),
              "cost_observation": observation(), "economics_policy": policy()}
    values.update(docs)
    supplied = {name: json.dumps(doc, sort_keys=True).encode("utf-8") for name, doc in values.items() if doc is not None}
    manifest = {"schema": s4.MANIFEST_SCHEMA, "benchmark_id": "S4_COST", "inputs": {
        name: {"ref": f"StegVerse-org/StegVerse-SDK:synthetic/{name}.json@{REV}",
               "sha256": hashlib.sha256(data).hexdigest()} for name, data in supplied.items()}}
    return manifest, supplied


class S4CostBenchmarkTests(unittest.TestCase):
    def test_allow_with_exact_sensitivity_and_reserve(self):
        out = s4.evaluate(*bundle())
        self.assertEqual(out["disposition"], "ALLOW")
        self.assertEqual(out["pricing_basis"]["status"], "COMPLETE_BASIS")
        self.assertEqual(out["pricing_basis"]["c_pricing"], "0.007")  # max(0.006875, 0.007)
        sens = out["predicates"]["FREE_TO_PAID_SENSITIVITY"]
        self.assertEqual(sens["breakeven_conversion"], "0.14")  # 1000*100*0.007 / (1000*5)
        self.assertEqual([r["breaks_even"] for r in sens["scenarios"]], [False, False, True])
        self.assertEqual(sens["scenarios"][2]["margin"], "300")  # 1000 - 700
        self.assertEqual(out["predicates"]["CONTINGENCY_RESERVE"]["reserve_needed"], "2100")
        self.assertFalse(any(out["authority"].values()))
        self.assertIs(out["realism_owner_accepted"], False)

    def test_each_predicate_denies_by_name(self):
        cases = {
            "FREE_TO_PAID_SENSITIVITY": {"economics_policy": policy(conversion_rates=["0.01", "0.1"])},
            "CONTINGENCY_RESERVE": {"economics_policy": policy(reserve_available="2099.99")},
        }
        for predicate, docs in cases.items():
            with self.subTest(predicate=predicate):
                out = s4.evaluate(*bundle(**docs))
                self.assertEqual((out["disposition"], out["failed_predicate"]), ("DENY", predicate))
                for field in ("failure_code", "required_evidence_or_repair", "retry_entrypoint",
                              "owning_existing_goal", "next_attempt"):
                    self.assertTrue(out[field])

    def test_unknown_observation_is_not_an_authenticated_sample(self):
        out = s4.evaluate(*bundle(cost_observation=observation(amount="UNKNOWN")))
        self.assertEqual(out["disposition"], "DENY")
        self.assertEqual(out["failed_predicate"], "AUTHENTICATED_OPERATING_COST_SAMPLE")
        self.assertEqual(out["pricing_basis"]["status"], "PROVISIONAL_SCENARIO")

    def test_missing_owner_input_is_fail_closed_input_not_supplied_by_name(self):
        for name in s4.REQUIRED_INPUTS:
            with self.subTest(missing=name):
                manifest, supplied = bundle()
                supplied.pop(name)
                with self.assertRaises(s4.Refused) as raised:
                    s4.evaluate(manifest, supplied)
                result = raised.exception.result
                self.assertEqual((result["disposition"], result["failure_code"]), ("FAIL_CLOSED", "INPUT_NOT_SUPPLIED"))
                self.assertEqual(result["evidence"]["input"], name)
                manifest["inputs"].pop(name)
                with self.assertRaises(s4.Refused) as raised:
                    s4.evaluate(manifest, supplied)
                self.assertEqual(raised.exception.result["failure_code"], "INPUT_NOT_SUPPLIED")

    def test_digest_and_reference_are_verified_nothing_fetched(self):
        manifest, supplied = bundle()
        supplied["rate_card"] = supplied["rate_card"] + b" "
        with self.assertRaises(s4.Refused) as raised:
            s4.evaluate(manifest, supplied)
        self.assertEqual(raised.exception.result["failure_code"], "INPUT_DIGEST_MISMATCH")
        for ref in ("StegVerse-org/StegVerse-SDK:pricing/x.json@main", "https://example.org/x.json", "pricing/x.json"):
            with self.subTest(ref=ref):
                manifest, supplied = bundle()
                manifest["inputs"]["rate_card"]["ref"] = ref
                with self.assertRaises(s4.Refused) as raised:
                    s4.evaluate(manifest, supplied)
                self.assertEqual(raised.exception.result["failure_code"], "INPUT_REFERENCE_MALFORMED")

    def test_invalid_values_and_manifest_identity_fail_closed(self):
        for docs, code in (({"economics_policy": policy(conversion_rates=["1.5"])}, "INPUT_VALUE_INVALID"),
                           ({"economics_policy": policy(users_per_period=1.5)}, "INPUT_VALUE_INVALID"),
                           ({"economics_policy": policy(schema="x")}, "INPUT_VALUE_INVALID"),
                           ({"execution_context": {**context(), "execution_locus": "MARS"}}, "COST_INPUT_INVALID")):
            with self.subTest(code=code, docs=list(docs)):
                with self.assertRaises(s4.Refused) as raised:
                    s4.evaluate(*bundle(**docs))
                self.assertEqual(raised.exception.result["failure_code"], code)
        manifest, supplied = bundle()
        manifest["benchmark_id"] = "S5_STRESS"
        with self.assertRaises(s4.Refused) as raised:
            s4.evaluate(manifest, supplied)
        self.assertEqual(raised.exception.result["failure_code"], "INPUT_MANIFEST_BENCHMARK")

    def test_deterministic_and_input_not_mutated(self):
        manifest, supplied = bundle()
        snapshot = copy.deepcopy((manifest, supplied))
        self.assertEqual(json.dumps(s4.evaluate(manifest, supplied), sort_keys=True),
                         json.dumps(s4.evaluate(manifest, supplied), sort_keys=True))
        self.assertEqual((manifest, supplied), snapshot)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            for docs, missing, code in (({}, None, 0), ({"economics_policy": policy(reserve_available="0")}, None, 2),
                                        ({}, "cost_observation", 1)):
                manifest, supplied = bundle(**docs)
                (d / "m.json").write_text(json.dumps(manifest), encoding="utf-8")
                args = [sys.executable, "-m", "stegverse.s4_cost_benchmark", str(d / "m.json")]
                for name, data in supplied.items():
                    if name == missing:
                        continue
                    (d / f"{name}.json").write_bytes(data)
                    args += ["--input", f"{name}={d / f'{name}.json'}"]
                done = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(done.returncode, code, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
