# GitHub governance quickstart

This page describes the reusable workflow in [`.github/workflows/governance-gate.yml`](../.github/workflows/governance-gate.yml) and the checker it runs, [`stegverse/governance_gate.py`](../stegverse/governance_gate.py).

The check compares a customer-supplied portable governance bundle with the hash and identity constraints inside that bundle. A passing report is a record of that comparison. It is not a safety determination, a compliance determination, or an authorization.

Tag `v1.3.0` is not published. `VERSION.json` keeps `release.tag` at `null` and `release_candidate.tag_publication` at `READY_PENDING_TV_TVC_EXECUTION`. TV/TVC publishes tags. Until tag `v1.3.0` exists, both the `uses:` ref below and the default `sdk_ref` fail to resolve.

## Call the pinned workflow

Add `.github/workflows/stegverse-governance.yml` in the customer repository:

```yaml
name: StegVerse governance
on: [pull_request]
permissions:
  contents: read
jobs:
  stegverse-governance:
    uses: StegVerse-org/StegVerse-SDK/.github/workflows/governance-gate.yml@v1.3.0
```

Callers should reference `@v1.3.0`. The workflow input `sdk_ref` defaults to `v1.3.0`, which is the SDK checkout the job uses to run the checker. Omit `sdk_ref` to use that default. The workflow file's own `uses:` ref and `sdk_ref` are separate pins; this minimal job sets only the workflow ref and leaves `sdk_ref` at its default.

The called workflow checks out the caller with `persist-credentials: false`, checks out `StegVerse-org/StegVerse-SDK` at `sdk_ref` with a sparse checkout of `stegverse/`, and runs:

```text
python3 -I .stegverse-sdk/stegverse/governance_gate.py caller \
  --bundle-glob "$BUNDLE_GLOB" \
  --output stegverse-governance-report.json \
  --summary "$GITHUB_STEP_SUMMARY"
```

`python3 -I` is isolated mode. The checker imports its verifier by path from that checkout. It does not install a package. `permissions` on the reusable workflow are `contents: read`.

Optional inputs, from the workflow file:

| Input | Default | Effect |
|---|---|---|
| `sdk_ref` | `v1.3.0` | Ref passed to `actions/checkout` for `StegVerse-org/StegVerse-SDK`. |
| `bundle_glob` | `.stegverse/governance/**/*.json` | Glob, relative to the caller repository, of JSON files treated as bundles. Repeatable only in the local CLI (`--bundle-glob`); the workflow passes one glob. |
| `check_schemas` | `true` | When `true`, walk `**/*.json` and classify a file when the object contains `$schema` or the file name ends with `.schema.json`. Classification does not change the disposition. Set `false` to pass `--no-schemas`. |

## What the customer supplies

The workflow has no manifest input. The customer commits the JSON files selected by `bundle_glob`. Each file must be one object whose `schema` is `stegverse.portable-governance-verification-bundle.v1`, or the checker records that file as `FAIL_CLOSED`.

The manifest constraint is the `manifest` object inside `ingress_interlock` (`stegverse.interlock-transition.v1`). The checker does not accept a separate manifest document and does not build one. For an interlock ingress it requires:

- `manifest.manifest_hash` and `manifest.source_state_hash`, each `sha256:` plus 64 lowercase hex digits
- `manifest.canonicalization` equal to `JCS_RFC8785_NFC`
- `manifest.predecessor_receipts` with at least one entry; each entry has `receipt_id`, `issuer`, and `receipt_hash` in the same hash form
- `connection.participant_boundary_receipt_hash` equal to one of those predecessor `receipt_hash` values
- `boundary.original_manifest_hash` equal to `manifest.manifest_hash`
- `connection.class` equal to `INTERLOCK` (the portable verifier rejects any other class)

The same bundle also carries `spe_envelope`, `spe_receipt`, and `steggate_bridge`, plus `package_id`, `transition_id`, `run_id`, and `stage` (`PRE_STEGGATE` or `POST_RETURN`). `POST_RETURN` additionally requires `interlock_return`. `PRE_STEGGATE` requires `interlock_return` to be JSON `null`.

`manifest_hash` is checked as a string and bound to `boundary.original_manifest_hash`. The checker does not recompute that hash from a manifest body, because the bundle does not contain one. Predecessor receipt objects are checked for the three fields above. They are not downloaded, and their bytes are not compared with a ledger.

## What the run writes, and how to verify it

The job output `disposition` is `PASS` or `FAIL_CLOSED`. The job always uploads `stegverse-governance-report.json` when that file exists. The step summary appended to `$GITHUB_STEP_SUMMARY` is a short Markdown rendering of the same report.

The report object is schema `stegverse.governance-gate-report.v1`. Fields written by `run_gate`:

