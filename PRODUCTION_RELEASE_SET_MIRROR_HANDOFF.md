# Production Release Set Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
credential_authority: TV/TVC
non-TV/TVC release credential permitted: false
```

## Goal

Every production-lane evaluator run must identify the exact released component set that participated, retain that set with exact-run custody, and distinguish it from whatever releases are current when replay/reconstruction occurs later.

## Canonical ODA3 aggregate release set

```text
release_set_id: ODA3-EVALUATOR-PATH-2026-08-18-R1
aggregate_manifest: evidence/oda3/aggregate-release-set-candidate-2026-08-18.json

sdk_entry              StegVerse-org/StegVerse-SDK
                       package stegverse-sdk 1.0.13
                       target tag v1.0.13
                       frozen candidate 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
                       frozen tree d238131690fdc3833cc861b69b0760e570e2b55a
                       release notes RELEASE_NOTES_EVALUATOR_PATH_1.0.13.md

manifest_route_carrier Data-Continuation/core-lite
                       package stegverse-core-lite 0.9.0
                       target tag v0.9.0
                       validated candidate 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
                       release notes RELEASE_NOTES_EVALUATOR_PATH_0.9.0.md

governance_runtime     StegVerse-Labs/StegCore
                       package stegcore 0.2.0
                       target tag v0.2.0
                       validated candidate 083557adec1bdbace09ebd10fb0765eb8e9a9d08
                       runtime identity stegverse:steggate:canonical:three-layer:v1
                       release notes RELEASE_NOTES_EVALUATOR_PATH_0.2.0.md

exact_run_custody      master-records/orchestration
                       package stegverse-master-records 0.1.0
                       target tag v0.1.0
                       validated candidate 6626c6a7f1df6bf531940c165b2f4db374e08b92
                       release notes RELEASE_NOTES_EVALUATOR_PATH_0.1.0.md
```

The SDK candidate is the already-frozen ODA3 source-validated candidate. Later receipt/documentation commits do not silently move that candidate. A replacement candidate requires a new source receipt and explicit release-set revision.

## External evaluator surface invariant

```text
evaluator submission surface: StegVerse SDK
direct evaluator Core-Lite submission: not authorized
direct evaluator StegCore submission: not authorized
direct evaluator StegGate submission: not authorized
```

The external evaluator enters through the controlled manifested SDK path. Core-Lite, StegCore, and StegGate remain downstream governed/internal surfaces for this experiment.

## Implemented SDK surfaces

```text
stegverse test-procedure
stegverse test-procedure --offline
stegverse production-releases catalog
stegverse production-releases installed
```

New governed runs through both:

```text
stegverse governance --select 0 --input <request.json>
python -m stegverse.public_inspection_runtime run <request.json>
```

bind `production_release_set` into exact-run evidence. Replay and reconstruction return:

```text
original_production_release_set
current_production_release_set
production_release_set_comparison
historical_release_set_available
```

## Release semantics

```text
moving branch != release identity
commit pin != release tag
release tag must resolve to immutable candidate commit
release notes/changelog are part of evaluator-facing release metadata
future release != historical runtime substitution
replay/reconstruction never rewrites original release-set evidence
```

`all_components_release_tag_bound` is true only when every installed production component can prove a tag-based source revision. A commit-only or untagged package is reported as `COMMIT_OR_PACKAGE_ONLY` rather than being represented as a release.

## Release readiness

The three dependency release handoffs now have fixed target tags and prepared release notes bound to the already-validated historical candidates. The SDK aggregate manifest fixes the SDK candidate and target tag as well.

```text
StegVerse SDK target: v1.0.13 -> 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
Core-Lite target:     v0.9.0  -> 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
StegCore target:      v0.2.0  -> 083557adec1bdbace09ebd10fb0765eb8e9a9d08
Master Records target:v0.1.0  -> 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

Actual tag/release publication remains a TV/TVC-governed release-authority action. GitHub Actions must not become runtime/control-plane authority and no non-TV/TVC release credential is permitted.

## Validation evidence

```text
workflow: Evaluator Contract Console Validation
run: 31963202570
head: fe6e0896d70b3a17e6add9d5691ee1d2d7f798c2
result: SUCCESS

ODA3 source/boundary validation:
run: 32166903844
job: 95808521073
validated head: d4d615bb63d02894b2e26497285d259892112739
validated tree: d238131690fdc3833cc861b69b0760e570e2b55a
merged frozen candidate: 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
24 source/boundary tests: PASS
17 exact artifacts hashed; missing artifacts: []
```

The ODA3 validated PR head and frozen SDK candidate share the exact same Git tree.

## Cross-repo worker tasks

Durable release-control handoffs:

```text
StegVerse-Labs/StegCore/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
Data-Continuation/core-lite/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
master-records/orchestration/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
```

Durable worker issues:

```text
StegVerse-Labs/StegCore#140
Data-Continuation/core-lite#15
master-records/orchestration#35
StegVerse-org/StegVerse-SDK#41
```

## Remaining executable work

```text
1. TV/TVC release authority publishes the four fixed tags against the exact candidates.
2. Publish/attach the prepared accessible release notes/changelogs.
3. Verify each tag resolves to the exact recorded candidate commit.
4. Update the aggregate manifest/catalog from tag-publication-pending to tag-bound.
5. Validate tag-based installation and release-set packet evidence.
6. Execute ODA3 issue #47 through evaluator -> SDK -> Core-Lite -> StegCore/StegGate -> Master Records.
7. Record the completed release set in exact-run custody and the evaluator-facing packet.
8. Verify release/changelog propagation to StegVerse-Labs/Site, GCAT-BCAT-Engine/Publisher, admissibility-wiki, and stegguardian-wiki.
```

## Status

```text
SDK-PRODUCTION-RELEASE-SET-001: IMPLEMENTED_SOURCE_VALIDATED
ODA3_AGGREGATE_RELEASE_SET: FROZEN_RELEASE_READY
RELEASE_NOTES_ALL_COMPONENTS: PREPARED
TARGET_TAGS_ALL_COMPONENTS: FIXED
TAG_PUBLICATION: PENDING_TV_TVC_RELEASE_AUTHORITY
ALL_COMPONENTS_RELEASE_TAG_BOUND: FALSE_UNTIL_RELEASES_EXIST
```
