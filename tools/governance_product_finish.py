"""GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001: E0 verifiers for the sealed expected_evidence_predicates, the finish verdict
bound to the TV/TVC release receipt, and the organization-ledger receipt candidate for GOVERNANCE_PRODUCT_RELEASE.

Every verifier reads .stegverse/governance-product/release-manifest.v1.json and the files and receipts it names, by
path. Each returns ALLOW or a six-field FAIL_CLOSED (failure_code, failed_predicate, required_evidence_or_repair,
retry_entrypoint, owning_existing_goal, next_attempt) and never raises: a missing or malformed input is a returned
refusal that names its next attempt. Each declares its lowest supported mode (E0) and its degraded form.

Ledger: this module emits a stegverse.canonical-state-transition-receipt/v1 candidate for the organization ledger
writer to append under ORGANIZATION_LEDGER_LOCK. It never appends, pushes or dispatches. hb_epoch and the prior state
come from the sealed organization-ledger head readback named in the manifest, never from a clock.

Lowest supported mode: E0 (standard library; git only to read the release-ref tree; no clock, no network, no LLM).
This module imports no module of the stegverse package; it reads the gate files as data.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

MANIFEST = ".stegverse/governance-product/release-manifest.v1.json"
GOAL = "GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001 (StegVerse-org/.github#164; StegVerse-Labs/.github#3326)"
RETRY = "python -m unittest tests.test_governance_product_finish_point (StegVerse-org/StegVerse-SDK)"
SIX = ("failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint", "owning_existing_goal",
       "next_attempt")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
NON_ALLOW_PREDICATE = "NON_ALLOW_PRODUCES_NO_EFFECT_IN_CUSTOMER_CONFORMANCE_RUN"
LEDGER_PREDICATE = "ORGANIZATION_RECEIPT_APPENDED_UNDER_LOCK:GOVERNANCE_PRODUCT_RELEASE"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def allow(predicate: str, **detail: Any) -> dict[str, Any]:
    return {"disposition": "ALLOW", "predicate": predicate, **detail}


def refuse(predicate: str, code: str, repair: str, nxt: str, **detail: Any) -> dict[str, Any]:
    return {"disposition": "FAIL_CLOSED", "predicate": predicate, "failure_code": code, "failed_predicate": predicate,
            "required_evidence_or_repair": repair, "retry_entrypoint": RETRY, "owning_existing_goal": GOAL,
            "next_attempt": nxt, **detail}


def _text(root: Path, rel: str) -> str | None:
    p = root / rel
    try:
        return p.read_text(encoding="utf-8") if p.is_file() else None
    except (OSError, UnicodeDecodeError):
        return None


def _json(root: Path, rel: str) -> Any:
    t = _text(root, rel)
    if t is None:
        return None
    try:
        return json.loads(t)
    except (ValueError, RecursionError):
        return ValueError("malformed")


def load_manifest(root: Path) -> Any:
    return _json(root, MANIFEST)


def _git(root: Path, *args: str) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)
    return p.returncode, p.stdout.strip()


def _pyproject_version(text: str) -> str | None:
    m = re.search(r"(?m)^\[project\][^\[]*?^version\s*=\s*['\"]([^'\"]+)['\"]", text, re.S)
    return m.group(1) if m else None


def _pyproject_dependencies(text: str) -> list[str] | None:
    m = re.search(r"(?ms)^\[project\].*?^dependencies\s*=\s*\[(.*?)^\]", text)
    if not m:
        return None
    body = "\n".join(line.split("#", 1)[0] for line in m.group(1).splitlines())
    return sorted(re.findall(r"['\"]([^'\"]+)['\"]", body))


def _release_receipt(root: Path, man: dict[str, Any], predicate: str) -> tuple[dict[str, Any] | None, dict | None]:
    spec = man.get("release_receipt") or {}
    rel = spec.get("path")
    rec = _json(root, rel) if isinstance(rel, str) else None
    nxt = "on the TV/TVC release receipt event (the release transition commits the receipt at " + str(rel) + ")"
    if rec is None:
        return None, refuse(predicate, "RELEASE_RECEIPT_ABSENT",
                            f"the TV/TVC release receipt {rel} ({spec.get('schema')}) naming tag and commit", nxt)
    if not isinstance(rec, dict):
        return None, refuse(predicate, "RELEASE_RECEIPT_MALFORMED", f"{rel} must be a JSON object", nxt)
    bad = [k for k, ok in (("schema", rec.get("schema") == spec.get("schema")),
                           ("issuer", rec.get("issuer") == spec.get("issuer")),
                           ("repository", rec.get("repository") == spec.get("repository")),
                           ("commit", isinstance(rec.get("commit"), str) and bool(HEX40.match(rec["commit"]))),
                           ("tag", isinstance(rec.get("tag"), str) and rec["tag"].startswith("v")),
                           ("allow_tag_update", rec.get("allow_tag_update") is False)) if not ok]
    if bad:
        return None, refuse(predicate, "RELEASE_RECEIPT_FIELDS_INVALID",
                            f"{rel}: fields {bad} must match the manifest's release_receipt and carry a 40-hex commit, "
                            "a v-tag and allow_tag_update false", nxt, invalid_fields=bad)
    return rec, None


# ------------------------------------------------------------------ verifiers (one per sealed predicate)
def v_product_claim(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "PRODUCT_CLAIM_LIMITED_TO_VERIFIABLE_RECEIPT_CHAIN_ON_CUSTOMER_SUPPLIED_MANIFEST_CONSTRAINTS"
    spec = man.get("product_claim") or {}
    findings = []
    for rel in spec.get("documents", []):
        t = _text(root, rel)
        if t is None:
            findings.append(f"{rel}: missing")
            continue
        low = t.lower()
        if not any(s.lower() in low for s in spec.get("required_any", [])):
            findings.append(f"{rel}: no statement of {spec.get('required_any')}")
        findings += [f"{rel}: forbidden '{s}'" for s in spec.get("forbidden", []) if s.lower() in low]
    if findings or not spec.get("documents"):
        return refuse(p, "PRODUCT_CLAIM_EXCEEDS_RECEIPT_CHAIN", "limit the claim documents to the receipt-chain claim: "
                      + "; ".join(findings or ["no claim documents declared"]), "on the next push that changes the claim documents",
                      findings=findings)
    return allow(p, documents=spec["documents"])


def v_package_identity(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "PACKAGE_VERSION_IDENTITY_CONSISTENT_ACROSS_PYPROJECT_INIT_VERSION_JSON"
    spec = man.get("package_identity") or {}
    py = _text(root, spec.get("pyproject", ""))
    init = _text(root, spec.get("init", ""))
    vj = _json(root, spec.get("version_json", ""))
    seen = {"pyproject": _pyproject_version(py) if py else None,
            "init": (re.search(r"(?m)^__version__\s*=\s*['\"]([^'\"]+)['\"]", init or "") or [None, None])[1],
            "version_json": vj.get(spec.get("version_json_field")) if isinstance(vj, dict) else None}
    if None in seen.values() or len(set(seen.values())) != 1:
        return refuse(p, "PACKAGE_VERSION_IDENTITY_MISMATCH", f"make the three versions equal and present: {seen}",
                      "on the next push that changes a version file", observed=seen)
    return allow(p, version=seen["pyproject"])


def v_pinned_tree(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "PINNED_REF_TREE_CONTAINS_GOVERNANCE_GATE_WORKFLOW_AND_MODULE"
    rec, bad = _release_receipt(root, man, p)
    if bad:
        return bad
    missing = []
    for path in man.get("gate_paths", []):
        rc, _ = _git(root, "cat-file", "-e", f"{rec['commit']}:{path}")
        if rc != 0:
            missing.append(path)
    if missing or not man.get("gate_paths"):
        return refuse(p, "RELEASE_REF_TREE_LACKS_GATE", f"the release commit {rec['commit']} must contain {missing or 'gate_paths'} "
                      "(degraded E0: the commit must be present in the local clone; fetch it read-only first)",
                      "on the next TV/TVC release receipt event", missing=missing)
    return allow(p, commit=rec["commit"], paths=man["gate_paths"])


def v_immutable_tag(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "IMMUTABLE_TAG_AND_GITHUB_RELEASE_PUBLISHED_UNDER_TV_TVC_AUTHORITY"
    rec, bad = _release_receipt(root, man, p)
    if bad:
        return bad
    ident = v_package_identity(root, man)
    if ident["disposition"] != "ALLOW" or rec["tag"] != "v" + ident["version"]:
        return refuse(p, "RELEASE_TAG_NOT_PACKAGE_VERSION", f"tag {rec['tag']} must be v<package version> "
                      f"({ident.get('version')})", "on the next TV/TVC release receipt event")
    if not (isinstance(rec.get("github_release"), dict) and rec["github_release"].get("state") == "PUBLISHED_VERIFIED"):
        return refuse(p, "GITHUB_RELEASE_NOT_PUBLISHED_VERIFIED", "the release receipt's github_release.state must be "
                      "PUBLISHED_VERIFIED", "on the next TV/TVC release receipt event")
    rc, peeled = _git(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{rec['tag']}^{{commit}}")
    if rc != 0 or peeled != rec["commit"]:
        return refuse(p, "RELEASE_TAG_NOT_AT_RECEIPT_COMMIT", f"refs/tags/{rec['tag']} must peel to {rec['commit']} "
                      f"(observed {peeled or 'absent'}; degraded E0: fetch tags read-only)", "on the next TV/TVC release receipt event")
    # The tag is observed in git; the TV/TVC issuance and the published GitHub release are claims in a committed file.
    # A committed receipt is not evidence that TV/TVC issued it, so the authority half fails closed until an
    # authenticated issuer route is bound (the same open decision as the C-review receipt, #556 6466819899).
    return refuse(p, "RELEASE_RECEIPT_PROVENANCE_UNVERIFIED", "bind the TV/TVC release receipt to an authenticated "
                  "issuer; the tag is observed but a committed receipt file does not prove TV/TVC issuance or the "
                  "GitHub release state", "on the decision naming the issuer route", tag=rec["tag"], commit=rec["commit"],
                  tag_observed_at_commit=True)


def v_release_notes(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "RELEASE_NOTES_SUPERSEDE_V1_0_1_SAFETY_STACK_OVERCLAIM"
    spec = man.get("release_notes") or {}
    t = _text(root, spec.get("path", ""))
    missing = list(spec.get("required", [])) if t is None else [s for s in spec.get("required", []) if s not in t]
    if t is None or missing or not spec.get("required"):
        return refuse(p, "RELEASE_NOTES_DO_NOT_SUPERSEDE_V1_0_1", f"{spec.get('path')} must contain {missing}",
                      "on the next push that changes the release notes", missing=missing)
    return allow(p, path=spec["path"])


def v_quickstart(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "CUSTOMER_QUICKSTART_INSTALL_UNINSTALL_AND_NONCLAIMS_PUBLISHED"
    spec = man.get("quickstart") or {}
    t = _text(root, spec.get("path", ""))
    heads = [spec.get(k) for k in ("install_heading", "uninstall_heading", "nonclaims_heading")]
    missing = [h for h in heads if not h or t is None or h not in t.splitlines()]
    if missing:
        return refuse(p, "QUICKSTART_SECTION_MISSING", f"{spec.get('path')} must have the headings {missing}",
                      "on the next push that changes the quickstart", missing=missing)
    return allow(p, path=spec["path"])


def v_no_new_dependency(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "NO_NEW_RUNTIME_DEPENDENCY_INTRODUCED"
    spec = man.get("dependencies") or {}
    t = _text(root, spec.get("pyproject", ""))
    deps = _pyproject_dependencies(t) if t else None
    base = sorted(spec.get("runtime_baseline", [])) if isinstance(spec.get("runtime_baseline"), list) else None
    if deps is None or base is None or deps != base:
        return refuse(p, "RUNTIME_DEPENDENCY_CHANGED", f"[project].dependencies must equal the manifest baseline {base}; "
                      f"observed {deps}", "on the next push that changes pyproject.toml", observed=deps)
    return allow(p, dependencies=deps)


def verify_chain(chain: Any) -> tuple[bool, str]:
    """Independent check of a hash-linked receipt chain: each entry's prior_state_ref_or_hash is the sha256 of the
    canonical JSON of the previous entry, and each entry's receipt_sha256 is the sha256 of itself without that field."""
    if not isinstance(chain, list) or not chain:
        return False, "chain must be a non-empty list"
    prev = None
    for i, entry in enumerate(chain):
        if not isinstance(entry, dict):
            return False, f"entry {i} is not an object"
        body = {k: v for k, v in entry.items() if k != "receipt_sha256"}
        if entry.get("receipt_sha256") != sha256_hex(canonical(body)):
            return False, f"entry {i} receipt_sha256 mismatch"
        if i and entry.get("prior_state_ref_or_hash") != prev:
            return False, f"entry {i} does not link to entry {i - 1}"
        prev = sha256_hex(canonical(entry))
    return True, "ok"


