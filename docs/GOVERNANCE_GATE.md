# StegVerse Governance Gate

The governance gate lets any GitHub repository run the bundle checker in its own CI. This is the free tier. Callers reference the workflow by commit `ba5bbf42eabec6a6ae3b0efdff7c683967a79083`.

## Install

Add `.github/workflows/stegverse-governance.yml` to your repository. Customer-facing steps, the supplied bundle, the report, uninstall, and the claim boundary are in [GITHUB_GOVERNANCE_QUICKSTART.md](GITHUB_GOVERNANCE_QUICKSTART.md).

```yaml
name: StegVerse governance
on: [pull_request, push]
permissions:
  contents: read
jobs:
  stegverse-governance:
    uses: StegVerse-org/StegVerse-SDK/.github/workflows/governance-gate.yml@ba5bbf42eabec6a6ae3b0efdff7c683967a79083
```

Optional inputs:

| Input | Default | Meaning |
|---|---|---|
| `sdk_ref` | `ba5bbf42eabec6a6ae3b0efdff7c683967a79083` | StegVerse-SDK commit that supplies the gate. Callers reference the workflow at that same commit. |
| `bundle_glob` | `.stegverse/governance/**/*.json` | Where your portable governance evidence bundles live |
| `check_schemas` | `true` | Classify your JSON Schema files against the SDK structural validator contract |

The workflow exposes `disposition` (`ALLOW` or `FAIL_CLOSED`) as an output and uploads `stegverse-governance-report.json` as an artifact. `FAIL_CLOSED` carries `failure_code`, `failed_predicate`, `required_evidence_or_repair`, `retry_entrypoint`, `owning_existing_goal`, and `next_attempt`. An empty bundle glob is `FAIL_CLOSED` / `NO_GOVERNANCE_BUNDLES_FOUND`.

## What it checks

1. **Governance evidence.** Each JSON file matched by `bundle_glob` is verified as a `stegverse.portable-governance-verification-bundle.v1` document:
   - ingress interlock, SPE envelope, SPE receipt, and StegGate bridge;
   - the hashes and identity fields those objects bind together. The checker does not fetch predecessor receipts and does not recompute `manifest_hash` from a manifest document that is not in the bundle.
   
   Any bundle that does not verify, is malformed or is unreadable fails the gate closed. The gate records that bundle's status as `ALLOW` only when the verifier status is `PASS`; any other verifier status is `FAIL_CLOSED`.
2. **Schemas.** Each JSON Schema is classified against the SDK structural validator contract. This is informational: it lists which schemas the stdlib-only SDK validator can enforce, and never fails the gate by itself.

## Boundary

- **Standard library only.** No package installation, credentials or network beyond the two checkouts, and no repository mutation (`contents: read`).
- **Receipt check only.** The report records `authority.verification_authority` as `NONE` and the other `authority` flags as false. See [GITHUB_GOVERNANCE_QUICKSTART.md](GITHUB_GOVERNANCE_QUICKSTART.md) for the claim boundary.
- The gate is a read-only verifier run by the customer, not a StegVerse state transition, and it emits no organization-ledger receipt.

## Limits in this workflow

| Recorded tier | Limits | Over the limit |
|---|---|---|
| `FREE` (`governance_gate.TIER`) | 25 bundles and 200 schemas (`FREE_TIER_LIMITS`) | `FAIL_CLOSED` with `FREE_TIER_LIMIT_EXCEEDED` |

Every report records `usage.bundles_verified` and `usage.schemas_classified`. `pricing/policy.candidate.json` and `pricing/rate-card.candidate.json` are candidate files pending owner decision. This workflow does not read them and does not issue an entitlement.

## Run locally

```bash
python3 -I stegverse/governance_gate.py path/to/repo --output report.json
```

The exit code is 0 for `ALLOW` and 1 for `FAIL_CLOSED`.
