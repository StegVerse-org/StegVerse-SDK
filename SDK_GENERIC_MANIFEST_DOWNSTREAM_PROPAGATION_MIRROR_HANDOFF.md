# SDK Generic Manifest Downstream Propagation Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
source_goal: SDK-PROCESSOR-GENERIC-MANIFEST-002
source_cosv: 71000000100110
continuation_goal: SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003
coordination_state: DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This handoff is the current source of truth for processor-generic downstream propagation, public governed-runtime distribution remediation, and the post-`v1.2.0` SDK successor source candidate.

## Canonical processor-generic semantics

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance-specific fields are not universal manifest requirements
unsupported or uninstalled processor/route execution fails closed
DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
```

Current executable processor:

```text
processing.capability: governance
processing.route_id: stegverse.route.canonical-governed.v1
processor-specific request: extensions.stegverse_governance_request
```

## Experiment-manifest correction — 2026-09-10

Experiment-specific protocol data belongs in the caller-authored experiment manifest rather than SDK behavior. `stegverse external-run --experiment-manifest <json>` retains that object unchanged under `extensions.experiment_manifest`, outside both source-native payload data and `extensions.stegverse_governance_request`. Changing an experiment therefore changes its manifest, not SDK code or a special runtime route.

ELAN Test 1 declares the E1/E2 state-establishment sequence, E3 evaluated condition, continuity requirements, non-interference statements, requested processing, and requested evidence in `inspection/examples/elan-test1-experiment-manifest.json`. The evaluator declaration remains separate WHAT/HOW/WHY metadata. The ELAN runbook consumes the caller-authored manifest rather than defining special SDK execution semantics.

The confidential source-owner packet remains outside this repository. Observable evidence received so far is limited to Events 1 and 2; the packet explicitly states Event 3 has not yet been submitted. No missing ELAN internal state is inferred.

PR #166 exact-head validation at `53e17cd67e7b2b27f0ffc0fa880d9f480c6cd202`:

```text
Evaluator Contract Console Validation 34491261898 PASS
Generic Manifest Downstream Contract Validation 34491261810 PASS
Manifest Builder Source Validation 34491261813 PASS
Evaluator Manifest Source Validation 34491261878 PASS
External Framework Public Submission Validation 34491261847 PASS
SDK Package Artifact Validation 34491261869 PASS
```

## Completed SDK generic-manifest package work

```text
completion PR: #138 MERGED
merge: 4e1942b487972874ce310f4a9ec031f529fa1f09
one-command surface: stegverse external-run
public preparation mode: --prepare-only
submission schema: stegverse.sdk.external-framework-submission.v1
executed schema: stegverse.sdk.external-framework-run.v1
```

The SDK preserves source-native data, evaluator preregistration outside the governance decision request, caller-authored experiment metadata outside the governance decision request, declared processor/route binding, caller-selected return projection, fail-closed unsupported routing, canonical `manifest_receipt_id`, replay, and reconstruction.

## Public runtime distribution remediation

```text
StegCore import namespace: stegcore
StegCore public distribution: stegverse-stegcore
StegCore target version: 0.3.0
StegCore distribution rename PR: StegVerse-Labs/StegCore#197 MERGED
StegCore merge: 9a35f39b3425a2c3e9592a03b0362a417094b809
StegCore README maintenance: COMPLETE

Master Records public distribution: stegverse-master-records
Master Records target version: 0.2.0
Master Records exact frozen source parent: 03312236c115bc814024d700810391340648601f
Master Records release-candidate commit: c524b1a0c1a43e49c70faeac7b67f78c5908e4e4
Master Records Trusted Publishing PR: master-records/orchestration#85 MERGED
Master Records README maintenance: COMPLETE
```

SDK governed-test candidate dependencies:

```text
stegverse-stegcore==0.3.0
stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
stegverse-master-records==0.2.0
```

## SDK successor state

```text
aggregate successor PR: StegVerse-org/StegVerse-SDK#165
branch: sdk-1.3.0-successor-candidate
head: b53fb8c26688c8ea02ac336c5b876b3e6aa189cb
candidate version: 1.3.0
intended tag: v1.3.0
version stage: SOURCE_CANDIDATE
release/tag/publication claim: NONE
```

PR #165 remains DRAFT. Its source validation passed, but anonymous governed-runtime installation remains blocked by missing public distribution `stegverse-stegcore==0.3.0`.

## Downstream completion state

### StegVerse-Labs/Site

```text
pertinent: YES
required propagation: align Site SDK preview/backend-facing manifest description with processing.capability, processing.route_id, processor-specific extensions, return_projection, manifest_receipt_id, and the portable submission boundary
current repository state: OBSERVED_BLOCKED
external_tasks_allowed: false
external_session_ownership_allowed: false
current machine blocker: SITE-0001-COHERENT-TRANSITION-THRESHOLD-ACTIVATION
completion predicate: FALSE
```

### StegVerse-Labs/admissibility-wiki

```text
pertinent: YES
required propagation: bounded processor-generic SDK interoperability doctrine
coordinator: issue #66
implementation owner: Worker D / issue #65
worker transition observed: false
completion predicate: FALSE
```

## Public surfaces

```text
canonical public domain: https://stegverse.org/
current Ecosystem Chat route: https://stegverse.org/ecosystem-chat.html
dedicated processor-generic hosted route: NOT YET OBSERVED
```

## Remaining work

```text
StegVerse-org/StegVerse-SDK:
  - merge PR #166 after exact-head validation if repository merge policy admits it
  - keep PR #165 draft while public package/release gate is unsatisfied
  - prepare ELAN Test 1 through the public SDK surface using the caller-authored experiment manifest and exact externally supplied source evidence
  - do not claim complete ELAN governed execution until Event 3 source evidence and experiment-applicable governance facts are available
  - after authentic public distributions exist, rerun Anonymous Governed Runtime Install and complete governed E2E custody/replay/reconstruction

StegVerse-Labs/StegCore:
  - authentic immutable/public publication of stegverse-stegcore 0.3.0 under canonical release gate

master-records/orchestration:
  - authentic immutable/public publication of stegverse-master-records 0.2.0 under canonical release gate

StegVerse-Labs/Site:
  - Site-owned admitted SDK preview/backend contract propagation after repository orchestration admits it

StegVerse-Labs/admissibility-wiki:
  - Worker D-owned processor-generic interoperability doctrine propagation
```

## Current status

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
experiment-manifest remediation: EXACT_HEAD_VALIDATION_PASS / PR_166_READY_FOR_MERGE_RECONCILIATION
SDK 1.3.0 source candidate: EXACT_HEAD_SOURCE_VALIDATED_MERGEABLE_DRAFT_PR_165
first proven anonymous-install blocker: stegverse-stegcore==0.3.0 NOT PUBLISHED
ELAN Test 1 source evidence: EVENTS_1_2_OBSERVED / EVENT_3_PENDING
Site completion predicate: FALSE / MACHINE_OWNED
admissibility completion predicate: FALSE / WORKER_OWNED
manual user work: NONE
```
