"""GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001 finish point: a NON-ALLOW produces no effect in a customer conformance run.

Predicate NON_ALLOW_PRODUCES_NO_EFFECT_IN_CUSTOMER_CONFORMANCE_RUN, run at the commit the TV/TVC release receipt
names (the verifier checks this file out at that ref; nothing here names or moves a ref).

What a customer conformance run is: a caller repository's job that `uses:` .github/workflows/governance-gate.yml at
that ref, and an effect job that `needs:` it. The effect happens only if the gate job succeeds. This test takes the
gate's own `run` step from the workflow file at this commit (so a change to that step changes the result), executes
its disposition half against the real stegverse/governance_gate.py read_workflow_disposition, and models the effect
job as "runs only if the gate step exits 0". It asserts that every non-ALLOW (FAIL_CLOSED, DENY, the pre-#534 PASS,
a malformed or missing report, or a checker exit status other than 0) leaves the effect unrun, and that only
ALLOW with checker status 0 lets it run.

Boundary: the checker's production of a disposition from customer bundles is not executed here. It is consumed as
the receipt of its owner's verifier (.github/workflows/governance-gate-selftest.yml), so this finish point exercises
no structural-validator, validator-inventory, schema-migration, tier-pricing or cost-component-registry module. The
last test checks that at run time: the disposition half imports no module of the stegverse package.

Consumed source pin (Coordination class D ruling: SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001 is a consumes-dependency,
not a fold). The gate workflow and governance_gate.py, which this test reads and executes, belong to that Goal, and so
does structural_validator_candidate.py, which governance_gate.run_gate loads by name. This test never calls run_gate,
so the validator is reachable but not executed. Before any of them is read or executed, each file's sha256 must equal
its content at the pinned commit STRUCTURAL_PIN["commit"]; on a mismatch every test that uses them fails closed with
the six fields and runs nothing. A change to any of them is a STRUCTURAL-owned edit: it is
routed to that Goal, and this pin moves only after that Goal publishes the new commit.

Lowest supported mode: E0 (standard library, the committed workflow and module, bash; no clock, no network).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/governance-gate.yml"
GATE_MODULE = ROOT / "stegverse/governance_gate.py"
CHECKER_MARKER = "status=$?"
STRUCTURAL_GOAL = "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"
STRUCTURAL_PIN = {
    "commit": "4c9dfac7b31c5dcd30a8bc9b13e6d11353a51328",  # last change to both files (StegVerse-org/StegVerse-SDK#534)
    "files": {
        ".github/workflows/governance-gate.yml": "1d14c9baf363e37a5b66a33016497869206a671a2a7d29596a95c23eedb82df0",
        "stegverse/governance_gate.py": "3db3e83c97764e912919018dcb560c011d3b499ea550aef43e3f61e64a36ee4f",
        # never executed here (only governance_gate.run_gate loads it, by name); pinned because the gate module
        # this test executes can reach it, so a STRUCTURAL change to it is routed, not absorbed
        "stegverse/structural_validator_candidate.py": "574b017a927acc9e4ef15ef90e0f71ddbdbd854dd1575ffa43bfbc1f1533bef7",
    },
}


def pin_refusal(root: Path = ROOT) -> dict | None:
    """None if every consumed STRUCTURAL file matches its pinned sha256; otherwise the six-field FAIL_CLOSED."""
    observed = {}
    for rel in STRUCTURAL_PIN["files"]:
        path = root / rel
        observed[rel] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
    mismatched = {rel: {"pinned": STRUCTURAL_PIN["files"][rel], "observed": observed[rel]}
                  for rel in STRUCTURAL_PIN["files"] if observed[rel] != STRUCTURAL_PIN["files"][rel]}
    if not mismatched:
        return None
    return {
        "disposition": "FAIL_CLOSED",
        "failure_code": "STRUCTURAL_CONSUMED_SOURCE_PIN_MISMATCH",
        "failed_predicate": "CONSUMED_STRUCTURAL_FILES_MATCH_SHA256_PIN",
        "required_evidence_or_repair": (
            f"these files differ from {STRUCTURAL_PIN['commit']}: {sorted(mismatched)}. A change to them is a "
            f"STRUCTURAL-owned edit: land it through {STRUCTURAL_GOAL}, then move STRUCTURAL_PIN (commit and sha256s) "
            "and the adjacency ruling's consumes_dependencies pin to that Goal's published commit"),
        "retry_entrypoint": "python -m unittest tests.test_governance_product_finish_point",
        "owning_existing_goal": STRUCTURAL_GOAL,
        "next_attempt": "the next run of this finish-point test after the pin or the files are repaired",
        "detail": mismatched,
    }


def gate_run_step() -> str:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "- id: run")
    run = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
    indent = len(lines[run + 1]) - len(lines[run + 1].lstrip())
    body = []
    for line in lines[run + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) < indent:
            break
        body.append(line[indent:])
    return "\n".join(body) + "\n"


def disposition_half(step: str) -> str:
    """The step after the checker call: status comes from the checker, the rest is verbatim."""
    head, sep, tail = step.partition(CHECKER_MARKER)
    if not sep:
        raise AssertionError("the gate run step no longer records the checker status")
    return "set +e\nstatus=$1\n" + tail


def conformance_run(report: str | None, checker_status: int) -> tuple[bool, str]:
    """(effect ran, disposition output) for one customer run with the given report and checker status."""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        sdk = work / ".stegverse-sdk" / GATE_MODULE.parent.name
        sdk.mkdir(parents=True)
        (sdk / "governance_gate.py").write_bytes(GATE_MODULE.read_bytes())
        if report is not None:
            (work / "stegverse-governance-report.json").write_text(report, encoding="utf-8")
        out = work / "github_output.txt"
        out.write_text("", encoding="utf-8")
        script = disposition_half(gate_run_step())
        env = {"PATH": "/usr/bin:/bin", "GITHUB_OUTPUT": str(out)}
        gate = subprocess.run(["bash", "-c", script, "bash", str(checker_status)], cwd=work, env=env,
                              capture_output=True, text=True, check=False)
        effect = work / "effect.txt"
        if gate.returncode == 0:  # the caller's `needs:` effect job runs only after a successful gate job
            effect.write_text("effect\n", encoding="utf-8")
        return effect.exists(), out.read_text(encoding="utf-8").strip()


class GovernanceProductFinishPoint(unittest.TestCase):
    def require_structural_pin(self) -> None:
        refusal = pin_refusal()
        if refusal is not None:
            self.fail(json.dumps(refusal, sort_keys=True))

    def test_finish_point_verdict(self) -> None:
        self.require_structural_pin()
        non_allow = {
            "fail_closed": ('{"disposition": "FAIL_CLOSED", "failure_code": "BUNDLE_VERIFICATION_FAILED"}\n', 1),
            "deny": ('{"disposition": "DENY"}\n', 1),
            "pre_534_pass": ('{"disposition": "PASS"}\n', 0),
            "malformed": ("not json\n", 0),
            "non_object": ("[]\n", 0),
            "missing_report": (None, 0),
            "allow_but_checker_failed": ('{"disposition": "ALLOW"}\n', 1),
        }
        for name, (report, status) in non_allow.items():
            with self.subTest(case=name):
                ran, output = conformance_run(report, status)
                self.assertFalse(ran, f"{name}: a non-ALLOW let the effect run")
                expected = "DENY" if name == "deny" else ("ALLOW" if name == "allow_but_checker_failed" else "FAIL_CLOSED")
                self.assertEqual(output, f"disposition={expected}")
        ran, output = conformance_run('{"disposition": "ALLOW"}\n', 0)
        self.assertTrue(ran, "ALLOW with checker status 0 must let the effect run")
        self.assertEqual(output, "disposition=ALLOW")

    def test_gate_job_is_read_only_and_exports_the_disposition(self) -> None:
        self.require_structural_pin()
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read\n", workflow)
        self.assertIn("value: ${{ jobs.gate.outputs.disposition }}", workflow)
        self.assertIn("disposition: ${{ steps.run.outputs.disposition }}", workflow)
        self.assertIn('if [ "$status" -eq 0 ] && [ "$disposition" = "ALLOW" ]; then exit 0; else exit 1; fi',
                      gate_run_step())

    def test_disposition_half_imports_no_stegverse_module(self) -> None:
        self.require_structural_pin()
        probe = ("import importlib.util, json, os, sys\n"
                 "spec = importlib.util.spec_from_file_location('governance_gate', sys.argv[1])\n"
                 "module = importlib.util.module_from_spec(spec)\n"
                 "spec.loader.exec_module(module)\n"
                 "module.read_workflow_disposition(sys.argv[2])\n"
                 "pkg = os.path.realpath(os.path.dirname(sys.argv[1]))\n"
                 "print(json.dumps(sorted(n for n, m in list(sys.modules.items()) if n != 'governance_gate'\n"
                 "    and os.path.realpath(getattr(m, '__file__', None) or '').startswith(pkg + os.sep))))\n")
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            report.write_text('{"disposition": "FAIL_CLOSED"}\n', encoding="utf-8")
            proc = subprocess.run([sys.executable, "-I", "-c", probe, str(GATE_MODULE), str(report)],
                                  capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), [])


    def test_structural_pin_mismatch_fails_closed_with_six_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in STRUCTURAL_PIN["files"]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_bytes((ROOT / rel).read_bytes())
            self.assertIsNone(pin_refusal(root))
            first = next(iter(STRUCTURAL_PIN["files"]))
            (root / first).write_bytes((root / first).read_bytes() + b"# edit\n")
            refusal = pin_refusal(root)
            self.assertIsNotNone(refusal)
            self.assertEqual(refusal["disposition"], "FAIL_CLOSED")
            for field in ("failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
                          "owning_existing_goal", "next_attempt"):
                self.assertTrue(refusal[field], field)
            self.assertEqual(refusal["owning_existing_goal"], STRUCTURAL_GOAL)
            self.assertEqual(sorted(refusal["detail"]), [first])
            (root / first).unlink()
            self.assertEqual(pin_refusal(root)["detail"][first]["observed"], "MISSING")


if __name__ == "__main__":
    unittest.main()
