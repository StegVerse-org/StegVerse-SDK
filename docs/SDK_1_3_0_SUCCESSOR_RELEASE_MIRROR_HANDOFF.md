# SDK 1.3.0 Successor Release Mirror Handoff

Updated: 2026-09-09

## Goal

Prepare a distinct post-`v1.2.0` StegVerse SDK successor source candidate that carries the processor-generic ingress and public governed-runtime distribution remediation without retargeting the frozen `v1.2.0` identity.

```text
goal: SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003
repository: StegVerse-org/StegVerse-SDK
candidate_version: 1.3.0
intended_tag: v1.3.0
candidate_branch: sdk-1.3.0-successor-candidate
source_parent: b229a7a93a59bdd93e134ed1e219e482a81aefb1
state: SOURCE_CANDIDATE
release_authority: TV/TVC
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

## Contained successor work

The candidate is stacked on SDK PR #163 and therefore includes its public governed-test distribution rewrite:

```text
stegverse-stegcore==0.3.0
stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
stegverse-master-records==0.2.0
```

It also includes the merged processor-generic external-framework SDK work inherited through the PR #163 source parent, including `stegverse external-run`, source-native manifest preservation, processor/route separation, preregistration retention outside governance input, caller-selected return projection, canonical receipt identity, replay, and reconstruction.

## Version-state contract

```text
pyproject.toml: 1.3.0
VERSION.json component_version: 1.3.0
VERSION.json version_stage: SOURCE_CANDIDATE
RELEASE_NOTES_1.3.0.md: present
candidate frozen_commit: null until exact freeze validation
candidate artifact validation: PENDING until observed
release.tag: null
release.commit: null
release evidence: empty
```

`scripts/check_component_version.py` enforces this source-candidate state and also enforces that the prior `v1.2.0` identity remains immutable.

## Prior frozen identity

```text
prior version: 1.2.0
prior tag: v1.2.0
prior release commit: beaabe0a06ef32f0f62fbe6bc360463b245bff61
retargeting permitted: false
```

No branch movement, PR merge, source validation, package build, or chat session may move or reinterpret that prior coordinate.

## Current distribution dependency gate

The public source-visibility defect has been remediated in source, but the anonymous governed-runtime install remains blocked until the exact public packages are authentically released:

```text
StegCore public distribution: stegverse-stegcore 0.3.0
Master Records public distribution: stegverse-master-records 0.2.0
latest SDK anonymous install evidence: run 34329494516 FAILURE at package installation
private source visibility is current blocker: false
exact PyPI publication is current blocker: true
```

Do not weaken the anonymous install gate. After authentic public publication, rerun it and require package identity verification, ELAN Test 1 execution, Master Records custody, replay, and reconstruction PASS.

## Release gate

Actual `v1.3.0` freeze/publication is not authorized by this source preparation. Before release:

1. exact candidate head must pass repository-native validation;
2. an exact frozen candidate commit must be recorded in `VERSION.json` and this handoff;
3. TVC successor policy must explicitly carry the new SDK coordinate rather than the old `v1.2.0` coordinate;
4. current TV/TVC GRANTED authorization and required SKAP double-interlock resident evidence must exist;
5. GitHub Release and PyPI publication must use immutable exact coordinates and Trusted Publisher provenance;
6. the anonymous governed-runtime install + ELAN E2E gate must pass against those published distributions.

The live TVC release-credential task remains `BLOCKED_DEPENDENCY` / `REQUESTED_NOT_GRANTED`; therefore no tag or release is created now.

## README maintenance

The candidate inherits PR #163 README maintenance, which already corrects the governed-test acquisition description to public distribution identities. No contradictory release claim is added: the README must continue to describe installation behavior without claiming that `v1.3.0` is published before publication evidence exists.

## Downstream propagation relationship

This version lane does not alter the two remaining downstream blockers for `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`:

```text
StegVerse-Labs/Site completion predicate: false / machine-owned
StegVerse-Labs/admissibility-wiki completion predicate: false / Worker D-owned
```

Publisher and stegGuardian still require no direct processor-generic contract mutation at this point.

## Next actions

```text
validate exact source-candidate head
if validation passes, freeze exact 1.3.0 source candidate without publishing
continue Site/Worker D observation only through their owned lanes
await exact public runtime package publication under TV/TVC gate
rerun anonymous governed-runtime install + ELAN E2E after publication
reconcile canonical task handoff and COSV registry after observed transitions
```
