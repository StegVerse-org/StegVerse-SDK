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

## Canonical production component set

```text
sdk_entry              StegVerse-org/StegVerse-SDK
                       package stegverse-sdk

governance_runtime     StegVerse-Labs/StegCore
                       package stegcore
                       validated governed-test pin 083557adec1bdbace09ebd10fb0765eb8e9a9d08

manifest_route_carrier Data-Continuation/core-lite
                       package stegverse-core-lite
                       validated governed-test pin 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8

exact_run_custody      master-records/orchestration
                       package stegverse-master-records
                       validated governed-test pin 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

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

## Current release gap

```text
StegVerse SDK latest published release: v1.0.12
StegVerse SDK source package version: 1.0.13
StegCore evaluator-runtime candidate: no matching release yet
Core-Lite evaluator-runtime candidate: no release yet
Master Records evaluator-runtime candidate: no release yet
```

The existing StegCore `stegcore-v1.0-constitution` release is not the runtime candidate pinned by the governed evaluator lane.

## Validation evidence

```text
workflow: Evaluator Contract Console Validation
run: 31963202570
head: fe6e0896d70b3a17e6add9d5691ee1d2d7f798c2
result: SUCCESS
```

The run exercised:

```text
pytest -q tests/test_evaluator_contract_console.py tests/test_production_release_set.py
stegverse contract
stegverse contract --schema
stegverse contract --example
stegverse test-procedure --offline
stegverse production-releases installed
python -m stegverse contract --all
```

and verified the production release-set schema, historical retention declaration, replay comparison declaration, and existing evaluator contract invariants.

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

These tasks require the TV/TVC-governed release workers to mint releases for the exact validated candidates, publish accessible changelogs, and propagate the resulting release identity back to the SDK.

## Remaining executable work

```text
1. Freeze final SDK 1.0.13 candidate head after release-set documentation is complete.
2. TV/TVC release workers validate and mint releases for the three pinned dependency commits.
3. Replace governed-test dependency commit references with the corresponding immutable release tags only after those tags exist.
4. Validate the tag-based installation and release-set packet evidence.
5. Publish SDK v1.0.13 from the final validated candidate.
6. Record completed release set in evaluator-facing release catalog/release notes.
7. Continue subsequent development on new/moving branches without altering released tags.
8. Verify release/changelog propagation to StegVerse-Labs/Site, GCAT-BCAT-Engine/Publisher, admissibility-wiki, and stegguardian-wiki.
```

## Status

```text
SDK-PRODUCTION-RELEASE-SET-001: IMPLEMENTED_SOURCE_VALIDATED
CROSS_REPO_RELEASE_ACTIVATION: DURABLY_ASSIGNED_TO_TV_TVC_RELEASE_WORKERS
ALL_COMPONENTS_RELEASE_TAG_BOUND: FALSE_UNTIL_RELEASES_EXIST
```
