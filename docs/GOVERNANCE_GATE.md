# StegVerse Governance Gate

The governance gate lets any GitHub repository run StegVerse governance checks in its own CI. This is the free tier.

## Install

Add `.github/workflows/stegverse-governance.yml` to your repository. Callers should reference `@v1.3.0`. Customer-facing steps, the supplied bundle, the report, uninstall, and the claim boundary are in [GITHUB_GOVERNANCE_QUICKSTART.md](GITHUB_GOVERNANCE_QUICKSTART.md).

Tag `v1.3.0` is not published yet. TV/TVC publishes tags. Until that tag exists, `@v1.3.0` and the default `sdk_ref` do not resolve.

```yaml
name: StegVerse governance
on: [pull_request, push]
permissions:
  contents: read
jobs:
  stegverse-governance:
    uses: StegVerse-org/StegVerse-SDK/.github/workflows/governance-gate.yml@v1.3.0
```

Optional inputs:

| Input | Default | Meaning |
|---|---|---|
| `sdk_ref` | `v1.3.0` | StegVerse-SDK ref that supplies the gate. Callers should reference `@v1.3.0`. The default resolves only after TV/TVC publishes that tag. |
| `bundle_glob` | `.stegverse/governance/**/*.json` | Where your portable governance evidence bundles live |
| `check_schemas` | `true` | Classify your JSON Schema files against the SDK structural validator contract |

The workflow exposes `disposition` (`PASS` or `FAIL_CLOSED`) as an output and uploads `stegverse-governance-report.json` as an artifact.

## What it checks

1. **Governance evidence.** Each JSON file matched by `bundle_glob` is verified as a `stegverse.portable-governance-verification-bundle.v1` document:
   - ingress interlock, SPE envelope, SPE receipt, and StegGate bridge;
   - the hashes and identity fields those objects bind together. The checker does not fetch predecessor receipts and does not recompute `manifest_hash` from a manifest document that is not in the bundle.
   
   Any bundle that does not verify, is malformed or is unreadable fails the gate closed.
2. **Schemas.** Each JSON Schema is classified against the SDK structural validator contract. This is informational: it lists which schemas the stdlib-only SDK validator can enforce, and never fails the gate.

## Boundary

- **Standard library only.** No package installation, credentials or network beyond the two checkouts, and no repository mutation (`contents: read`).
- **Receipt check only.** The report records `authority.verification_authority` as `NONE` and the other `authority` flags as false. See [GITHUB_GOVERNANCE_QUICKSTART.md](GITHUB_GOVERNANCE_QUICKSTART.md) for the claim boundary.

## Limits in this workflow

| Recorded tier | Limits | Over the limit |
|---|---|---|
| `FREE` (`governance_gate.TIER`) | 25 bundles and 200 schemas (`FREE_TIER_LIMITS`) | `FAIL_CLOSED` with `FREE_TIER_LIMIT_EXCEEDED` |

Every report records `usage.bundles_verified` and `usage.schemas_classified`. `pricing/policy.candidate.json` and `pricing/rate-card.candidate.json` are candidate files pending owner decision. This workflow does not read them and does not issue an entitlement.

## Run locally

```bash
python3 -I stegverse/governance_gate.py path/to/repo --output report.json
```

The exit code is 0 for `PASS` and 1 for `FAIL_CLOSED`.
