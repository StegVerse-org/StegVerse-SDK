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

Finish verdict (Coordination class D rulings LC-GOV-01/03/08, 2026-10-23): test_finish_point_verdict also runs
tools/governance_product_finish.py, which verifies every sealed predicate against the release manifest
.stegverse/governance-product/release-manifest.v1.json and the receipts it names, binds the finish ref to the TV/TVC
release receipt's commit, and emits the GOVERNANCE_PRODUCT_RELEASE organization-ledger receipt candidate (never
appended here). Until the release receipt, the C-review receipt and the ledger readback exist, its verdict is a
six-field FAIL_CLOSED; the fixture test shows the same code reaching ALLOW from receipts alone, with no code edit.

Lowest supported mode: E0 (standard library, the committed workflow and module, bash, git; no clock, no network).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/governance-gate.yml"
GATE_MODULE = ROOT / "stegverse/governance_gate.py"
CHECKER_MARKER = "status=$?"
FINISH_MODULE = ROOT / "tools/governance_product_finish.py"
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
              "owning_existing_goal", "next_attempt")
SEALED_PREDICATES = (
    "PRODUCT_CLAIM_LIMITED_TO_VERIFIABLE_RECEIPT_CHAIN_ON_CUSTOMER_SUPPLIED_MANIFEST_CONSTRAINTS",
    "PACKAGE_VERSION_IDENTITY_CONSISTENT_ACROSS_PYPROJECT_INIT_VERSION_JSON",
    "PINNED_REF_TREE_CONTAINS_GOVERNANCE_GATE_WORKFLOW_AND_MODULE",
    "IMMUTABLE_TAG_AND_GITHUB_RELEASE_PUBLISHED_UNDER_TV_TVC_AUTHORITY",
    "RELEASE_NOTES_SUPERSEDE_V1_0_1_SAFETY_STACK_OVERCLAIM",
    "CUSTOMER_QUICKSTART_INSTALL_UNINSTALL_AND_NONCLAIMS_PUBLISHED",
    "NO_NEW_RUNTIME_DEPENDENCY_INTRODUCED",
    "NON_ALLOW_PRODUCES_NO_EFFECT_IN_CUSTOMER_CONFORMANCE_RUN",
    "INDEPENDENT_RECEIPT_CHAIN_VERIFICATION_PASS_AND_TAMPER_FAIL",
    "LICENSE_AND_TERMS_FILE_SHA256_MATCHES_RELEASE_MANIFEST",
    "ROLLBACK_PROCEDURE_DOCUMENTED_WITHOUT_TAG_RETARGET",
    "ORGANIZATION_RECEIPT_APPENDED_UNDER_LOCK:GOVERNANCE_PRODUCT_RELEASE",
    "ENTITLEMENT_SEPARATE_FROM_DISPOSITION_CONSUMING_SDK_COST_DERIVED_TIER_PRICING_OUTPUT",
)
FIXTURE_FILES = (
    ".stegverse/governance-product/release-manifest.v1.json", ".github/workflows/governance-gate.yml",
    "stegverse/governance_gate.py", "stegverse/__init__.py", "pyproject.toml", "VERSION.json", "LICENSE",
    "RELEASE_NOTES_1.3.0.md", "docs/GITHUB_GOVERNANCE_QUICKSTART.md", "docs/GOVERNANCE_PRODUCT_RELEASE_DEFAULTS.md",
    "fixtures/governance_product_receipt_chain.json", "pricing/candidate-report.json",
)


