# Unreleased: StegVerse Governance gate

The version is not set here. The owner and TV/TVC decide it. Coordination: [StegVerse-Labs/.github#3183](https://github.com/StegVerse-Labs/.github/issues/3183).

These notes describe the gate as shipped by [pull request #534](https://github.com/StegVerse-org/StegVerse-SDK/pull/534) (`4f3916aad9f0861436031a252b3223d63b690521` on `cursor/governance-release-prep-940e`). They do not publish a tag or a GitHub Release. `VERSION.json` keeps `release.tag` at `null` and `release_candidate.tag_publication` at `READY_PENDING_TV_TVC_EXECUTION`. The recorded candidate `b1376d3e3e3c79b6e996d32766bfd7e41cd0ccc4` does not contain `governance-gate.yml`. `development_line` is `1.4.0.dev0` with `release_identity` false. This note does not choose a version.

## Claim

A verifiable receipt chain built on customer-supplied manifest constraints.

The gate compares a customer-supplied `stegverse.portable-governance-verification-bundle.v1` with the hash and identity fields inside that bundle. An `ALLOW` report is a record of that comparison.

## The gate

Reusable workflow `.github/workflows/governance-gate.yml` (`workflow_call`), as changed on #534 at `4f3916aad9f0861436031a252b3223d63b690521`.

`uses: StegVerse-org/StegVerse-SDK/.github/workflows/governance-gate.yml@ba5bbf42eabec6a6ae3b0efdff7c683967a79083` runs the pre-#534 workflow, whose `sdk_ref` defaults to `main` and whose actions are tag-pinned, so customers should not adopt it for the new behaviour; the pin becomes valid after the owner merges #534 and the follow-up retargets `uses:` and `sdk_ref` to the merge commit.

```yaml
jobs:
  stegverse-governance:
    uses: StegVerse-org/StegVerse-SDK/.github/workflows/governance-gate.yml@<534-merge-commit>
    with:
      sdk_ref: <534-merge-commit>
```

On this #534 head the workflow file still defaults `sdk_ref` to `ba5bbf42eabec6a6ae3b0efdff7c683967a79083`, which checks out the pre-#534 checker (`PASS`, and an empty glob passes). The workflow ref and `sdk_ref` are separate pins.

The called workflow checks out the caller with `contents: read` and `persist-credentials: false`, sparse-checks out `stegverse/` at `sdk_ref`, and runs `python3 -I` on `stegverse/governance_gate.py`. It does not install a package. It verifies each JSON file selected by `bundle_glob` (default `.stegverse/governance/**/*.json`) and, unless `check_schemas` is false, classifies JSON Schemas. Classification does not change the disposition. The job output is `ALLOW` or `FAIL_CLOSED`, written as `disposition=$disposition` to `$GITHUB_OUTPUT`. The job is green only on `ALLOW`: it exits 0 only when the checker status is 0 and the disposition is `ALLOW`, and exits 1 otherwise. A missing or unparsable report, or a checker without `read_workflow_disposition` (the `ba5bbf42` checker), falls back to `FAIL_CLOSED` and exit 1. It uploads `stegverse-governance-report.json` (`stegverse.governance-gate-report.v1`) when that file exists.

`run_gate` selects the disposition in this order: over 25 bundles or 200 schemas is `FAIL_CLOSED` / `FREE_TIER_LIMIT_EXCEEDED`; otherwise an empty bundle glob is `FAIL_CLOSED` / `NO_GOVERNANCE_BUNDLES_FOUND`; otherwise any selected bundle whose status is not `ALLOW` is `FAIL_CLOSED` / `BUNDLE_VERIFICATION_FAILED`; otherwise `ALLOW` / `ALL_BUNDLES_VERIFIED`. The report records tier string `FREE`. The underlying verifier report uses status `PASS`; the gate maps that to bundle status `ALLOW`. A missing or unrecognized verifier status is bundle status `FAIL_CLOSED`.

Every `FAIL_CLOSED` report carries `failure_code`, `failed_predicate`, `required_evidence_or_repair`, `retry_entrypoint`, `owning_existing_goal`, and `next_attempt`. `failure_code` is the same string as `reason`. `retry_entrypoint` is `stegverse/governance_gate.py::run_gate`. `owning_existing_goal` is `SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001`.

On an interlock ingress, `validate_interlock_transition` checks the manifest constraints inside that bundle. Those include `manifest.manifest_hash` and `manifest.source_state_hash` (`sha256:` plus 64 lowercase hex digits), `manifest.canonicalization` equal to `JCS_RFC8785_NFC`, at least one `manifest.predecessor_receipts` entry (`receipt_id`, `issuer`, `receipt_hash`), `connection.participant_boundary_receipt_hash` equal to one of those receipt hashes, and `boundary.original_manifest_hash` equal to `manifest.manifest_hash`. The verifier then recomputes the SPE candidate, envelope, receipt, and bridge hashes and requires `package_id`, `transition_id`, and `run_id` to match across the ingress, envelope, receipt, and bridge. It does not recompute `manifest_hash` from a manifest body, and it does not download predecessor receipts.

## Notable changes since v1.0.12

Range starts at tag `v1.0.12` (`04f774731dc438b1585d1040e17dc708f705447a`). The dependency and validator notes below are the tree #534 builds on. The disposition and job-exit notes above are `.github/workflows/governance-gate.yml` and `stegverse/governance_gate.py` on #534 at `4f3916aad9f0861436031a252b3223d63b690521`.

### Runtime dependencies

At `v1.0.12`, `pyproject.toml` required `requests`, `pyyaml`, and `python-dotenv`.

- #496 removed `pyyaml` and `python-dotenv` (declared, never imported). `requests` stayed the only core dependency.
- #520 (`85c7e67`) removed `requests`. JSON-over-HTTP uses `stegverse/_stdlib_http.py` (stdlib `urllib`).
- `[project].dependencies` is empty. `requirements.txt` states there are no third-party runtime dependencies.
- `package-artifact-validation.yml` refuses a wheel that reintroduces `pyyaml`, `python-dotenv`, or `requests`.

The gate loads the verifier and validator by path. Optional `dev`, `governed-test`, and `manifold-test` extras are not runtime dependencies of the gate.

### Validator

`stegverse/structural_validator_candidate.py` contract version is `1.6`. The gate copies that version into the report and records, per schema file, `sdk_contract_compatible` and `blocking_codes`. Those fields do not select `ALLOW` or `FAIL_CLOSED`.

Contract steps since the candidate landed: JSON equality for `const` / `enum`; array bounds and annotation keywords (1.1); `$schema` / `$id` as root identity metadata (1.2); `pattern` limited to a dialect-neutral subset (1.3); `date` and `date-time` asserted with the standard library, RFC 3339 (1.4); dialect-dependent pattern syntax excluded (1.5); `allOf`, `if` / `then` / `else`, local `$ref` / `$defs`, and exclusive bounds (1.6); arbitrary-precision integers in `uniqueItems` (#508).

The structural validator rejects unsupported keywords, non-JSON instances, schemas or instances past its depth bounds, patterns outside its subset, and `$ref` forms other than `#/$defs/<name>`. `CONTRACT["divergences_fail_closed"]` records that it may reject a document JSON Schema 2020-12 would accept. Those results stay inside schema classification.

## What this note does not claim

- No safety determination, no compliance determination, and no authorization.
- The report `authority` object is `verification_authority: NONE`, with `execution_authorized`, `standing_minted`, `admissibility_decided`, `custody_claimed`, and `credential_issued` false.
- An `ALLOW` report does not mean a transition was executed or stored on a ledger. The checker does not contact a ledger.
- An empty bundle glob is not a receipt chain.
- Schema classification does not select the disposition and is not a scan for code patterns.
- No price, paid tier, or entitlement is approved here.
- This note does not publish a tag or a GitHub Release, and it does not name the merge commit.

## Supersedes the v1.0.1 release text

GitHub Release [v1.0.1](https://github.com/StegVerse-org/StegVerse-SDK/releases/tag/v1.0.1) (2026-04-29) advertised a **5-layer safety stack** and **Automatic DENY for dangerous code patterns** (`os.system`, `eval`, `pickle`, and similar). Those statements are beyond the receipt-chain claim. This note supersedes that release text. It does not claim a safety stack and does not claim automatic denial of code patterns.

This file does not edit the published v1.0.1 release. Tag and release text remain with TV/TVC.
