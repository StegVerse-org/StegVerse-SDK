#!/usr/bin/env python3
"""REPOSITORY_LEDGER_INITIALIZATION: a manifest-driven transition that creates
the first receipt (genesis) of the SDK's repository chain, with a receipt of its own.

This follows the existing pattern used by StegVerse-org/.github and
StegVerse-Labs/.github (and TVC#525): `.stegverse/transition-ledger/contract.json`
`repository_ledger_location` names a subtree
(`repository-ledger/<org>/<repo>`) of the organization's
`refs/stegverse/organization-ledger`. The repository chain is
`<namespace>/HEAD.json` plus `<namespace>/receipts/<sha256>.json`, each
receipt is `stegverse.repo-transition-receipt/v1`, and the first receipt is
the one whose `previous_receipt_sha256` is null. No second ledger root is
created (`new_ledger_root: false`).

Modes:
* plan (default): read only. It returns the decision and the exact genesis
  receipt that apply would write. Nothing is written.
* apply: writes the genesis receipt and HEAD.json, then reads them back. It
  accepts only a LOCAL ledger location: a POSIX directory, or
  `git+/absolute/path/to/repo#refs/stegverse/organization-ledger`. Remote
  locations are refused. Publishing the organization ledger ref is the
  organization's own append (organization-ledger-transition.yml under
  ORGANIZATION_LEDGER_LOCK), never this lane's.

Time comes only from the supplied hb_epoch. No clock is read and
`observed_at` is null. Every non-ALLOW carries the six fields. Stdlib plus the
git CLI only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / ".stegverse/transition-ledger/contract.json"
MANIFEST_SCHEMA = "stegverse.sdk.repository-ledger-initialization-manifest/v1"
DECISION_SCHEMA = "stegverse.sdk.repository-ledger-initialization-decision/v1"
RECEIPT_SCHEMA = "stegverse.repo-transition-receipt/v1"
TRANSITION_CLASS = "REPOSITORY_LEDGER_INITIALIZATION"
OWNING_GOAL = "ORGANIZATION-BATCH-CUSTODY-REPLAY-001"
ENTRYPOINT = "scripts/initialize_repository_ledger.py"
GIT_SCHEME = "git+"
EPOCH = re.compile(r"^[0-9]+$")
SHA_HEX = re.compile(r"^[0-9a-f]{64}$")
OID = re.compile(r"^[0-9a-f]{40}$")
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(value: Any) -> str:
    raw = value if isinstance(value, (bytes, bytearray)) else canon(value)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


class Refusal(Exception):
    def __init__(self, disposition: str, failure_code: str, failed_predicate: str,
                 required: str, next_attempt: str, retry: str = ENTRYPOINT) -> None:
        super().__init__(failure_code)
        self.fields = {
            "disposition": disposition,
            "failure_code": failure_code,
            "failed_predicate": failed_predicate,
            "required_evidence_or_repair": required,
            "retry_entrypoint": retry,
            "owning_existing_goal": OWNING_GOAL,
            "next_attempt": next_attempt,
        }


def _fail(code: str, predicate: str, required: str, next_attempt: str, **kw: str) -> Refusal:
    return Refusal("FAIL_CLOSED", code, predicate, required, next_attempt, **kw)


def _deny(code: str, predicate: str, required: str, next_attempt: str) -> Refusal:
    return Refusal("DENY", code, predicate, required, next_attempt)


# ---------------------------------------------------------------- stores
class PosixStore:
    """The namespace directory itself is the store root, as emit.py's lr() is."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.locator = str(root)

    def head_oid(self) -> str | None:
        return None

    def get(self, key: str) -> Any:
        path = self.root / key
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, files: dict[str, Any], expected_oid: str | None, message: str) -> str | None:
        for key, value in files.items():
            path = self.root / key
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            os.replace(tmp, path)
        return None


