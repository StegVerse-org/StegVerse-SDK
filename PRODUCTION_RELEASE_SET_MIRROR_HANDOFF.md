# Production Release Set Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
credential_authority: TV/TVC
non-TV/TVC release credential permitted: false
current_public_package_candidate: 1.1.0
current_public_tag_candidate: v1.1.0
historical_v1.0.13_mutable: false
```

## Governing goal

Every governed evaluator run must identify the exact immutable released component set that participated, retain that set with exact-run custody, and distinguish it from both moving source branches and later releases used during replay/reconstruction.

The release-set mechanism is evaluator-neutral. A named evaluation supplies configuration and evidence requirements through the generalized SDK surface; it does not create a custom SDK route or custom StegGate semantics.

## 2026-08-19 package/version identity reconciliation

Live inspection confirmed three conflicting SDK identities had accumulated:

```text
historical Git tag v1.0.13
  -> f219afa17dcb020dc1e13b72f859a86627c5644b
  -> commit message: Bump to 1.0.13
  -> date: 2026-04-29

modern pyproject.toml before repair
  -> package version 1.0.13

legacy setup.py before repair
  -> package version 2.1.0
  -> different dependency/Python/entry-point metadata
```

The modern evaluator-capable SDK source is more than a patch-level change from the historical 1.0.13 source. The previously frozen modern candidate was 1242 commits ahead of historical `v1.0.13`.

Resolution merged in PR #50:

```text
merge_commit: 459e88f640c36805ae2e24484604f3976809b69f
canonical package metadata source: pyproject.toml
canonical modern package version: 1.1.0
legacy setup.py: metadata-free compatibility shim
target public SDK tag: v1.1.0
```

`v1.0.13` is immutable historical evidence and MUST NOT be moved or reused. Modern SDK source MUST NOT be published to PyPI as `1.0.13`. The unpublished tags `v1.0.13-oda3-r1` and `v1.0.13-evaluation-r2` are superseded release candidates and MUST NOT be published after this correction.

A `1.1.0` candidate is not frozen merely because PR #50 merged. Package artifact validation is now required before an exact successor candidate can be frozen.

## Generalized testing-surface invariant

```text
SDK testing surface: generalized
evaluator/test package: configuration + evidence request
named evaluator/study: instance, not architecture
custom evaluator SDK lane: prohibited
custom evaluator StegGate semantics: prohibited
unsupported capability: reject before execution
new capability needed by one study: develop/version/validate/publish generally before use
```

## Current R2 aggregate release-set state

The former SDK coordinate in `EVALUATION-BOUNDARY-2026-08-18-R2` is superseded because it used an already-consumed package identity. The downstream executable-source lineage remains separately preserved; no moving branch is substituted for it.

```text
release_set_id: EVALUATION-BOUNDARY-2026-08-18-R2
state: SUPERSEDED_PENDING_SUCCESSOR_REISSUE
reason: SDK_PACKAGE_VERSION_IDENTITY_COLLISION

sdk_entry
  repo: StegVerse-org/StegVerse-SDK
  superseded candidate: cfd6069823cc35d263ce0128fb0e6c0125d8bb64
  superseded tag: v1.0.13-evaluation-r2
  successor package: 1.1.0
  successor tag: v1.1.0
  successor candidate: PENDING_PACKAGE_ARTIFACT_VALIDATION_AND_FREEZE

manifest_route_carrier
  repo: Data-Continuation/core-lite
  executable source parent: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
  note-only successor previously recorded for R2: 018e608018a793ee6dc62f4fdea59a3415e6e80e

governance_runtime
  repo: StegVerse-Labs/StegCore
  executable source parent: 083557adec1bdbace09ebd10fb0765eb8e9a9d08
  note-only successor previously recorded for R2: 23b388ce23b08097593b5b5593eb4061e0ff5242
  runtime identity: stegverse:steggate:canonical:three-layer:v1

exact_run_custody
  repo: master-records/orchestration
  executable source parent: 6626c6a7f1df6bf531940c165b2f4db374e08b92
  note-only successor previously recorded for R2: 4826f753641cc82bbb885f919494a6c1318fbae4
