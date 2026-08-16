# Production Release Sets

Production-lane evaluator evidence must identify the exact software state that participated in a governed run. A moving branch is not a sufficient historical identifier.

## Evaluator inspection

```bash
stegverse test-procedure
stegverse production-releases catalog
stegverse production-releases installed
```

`stegverse test-procedure` shows the evaluator contract, the canonical test path, the installed production release set, and—unless `--offline` is used—the current public release catalog.

The catalog covers:

```text
StegVerse-org/StegVerse-SDK
StegVerse-Labs/StegCore
Data-Continuation/core-lite
master-records/orchestration
```

Each public release entry includes its tag, publication time, release URL, and release-body changelog.

## Run evidence

New production-validation runs retain a `production_release_set` with the exact installed component identities. Each component reports:

```text
repository
distribution/package
installed version
commit SHA when available
requested source revision when available
release tag when provable
release/changelog URL when tag-bound
release binding status
```

A commit pin is not represented as a release. Until a component is installed from a durable release tag, it is reported as `COMMIT_OR_PACKAGE_ONLY`.

## Replay and reconstruction

Replay and reconstruction preserve the original release set and also inspect the current installed set. Their returned artifact includes:

```text
original_production_release_set
current_production_release_set
production_release_set_comparison
```

This allows an evaluator returning weeks or months later to see that the original run used release set A while the currently installed ecosystem uses release set B. The historical record is not mutated.

## Release procedure

For a validated production-lane state:

1. identify the exact commits that were actually validated;
2. tag and publish those exact commits rather than substituting later `main` heads;
3. publish an accessible changelog/release note for every component release;
4. record the release identities in the SDK release catalog;
5. install production dependencies from those immutable release tags;
6. validate the tag-based installation;
7. publish the matching SDK release;
8. continue later development without moving or reusing the released tags.

A later release is comparable to an earlier release, not a replacement for it.

## Authority boundary

Release metadata is provenance evidence. It does not grant execution authority, change StegGate disposition, or permit route augmentation.
