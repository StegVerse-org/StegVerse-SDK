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

Lowest supported mode: E0 (standard library, the committed workflow and module, bash; no clock, no network).
"""
from __future__ import annotations

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
        sdk = work / ".stegverse-sdk" / "stegverse"
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
    def test_finish_point_verdict(self) -> None:
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
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read\n", workflow)
        self.assertIn("value: ${{ jobs.gate.outputs.disposition }}", workflow)
        self.assertIn("disposition: ${{ steps.run.outputs.disposition }}", workflow)
        self.assertIn('if [ "$status" -eq 0 ] && [ "$disposition" = "ALLOW" ]; then exit 0; else exit 1; fi',
                      gate_run_step())

    def test_disposition_half_imports_no_stegverse_module(self) -> None:
        probe = ("import importlib.util, json, sys\n"
                 "spec = importlib.util.spec_from_file_location('governance_gate', sys.argv[1])\n"
                 "module = importlib.util.module_from_spec(spec)\n"
                 "spec.loader.exec_module(module)\n"
                 "module.read_workflow_disposition(sys.argv[2])\n"
                 "print(json.dumps(sorted(m for m in sys.modules if m.split('.')[0] == 'stegverse')))\n")
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            report.write_text('{"disposition": "FAIL_CLOSED"}\n', encoding="utf-8")
            proc = subprocess.run([sys.executable, "-I", "-c", probe, str(GATE_MODULE), str(report)],
                                  capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), [])


if __name__ == "__main__":
    unittest.main()
