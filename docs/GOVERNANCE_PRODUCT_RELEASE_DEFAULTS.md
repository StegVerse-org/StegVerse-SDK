# Governance product release defaults

The release defaults for GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001 live in `.stegverse/governance-product/release-manifest.v1.json`. No step waits on a person. Each decision has a default and a class:

| Decision | Default | Class |
|---|---|---|
| Tag target | a new immutable tag `v<pyproject version>` at the commit named by the TV/TVC release receipt; `allow_tag_update` false | A: TV/TVC release transition plus its receipt |
| License | the in-tree `LICENSE` (MIT), checked by sha256 | C: provisional at E1, C-review receipt pending |
| Distribution | the reusable workflow `.github/workflows/governance-gate.yml` at the released commit, plus the GitHub release asset | D |
| Entitlement | separate from the gate disposition; issued by TV/TVC from the consumed cost-derived tier pricing output | B: separation verifier built here |
| Rollback | supersede with a new version | D |
| License predicate | `LICENSE_AND_TERMS_FILE_SHA256_MATCHES_RELEASE_MANIFEST` | D |
| Release ingress | the manifest-driven TVC release transition | A |

`tools/governance_product_finish.py` checks every sealed predicate against this manifest at E0. Each result is either ALLOW or a FAIL_CLOSED that names its six fields.

## Rollback

To roll back, publish a superseding version under a new immutable tag that carries the fix or the revert. Never retarget, delete or replace a published tag or release asset. Customers move their `uses:` pin to the superseding commit. The older tag stays where it is, and the release notes of the superseding version name it as superseded.

## Time and paths

Every path comes from the manifest. The epoch and the prior state of the organization-ledger receipt come from the sealed organization-ledger head readback. Nothing reads a clock. The ledger writer appends the emitted receipt candidate under `ORGANIZATION_LEDGER_LOCK`. This repository never appends.
