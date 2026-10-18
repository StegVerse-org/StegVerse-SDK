"""REPOSITORY_LEDGER_INITIALIZATION: plan, apply on local ledgers only, idempotence,
and a six-field refusal on every non-ALLOW. No network, no clock, no token."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("initialize_repository_ledger",
                                              ROOT / "scripts/initialize_repository_ledger.py")
init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(init)

MANIFEST_PATH = ROOT / ".stegverse/transition-ledger/initialization-manifest.v1.json"
SIX = init.SIX_FIELDS
EPOCH = "469411900"


def git(repo: Path, *args: str, data: bytes | None = None) -> str:
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(repo)}
    return subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True,
                          check=True, env=env).stdout.decode().strip()


def org_ledger(tmp: Path, with_other_repo_chain: bool = True) -> tuple[Path, str]:
    """A local bare repo holding a refs/stegverse/organization-ledger shaped like the StegVerse-org one."""
    repo = tmp / "org-ledger.git"
    subprocess.run(["git", "init", "-q", "--bare", str(repo)], check=True)
    blob = git(repo, "hash-object", "-w", "--stdin", data=b'{"organization": "StegVerse-org"}\n')
    entries = f"100644 blob {blob}\tHEAD.json\n"
    tree = git(repo, "mktree", data=entries.encode())
    if with_other_repo_chain:
        sub = git(repo, "mktree", data=f"100644 blob {blob}\tHEAD.json\n".encode())
        dotgithub = git(repo, "mktree", data=f"040000 tree {sub}\t.github\n".encode())
        org = git(repo, "mktree", data=f"040000 tree {dotgithub}\tStegVerse-org\n".encode())
        tree = git(repo, "mktree", data=(entries + f"040000 tree {org}\trepository-ledger\n").encode())
    commit = git(repo, "commit-tree", tree, "-m", "organization ledger append receipts/x.json")
    git(repo, "update-ref", "refs/stegverse/organization-ledger", commit)
    return repo, commit


def manifest_for(head: str, **overrides) -> bytes:
    m = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    m["expected_organization_ledger_head"] = head
    m.update(overrides)
    return (json.dumps(m, indent=2, sort_keys=True) + "\n").encode()


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


class RefusalShape(unittest.TestCase):
    def assertSixField(self, decision, disposition, code):
        self.assertEqual(decision["disposition"], disposition, decision)
        self.assertEqual(decision["failure_code"], code, decision)
        for field in SIX:
            self.assertTrue(decision.get(field), f"{field} missing: {decision}")
        self.assertFalse(decision["consequence_committed"])
        body = {k: v for k, v in decision.items() if k != "decision_sha256"}
        self.assertEqual(decision["decision_sha256"], init.sha(body))


class ContractAndManifestTests(RefusalShape):
    def test_contract_declares_the_subtree_of_the_existing_org_ledger_ref(self):
        location = init.load_contract()["repository_ledger_location"]
        self.assertEqual(location["repository"], "StegVerse-org/.github")
        self.assertEqual(location["ref"], "refs/stegverse/organization-ledger")
        self.assertEqual(location["namespace"], "repository-ledger/StegVerse-org/StegVerse-SDK")
        self.assertIs(location["new_ledger_root"], False)

    def test_committed_manifest_is_bound_to_the_contract_and_holds_no_epoch_or_secret(self):
        raw = MANIFEST_PATH.read_bytes()
        manifest = json.loads(raw)
        init.validate_manifest(manifest, init.load_contract())
        self.assertEqual(manifest["hb_epoch"], "SUPPLIED_AT_EXECUTION_NOT_IN_MANIFEST")
        self.assertNotRegex(raw.decode(), r"(?i)(token|secret|password|ghp_|github_pat_)")


class PlanTests(RefusalShape):
    def test_plan_on_git_ledger_writes_nothing_and_names_the_exact_genesis(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = org_ledger(Path(tmp))
            raw = manifest_for(head)
            d = init.decide(raw, digest(raw), EPOCH, f"git+{repo}#refs/stegverse/organization-ledger")
            self.assertEqual((d["disposition"], d["result"]), ("ALLOW", "PLANNED_NO_WRITE"), d)
            self.assertFalse(d["consequence_committed"])
            self.assertEqual(git(repo, "rev-parse", "refs/stegverse/organization-ledger"), head)
            g = d["genesis_receipt"]
            self.assertIsNone(g["previous_receipt_sha256"])
            self.assertIsNone(g["observed_at"])
            self.assertEqual(g["schema"], "stegverse.repo-transition-receipt/v1")
            self.assertEqual(g["hb_reference"]["epoch"], int(EPOCH))
            self.assertIs(g["hb_reference"]["derived_from_clock"], False)
            self.assertTrue(init.verify_receipt(g, g["receipt_sha256"]))
            self.assertEqual(d["would_write"], [
                "repository-ledger/StegVerse-org/StegVerse-SDK/receipts/" + g["receipt_sha256"][7:] + ".json",
                "repository-ledger/StegVerse-org/StegVerse-SDK/HEAD.json"])

    def test_the_genesis_is_deterministic_for_one_manifest_and_epoch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = org_ledger(Path(tmp))
            raw = manifest_for(head)
            loc = f"git+{repo}#refs/stegverse/organization-ledger"
            a = init.decide(raw, digest(raw), EPOCH, loc)["genesis_receipt"]
            b = init.decide(raw, digest(raw), EPOCH, loc)["genesis_receipt"]
            self.assertEqual(a, b)
            c = init.decide(raw, digest(raw), str(int(EPOCH) + 1), loc)["genesis_receipt"]
            self.assertNotEqual(a["receipt_sha256"], c["receipt_sha256"])


class ApplyTests(RefusalShape):
    def test_apply_on_a_local_git_ledger_appends_one_commit_and_reads_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = org_ledger(Path(tmp))
            raw = manifest_for(head)
            loc = f"git+{repo}#refs/stegverse/organization-ledger"
            d = init.decide(raw, digest(raw), EPOCH, loc, mode="apply")
            self.assertEqual((d["disposition"], d["result"], d["readback"]), ("ALLOW", "INITIALIZED", "VERIFIED"), d)
            after = git(repo, "rev-parse", "refs/stegverse/organization-ledger")
            self.assertEqual(d["organization_ledger_head_after"], after)
            self.assertEqual(git(repo, "rev-parse", after + "^"), head)  # fast-forward, nothing rewritten
            head_doc = json.loads(git(repo, "show", after + ":repository-ledger/StegVerse-org/StegVerse-SDK/HEAD.json"))
            self.assertEqual(head_doc["receipt_sha256"], d["genesis_receipt"]["receipt_sha256"])
            # the other repository's chain and the organization HEAD are untouched
            self.assertEqual(git(repo, "rev-parse", f"{head}:repository-ledger/StegVerse-org/.github"),
                             git(repo, "rev-parse", f"{after}:repository-ledger/StegVerse-org/.github"))
            self.assertEqual(git(repo, "rev-parse", f"{head}:HEAD.json"), git(repo, "rev-parse", f"{after}:HEAD.json"))

    def test_rerun_after_initialization_is_a_noop_allow(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = org_ledger(Path(tmp))
            raw = manifest_for(head)
            loc = f"git+{repo}#refs/stegverse/organization-ledger"
            init.decide(raw, digest(raw), EPOCH, loc, mode="apply")
            after = git(repo, "rev-parse", "refs/stegverse/organization-ledger")
            again = init.decide(raw, digest(raw), EPOCH, loc, mode="apply")
            self.assertEqual((again["disposition"], again["result"]),
                             ("ALLOW", "NOOP_ALREADY_INITIALIZED_BY_THIS_MANIFEST"), again)
            self.assertEqual(git(repo, "rev-parse", "refs/stegverse/organization-ledger"), after)

    def test_an_existing_different_chain_is_never_rerooted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, head = org_ledger(Path(tmp))
            raw = manifest_for(head)
            loc = f"git+{repo}#refs/stegverse/organization-ledger"
            init.decide(raw, digest(raw), EPOCH, loc, mode="apply")
            raw2 = manifest_for(git(repo, "rev-parse", "refs/stegverse/organization-ledger"))
            d = init.decide(raw2, digest(raw2), str(int(EPOCH) + 7), loc, mode="apply")
            self.assertSixField(d, "FAIL_CLOSED", "REPOSITORY_LEDGER_ALREADY_INITIALIZED")

    def test_apply_on_a_posix_root_writes_head_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = manifest_for("a" * 40)
            d = init.decide(raw, digest(raw), EPOCH, str(Path(tmp) / "ns"), mode="apply")
            self.assertEqual(d["result"], "INITIALIZED", d)
            head = json.loads((Path(tmp) / "ns/HEAD.json").read_text())
            receipt = json.loads((Path(tmp) / "ns/receipts" / (head["receipt_sha256"][7:] + ".json")).read_text())
            self.assertTrue(init.verify_receipt(receipt, head["receipt_sha256"]))


class RefusalTests(RefusalShape):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo, self.head = org_ledger(Path(self._tmp.name))
        self.loc = f"git+{self.repo}#refs/stegverse/organization-ledger"
        self.raw = manifest_for(self.head)

    def tearDown(self):
        self._tmp.cleanup()

    def unchanged(self):
        self.assertEqual(git(self.repo, "rev-parse", "refs/stegverse/organization-ledger"), self.head)

    def test_missing_epoch(self):
        d = init.decide(self.raw, digest(self.raw), None, self.loc, mode="apply")
        self.assertSixField(d, "FAIL_CLOSED", "HB_EPOCH_NOT_SUPPLIED"); self.unchanged()

    def test_invalid_epoch(self):
        for bad in ("-1", "1.5", "abc", " 3"):
            d = init.decide(self.raw, digest(self.raw), bad, self.loc, mode="apply")
            self.assertSixField(d, "FAIL_CLOSED", "HB_EPOCH_INVALID")
        self.unchanged()

    def test_manifest_digest_missing_or_mismatched(self):
        self.assertSixField(init.decide(self.raw, None, EPOCH, self.loc, mode="apply"),
                            "FAIL_CLOSED", "MANIFEST_HASH_NOT_SUPPLIED")
        self.assertSixField(init.decide(self.raw, "sha256:" + "0" * 64, EPOCH, self.loc, mode="apply"),
                            "FAIL_CLOSED", "MANIFEST_HASH_MISMATCH")
        self.unchanged()

    def test_manifest_not_bound_to_contract(self):
        for key, value in (("namespace", "repository-ledger/StegVerse-org/Other"), ("new_ledger_root", True),
                           ("organization_ledger_ref", "refs/heads/main"), ("repository", "StegVerse-Labs/StegVerse-SDK")):
            raw = manifest_for(self.head, **{key: value})
            self.assertSixField(init.decide(raw, digest(raw), EPOCH, self.loc, mode="apply"),
                                "DENY", "MANIFEST_NOT_BOUND_TO_CONTRACT")
        self.unchanged()

    def test_organization_ledger_head_moved(self):
        raw = manifest_for("b" * 40)
        self.assertSixField(init.decide(raw, digest(raw), EPOCH, self.loc, mode="apply"),
                            "FAIL_CLOSED", "ORGANIZATION_LEDGER_HEAD_MOVED")
        self.unchanged()

    def test_remote_ledger_location_is_refused(self):
        for loc in ("git+https://github.com/StegVerse-org/.github.git#refs/stegverse/organization-ledger",
                    "git+git@github.com:StegVerse-org/.github.git#refs/stegverse/organization-ledger",
                    "https://example.invalid/ledger"):
            self.assertSixField(init.decide(self.raw, digest(self.raw), EPOCH, loc, mode="apply"),
                                "FAIL_CLOSED", "LEDGER_LOCATION_NOT_LOCAL")

    def test_absent_organization_ledger_ref_is_never_rooted_here(self):
        empty = Path(self._tmp.name) / "empty.git"
        subprocess.run(["git", "init", "-q", "--bare", str(empty)], check=True)
        d = init.decide(self.raw, digest(self.raw), EPOCH, f"git+{empty}#refs/stegverse/organization-ledger", mode="apply")
        self.assertSixField(d, "FAIL_CLOSED", "ORGANIZATION_LEDGER_REF_ABSENT")

    def test_contract_without_location_fails_closed(self):
        contract = {k: v for k, v in init.load_contract().items() if k != "repository_ledger_location"}
        d = init.decide(self.raw, digest(self.raw), EPOCH, self.loc, contract=contract)
        self.assertSixField(d, "FAIL_CLOSED", "REPOSITORY_LEDGER_LOCATION_NOT_DECLARED")

    def test_cli_refusal_exits_nonzero_with_six_fields(self):
        out = subprocess.run([sys.executable, str(ROOT / "scripts/initialize_repository_ledger.py"),
                              "--manifest", str(MANIFEST_PATH), "--ledger-location", self.loc],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 1)
        self.assertSixField(json.loads(out.stdout), "FAIL_CLOSED", "MANIFEST_HASH_NOT_SUPPLIED")


class SourceBoundaryTests(unittest.TestCase):
    def test_source_reads_no_clock_no_token_and_no_network(self):
        text = (ROOT / "scripts/initialize_repository_ledger.py").read_text(encoding="utf-8")
        for forbidden in ("datetime", "time.time", "urllib", "http.client", "requests", "socket",
                          "GITHUB_TOKEN", "GH_TOKEN", "TVC_EPHEMERAL_GITHUB_TOKEN", '"push"'):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