def v_receipt_chain(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "INDEPENDENT_RECEIPT_CHAIN_VERIFICATION_PASS_AND_TAMPER_FAIL"
    rel = (man.get("receipt_chain") or {}).get("fixture", "")
    chain = _json(root, rel)
    ok, why = verify_chain(chain)
    if not ok:
        return refuse(p, "RECEIPT_CHAIN_VERIFICATION_FAILED", f"{rel}: {why}", "on the next push that changes the chain")
    tampered = json.loads(json.dumps(chain))
    tampered[-1]["transition_outcome"] = "TAMPERED"
    t_ok, _ = verify_chain(tampered)
    if t_ok:
        return refuse(p, "RECEIPT_CHAIN_TAMPER_NOT_DETECTED", "a tampered chain must fail verification",
                      "on the next push that changes the verifier")
    return allow(p, entries=len(chain), tamper="FAIL_DETECTED")


def v_license(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "LICENSE_AND_TERMS_FILE_SHA256_MATCHES_RELEASE_MANIFEST"
    spec = man.get("license") or {}
    lp = root / spec.get("path", "LICENSE")
    seen = sha256_hex(lp.read_bytes()) if lp.is_file() else "MISSING"
    py = _text(root, "pyproject.toml") or ""
    text_ok = re.search(r"(?m)^license\s*=\s*\{\s*text\s*=\s*['\"]" + re.escape(str(spec.get("pyproject_license_text")))
                        + r"['\"]", py) is not None
    if seen != spec.get("sha256") or not text_ok:
        return refuse(p, "LICENSE_FILE_HASH_MISMATCH", f"{spec.get('path')} sha256 must be {spec.get('sha256')} (observed "
                      f"{seen}) and pyproject license text {spec.get('pyproject_license_text')}",
                      "on the next push that changes LICENSE or pyproject.toml", observed=seen)
    cr = spec.get("c_review_receipt") or {}
    rec = _json(root, cr.get("path", ""))
    if not (isinstance(rec, dict) and rec.get("schema") == cr.get("schema") and rec.get("license_sha256") == seen
            and rec.get("disposition") == "ALLOW"):
        return refuse(p, "C_REVIEW_RECEIPT_PENDING", f"class C decision, provisional at E1: a C-review receipt at "
                      f"{cr.get('path')} ({cr.get('schema')}) with license_sha256 {seen} and disposition ALLOW",
                      "on the C-review receipt event", provisional_mode="E1", license_sha256=seen)
    # A committed C-review JSON is a claim that the review happened, not evidence of who reviewed: it never becomes
    # this predicate's ALLOW. The authenticating route (a TV/TVC-issued review receipt, an organization-ledger receipt,
    # or another the owner names) is an open decision on StegVerse-org/StegVerse-SDK#556; until one is bound here the
    # predicate fails closed whatever the JSON says.
    return refuse(p, "C_REVIEW_PROVENANCE_UNVERIFIED", "bind the C-review receipt to an authenticated issuer (route open "
                  "on StegVerse-org/StegVerse-SDK#556: TV/TVC review receipt, organization-ledger receipt, or owner-named); "
                  "a committed local review file is not evidence of the reviewer", "on the decision naming the route",
                  provisional_mode="E1", license_sha256=seen)


def v_rollback(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "ROLLBACK_PROCEDURE_DOCUMENTED_WITHOUT_TAG_RETARGET"
    spec = man.get("rollback") or {}
    t = _text(root, spec.get("document", ""))
    missing = list(spec.get("required", [])) if t is None else [s for s in spec.get("required", []) if s not in t]
    if spec.get("mode") != "SUPERSEDE_NEVER_RETARGET" or t is None or missing:
        return refuse(p, "ROLLBACK_PROCEDURE_NOT_SUPERSEDE_ONLY", f"rollback.mode SUPERSEDE_NEVER_RETARGET and "
                      f"{spec.get('document')} containing {missing}", "on the next push that changes the rollback document",
                      missing=missing)
    return allow(p, document=spec["document"])


def v_entitlement(root: Path, man: dict[str, Any]) -> dict[str, Any]:
    p = "ENTITLEMENT_SEPARATE_FROM_DISPOSITION_CONSUMING_SDK_COST_DERIVED_TIER_PRICING_OUTPUT"
    spec = man.get("entitlement") or {}
    hits = []
    for rel in man.get("gate_paths", []):
        t = (_text(root, rel) or "").lower()
        hits += [f"{rel}:{tok}" for tok in spec.get("gate_forbidden_tokens", []) if tok.lower() in t]
    out = _json(root, spec.get("pricing_output", ""))
    if spec.get("mode") != "SEPARATE_FROM_DISPOSITION" or hits:
        return refuse(p, "ENTITLEMENT_COUPLED_TO_DISPOSITION", f"the gate files must carry no entitlement input: {hits}",
                      "on the next push that changes the gate files (routed to SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001)",
                      hits=hits)
    if not isinstance(out, dict):
        return refuse(p, "COST_DERIVED_TIER_PRICING_OUTPUT_ABSENT", f"the consumed SDK-COST-DERIVED-TIER-PRICING-001 "
                      f"output {spec.get('pricing_output')} as a JSON object", "on that Goal's next output event")
    return allow(p, pricing_output=spec["pricing_output"], pricing_output_sha256=sha256_hex(canonical(out)))


LEDGER_REF = "refs/stegverse/organization-ledger"
LEDGER_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
LEDGER_MAX_RECEIPTS = 100000
GIT_OID = re.compile(r"^[0-9a-f]{40}$")


def _ledger_ref_oid(git_dir: Path) -> str | None:
    """The commit the ledger ref of a local git copy points at, or None. git only; no network."""
    try:
        p = subprocess.run(["git", "--git-dir", str(git_dir), "rev-parse", "--verify", "--quiet",
                            LEDGER_REF + "^{commit}"], capture_output=True, check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    oid = p.stdout.decode("ascii", "replace").strip() if p.returncode == 0 else ""
    return oid if GIT_OID.fullmatch(oid) else None


def _ledger_doc(git_dir: Path, path: str, rev: str = LEDGER_REF) -> Any:
    """One JSON document from a revision of a local git copy (the ledger ref by default), or None. git only; no
    network."""
    try:
        p = subprocess.run(["git", "--git-dir", str(git_dir), "show", f"{rev}:{path}"], capture_output=True,
                           check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None


def _ledger_sha(value: Any) -> str:
    # The organization ledger's own digest form (StegVerse-org/.github resident-runtime/aggregate_repo_transition.py
    # sha): "sha256:" + sha256 of the same canonical JSON this module uses.
    return "sha256:" + sha256_hex(canonical(value))


def read_ledger_chain(git_dir: Path, rev: str = LEDGER_REF) -> tuple[list[dict[str, Any]] | None, tuple[str, str] | None]:
    """Walk refs/stegverse/organization-ledger in a local copy from HEAD to genesis, the way the organization's own
    readback (resident-runtime/organization_ledger_readback.py) does: every receipt verifies against its own body and
    the chain has no gap, cycle or fork. Returns (chain oldest first, None) or (None, (failed check, detail))."""
    head = _ledger_doc(git_dir, "HEAD.json", rev)
    if not isinstance(head, dict):
        return None, ("ORGANIZATION_LEDGER_HEAD_PRESENT", f"no readable HEAD.json on {LEDGER_REF} in {git_dir}")
    chain: list[dict[str, Any]] = []
    cursor, seen = head.get("receipt_sha256"), set()
    while cursor is not None:
        if not (isinstance(cursor, str) and LEDGER_DIGEST.match(cursor)):
            return None, ("ORGANIZATION_LEDGER_DIGEST_WELL_FORMED", str(cursor))
        if cursor in seen or len(seen) >= LEDGER_MAX_RECEIPTS:
            return None, ("ORGANIZATION_LEDGER_CHAIN_IS_ACYCLIC", cursor)
        seen.add(cursor)
        receipt = _ledger_doc(git_dir, "receipts/" + cursor.split(":", 1)[1] + ".json", rev)
        if not isinstance(receipt, dict):
            return None, ("ORGANIZATION_LEDGER_CHAIN_IS_COMPLETE", "missing " + cursor)
        body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
        if receipt.get("receipt_sha256") != cursor or _ledger_sha(body) != cursor:
            return None, ("ORGANIZATION_RECEIPT_VERIFIES_AGAINST_ITS_BODY", cursor)
        chain.append(receipt)
        cursor = receipt.get("previous_receipt_sha256")
    chain.reverse()
    return chain, None


def _v_ledger_copy(man: dict[str, Any], candidate: dict[str, Any], ledger_copy: Path, nxt: str,
                   ledger_oid: str | None = None) -> dict[str, Any]:
    """The predicate observed in a local copy of the organization ledger rather than a committed claim about it.

    When ``ledger_oid`` is given, the copy's ledger ref must resolve to exactly that commit and every read is made at
    it, so the verdict names one fixed ledger state. The OID is still caller-supplied, so it fixes which state was
    checked but does not authenticate it. The consumed candidate must record an OBSERVED release, and exactly one
    receipt may consume it."""
    p = LEDGER_PREDICATE
    spec = man.get("organization_ledger") or {}
    rev = LEDGER_REF
    if ledger_oid is not None:
        if not (isinstance(ledger_oid, str) and GIT_OID.fullmatch(ledger_oid)):
            return refuse(p, "ORGANIZATION_LEDGER_OID_MALFORMED", f"a 40-hex commit id for {LEDGER_REF}", nxt,
                          ledger_oid=str(ledger_oid))
        copy_oid = _ledger_ref_oid(Path(ledger_copy))
        if copy_oid != ledger_oid:
            return refuse(p, "ORGANIZATION_LEDGER_COPY_OID_MISMATCH", f"a local copy whose {LEDGER_REF} is exactly "
                          f"{ledger_oid}", nxt, expected_oid=ledger_oid, copy_oid=copy_oid)
        rev = ledger_oid
    if candidate.get("transition_outcome") != "OBSERVED":
        return refuse(p, "ORGANIZATION_LEDGER_CANDIDATE_NOT_OBSERVED", "a release candidate whose transition_outcome is "
                      "OBSERVED; appending a refused release records the refusal, it does not release", nxt,
                      candidate_outcome=candidate.get("transition_outcome"))
    chain, bad = read_ledger_chain(Path(ledger_copy), rev)
    if bad:
        return refuse(p, "ORGANIZATION_LEDGER_CHAIN_INVALID", f"a local copy of StegVerse-org/.github {LEDGER_REF} whose "
                      f"chain verifies from HEAD to genesis (failed check {bad[0]}: {bad[1]})", nxt,
                      failed_check=bad[0], ledger_copy=str(ledger_copy))
    want = _ledger_sha(candidate)
    found = [i for i, r in enumerate(chain) if r.get("canonical_state_transition_receipt_sha256") == want]
    if not found:
        return refuse(p, "ORGANIZATION_LEDGER_RECEIPT_NOT_FOUND", f"an organization receipt consuming the emitted "
                      f"candidate {want} on {LEDGER_REF}", nxt, candidate_sha256=want, chain_length=len(chain))
    if len(found) > 1:
        return refuse(p, "ORGANIZATION_LEDGER_RECEIPT_DUPLICATED", f"exactly one organization receipt consuming {want}",
                      nxt, candidate_sha256=want, consuming_receipts=len(found))
    at = found[0]
    rec = chain[at]
    source = _ledger_doc(Path(ledger_copy), "source-receipts/" + want.split(":", 1)[1] + ".json", rev)
    mismatched = [name for name, ok in (
        ("source_transition_sha256", rec.get("source_transition_sha256") == want),
        ("source_receipt_schema", rec.get("source_receipt_schema") == candidate.get("schema")),
        ("org_transition_class", rec.get("org_transition_class") == spec.get("transition_class")),
        ("retained_source_receipt", isinstance(source, dict) and _ledger_sha(source) == want)) if not ok]
    if mismatched:
        return refuse(p, "ORGANIZATION_LEDGER_RECEIPT_NOT_BOUND_TO_CANDIDATE", f"the receipt consuming {want} must name "
                      f"it as its source, keep its schema and class {spec.get('transition_class')}, and retain its bytes",
                      nxt, mismatched=mismatched, org_receipt_sha256=rec.get("receipt_sha256"))
    prior = "sha256:" + str(candidate.get("prior_state_ref_or_hash"))
    if prior not in [r.get("receipt_sha256") for r in chain[:at]]:
        return refuse(p, "ORGANIZATION_LEDGER_RECEIPT_NOT_AFTER_SEALED_HEAD", f"the release receipt must follow the sealed "
                      f"head {prior} the candidate was built on", nxt, org_receipt_sha256=rec.get("receipt_sha256"))
    # Every check above holds, but only against the copy itself: a fork or a re-hashed, re-chained copy passes them
    # too. Nothing here binds the copy's tip to StegVerse-org/.github, so the predicate fails closed with the
    # verified chain as evidence until an authenticated anchor for the ledger tip is bound.
    return refuse(p, "ORGANIZATION_LEDGER_COPY_PROVENANCE_UNBOUND", "bind the local copy's ledger tip to an "
                  "authenticated anchor for StegVerse-org/.github refs/stegverse/organization-ledger; a self-consistent "
                  "chain is not proof of origin", nxt, chain_internally_consistent=True,
                  source_receipt_sha256=want.split(":", 1)[1], org_receipt_sha256=rec["receipt_sha256"],
                  sealed_head=prior, chain_length=len(chain), ledger_oid=ledger_oid)


def v_ledger(root: Path, man: dict[str, Any], candidate: dict[str, Any] | None = None,
             ledger_copy: Path | None = None, ledger_oid: str | None = None) -> dict[str, Any]:
    p = LEDGER_PREDICATE
    spec = (man.get("organization_ledger") or {}).get("readback") or {}
    rb = _json(root, spec.get("path", ""))
    nxt = "after the organization ledger writer appends the emitted receipt and its readback is committed"
    if ledger_copy is not None:
        if candidate is None:
            return refuse(p, "ORGANIZATION_LEDGER_READBACK_MISMATCH", "a ledger receipt candidate to look for", nxt)
        return _v_ledger_copy(man, candidate, Path(ledger_copy), "after the organization ledger writer appends the "
                              "emitted receipt; then re-run with a fresh local copy of the ledger ref", ledger_oid)
    if not isinstance(rb, dict) or rb.get("schema") != spec.get("schema"):
        return refuse(p, "ORGANIZATION_LEDGER_READBACK_ABSENT", f"a readback {spec.get('path')} ({spec.get('schema')}) "
                      "of refs/stegverse/organization-ledger showing the GOVERNANCE_PRODUCT_RELEASE receipt under "
                      "ORGANIZATION_LEDGER_LOCK", nxt)
    want = sha256_hex(canonical(candidate)) if candidate else None
    if candidate is None or rb.get("source_receipt_sha256") != want or rb.get("ledger_lock") != "ORGANIZATION_LEDGER_LOCK":
        return refuse(p, "ORGANIZATION_LEDGER_READBACK_MISMATCH", f"the readback must name source_receipt_sha256 {want} "
                      "and ledger_lock ORGANIZATION_LEDGER_LOCK", nxt)
    # A committed local JSON readback is a claim about the ledger, not a read of it. Until this verifier reads
    # refs/stegverse/organization-ledger itself (the anonymous public-ledger route, E0, no credential) and checks the
    # receipt's digest, ancestry, issuer and lock there, the predicate fails closed whatever the JSON says.
    receipt_hash = rb.get("org_receipt_sha256")
    if not isinstance(receipt_hash, str) or HEX64.fullmatch(receipt_hash) is None:
        return refuse(p, "ORGANIZATION_LEDGER_RECEIPT_HASH_INVALID", "a 64-hex org_receipt_sha256 read back from "
                      "refs/stegverse/organization-ledger", nxt)
    return refuse(p, "ORGANIZATION_LEDGER_PROVENANCE_UNVERIFIED", "pass a local copy of refs/stegverse/organization-ledger "
                  "(finish_verdict(..., ledger_copy=DIR), e.g. fetched anonymously from StegVerse-org/.github) so the "
                  "receipt's digest, chain and ancestry from the sealed head are verified on the ledger itself; a "
                  "committed local readback is not evidence", nxt,
                  source_receipt_sha256=want, claimed_org_receipt_sha256=receipt_hash)


VERIFIERS: dict[str, Callable[[Path, dict[str, Any]], dict[str, Any]]] = {
    "PRODUCT_CLAIM_LIMITED_TO_VERIFIABLE_RECEIPT_CHAIN_ON_CUSTOMER_SUPPLIED_MANIFEST_CONSTRAINTS": v_product_claim,
    "PACKAGE_VERSION_IDENTITY_CONSISTENT_ACROSS_PYPROJECT_INIT_VERSION_JSON": v_package_identity,
    "PINNED_REF_TREE_CONTAINS_GOVERNANCE_GATE_WORKFLOW_AND_MODULE": v_pinned_tree,
    "IMMUTABLE_TAG_AND_GITHUB_RELEASE_PUBLISHED_UNDER_TV_TVC_AUTHORITY": v_immutable_tag,
    "RELEASE_NOTES_SUPERSEDE_V1_0_1_SAFETY_STACK_OVERCLAIM": v_release_notes,
    "CUSTOMER_QUICKSTART_INSTALL_UNINSTALL_AND_NONCLAIMS_PUBLISHED": v_quickstart,
    "NO_NEW_RUNTIME_DEPENDENCY_INTRODUCED": v_no_new_dependency,
    "INDEPENDENT_RECEIPT_CHAIN_VERIFICATION_PASS_AND_TAMPER_FAIL": v_receipt_chain,
    "LICENSE_AND_TERMS_FILE_SHA256_MATCHES_RELEASE_MANIFEST": v_license,
    "ROLLBACK_PROCEDURE_DOCUMENTED_WITHOUT_TAG_RETARGET": v_rollback,
    "ENTITLEMENT_SEPARATE_FROM_DISPOSITION_CONSUMING_SDK_COST_DERIVED_TIER_PRICING_OUTPUT": v_entitlement,
}
DEGRADED_FORM = ("E0: the verifier reads the manifest and the files and receipts it names by path; an absent input is a "
                 "returned six-field FAIL_CLOSED naming its next attempt; E1-E3 LLM lanes may only author repairs to the "
                 "inputs, the deterministic verifier alone decides")
LOWEST_MODE = {name: "E0" for name in list(VERIFIERS) + [LEDGER_PREDICATE, NON_ALLOW_PREDICATE]}


def _guard(fn: Callable[..., dict[str, Any]], name: str, *args: Any) -> dict[str, Any]:
    try:
        out = fn(*args)
    except Exception as exc:  # a verifier never stops the ladder: an unexpected error is a six-field refusal
        out = refuse(name, "VERIFIER_INTERNAL_ERROR", f"{type(exc).__name__}: {exc}", "on the next push that repairs the verifier")
    out.setdefault("lowest_supported_mode", "E0")
    out.setdefault("degraded_form", DEGRADED_FORM)
    return out


def ledger_receipt_candidate(root: Path, man: dict[str, Any], verdict: dict[str, Any]) -> dict[str, Any]:
    """The GOVERNANCE_PRODUCT_RELEASE canonical-state transition receipt for the organization ledger writer, or a
    six-field refusal. Epoch and prior state come from the sealed ledger head readback; nothing reads a clock."""
    p = LEDGER_PREDICATE
    spec = man.get("organization_ledger") or {}
    head = _json(root, (spec.get("ledger_head") or {}).get("path", ""))
    rec, bad = _release_receipt(root, man, p)
    if bad:
        return bad
    if not (isinstance(head, dict) and head.get("schema") == (spec.get("ledger_head") or {}).get("schema")
            and isinstance(head.get("head_sha256"), str) and HEX64.match(head["head_sha256"])
            and isinstance(head.get("hb_epoch"), int) and not isinstance(head.get("hb_epoch"), bool)):
        return refuse(p, "ORGANIZATION_LEDGER_HEAD_UNSEALED", f"a sealed head readback {(spec.get('ledger_head') or {}).get('path')} "
                      "with head_sha256 (64 hex) and integer hb_epoch from refs/stegverse/organization-ledger",
                      "on the next sealed organization-ledger head readback")
    content = {"transition_class": spec.get("transition_class"), "tag": rec["tag"], "commit": rec["commit"],
               "verdict": verdict.get("disposition"), "predicates": verdict.get("predicates"),
               "release_receipt_sha256": sha256_hex(canonical(rec))}
    tid = f"{spec.get('transition_class')}:{rec['tag']}:{rec['commit']}"
    return {"schema": "stegverse.canonical-state-transition-receipt/v1", "transition_id": tid, "transition_sequence": 1,
            "subject_or_correlation_id": "GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001",
            "transition_outcome": "OBSERVED" if verdict.get("disposition") == "ALLOW" else "REFUSED",
            "prior_state_ref_or_hash": head["head_sha256"], "hb_epoch": head["hb_epoch"],
            "required_evidence_manifest": [{"evidence_id": "governance_product_release_verdict",
                                            "evidence_type": "GOVERNANCE_PRODUCT_RELEASE", "origin_transition_id": tid,
                                            "encoding": "canonical-json", "content": content,
                                            "sha256": sha256_hex(canonical(content))}],
            "appended_by": spec.get("appender"), "append_performed": False}


def finish_verdict(root: Path, non_allow_result: dict[str, Any] | None = None,
                   ledger_copy: Path | None = None, ledger_oid: str | None = None) -> dict[str, Any]:
    """Every sealed predicate's verifier, the release-receipt binding and the ledger receipt candidate. ALLOW only when
    all thirteen predicates are ALLOW; otherwise the first refusal's six fields. Never raises."""
    root = Path(root)
    man = load_manifest(root)
    if not isinstance(man, dict) or man.get("schema") != "stegverse.governance-product-release-manifest/v1":
        r = refuse("RELEASE_MANIFEST_PRESENT", "RELEASE_MANIFEST_ABSENT_OR_MALFORMED", f"{MANIFEST} with schema "
                   "stegverse.governance-product-release-manifest/v1", "on the next push that adds the manifest")
        return dict(r, predicates={}, lowest_supported_mode="E0", degraded_form=DEGRADED_FORM)
    results = {name: _guard(fn, name, root, man) for name, fn in VERIFIERS.items()}
    # A caller-supplied dict is an assertion about a customer run, not an observed customer run: it never becomes this
    # predicate's ALLOW. The predicate turns ALLOW only through a receipt-bound customer conformance run (not yet built).
    if isinstance(non_allow_result, dict):
        results[NON_ALLOW_PREDICATE] = refuse(
            NON_ALLOW_PREDICATE, "CUSTOMER_CONFORMANCE_ORIGIN_UNVERIFIED", "a customer conformance run of the pinned "
            "workflow bound to its run identity, immutable source and no-effect evidence through a receipt; a "
            "caller-supplied result is not that run", "on the receipt-bound customer conformance run",
            claimed_disposition=non_allow_result.get("disposition"))
    else:
        results[NON_ALLOW_PREDICATE] = refuse(
            NON_ALLOW_PREDICATE, "FINISH_TEST_RESULT_NOT_SUPPLIED", "run tests.test_governance_product_finish_point."
            "GovernanceProductFinishPoint.test_finish_point_verdict and pass its result", "on the next finish-point run")
    results[NON_ALLOW_PREDICATE].setdefault("lowest_supported_mode", "E0")
    results[NON_ALLOW_PREDICATE].setdefault("degraded_form", DEGRADED_FORM)
    pre = {"disposition": "ALLOW" if all(r["disposition"] == "ALLOW" for r in results.values()) else "FAIL_CLOSED",
           "predicates": {k: r["disposition"] for k, r in results.items()}}
    candidate = _guard(ledger_receipt_candidate, LEDGER_PREDICATE, root, man, pre)
    is_candidate = candidate.get("schema") == "stegverse.canonical-state-transition-receipt/v1"
    results[LEDGER_PREDICATE] = _guard(v_ledger, LEDGER_PREDICATE, root, man, candidate if is_candidate else None,
                                       ledger_copy, ledger_oid)
    order = list(VERIFIERS) + [NON_ALLOW_PREDICATE, LEDGER_PREDICATE]
    failing = [results[k] for k in order if results[k]["disposition"] != "ALLOW"]
    doc = {"schema": "stegverse.governance-product-finish-verdict/v1", "task_id": "GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001",
           "disposition": "ALLOW" if not failing else "FAIL_CLOSED",
           "predicates": {k: results[k]["disposition"] for k in order}, "results": results,
           "ledger_receipt_candidate": candidate if is_candidate else None,
           "ledger_receipt_refusal": None if is_candidate else candidate,
           "lowest_supported_mode": "E0", "degraded_form": DEGRADED_FORM,
           "clock_read": False, "network_used": False, "ledger_appended": False}
    if failing:
        doc.update({k: failing[0][k] for k in SIX})
    return doc


def release_ref_binding(root: Path, head_commit: str) -> dict[str, Any]:
    """Bind the finish run to the TV/TVC release receipt's commit. Never raises."""
    return _guard(_release_ref_binding, "FINISH_POINT_RUNS_AT_RELEASE_RECEIPT_REF", root, head_commit)


def _release_ref_binding(root: Path, head_commit: str) -> dict[str, Any]:
    """The receipt is committed after the release, so it can never sit in the commit it names. The finish point runs at
    the checkout holding the receipt and requires: the receipt's commit is that checkout or its ancestor, and every
    path changed since the receipt's commit is release evidence under the receipt's own directory. Then every file the
    verifiers read is the release commit's. Six-field FAIL_CLOSED otherwise (git history must be present)."""
    p = "FINISH_POINT_RUNS_AT_RELEASE_RECEIPT_REF"
    man = load_manifest(Path(root))
    if not isinstance(man, dict):
        return refuse(p, "RELEASE_MANIFEST_ABSENT_OR_MALFORMED", MANIFEST, "on the next push that adds the manifest")
    rec, bad = _release_receipt(Path(root), man, p)
    if bad:
        return bad
    root = Path(root)
    if rec["commit"] != head_commit:
        rc, _ = _git(root, "merge-base", "--is-ancestor", rec["commit"], head_commit)
        if rc != 0:
            return refuse(p, "FINISH_REF_NOT_DESCENDANT_OF_RELEASE_COMMIT", f"run the finish point at {rec['commit']} or a "
                          f"descendant of it (checkout {head_commit}); full history must be fetched",
                          "on the finish run at a descendant of the receipt commit", release_commit=rec["commit"])
        rc, out = _git(root, "diff", "--name-only", rec["commit"], head_commit)
        evidence_dir = str(Path((man.get("release_receipt") or {}).get("path", "")).parent) + "/"
        changed = [x for x in out.splitlines() if x]
        drift = [x for x in changed if not x.startswith(evidence_dir)]
        if rc != 0 or drift:
            return refuse(p, "RELEASE_TREE_CHANGED_SINCE_RELEASE_COMMIT", f"only release evidence under {evidence_dir} may "
                          f"change after {rec['commit']}; changed: {drift[:20]}", "on a finish run whose tree equals the "
                          "release commit outside the evidence directory", release_commit=rec["commit"], drift=drift[:50])
    return allow(p, release_commit=rec["commit"], tag=rec["tag"])


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001 finish verdict (E0)")
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--ledger-copy", default=None, help=f"local git copy holding {LEDGER_REF}")
    ap.add_argument("--ledger-oid", default=None, help=f"pin every read to this commit of {LEDGER_REF}")
    a = ap.parse_args()
    print(json.dumps(finish_verdict(Path(a.root), ledger_copy=Path(a.ledger_copy) if a.ledger_copy else None,
                                    ledger_oid=a.ledger_oid),
                     indent=2, sort_keys=True))
