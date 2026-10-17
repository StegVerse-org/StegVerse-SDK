# StegVerse Governance v1.3.0

Draft notes for the first GitHub product release. Coordination: [StegVerse-Labs/.github#3183](https://github.com/StegVerse-Labs/.github/issues/3183).

These notes describe the governance gate on `main` after tag `v1.0.12` (`04f774731dc438b1585d1040e17dc708f705447a`). They do not publish a tag or a GitHub Release. `VERSION.json` keeps `release.tag` at `null` and `release_candidate.tag_publication` at `READY_PENDING_TV_TVC_EXECUTION`. The frozen candidate recorded there (`source_candidate_commit` `3cd3198375b687e73f06071e9c16e18d8a1c527c`) is not this moving `main`. `development_line` is `1.4.0.dev0` with `release_identity` false. TV/TVC publishes the tag and the release.

## Claim

A verifiable receipt chain built on customer-supplied manifest constraints.

The gate compares a customer-supplied `stegverse.portable-governance-verification-bundle.v1` with the hash and identity fields inside that bundle. A `PASS` report is a record of that comparison.

## What ships

Reusable workflow [`.github/workflows/governance-gate.yml`](.github/workflows/governance-gate.yml) (`workflow_call`). Pin the caller at the release tag:

```yaml
jobs:
  stegverse-governance:
    uses: StegVerse-org/StegVerse-SDK/.github/workflows/governance-gate.yml@v1.3.0
```

`@v1.3.0` resolves only after TV/TVC publishes that tag. On this `main` the workflow comment and the `sdk_ref` default are still `main`. [Pull request #534](https://github.com/StegVerse-org/StegVerse-SDK/pull/534) sets the documented pin and the default `sdk_ref` to `v1.3.0`. The `uses:` ref and `sdk_ref` are separate pins.

Install, the bundle fields the checker reads, and how to recompute the hashes: `docs/GITHUB_GOVERNANCE_QUICKSTART.md`, added in [pull request #534](https://github.com/StegVerse-org/StegVerse-SDK/pull/534) (not on this `main`).

The called workflow checks out the caller with `contents: read` and `persist-credentials: false`, sparse-checks out `stegverse/` from this repository at `sdk_ref`, and runs `python3 -I` on `stegverse/governance_gate.py`. It does not install a package. It verifies each JSON file selected by `bundle_glob` (default `.stegverse/governance/**/*.json`) and, unless `check_schemas` is false, classifies JSON Schemas. Classification does not change the disposition. The job output is `PASS` or `FAIL_CLOSED`. It uploads `stegverse-governance-report.json` (`stegverse.governance-gate-report.v1`).

On an interlock ingress, `validate_interlock_transition` checks the manifest constraints inside that bundle. Those include `manifest.manifest_hash` and `manifest.source_state_hash` (`sha256:` plus 64 lowercase hex digits), `manifest.canonicalization` equal to `JCS_RFC8785_NFC`, at least one `manifest.predecessor_receipts` entry (`receipt_id`, `issuer`, `receipt_hash`), `connection.participant_boundary_receipt_hash` equal to one of those receipt hashes, and `boundary.original_manifest_hash` equal to `manifest.manifest_hash`. The verifier then recomputes the SPE candidate, envelope, receipt, and bridge hashes and requires `package_id`, `transition_id`, and `run_id` to match across the ingress, envelope, receipt, and bridge. It does not recompute `manifest_hash` from a manifest body, and it does not download predecessor receipts.

## Notable changes since v1.0.12

### Runtime dependencies

At `v1.0.12`, `pyproject.toml` required `requests`, `pyyaml`, and `python-dotenv`.

- #496 removed `pyyaml` and `python-dotenv` (declared, never imported). `requests` stayed the only core dependency.
- #520 (`85c7e67`) removed `requests`. JSON-over-HTTP uses `stegverse/_stdlib_http.py` (stdlib `urllib`).
- `[project].dependencies` is empty. `requirements.txt` states there are no third-party runtime dependencies.
- `package-artifact-validation.yml` refuses a wheel that reintroduces `pyyaml`, `python-dotenv`, or `requests`.

The gate loads the verifier and validator by path. Optional `dev`, `governed-test`, and `manifold-test` extras are not runtime dependencies of the gate.

On this `main`, `pyproject.toml` `version` is `1.3.0`. `stegverse.__version__` is still `1.0.0`. Alignment of the import version is in open pull request #534, not in this file.

### Validator

`stegverse/structural_validator_candidate.py` contract version is `1.6`. The gate copies that version into the report and records, per schema file, `sdk_contract_compatible` and `blocking_codes`. Those fields do not select `PASS` or `FAIL_CLOSED`.

Contract steps on `main` since the candidate landed: JSON equality for `const` / `enum`; array bounds and annotation keywords (1.1); `$schema` / `$id` as root identity metadata (1.2); `pattern` limited to a dialect-neutral subset (1.3); `date` and `date-time` asserted with the standard library, RFC 3339 (1.4); dialect-dependent pattern syntax excluded (1.5); `allOf`, `if` / `then` / `else`, local `$ref` / `$defs`, and exclusive bounds (1.6); arbitrary-precision integers in `uniqueItems` (#508).

### Fail-closed

In `stegverse/governance_gate.py`:

- A selected bundle that fails verification, is not a JSON object, or cannot be read is recorded `FAIL_CLOSED`. The run is then `FAIL_CLOSED` / `BUNDLE_VERIFICATION_FAILED`.
- More than 25 bundles or 200 schemas is `FAIL_CLOSED` / `FREE_TIER_LIMIT_EXCEEDED`. That check runs before bundle results. The report records tier string `FREE`.
- The process exits 0 on `PASS` and 1 on `FAIL_CLOSED`.
- `PASS` / `NO_GOVERNANCE_BUNDLES_FOUND` means the glob matched nothing.

The structural validator rejects unsupported keywords, non-JSON instances, schemas or instances past its depth bounds, patterns outside its subset, and `$ref` forms other than `#/$defs/<name>`. `CONTRACT["divergences_fail_closed"]` records that it may reject a document JSON Schema 2020-12 would accept. Those results stay inside schema classification.

## What this release does not claim

- No safety determination, no compliance determination, and no authorization.
- The report `authority` object is `verification_authority: NONE`, with `execution_authorized`, `standing_minted`, `admissibility_decided`, `custody_claimed`, and `credential_issued` false.
- A `PASS` report does not mean a transition was executed or stored on a ledger. The checker does not contact a ledger.
- An empty bundle glob is not a receipt chain.
- Schema classification is not a pass/fail of the run and is not a scan for code patterns.
- No price, paid tier, or entitlement is approved here.
- This note does not publish tag `v1.3.0` or a GitHub Release.

## Supersedes the v1.0.1 release text

GitHub Release [v1.0.1](https://github.com/StegVerse-org/StegVerse-SDK/releases/tag/v1.0.1) (2026-04-29) advertised a **5-layer safety stack** and **Automatic DENY for dangerous code patterns** (`os.system`, `eval`, `pickle`, and similar). Those statements are beyond the claim of this release. This note supersedes that release text for StegVerse Governance v1.3.0. This release does not claim a safety stack and does not claim automatic denial of code patterns.

This file does not edit the published v1.0.1 release. Tag and release text remain with TV/TVC.