- `tier`: the string `FREE`
- `disposition`: `PASS` or `FAIL_CLOSED`
- `reason`: `ALL_BUNDLES_VERIFIED`, `NO_GOVERNANCE_BUNDLES_FOUND`, `BUNDLE_VERIFICATION_FAILED`, or `FREE_TIER_LIMIT_EXCEEDED`
- `usage.bundles_verified`, `usage.schemas_classified`, `usage.limits` (`bundles` 25, `schemas` 200), `usage.over_limit`
- `bundles[]`: `path`, `status`, and either `report_sha256` or `error`
- `schemas`: counts and per-file `sdk_contract_compatible` plus `blocking_codes`
- `sdk_validator_contract`: the structural validator contract version loaded from the `sdk_ref` checkout
- `authority`: the six fields listed in the claim boundary below

The limit check runs first. A count above either limit is `FAIL_CLOSED` / `FREE_TIER_LIMIT_EXCEEDED`, including a run with no bundles and more than 200 classified schemas. Otherwise `PASS` / `ALL_BUNDLES_VERIFIED` means every selected bundle returned status `PASS` from `verify_portable_governance_bundle`. `PASS` / `NO_GOVERNANCE_BUNDLES_FOUND` means the glob matched no bundles and the schema count was within its limit. A bundle that fails verification, is not a JSON object, or cannot be read is `FAIL_CLOSED` / `BUNDLE_VERIFICATION_FAILED`. The process exit code is 0 for `PASS` and 1 for `FAIL_CLOSED`. Schema results never select the disposition.

For each bundle that verifies, `report_sha256` is the hex SHA-256 of `json.dumps(verifier_report, sort_keys=True)` encoded as UTF-8. The uploaded gate report does not include the verifier report body. The verifier report schema is `stegverse.portable-governance-verification-report.v1`. On success it includes `status` `PASS`, `bundle_hash`, `ingress_interlock_hash`, `bridge_hash`, and `checks`. Those checks are the labels the verifier appends after each comparison succeeds:

- `INGRESS_INTERLOCK_VALID`
- `SPE_ENVELOPE_HASH_VALID`
- `SPE_RECEIPT_HASH_VALID`
- `IDENTITY_CONTINUITY_VALID`
- `SPE_BINDING_VALID`
- `STEGGATE_BRIDGE_HASH_VALID`
- `AUTHORITY_NON_TRANSFER_VALID`
- `INTERLOCK_RETURN_VALID` only when `stage` is `POST_RETURN`

To recompute the chain, check out `StegVerse-org/StegVerse-SDK` at the same ref the run used and, from that checkout, run the standard-library checker against the customer repository:

```bash
python3 -I stegverse/governance_gate.py /path/to/customer/repo \
  --bundle-glob '.stegverse/governance/**/*.json' \
  --output report.json
```

Match `sdk_ref` to the ref you check out. Otherwise the local report is a different checker than the Actions run. The verifier recomputes the SPE candidate hash, envelope hash, receipt hash, and bridge hash with `stable_hash`: SHA-256 of UTF-8 JSON produced with sorted object keys, separators `(",", ":")`, and `ensure_ascii` false. That digest is lowercase hex with no prefix. It recomputes the ingress interlock hash with `canonical_hash`, which is the same JSON encoding prefixed by `sha256:`. It then requires `package_id`, `transition_id`, and `run_id` to match across the ingress, envelope, receipt, and bridge, and requires the bridge's stored ingress, receipt, candidate, and envelope hashes to match those recomputed values.

The SPE receipt must have `execution_authorized`, `execution_performed`, and `master_record_installed` all false. The bridge must keep `admissibility_candidate.decision` at `PENDING`, `authority.sdk_authority` at `NONE`, and `authority.execution_authorized` false. A `standing_result` string inside the receipt, including `ALLOW`, is not re-derived by this checker and is not treated as permission to execute.

## Uninstall

Delete the customer workflow file, or delete the job whose `uses:` value points at `governance-gate.yml`. That is the whole install: the reusable workflow does not commit to the caller, install a package, or store a credential. Files the customer committed under the bundle glob remain until the customer deletes them. The report artifact stays on the Actions run that uploaded it, subject to that repository's artifact retention. This workflow does not delete artifacts.

## Claim boundary

The claim this workflow can support is a verifiable receipt chain for the bundle the customer supplied: the manifest hashes and predecessor receipt references inside that bundle, the recomputed SPE and bridge hashes, and the identity fields that tie those objects together.

A `PASS` report does not say the caller is safe, compliant, or authorized. The report records this `authority` object on every run:

- `verification_authority`: `NONE`
- `execution_authorized`: false
- `standing_minted`: false
- `admissibility_decided`: false
- `custody_claimed`: false
- `credential_issued`: false

The checker does not perform a state transition, admit a new action, contact an organization ledger, or retrieve predecessor receipts. `NO_GOVERNANCE_BUNDLES_FOUND` is still `PASS`; an empty glob is not evidence that a transition occurred. JSON Schema classification is a compatibility list for the SDK structural validator and does not pass or fail the run.
