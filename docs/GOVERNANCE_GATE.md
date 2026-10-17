# StegVerse Governance Gate

The governance gate lets any GitHub repository run StegVerse governance checks in its own CI. This is the free tier.

## Install

Add `.github/workflows/stegverse-governance.yml` to your repository:

```yaml
name: StegVerse governance
on: [pull_request, push]
permissions:
  contents: read
jobs:
  stegverse-governance:
    uses: StegVerse-org/StegVerse-SDK/.github/workflows/governance-gate.yml@main
```

Optional inputs:

| Input | Default | Meaning |
|---|---|---|
| `sdk_ref` | `main` | StegVerse-SDK ref that supplies the gate. Pin a tag or commit for reproducible runs. |
| `bundle_glob` | `.stegverse/governance/**/*.json` | Where your portable governance evidence bundles live |
| `check_schemas` | `true` | Classify your JSON Schema files against the SDK structural validator contract |

The workflow exposes `disposition` (`PASS` or `FAIL_CLOSED`) as an output and uploads `stegverse-governance-report.json` as an artifact.

## What it checks

1. **Governance evidence.** Each portable governance bundle (`stegverse.portable-governance-verification-bundle`) is independently verified:
   - Interlock ingress, SPE envelope and receipt, and StegGate bridge;
   - every hash and identity binding.
   
   Any bundle that does not verify, is malformed or is unreadable fails the gate closed.
2. **Schemas.** Each JSON Schema is classified against the SDK structural validator contract. This is informational: it lists which schemas the stdlib-only SDK validator can enforce, and never fails the gate.

Every `FAIL_CLOSED` report carries an `actionable_disposition` with `failure_code`, `failed_predicate`, `required_evidence_or_repair`, `retry_entrypoint`, `owning_existing_goal` and `next_attempt`, per the ecosystem state-transition disposition invariant.

## Guarantees

- **Standard library only.** No package installation, credentials or network beyond the two checkouts, and no repository mutation (`contents: read`).
- **Evidence only.** The report grants no execution, admissibility, standing, custody or credential authority. Governed transitions still go through Interlock/InTr and the Organization ledger.

## Tiers

| Tier | Limits | Notes |
|---|---|---|
| Free (this workflow) | 25 bundles and 200 schemas per run | A run over a limit fails closed with `FREE_TIER_LIMIT_EXCEEDED` |

Every report records metered usage (`usage.bundles_verified`, `usage.schemas_classified`). Paid tiers will be priced from the ecosystem's per-action and per-receipt cost evaluation, checked against current market pricing. They will add higher limits, Organization-ledger receipts, replay and support; those entitlements will be issued through TV/TVC.

## Run locally

```bash
python3 -I stegverse/governance_gate.py path/to/repo --output report.json
```

The exit code is 0 for `PASS` and 1 for `FAIL_CLOSED`.