class GitRefStore:
    """A subtree of a ref in a LOCAL git repository. Writes are one commit whose
    parent is the observed ref head, published with update-ref's old-value
    compare-and-swap, so a lost race fails closed instead of overwriting."""

    def __init__(self, repo: Path, ref: str, namespace: str) -> None:
        self.repo, self.ref, self.namespace = repo, ref, namespace
        self.locator = f"{GIT_SCHEME}{repo}#{ref}:{namespace}"

    def _git(self, *args: str, data: bytes | None = None, check: bool = True) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update({"GIT_AUTHOR_NAME": "SDK repository ledger initialization",
                    "GIT_AUTHOR_EMAIL": "sdk@stegverse.invalid",
                    "GIT_COMMITTER_NAME": "SDK repository ledger initialization",
                    "GIT_COMMITTER_EMAIL": "sdk@stegverse.invalid",
                    # Fixed commit time: no clock is read for the ledger commit.
                    "GIT_AUTHOR_DATE": "1970-01-01T00:00:00Z",
                    "GIT_COMMITTER_DATE": "1970-01-01T00:00:00Z"})
        return subprocess.run(["git", "-C", str(self.repo), *args], input=data,
                              capture_output=True, env=env, check=check)

    def head_oid(self) -> str | None:
        out = self._git("rev-parse", "--verify", "-q", self.ref + "^{commit}", check=False)
        value = out.stdout.decode().strip()
        return value if out.returncode == 0 and OID.match(value) else None

    def get(self, key: str) -> Any:
        oid = self.head_oid()
        if oid is None:
            return None
        out = self._git("show", f"{oid}:{self.namespace}/{key}", check=False)
        if out.returncode != 0:
            return None
        return json.loads(out.stdout.decode("utf-8"))

    def write(self, files: dict[str, Any], expected_oid: str | None, message: str) -> str | None:
        if expected_oid is None:
            raise ValueError("a git ledger store is never rooted here")
        index = self.repo / ".sdk-ledger-init.index"
        env_index = {"GIT_INDEX_FILE": str(index)}
        try:
            def git_idx(*args: str, data: bytes | None = None) -> str:
                env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
                env.update(env_index)
                return subprocess.run(["git", "-C", str(self.repo), *args], input=data,
                                      capture_output=True, env=env, check=True).stdout.decode().strip()
            git_idx("read-tree", expected_oid)
            for key, value in files.items():
                blob = self._git("hash-object", "-w", "--stdin",
                                 data=(json.dumps(value, indent=2, sort_keys=True) + "\n").encode()).stdout.decode().strip()
                git_idx("update-index", "--add", "--cacheinfo", f"100644,{blob},{self.namespace}/{key}")
            tree = git_idx("write-tree")
        finally:
            if index.exists():
                index.unlink()
        commit = self._git("commit-tree", tree, "-p", expected_oid, "-m", message).stdout.decode().strip()
        swap = self._git("update-ref", self.ref, commit, expected_oid, check=False)
        if swap.returncode != 0:
            raise _fail("ORGANIZATION_LEDGER_HEAD_MOVED", "ORGANIZATION_LEDGER_REF_UNCHANGED_SINCE_OBSERVED",
                        "re-observe the organization ledger head and re-issue the manifest bound to it",
                        "on a manifest bound to the current organization ledger head")
        return commit


