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
frozen_sdk_candidate: 922d6c5235229e854c36e1a194dc99ed15a31b51
frozen_sdk_tree: d9ddda3dbe942324c921051d89ec19eec3970b16
```

## Governing goal

Every governed evaluator run must identify the exact immutable released component set that participated, retain that set with exact-run custody, and distinguish it from both moving source branches and later releases used during replay/reconstruction.

The release-set mechanism is evaluator-neutral. A named evaluation supplies configuration and evidence requirements through the generalized SDK surface; it does not create a custom SDK route or custom StegGate semantics.

## Package/version identity reconciliation

Historical `v1.0.13` resolves to `f219afa17dcb020dc1e13b72f859a86627c5644b` (`Bump to 1.0.13`, 2026-04-29). Modern SDK source had continued declaring package `1.0.13`, while legacy `setup.py` independently declared `2.1.0` with conflicting dependency, Python, and console metadata.

PR #50 repaired that split:

```text
PR #50 merge: 459e88f640c36805ae2e24484604f3976809b69f
canonical metadata source: pyproject.toml
canonical modern package version: 1.1.0
legacy setup.py: metadata-free compatibility shim
target public SDK tag: v1.1.0
```

`v1.0.13` is immutable historical evidence and MUST NOT be moved or reused. Modern SDK source MUST NOT be published to PyPI as `1.0.13`. The unpublished `v1.0.13-oda3-r1` and `v1.0.13-evaluation-r2` candidates are superseded and MUST NOT be published.

## Exact 1.1.0 artifact proof and candidate freeze

A dedicated non-authorizing package-artifact gate was installed in PR #51 and exercised by PR #52.

```text
validation workflow: SDK Package Artifact Validation (Non-Authorizing)
validation run: 32251339936
validated PR head: 2d70d6e2279aecc3195d52086e6b259a4629d620
validated tree: d9ddda3dbe942324c921051d89ec19eec3970b16
result: SUCCESS
PR #52 squash merge: 922d6c5235229e854c36e1a194dc99ed15a31b51
merge tree: d9ddda3dbe942324c921051d89ec19eec3970b16
```

The validated PR head and squash-merge candidate have the exact same Git tree. The artifact proof therefore applies to the frozen merge source tree without substituting moving `main`.

The successful gate proved:

```text
python -m build: PASS
exactly one wheel + one sdist: PASS
wheel Name: stegverse-sdk
wheel Version: 1.1.0
wheel Requires-Python: >=3.9
canonical dependencies from pyproject.toml: PASS
canonical console entry points from pyproject.toml: PASS
python setup.py --name: stegverse-sdk
python setup.py --version: 1.1.0
fresh virtualenv wheel install: PASS
import stegverse: PASS
installed distribution version: 1.1.0
stegverse --help smoke: PASS
GITHUB_TOKEN/GH_TOKEN/PYPI_API_TOKEN during validation: ABSENT
release authority from validation: NONE
```

Candidate freeze:

```text
SDK 1.1.0 frozen candidate: 922d6c5235229e854c36e1a194dc99ed15a31b51
SDK 1.1.0 frozen tree: d9ddda3dbe942324c921051d89ec19eec3970b16
target tag: v1.1.0
candidate state: ARTIFACT_VALIDATED_FROZEN_AWAITING_TVC_RELEASE_SET_REISSUE
```

Later task/handoff commits do not alter this frozen candidate. Any release-worthy source change after the freeze requires a new artifact proof and new release-set revision.

## Superseded R2 and successor requirement

```text
superseded release_set_id: EVALUATION-BOUNDARY-2026-08-18-R2
superseded SDK coordinate: StegVerse-org/StegVerse-SDK@v1.0.13-evaluation-r2
superseded SDK commit: cfd6069823cc35d263ce0128fb0e6c0125d8bb64
state: SUPERSEDED_DO_NOT_PUBLISH
```

TVC must reissue the generalized aggregate release set as a new immutable revision with `StegVerse-org/StegVerse-SDK@v1.1.0` bound exactly to `922d6c5235229e854c36e1a194dc99ed15a31b51`. Reissue preserves the superseded R2 evidence rather than rewriting it.

Downstream source lineage retained from R2 pending revalidation in the successor set:

```text
Data-Continuation/core-lite
  release candidate: 018e608018a793ee6dc62f4fdea59a3415e6e80e
  executable parent: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8