```

The aggregate set MUST be reissued after the exact SDK 1.1.0 successor candidate is frozen. Reissue means a new immutable release-set revision/task; it does not rewrite the superseded R2 evidence.

## Package artifact validation gate

The successor SDK candidate must prove all of the following from exact source before freeze:

```text
python -m build: PASS
exactly one wheel + one sdist: PASS
wheel Name: stegverse-sdk
wheel Version: 1.1.0
wheel Requires-Python: >=3.9
canonical dependencies derived from pyproject.toml
canonical console entry points derived from pyproject.toml
python setup.py --version: 1.1.0
fresh virtualenv wheel install: PASS
import stegverse: PASS
installed metadata version: 1.1.0
stegverse --help smoke test: PASS
release credentials present during validation: NONE
```

The repository contains a non-authorizing validation workflow for this purpose at `.github/workflows/package-artifact-validation.yml`. It may validate source-built artifacts but has no tag, release, publication, push, OIDC, runtime, or TV/TVC credential authority.

## Release semantics

```text
moving branch != release identity
source validation != released
workflow pass != runtime
package build != publication
tag readiness != tag publication
release readiness != released
published package != runtime activation
commit pin != release tag
release tag must resolve to immutable candidate commit
existing tag must never be retargeted
future release != historical runtime substitution
replay/reconstruction never rewrites original release-set evidence
```

## TV/TVC boundary

Actual tag, GitHub Release, and package publication remains a TV/TVC-governed release-authority action. GitHub Actions is validation-only and must not become production/runtime/control-plane/release authority. No non-TV/TVC release credential is permitted.

The existing SDK release task is intentionally `REVIEW_REQUIRED_VERSION_IDENTITY_REPAIR` until the 1.1.0 artifact gate passes and an exact successor candidate is frozen.

## Cross-repo coordination

```text
StegVerse-org/StegVerse-SDK#47
StegVerse-Labs/TVC aggregate-release task: successor revision required after SDK freeze
Data-Continuation/core-lite/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
master-records/orchestration/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
```

## Remaining executable work

```text
1. Merge and observe PASS for exact SDK 1.1.0 package-artifact validation.
2. Freeze the resulting exact SDK 1.1.0 successor candidate commit.
3. Reissue the TVC aggregate release-set/task with v1.1.0 bound to that exact SDK candidate; retain superseded R2 evidence unchanged.
4. Revalidate all four component coordinates and release notes as one exact set.
5. TV/TVC publishes/verifies the immutable tags/releases and stegverse-sdk 1.1.0 package.
6. Verify PyPI metadata/artifact identity, GitHub tag resolution, GitHub Release identity, and clean-install behavior all agree.
7. Update the aggregate manifest/catalog from pending to tag-bound and retain the TVC aggregate-release receipt.
8. Execute the exact governed evaluator submission beginning at the ordinary SDK manifest ingress.
9. Retain submitted manifest, governed result, route/manifest receipts, Master Records custody, reconstruction/replay evidence, and independent verification.
10. Verify release/changelog propagation to StegVerse-Labs/Site (or canonical successor if renamed), GCAT-BCAT-Engine/Publisher, admissibility-wiki, and stegguardian-wiki.
```

## Status

```text
SDK_GENERALIZED_TESTING_SURFACE: IMPLEMENTED_SOURCE_VALIDATED_MERGED
SDK_HISTORICAL_V1_0_13: IMMUTABLE_PRESERVED
SDK_METADATA_SPLIT: REPAIRED_ON_MAIN_PR50
SDK_CANONICAL_PACKAGE_VERSION: 1.1.0
SDK_1_1_0_ARTIFACT_VALIDATION: IN_PROGRESS
SDK_1_1_0_FROZEN_CANDIDATE: PENDING
OLD_V1_0_13_DERIVED_CANDIDATES: SUPERSEDED_DO_NOT_PUBLISH
AGGREGATE_RELEASE_SET_SUCCESSOR: PENDING_REISSUE_AFTER_SDK_FREEZE
TAG_PUBLICATION: NOT_AUTHORIZED_UNTIL_TVC_SUCCESSOR_SET_READY
ALL_COMPONENTS_RELEASE_TAG_BOUND: FALSE
EXACT_GOVERNED_RUN: PROHIBITED_UNTIL_AGGREGATE_RELEASE_VERIFIED
```
