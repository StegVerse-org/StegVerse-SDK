# Production Release Sets

Production-lane evaluator evidence must identify the exact software state that participated in a governed run. A moving branch is not a sufficient historical identifier.

## Identifying the SDK of record

The SDK of record is identified from its tags and published releases, never from branch recency. A release candidate whose tag and package publication are pending is not a release. This is item 6 of the owner's [system-division statement](SYSTEM_DIVISION.md).

Before identifying a release or describing a capability as released:

1. State the component and product scope. An experiment snapshot in this repository is not automatically a release of the SDK package.
2. Read the repository's tag refs and published release records. Resolve an annotated tag to its commit; record both the tag object and the peeled commit when applicable. A moving release target such as `main` is not the tag's immutable source identity.
3. Retain the matching tag, immutable commit, published release URL, publication time and prerelease state. Report tag-only, release-only, missing and conflicting evidence explicitly. Package publication is a separate check; do not infer it from a tag or release page.
4. When only a candidate or commit is established, use `RELEASE_CANDIDATE` or `COMMIT_OR_PACKAGE_ONLY` as applicable and state what publication evidence is missing. A newer branch or larger version string does not promote a candidate into a release.
5. If an experiment intentionally uses a revised source commit, freeze and name that commit as the experiment's source identity while retaining the independently established release identity. Do not rewrite the original run's release basis during replay.
6. Verify capability claims against the selected immutable release/source and its retained evidence. A validation run establishes its tested scope; it does not publish a release or establish runtime activation.

Record the operating check where the lane files its outcome:

| Field | Required evidence |
|---|---|
| Component / product scope | SDK package, experiment snapshot, or other named component |
| Tag / tag object | Exact ref and immutable object, or an explicit absence |
| Source commit | Peeled tag commit, independently distinguished from branch head |
| Published release | Matching release URL, publication time and prerelease state, or explicit absence |
| Package publication | Independently observed package identity, or unverified/pending |
| Candidate / source identity | Exact candidate or experiment commit and its evidence class |
| Capability basis | Selected immutable source and the validation/runtime evidence actually observed |

This check records identity and provenance. The existing TV/TVC publication authority and repository integration requirements still apply.

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

New sets use schema `stegverse.production-release-set.v2`. Its run-evidence component has the role `downstream_run_evidence` and is the SDK's own local run record (`stegverse/local_run_record.py`; non-authoritative, authority_effect NONE, completes_transition false). Schema `v1` is frozen: its roles, including the former `exact_run_custody` entry for `stegverse-master-records`, stay only so a recorded v1 set verifies exactly as recorded. Master Records is not a release-set component of new runs; sovereign completion comes only from a verified organization-ledger readback (`stegverse/organization_ledger_evidence.py`).

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