StegVerse-Labs/StegCore
  release candidate: 23b388ce23b08097593b5b5593eb4061e0ff5242
  executable parent: 083557adec1bdbace09ebd10fb0765eb8e9a9d08
  runtime identity: stegverse:steggate:canonical:three-layer:v1

master-records/orchestration
  release candidate: 4826f753641cc82bbb885f919494a6c1318fbae4
  executable parent: 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

## Release semantics

```text
moving branch != release identity
source validation != released
artifact validation != released
workflow pass != runtime
package build != publication
tag readiness != tag publication
release readiness != released
published package != runtime activation
commit pin != release tag
existing tag must never be retargeted
replay/reconstruction never rewrites original release-set evidence
```

## TV/TVC boundary

Actual tag, GitHub Release, and package publication remains a TV/TVC-governed release-authority action. GitHub Actions is validation-only and must not become production/runtime/control-plane/release authority. No non-TV/TVC release credential is permitted.

## Cross-repo coordination

```text
StegVerse-org/StegVerse-SDK#47
StegVerse-Labs/TVC/TVC_MIRROR_HANDOFF.md
StegVerse-Labs/TVC/docs/AGGREGATE_RELEASE_MIRROR_HANDOFF.md
StegVerse-Labs/TVC successor aggregate-release task: REQUIRED
Data-Continuation/core-lite/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
master-records/orchestration/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
```

## Remaining executable work

```text
1. Reissue the TVC aggregate release configuration/catalog/task with v1.1.0 -> 922d6c5235229e854c36e1a194dc99ed15a31b51.
2. Disable the superseded R2 publication entrypoints so the old SDK coordinate cannot execute accidentally.
3. Run exact TVC source validation for the successor policy in an admitted TVC source environment.
4. Invoke successor readiness; remain blocked if TVC-managed ephemeral publication capability is absent.
5. TV/TVC publishes/verifies all immutable tags/releases and stegverse-sdk 1.1.0 only when READY.
6. Verify PyPI artifact identity, GitHub tag resolution, GitHub Release identity, and clean-install behavior agree with the frozen candidate.
7. Retain and verify the TVC aggregate-release receipt and update release catalog to tag-bound.
8. Execute the exact governed evaluator submission beginning at ordinary SDK manifest ingress.
9. Retain manifest/result/route receipts/Master Records custody/reconstruction/replay/independent verification evidence.
10. Verify release/changelog propagation to StegVerse-Labs/Site (or canonical successor if renamed), GCAT-BCAT-Engine/Publisher, admissibility-wiki, and stegguardian-wiki.
```

## Status

```text
SDK_GENERALIZED_TESTING_SURFACE: IMPLEMENTED_SOURCE_VALIDATED_MERGED
SDK_HISTORICAL_V1_0_13: IMMUTABLE_PRESERVED
SDK_METADATA_SPLIT: REPAIRED
SDK_CANONICAL_PACKAGE_VERSION: 1.1.0
SDK_1_1_0_ARTIFACT_VALIDATION: PASS
SDK_1_1_0_FROZEN_CANDIDATE: 922d6c5235229e854c36e1a194dc99ed15a31b51
OLD_V1_0_13_DERIVED_CANDIDATES: SUPERSEDED_DO_NOT_PUBLISH
AGGREGATE_RELEASE_SET_SUCCESSOR: REQUIRED_TVC_REISSUE
TAG_PUBLICATION: NOT_YET_AUTHORIZED
PYPI_1_1_0_PUBLICATION: NOT_YET_PUBLISHED
ALL_COMPONENTS_RELEASE_TAG_BOUND: FALSE
EXACT_GOVERNED_RUN: PROHIBITED_UNTIL_AGGREGATE_RELEASE_VERIFIED
ARCHIVE_ELIGIBILITY: FALSE
```