def open_store(location: str, namespace: str, ref: str) -> PosixStore | GitRefStore:
    if location.startswith(GIT_SCHEME):
        body = location[len(GIT_SCHEME):]
        repo_part, _, ref_part = body.partition("#")
        ref_part = ref_part.split(":", 1)[0] or ref
        if "://" in repo_part or repo_part.startswith("git@") or not repo_part.startswith("/"):
            raise _fail("LEDGER_LOCATION_NOT_LOCAL", "LEDGER_LOCATION_IS_A_LOCAL_MATERIALIZED_CHECKOUT",
                        "supply git+/absolute/path#<ref> of a local checkout; publication of the ref is the "
                        "organization's own append, not this transition's",
                        "with a local materialized ledger checkout")
        if ref_part != ref:
            raise _deny("LEDGER_REF_NOT_DESIGNATED", "LEDGER_REF_EQUALS_CONTRACT_REF",
                        f"use the designated ref {ref}", "with the designated ref")
        repo = Path(repo_part)
        if not repo.exists():
            raise _fail("LEDGER_LOCATION_UNREADABLE", "LEDGER_LOCATION_EXISTS",
                        "materialize the organization ledger checkout first", "after materialization")
        return GitRefStore(repo, ref, namespace)
    if "://" in location:
        raise _fail("LEDGER_LOCATION_NOT_LOCAL", "LEDGER_LOCATION_IS_A_LOCAL_MATERIALIZED_CHECKOUT",
                    "supply a local POSIX directory or git+/absolute/path#<ref>",
                    "with a local materialized ledger location")
    return PosixStore(Path(location).expanduser().resolve())


# ---------------------------------------------------------------- decision
def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def hb_reference(hb_epoch: str | None) -> dict[str, Any]:
    if hb_epoch is None or hb_epoch == "":
        raise _fail("HB_EPOCH_NOT_SUPPLIED", "SUPPLIED_HB_EPOCH_PRESENT",
                    "supply --hb-epoch from the heartbeat carrier; no clock is read in its place",
                    "with a supplied hb_epoch")
    if not isinstance(hb_epoch, str) or not EPOCH.match(hb_epoch):
        raise _fail("HB_EPOCH_INVALID", "SUPPLIED_HB_EPOCH_IS_A_NON_NEGATIVE_INTEGER",
                    "supply hb_epoch as a decimal digit string", "with a valid hb_epoch")
    epoch = int(hb_epoch)
    return {"authority_effect": "NONE", "derived_from_clock": False, "epoch": epoch,
            "generation": epoch, "heartbeat_id": f"HB:{epoch}", "phase_offset_ns": None,
            "progression_dependency": "SUPPLIED_EPOCH"}


