# SDK 1.2.0 Successor Release Mirror Handoff

Updated: 2026-08-26T14:53:00-05:00

## Goal

Maintain the exact StegVerse SDK 1.2.0 successor release candidate and its release boundary without changing the already validated executable governance source.

```text
goal_id: SDK-1.2.0-SUCCESSOR-RELEASE-001
repository: StegVerse-org/StegVerse-SDK
canonical_branch: main
state: SOURCE_CANDIDATE_VALIDATED_MERGED_RELEASE_PENDING
release_authority: TV/TVC
sdk_authority: NONE
```

## Exact successor identity

The authoritative cross-repository release preparation is `StegVerse-Labs/TVC/docs/POST_RETURN_SUCCESSOR_RELEASE_PREPARATION_MIRROR_HANDOFF.md`.

```text
package: stegverse-sdk
version: 1.2.0
intended_tag: v1.2.0
release_commit: beaabe0a06ef32f0f62fbe6bc360463b245bff61
source_parent: 47a85c402d8d72e1db90445ec272fa83e8a40b08
release_notes: RELEASE_NOTES_1.2.0.md
release relation: exact one-commit note-only successor
```

Current SDK `main` includes the final TVC release-alignment merge at `b736efb6aa3b229852c866b3f618fc3cd48675b0`; moving `main` is not the release identity.

## Validation evidence

```text
Release Dependency Alignment run: 32911807451 PASS
Package Artifact Validation run: 32911807409 PASS
```

The final governed-test source-parent pins accepted by the validated SDK artifact are:

```text
StegCore: ef38410505b0ef3e84148892b1d6e3cdef20f300
Core-Lite: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
Master Records: 03312236c115bc814024d700810391340648601f
```

The earlier candidate pins `124ea6b...` and `3dae8832...` are superseded for the final aggregate release identity.

## Release-only mutation boundary

This lane changes release/package identity and release notes only. It must not reinterpret governance runtime semantics, POST_RETURN behavior, Interlock contracts, standing bridge semantics, or consequence authority.

```text
source validation != release
artifact validation != release
merged candidate != released
moving main != release identity
credential authority: TV/TVC ONLY
GitHub Actions release/runtime authority: NONE
published tag retargeting: PROHIBITED
```

## Trusted Publishing relationship

The SDK repository contains the merged GitHub OIDC Trusted Publishing workflow `.github/workflows/release.yml`, installed through SDK PR #68 / merge `1975838eaa1387f9cc31ffd018103a3793fb4c7d`. PyPI is configured to trust `StegVerse-org/StegVerse-SDK`, workflow `release.yml`, environment `pypi`.

That workflow is publication transport after an exact authorized GitHub Release exists; it does not choose the release candidate or grant TV/TVC release authority. No static `PYPI_TOKEN` is required by the canonical path.

## Current publication state

```text
SDK 1.2.0 source candidate: VALIDATED_MERGED
SDK v1.2.0 immutable tag: NOT YET VERIFIED/PUBLISHED
SDK 1.2.0 GitHub Release: NOT YET VERIFIED/PUBLISHED
PyPI stegverse-sdk 1.2.0: NOT YET VERIFIED/PUBLISHED
Trusted Publisher provenance: NOT YET OBSERVED FOR 1.2.0
successor aggregate receipt: NOT PRESENT
POST_RETURN production proof: NOT COMPLETE
```

Public PyPI currently remains on the historical 1.0.x line until the TV/TVC successor release executes; do not confuse repository version 1.2.0 with a published PyPI release.

## Cross-repository successor set

Canonical exact set is maintained by TVC and currently includes:

- StegVerse SDK 1.2.0 release commit `beaabe0a...`;
- Core-Lite 0.9.0 existing immutable release `018e6080...`;
- StegCore 0.3.0 release commit `58445bb1...`;
- Master Records 0.2.0 release commit `c524b1a0...`.

Actual release requires the exact TV/TVC successor policy, proof-capability containment, a current explicit GRANTED authorization, real SKAP double-Interlock credential custody, immutable tag/release publication, PyPI wheel+sdist Trusted Publisher integrity verification, and a retained aggregate receipt.

## User/manual boundary

No credential may be sent through chat, Drive, GitHub, issues, logs, or screenshots. If the trusted TV/TVC ingress later requests the short-lived release credential, it must be entered only through that bounded owner-authorized surface.

GitHub environment protection for `pypi` is a repository-settings hardening step; the canonical publishing workflow may reference the environment, but required-reviewer/tag protection must be configured in GitHub settings if not already present.

## Next executable boundary

Continue from `StegVerse-Labs/TVC/docs/POST_RETURN_SUCCESSOR_RELEASE_PREPARATION_MIRROR_HANDOFF.md` and `tasks/TVC-POST-RETURN-SKAP-RELEASE-CREDENTIAL-126.json`. Do not publish from moving SDK `main`; do not reuse/move historical tags; do not substitute generic GitHub credentials for TV/TVC authority.

## Completion

This SDK source lane is source-complete and validated. It is not released or activated until the exact successor aggregate release verifies, PyPI provenance is observed, and the downstream genuine POST_RETURN governed proof is retained and reconstructable.
