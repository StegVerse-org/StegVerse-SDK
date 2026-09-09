# SDK 1.3.0 Deployable Unit Mirror Handoff

Updated: 2026-09-09
Repository: `StegVerse-org/StegVerse-SDK`

## Goal

Prepare one deployable successor SDK package that contains the completed processor-generic external-framework path without retargeting the separately frozen SDK 1.2.0 release identity.

```text
goal_id: SDK-1.3.0-DEPLOYABLE-UNIT-001
package: stegverse-sdk
version: 1.3.0
intended_tag: v1.3.0
state: CANDIDATE_PREPARATION_ACTIVE_UPSTREAM_PUBLICATION_BLOCKED
canonical_pr: StegVerse-org/StegVerse-SDK#163
```

## Included SDK capability

The candidate includes:
- processor-generic `stegverse.ingress-manifest.v1` semantics;
- source-native manifested-data preservation;
- explicit processing capability and route binding;
- Manifest Builder;
- `stegverse external-run` and `--prepare-only`;
- preregistration isolation from decision inputs;
- caller-selected projection;
- manifest receipt output;
- replay and reconstruction;
- reproducible ELAN Test 1 fixture/runbook;
- corrected public governed-runtime dependency model.

## Public governed-test dependency contract

```text
stegverse-stegcore==0.3.0
stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
stegverse-master-records==0.2.0
```

The exact upstream source bindings remain enforced by `stegverse/release_dependency_alignment.py`.

## Current validation state

On PR #163 head `b229a7a93a59bdd93e134ed1e219e482a81aefb1`, all ordinary SDK validation lanes passed except `Anonymous Governed Runtime Install` run `34329494516`.

That workflow failed during dependency resolution with:

```text
No matching distribution found for stegverse-stegcore==0.3.0
```

This is an upstream package-publication blocker, not a generic SDK source failure.

## Upstream publication trackers

```text
StegVerse-Labs/StegCore#198
  -> publish exact stegverse-stegcore==0.3.0
  -> exact SDK source binding ef38410505b0ef3e84148892b1d6e3cdef20f300

master-records/orchestration#88
  -> publish exact stegverse-master-records==0.2.0
  -> exact SDK source binding 03312236c115bc814024d700810391340648601f
```

Both upstream release lanes already contain Trusted Publishing workflows. Publication evidence must be authentic before this SDK candidate is promoted.

## Merge readiness contract

PR #163 may leave draft only after:
1. both public runtime distributions are anonymously resolvable;
2. Anonymous Governed Runtime Install PASS;
3. ELAN Test 1 governed execution PASS;
4. receipt/custody/replay/reconstruction PASS;
5. package identity reports `stegverse-sdk==1.3.0`;
6. exact-head SDK package/dependency/source checks PASS.

## Release boundary

`v1.2.0` is immutable and must not be moved or reused.

The 1.3.0 package candidate is not RELEASED merely because source or CI passes. A real `v1.3.0` tag/GitHub Release/PyPI publication must be separately observed before release state is promoted.

## Canonical continuation

- SDK PR #163
- SDK issue #145
- SDK issue #139
- StegCore issue #198
- Master Records issue #88
- `RELEASE_NOTES_1.3.0.md`