def validate_manifest(manifest: Any, contract: dict[str, Any]) -> dict[str, Any]:
    location = contract.get("repository_ledger_location")
    if not isinstance(location, dict):
        raise _fail("REPOSITORY_LEDGER_LOCATION_NOT_DECLARED", "CONTRACT_DECLARES_REPOSITORY_LEDGER_LOCATION",
                    "declare repository_ledger_location in .stegverse/transition-ledger/contract.json",
                    "after the contract declares the location")
    if not isinstance(manifest, dict) or manifest.get("schema") != MANIFEST_SCHEMA:
        raise _deny("MANIFEST_SCHEMA_MISMATCH", "MANIFEST_SCHEMA_IS_" + MANIFEST_SCHEMA,
                    "supply a " + MANIFEST_SCHEMA + " manifest", "with a conforming manifest")
    expected = {
        "repository": contract["repository"],
        "transition_class": TRANSITION_CLASS,
        "organization_ledger_repository": location.get("repository"),
        "organization_ledger_ref": location.get("ref"),
        "namespace": location.get("namespace"),
        "new_ledger_root": False,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise _deny("MANIFEST_NOT_BOUND_TO_CONTRACT", "MANIFEST_" + key.upper() + "_EQUALS_CONTRACT",
                        f"set {key} to {value!r} as declared by the contract", "with a contract-bound manifest")
    if location.get("namespace") != "repository-ledger/" + contract["repository"] or location.get("new_ledger_root") is not False:
        raise _deny("REPOSITORY_LEDGER_LOCATION_INVALID", "NAMESPACE_IS_REPOSITORY_LEDGER_SUBTREE_OF_EXISTING_REF",
                    "namespace must be repository-ledger/<repository> on an existing ref", "after contract repair")
    head = manifest.get("expected_organization_ledger_head")
    if not isinstance(head, str) or not OID.match(head):
        raise _deny("EXPECTED_LEDGER_HEAD_NOT_BOUND", "MANIFEST_BINDS_OBSERVED_ORGANIZATION_LEDGER_HEAD",
                    "bind expected_organization_ledger_head to the observed 40-hex commit", "with a bound head")
    return manifest


def genesis_receipt(manifest: dict[str, Any], manifest_sha256: str, contract: dict[str, Any],
                    hb: dict[str, Any]) -> dict[str, Any]:
    repository = contract["repository"]
    contract_sha256 = sha(contract)
    body = {
        "schema": RECEIPT_SCHEMA,
        "repository": repository,
        "transition_id": f"{TRANSITION_CLASS}:{repository}",
        "transition_class": TRANSITION_CLASS,
        "predecessor_state_sha256": sha({"repository": repository, "repository_ledger": "ABSENT",
                                         "organization_ledger_head": manifest["expected_organization_ledger_head"]}),
        "successor_state_sha256": sha({"repository": repository, "repository_ledger": "INITIALIZED",
                                       "namespace": manifest["namespace"], "contract_sha256": contract_sha256}),
        "evidence": {
            "authority_effect": "NONE_INITIALIZATION_ONLY",
            "manifest_sha256": manifest_sha256,
            "contract_sha256": contract_sha256,
            "organization_ledger_repository": manifest["organization_ledger_repository"],
            "organization_ledger_ref": manifest["organization_ledger_ref"],
            "organization_ledger_head_observed": manifest["expected_organization_ledger_head"],
            "namespace": manifest["namespace"],
            "new_ledger_root": False,
        },
        "authority_effect": "NONE",
        "hb_reference": hb,
        "observed_at": None,
        "previous_receipt_sha256": None,
    }
    return {**body, "receipt_sha256": sha(body)}


def verify_receipt(receipt: Any, address: str) -> bool:
    return (isinstance(receipt, dict) and receipt.get("receipt_sha256") == address
            and sha({k: v for k, v in receipt.items() if k != "receipt_sha256"}) == address)


def decide(manifest_bytes: bytes, manifest_sha256: str | None, hb_epoch: str | None, location: str,
           mode: str = "plan", contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = load_contract() if contract is None else contract
    attempt: dict[str, Any] = {"schema": DECISION_SCHEMA, "transition_class": TRANSITION_CLASS,
                               "repository": contract.get("repository"), "mode": mode,
                               "consequence_committed": False, "authority_effect": "NONE"}
    try:
        if mode not in ("plan", "apply"):
            raise _deny("MODE_NOT_ADMITTED", "MODE_IS_PLAN_OR_APPLY", "use --mode plan or apply", "with a valid mode")
        observed = sha(manifest_bytes)
        attempt["manifest_sha256"] = observed
        if not manifest_sha256:
            raise _fail("MANIFEST_HASH_NOT_SUPPLIED", "MANIFEST_SHA256_SUPPLIED",
                        "supply --manifest-sha256 for the exact manifest bytes", "with the manifest digest")
        if manifest_sha256 != observed:
            raise _fail("MANIFEST_HASH_MISMATCH", "MANIFEST_BYTES_HASH_TO_SUPPLIED_DIGEST",
                        "supply the manifest whose bytes hash to --manifest-sha256", "with matching manifest bytes")
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise _fail("MANIFEST_UNREADABLE", "MANIFEST_IS_JSON", "supply a JSON manifest", "with a readable manifest")
        manifest = validate_manifest(manifest, contract)
        hb = hb_reference(hb_epoch)
        attempt["hb_reference"] = hb
        store = open_store(location, manifest["namespace"], manifest["organization_ledger_ref"])
        attempt["ledger_location"] = store.locator
        receipt = genesis_receipt(manifest, observed, contract, hb)
        address = receipt["receipt_sha256"]
        receipt_key = "receipts/" + address.split(":", 1)[1] + ".json"
        head_doc = {"receipt_path": f"{manifest['organization_ledger_ref']}:{manifest['namespace']}/{receipt_key}",
                    "receipt_sha256": address, "repository": contract["repository"]}
        attempt["genesis_receipt"] = receipt

        existing = store.get("HEAD.json")
        if existing is not None:
            if isinstance(existing, dict) and existing.get("receipt_sha256") == address \
                    and verify_receipt(store.get(receipt_key), address):
                attempt.update({"disposition": "ALLOW", "result": "NOOP_ALREADY_INITIALIZED_BY_THIS_MANIFEST",
                                "readback": "VERIFIED"})
                return _seal(attempt)
            raise _fail("REPOSITORY_LEDGER_ALREADY_INITIALIZED", "REPOSITORY_LEDGER_HEAD_ABSENT_BEFORE_INITIALIZATION",
                        "none: an existing chain is extended by its own transitions, never re-rooted",
                        "none for initialization; append through .stegverse/transition-ledger/emit.py")

        head_oid = store.head_oid()
        if isinstance(store, GitRefStore):
            if head_oid is None:
                raise _fail("ORGANIZATION_LEDGER_REF_ABSENT", "DESIGNATED_ORGANIZATION_LEDGER_REF_EXISTS",
                            "the organization ledger ref must already exist (new_ledger_root false)",
                            "after the organization ledger ref is materialized")
            if head_oid != manifest["expected_organization_ledger_head"]:
                raise _fail("ORGANIZATION_LEDGER_HEAD_MOVED", "ORGANIZATION_LEDGER_REF_UNCHANGED_SINCE_OBSERVED",
                            "re-observe the organization ledger head and re-issue the manifest bound to it",
                            "on a manifest bound to the current organization ledger head")
        attempt["organization_ledger_head_before"] = head_oid
        files = {receipt_key: receipt, "HEAD.json": head_doc}
        attempt["would_write"] = [f"{manifest['namespace']}/{k}" for k in files]
        if mode == "plan":
            attempt.update({"disposition": "ALLOW", "result": "PLANNED_NO_WRITE"})
            return _seal(attempt)

        message = f"organization ledger append {manifest['namespace']}/{receipt_key}"
        after = store.write(files, head_oid, message)
        attempt["consequence_committed"] = True
        attempt["organization_ledger_head_after"] = after
        read_head = store.get("HEAD.json")
        if read_head != head_doc or not verify_receipt(store.get(receipt_key), address):
            raise _fail("READBACK_MISMATCH", "WRITTEN_GENESIS_READS_BACK_BYTE_EQUAL",
                        "inspect the ledger location; nothing is re-minted over a mismatch",
                        "after the ledger location is inspected")
        attempt.update({"disposition": "ALLOW", "result": "INITIALIZED", "readback": "VERIFIED"})
        return _seal(attempt)
    except Refusal as refusal:
        attempt.update(refusal.fields)
        return _seal(attempt)


def _seal(attempt: dict[str, Any]) -> dict[str, Any]:
    body = {k: v for k, v in attempt.items() if k != "decision_sha256"}
    return {**body, "decision_sha256": sha(body)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--hb-epoch")
    parser.add_argument("--ledger-location", required=True)
    parser.add_argument("--mode", default="plan")
    parser.add_argument("--receipt-out")
    args = parser.parse_args(argv)
    try:
        raw = Path(args.manifest).read_bytes()
    except OSError:
        raw = b""
    decision = decide(raw, args.manifest_sha256, args.hb_epoch, args.ledger_location, args.mode)
    text = json.dumps(decision, indent=2, sort_keys=True) + "\n"
    if args.receipt_out:
        Path(args.receipt_out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if decision.get("disposition") == "ALLOW" else 1


if __name__ == "__main__":
    sys.exit(main())