def finish_module():
    spec = importlib.util.spec_from_file_location("governance_product_finish", FINISH_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str) -> str:
    env = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(root),
           "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z"}
    return subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "-c",
                           "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args], cwd=root, env=env,
                          capture_output=True, text=True, check=True).stdout.strip()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
        # the finish verdict over every sealed predicate, with this test's own predicate observed ALLOW above
        verdict = finish_module().finish_verdict(ROOT, {
            "disposition": "ALLOW", "predicate": "NON_ALLOW_PRODUCES_NO_EFFECT_IN_CUSTOMER_CONFORMANCE_RUN"})
        print(json.dumps({k: verdict.get(k) for k in ("disposition", "predicates") + SIX_FIELDS}, sort_keys=True))
        self.assertEqual(sorted(verdict["predicates"]), sorted(SEALED_PREDICATES))
        self.assertIn(verdict["disposition"], ("ALLOW", "FAIL_CLOSED"))
        self.assertFalse(verdict["clock_read"] or verdict["network_used"] or verdict["ledger_appended"])
        for name, result in verdict["results"].items():
            self.assertEqual(result["lowest_supported_mode"], "E0", name)
            self.assertTrue(result["degraded_form"], name)
            if result["disposition"] != "ALLOW":
                self.assertEqual(result["disposition"], "FAIL_CLOSED", name)
                for field in SIX_FIELDS:
                    self.assertTrue(result[field], f"{name}: {field}")
        if verdict["disposition"] != "ALLOW":
            for field in SIX_FIELDS:
                self.assertTrue(verdict[field], field)

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

    def release_fixture(self, tmp: str):
        """A repository built from this commit's files, released by fixture receipts. Returns (root, module)."""
        root = Path(tmp) / "repo"
        for rel in FIXTURE_FILES:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, root / rel)
        git(root, "init", "-q")
        git(root, "add", "--", *FIXTURE_FILES)
        git(root, "commit", "-q", "-m", "fixture release")
        commit = git(root, "rev-parse", "HEAD")
        module = finish_module()
        manifest = module.load_manifest(root)
        version = module.v_package_identity(root, manifest)["version"]
        git(root, "tag", f"v{version}", commit)
        lic = manifest["license"]
        write_json(root / manifest["release_receipt"]["path"], {
            "schema": manifest["release_receipt"]["schema"], "issuer": "TV/TVC",
            "repository": manifest["release_receipt"]["repository"], "tag": f"v{version}", "commit": commit,
            "allow_tag_update": False, "github_release": {"state": "PUBLISHED_VERIFIED"}})
        write_json(root / lic["c_review_receipt"]["path"], {
            "schema": lic["c_review_receipt"]["schema"], "license_sha256": lic["sha256"], "disposition": "ALLOW"})
        write_json(root / manifest["organization_ledger"]["ledger_head"]["path"], {
            "schema": manifest["organization_ledger"]["ledger_head"]["schema"], "head_sha256": "ab" * 32, "hb_epoch": 41})
        return root, module, manifest, commit

    LEDGER = "ORGANIZATION_RECEIPT_APPENDED_UNDER_LOCK:GOVERNANCE_PRODUCT_RELEASE"
    LICENSE = "LICENSE_AND_TERMS_FILE_SHA256_MATCHES_RELEASE_MANIFEST"
    NON_ALLOW = "NON_ALLOW_PRODUCES_NO_EFFECT_IN_CUSTOMER_CONFORMANCE_RUN"

    def write_readback(self, root, module, manifest, candidate, **fields) -> None:
        body = {"schema": manifest["organization_ledger"]["readback"]["schema"], "ledger_lock": "ORGANIZATION_LEDGER_LOCK",
                "source_receipt_sha256": module.sha256_hex(module.canonical(candidate))}
        body.update(fields)
        write_json(root / manifest["organization_ledger"]["readback"]["path"], body)

    def assert_six_field_refusal(self, result, code) -> None:
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failure_code"], code)
        for field in SIX_FIELDS:
            self.assertTrue(result[field], field)

    def test_finish_verdict_refuses_unverified_receipts(self) -> None:
        # Synthetic receipts satisfy every file-bound predicate, but a committed ledger readback and a caller-supplied
        # customer result are claims, so the verdict stays FAIL_CLOSED on exactly those two predicates.
        observed = {"disposition": "ALLOW", "predicate": self.NON_ALLOW}
        with tempfile.TemporaryDirectory() as tmp:
            root, module, manifest, commit = self.release_fixture(tmp)
            before = module.finish_verdict(root, observed)
            self.assertEqual(before["disposition"], "FAIL_CLOSED")
            candidate = before["ledger_receipt_candidate"]
            self.assertEqual(candidate["schema"], "stegverse.canonical-state-transition-receipt/v1")
            self.assertEqual((candidate["hb_epoch"], candidate["prior_state_ref_or_hash"]), (41, "ab" * 32))
            self.assertFalse(candidate["append_performed"])
            self.write_readback(root, module, manifest, candidate, org_receipt_sha256="cd" * 32)
            after = module.finish_verdict(root, observed)
            self.assertEqual(after["disposition"], "FAIL_CLOSED", json.dumps(after["predicates"], sort_keys=True))
            blocked = {k for k, v in after["predicates"].items() if v != "ALLOW"}
            self.assertEqual(blocked, {self.LEDGER, self.NON_ALLOW, self.LICENSE})
            self.assert_six_field_refusal(after["results"][self.NON_ALLOW], "CUSTOMER_CONFORMANCE_ORIGIN_UNVERIFIED")
            self.assert_six_field_refusal(after["results"][self.LEDGER], "ORGANIZATION_LEDGER_PROVENANCE_UNVERIFIED")
            self.assertEqual(after["failure_code"], "C_REVIEW_PROVENANCE_UNVERIFIED")  # first refusal in predicate order
            self.assertEqual(module.release_ref_binding(root, commit)["disposition"], "ALLOW")

    def test_committed_c_review_file_is_not_reviewer_evidence(self) -> None:
        # GPT-6 (#556, 6369045329): v_license accepted a local C-review JSON by schema, hash and disposition.
        with tempfile.TemporaryDirectory() as tmp:
            root, module, manifest, _ = self.release_fixture(tmp)
            self.assert_six_field_refusal(module.v_license(root, manifest), "C_REVIEW_PROVENANCE_UNVERIFIED")
            (root / manifest["license"]["c_review_receipt"]["path"]).unlink()
            self.assert_six_field_refusal(module.v_license(root, manifest), "C_REVIEW_RECEIPT_PENDING")

    def test_untrusted_local_ledger_readbacks_never_admit_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, module, manifest, _ = self.release_fixture(tmp)
            candidate = module.finish_verdict(root, None)["ledger_receipt_candidate"]
            cases = {
                "absent": ({}, "ORGANIZATION_LEDGER_RECEIPT_HASH_INVALID"),
                "null": ({"org_receipt_sha256": None}, "ORGANIZATION_LEDGER_RECEIPT_HASH_INVALID"),
                "not_hex": ({"org_receipt_sha256": "zz" * 32}, "ORGANIZATION_LEDGER_RECEIPT_HASH_INVALID"),
                "upper_hex": ({"org_receipt_sha256": "CD" * 32}, "ORGANIZATION_LEDGER_RECEIPT_HASH_INVALID"),
                "short": ({"org_receipt_sha256": "cd" * 31}, "ORGANIZATION_LEDGER_RECEIPT_HASH_INVALID"),
                "non_string": ({"org_receipt_sha256": 7}, "ORGANIZATION_LEDGER_RECEIPT_HASH_INVALID"),
                "plausible_forged": ({"org_receipt_sha256": "cd" * 32}, "ORGANIZATION_LEDGER_PROVENANCE_UNVERIFIED"),
            }
            for name, (fields, code) in cases.items():
                with self.subTest(case=name):
                    self.write_readback(root, module, manifest, candidate, **fields)
                    self.assert_six_field_refusal(module.v_ledger(root, manifest, candidate), code)
            self.write_readback(root, module, manifest, {"forged": "candidate"}, org_receipt_sha256="cd" * 32)
            self.assert_six_field_refusal(module.v_ledger(root, manifest, candidate), "ORGANIZATION_LEDGER_READBACK_MISMATCH")

    def test_caller_supplied_allow_is_not_authenticated_customer_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, module, _, _ = self.release_fixture(tmp)
            for claim in ({"disposition": "ALLOW", "predicate": self.NON_ALLOW}, {"disposition": "ALLOW"},
                          {"disposition": "DENY"}, {}):
                with self.subTest(claim=claim):
                    result = module.finish_verdict(root, claim)["results"][self.NON_ALLOW]
                    self.assert_six_field_refusal(result, "CUSTOMER_CONFORMANCE_ORIGIN_UNVERIFIED")
            self.assert_six_field_refusal(module.finish_verdict(root, None)["results"][self.NON_ALLOW],
                                          "FINISH_TEST_RESULT_NOT_SUPPLIED")

    def test_finish_verdict_tamper_cases_fail_closed_with_six_fields(self) -> None:
        observed = {"disposition": "ALLOW", "predicate": "NON_ALLOW_PRODUCES_NO_EFFECT_IN_CUSTOMER_CONFORMANCE_RUN"}
        with tempfile.TemporaryDirectory() as tmp:
            root, module, manifest, commit = self.release_fixture(tmp)
            def check(result, code):
                self.assertEqual(result["disposition"], "FAIL_CLOSED")
                self.assertEqual(result["failure_code"], code)
                for field in SIX_FIELDS:
                    self.assertTrue(result[field], field)
            check(module.release_ref_binding(root, "0" * 40), "FINISH_REF_NOT_RELEASE_RECEIPT_COMMIT")
            lic = root / "LICENSE"
            original = lic.read_bytes()
            lic.write_bytes(original + b"\n")
            check(module.v_license(root, manifest), "LICENSE_FILE_HASH_MISMATCH")
            lic.write_bytes(original)
            (root / manifest["license"]["c_review_receipt"]["path"]).unlink()
            check(module.v_license(root, manifest), "C_REVIEW_RECEIPT_PENDING")
            py = root / "pyproject.toml"
            text = py.read_text(encoding="utf-8")
            py.write_text(text.replace("dependencies = [", 'dependencies = [\n  "requests",', 1), encoding="utf-8")
            check(module.v_no_new_dependency(root, manifest), "RUNTIME_DEPENDENCY_CHANGED")
            py.write_text(text, encoding="utf-8")
            other = git(root, "commit-tree", "-m", "another commit", commit + "^{tree}")
            git(root, "tag", "-f", "v" + module.v_package_identity(root, manifest)["version"], other)
            check(module.v_immutable_tag(root, manifest), "RELEASE_TAG_NOT_AT_RECEIPT_COMMIT")
            (root / manifest["organization_ledger"]["ledger_head"]["path"]).unlink()
            verdict = module.finish_verdict(root, observed)
            check(verdict["ledger_receipt_refusal"], "ORGANIZATION_LEDGER_HEAD_UNSEALED")
            (root / manifest["release_receipt"]["path"]).unlink()
            check(module.v_pinned_tree(root, manifest), "RELEASE_RECEIPT_ABSENT")
            chain = json.loads((root / manifest["receipt_chain"]["fixture"]).read_text(encoding="utf-8"))
            chain[0]["transition_outcome"] = "TAMPERED"
            self.assertFalse(module.verify_chain(chain)[0])
            (root / module.MANIFEST).unlink()
            check(module.finish_verdict(root, observed), "RELEASE_MANIFEST_ABSENT_OR_MALFORMED")

    def build_ledger(self, tmp, module, receipts_and_sources):
        """A local git copy holding refs/stegverse/organization-ledger with the given (receipt body, source) pairs,
        chained oldest first. Returns (git_dir, [receipt digests])."""
        work = Path(tmp) / "ledger-work"
        work.mkdir()
        git(work, "init", "-q")
        previous, digests = None, []
        for body, source in receipts_and_sources:
            body = dict(body, previous_receipt_sha256=previous)
            digest = "sha256:" + module.sha256_hex(module.canonical(body))
            write_json(work / "receipts" / (digest.split(":")[1] + ".json"), dict(body, receipt_sha256=digest))
            if source is not None:
                key = "sha256:" + module.sha256_hex(module.canonical(source))
                write_json(work / "source-receipts" / (key.split(":")[1] + ".json"), source)
            previous = digest
            digests.append(digest)
        write_json(work / "HEAD.json", {"organization": "StegVerse-org", "receipt_sha256": previous})
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", "ledger")
        git(work, "update-ref", module.LEDGER_REF, "HEAD")
        return work / ".git", digests

    def org_receipt(self, cls="REPO_STATE_PROPAGATION", **fields):
        base = {"schema": "stegverse.organization-transition-receipt/v1", "organization": "StegVerse-org",
                "org_transition_class": cls, "canonical_state_transition_receipt_sha256": None,
                "source_transition_sha256": "sha256:" + "0" * 64, "source_receipt_schema": "stegverse.repo-transition-receipt/v1"}
        base.update(fields)
        return base

    def released_ledger(self, tmp, *, order="after", cls="GOVERNANCE_PRODUCT_RELEASE", retain=True, tamper=False):
        """Fixture release whose candidate is consumed on a synthetic ledger. Returns (root, module, manifest, git_dir)."""
        root, module, manifest, _ = self.release_fixture(tmp)
        genesis = self.org_receipt(chain_genesis=True)
        sealed_digest = "sha256:" + module.sha256_hex(module.canonical(dict(genesis, previous_receipt_sha256=None)))
        write_json(root / manifest["organization_ledger"]["ledger_head"]["path"], {
            "schema": manifest["organization_ledger"]["ledger_head"]["schema"],
            "head_sha256": sealed_digest.split(":")[1], "hb_epoch": 41})
        candidate = module.finish_verdict(root, None)["ledger_receipt_candidate"]
        want = "sha256:" + module.sha256_hex(module.canonical(candidate))
        release = self.org_receipt(cls, canonical_state_transition_receipt_sha256=want, source_transition_sha256=want,
                                   source_receipt_schema=candidate["schema"])
        pairs = [(genesis, None), (release, candidate if retain else None)]
        if order == "before":
            # the release receipt precedes the head the candidate was sealed on
            other = self.org_receipt(chain_genesis=True, note="other genesis")
            pairs = [(other, None), (release, candidate if retain else None), (genesis, None)]
        git_dir, _ = self.build_ledger(tmp, module, pairs)
        if tamper:
            work = git_dir.parent
            f = next((work / "receipts").glob("*.json"))
            doc = json.loads(f.read_text(encoding="utf-8"))
            doc["authority_effect"] = "TAMPERED"
            write_json(f, doc)
            git(work, "commit", "-q", "-am", "tamper")
            git(work, "update-ref", module.LEDGER_REF, "HEAD")
        return root, module, manifest, git_dir, candidate

    def test_ledger_copy_with_consuming_receipt_admits_only_the_ledger_predicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, module, manifest, git_dir, candidate = self.released_ledger(tmp)
            result = module.v_ledger(root, manifest, candidate, git_dir)
            self.assertEqual(result["disposition"], "ALLOW", json.dumps(result, sort_keys=True))
            self.assertEqual(result["chain_length"], 2)
            # the overall verdict still refuses: a caller-supplied customer result never becomes ALLOW
            verdict = module.finish_verdict(root, {"disposition": "ALLOW"}, ledger_copy=git_dir)
            self.assertEqual(verdict["predicates"][self.LEDGER], "ALLOW")
            self.assertEqual(verdict["disposition"], "FAIL_CLOSED")
            self.assertEqual(verdict["results"][self.NON_ALLOW]["failure_code"], "CUSTOMER_CONFORMANCE_ORIGIN_UNVERIFIED")

    def test_ledger_copy_negatives_fail_closed_with_six_fields(self) -> None:
        cases = {
            "class": ({"cls": "REPO_STATE_PROPAGATION"}, "ORGANIZATION_LEDGER_RECEIPT_NOT_BOUND_TO_CANDIDATE"),
            "source not retained": ({"retain": False}, "ORGANIZATION_LEDGER_RECEIPT_NOT_BOUND_TO_CANDIDATE"),
            "before sealed head": ({"order": "before"}, "ORGANIZATION_LEDGER_RECEIPT_NOT_AFTER_SEALED_HEAD"),
            "tampered receipt": ({"tamper": True}, "ORGANIZATION_LEDGER_CHAIN_INVALID"),
        }
        for name, (kw, code) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                root, module, manifest, git_dir, candidate = self.released_ledger(tmp, **kw)
                self.assert_six_field_refusal(module.v_ledger(root, manifest, candidate, git_dir), code)
        with tempfile.TemporaryDirectory() as tmp:
            root, module, manifest, _ = self.release_fixture(tmp)
            candidate = module.finish_verdict(root, None)["ledger_receipt_candidate"]
            git_dir, _ = self.build_ledger(tmp, module, [(self.org_receipt(chain_genesis=True), None)])
            self.assert_six_field_refusal(module.v_ledger(root, manifest, candidate, git_dir),
                                          "ORGANIZATION_LEDGER_RECEIPT_NOT_FOUND")
            self.assert_six_field_refusal(module.v_ledger(root, manifest, candidate, Path(tmp) / "absent"),
                                          "ORGANIZATION_LEDGER_CHAIN_INVALID")
            self.assert_six_field_refusal(module.v_ledger(root, manifest, {"forged": "candidate"}, git_dir),
                                          "ORGANIZATION_LEDGER_RECEIPT_NOT_FOUND")

    def test_finish_module_reads_no_clock_root_path_or_stegverse_module(self) -> None:
        source = FINISH_MODULE.read_text(encoding="utf-8")
        for forbidden in ("datetime", "time.time", "import time", "/var/lib", "urllib", "socket", "import stegverse",
                          "from stegverse"):
            self.assertNotIn(forbidden, source, forbidden)


if __name__ == "__main__":
    unittest.main()
