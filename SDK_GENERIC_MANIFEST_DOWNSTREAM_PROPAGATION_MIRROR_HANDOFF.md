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

The experiment-specific ELAN Event-3 protocol is no longer treated as SDK behavior. The SDK now exposes one generic caller-facing `--experiment-manifest` input on `stegverse external-run`. When supplied, the caller-authored object is retained unchanged under `extensions.experiment_manifest` in the generated `stegverse.ingress-manifest.v1` and remains separate from the processor-specific governance request.

The ELAN-specific protocol is declared in:

```text
inspection/examples/elan-test1-experiment-manifest.json
```

That manifest declares the controlled state-establishment sequence, evaluated condition, continuity requirements, non-interference statements, requested processing, and requested evidence. Changing those experiment-specific values does not require SDK code changes or a special runtime route.

The source payload, governance request, evaluator declaration, and experiment manifest remain separate inputs. The evaluator declaration now refers to the caller-declared experiment protocol rather than embedding it. The runbook now documents this separation and passes `--experiment-manifest` explicitly.

Branch implementation evidence:

```text
branch: sdk-evaluator-bias-remediation
PR: #166 DRAFT
experiment manifest creation: 1b14080d9c558e2a12ed9e1da906478450e21fc1
generic external-run experiment-manifest support: 0e87727d215c4af9e64935e551652550d7576f59
experiment-manifest regression coverage: 2e9eb07bb0c1aadc0bc11fcdeebbf8ee5a94fc8c
runbook manifest-boundary correction: e4aa2215c91c218a5ee8cf7af1b9d72d780028d8
evaluator declaration separation: ba91c2ef102bf6c6787b78996125162caec8134f
exact validated head: fc198266570f24a4c7bba57dfb63b1f5adaf1bc2
merge claim: NONE
```

Exact-head PR #166 validation:

```text
Generic Manifest Downstream Contract Validation 34489612531 PASS
Evaluator Manifest Source Validation 34489612534 PASS
Manifest Builder Source Validation 34489612514 PASS
External Framework Public Submission Validation 34489612580 PASS
Evaluator Contract Console Validation 34489612530 PASS
SDK Package Artifact Validation 34489612526 PASS
```

The confidential source-owner ELAN PDF remains outside the public repository. No runtime outcome is inferred from it.

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

## Successor consolidation and merge-base repair

SDK PR #163 is CLOSED / SUPERSEDED. Its public-distribution rewrite and README correction are incorporated into aggregate SDK PR #165.

```text
aggregate successor PR: StegVerse-org/StegVerse-SDK#165
branch: sdk-1.3.0-successor-candidate
head: b53fb8c26688c8ea02ac336c5b876b3e6aa189cb
candidate version: 1.3.0
intended tag: v1.3.0
version stage: SOURCE_CANDIDATE
prior frozen SDK identity: v1.2.0 / beaabe0a06ef32f0f62fbe6bc360463b245bff61
v1.2.0 retargeting permitted: false
release/tag/publication claim: NONE
```

PR #165 remains DRAFT. Its source validation passed, but anonymous governed-runtime installation is still blocked by missing public distribution `stegverse-stegcore==0.3.0`.

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

Conectrr contamination is resolved. Site remains machine-owned; do not collide with its task lane.

### StegVerse-Labs/admissibility-wiki

```text
pertinent: YES
required propagation: bounded processor-generic SDK interoperability doctrine
coordinator: issue #66
implementation owner: Worker D / issue #65
transfer comment: #65 issuecomment-5592480056
public-route constraint: #65 issuecomment-5593234328
worker transition observed: false
completion predicate: FALSE
```

Do not duplicate Worker D implementation.

### GCAT-BCAT-Engine/Publisher

```text
pertinent: NO_DIRECT_CONTRACT_CHANGE
action: preserve Site-derived projection-only boundary
```

### StegVerse-002/stegguardian-wiki

```text
pertinent: NO_DIRECT_CONTRACT_CHANGE
action: preserve downstream interpretation-only boundary
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
experiment-manifest remediation: EXACT_HEAD_VALIDATION_PASS / PR_166_DRAFT_PENDING_MERGE
SDK 1.3.0 source candidate: EXACT_HEAD_SOURCE_VALIDATED_MERGEABLE_DRAFT_PR_165
first proven anonymous-install blocker: stegverse-stegcore==0.3.0 NOT PUBLISHED
ELAN Test 1 source evidence: EVENTS_1_2_OBSERVED / EVENT_3_PENDING
Site completion predicate: FALSE / MACHINE_OWNED
admissibility completion predicate: FALSE / WORKER_OWNED
manual user work: NONE
```
