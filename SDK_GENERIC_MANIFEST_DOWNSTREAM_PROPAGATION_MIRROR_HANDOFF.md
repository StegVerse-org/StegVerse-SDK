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
```

Current executable processor:

```text
processing.capability: governance
processing.route_id: stegverse.route.canonical-governed.v1
processor-specific request: extensions.stegverse_governance_request
```

## ELAN Event-3 experiment-integrity remediation — 2026-09-10

The ELAN three-event protocol has been reconciled against the evaluator-defined-manifest/non-interference contract.

The corrected experimental model is:

```text
S0 -> Event 1 -> S1 -> Event 2 -> S2 -> Event 3 (no new human input for the preregistered interval) -> observe resulting state/behavior
```

Events 1 and 2 are controlled state-establishment conditions required to reach the state under test. Event 3 is the evaluated condition. The fixed lead-in is therefore not itself prohibited evaluator bias merely because StegVerse specified it; substituting an unrelated independently chosen lead-in could fail to establish S2 and therefore fail to test the intended condition.

The non-interference boundary applies to expected source-framework semantics and outcomes, not to legitimate controlled preconditions. The SDK must not pre-author or inject expected ELAN interpretation, expected internal state, expected Event-3 response/withholding, expected agreement/disagreement with governance, or expected comparative disposition into the authentic experiment path.

The prior ELAN evaluator declaration contained an explicit expected comparative observation. On branch `sdk-evaluator-bias-remediation`, that expectation has been removed and the declaration is now outcome-neutral. `docs/ELAN_TEST1_RUNBOOK.md` now distinguishes state establishment from the evaluated condition, requires continuity evidence into Event 3, and states that externally produced source-native evidence must be preserved before StegVerse interpretation. Root `README.md` now documents the reusable controlled-state experiment-integrity rule.

External evidence received before this remediation:

```text
artifact: 1.ELAN_TEST_TRACE_EN_09.09.2026.pdf
artifact confidentiality marking: Royal ELAN License 2026 / Confidential
Event 1: observed in packet
Event 2: observed in packet
Event 3: packet explicitly states not yet submitted
source-owner description: ELAN responses in native state / unmodified
public-repository publication of confidential packet: prohibited absent source-owner permission
```

The packet is not committed to this repository. Its observable content establishes only Events 1 and 2; internal ELAN state must not be inferred from linguistic output. The packet states Event 3 will occur in a separate session. Because Event 3 tests the condition following S2, a separate session is acceptable only if source-native continuity/resumption from S2 is evidenced; otherwise the execution must be classified as reset/reconstructed/unverified rather than silently treated as continuous.

Current remediation branch evidence:

```text
branch: sdk-evaluator-bias-remediation
outcome-neutral evaluator declaration commit: e2bc9f3394aa056352f10d32c9503cac2a9481cd
Event-3 runbook correction commit: 642ccfd7dc6f784f9e60e0c0b93081485d997f23
README experiment-integrity correction commit: 0c9f7f8a4289cd9ea48e95885ffca59ffa05931b
PR: #166 DRAFT
validation: PR head before invariant repair had 4 PASS / 1 FAIL; failure was only missing canonical handoff state token and is repaired in the current head
merge claim: NONE
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

The SDK preserves source-native data, evaluator preregistration outside the governance decision request, declared processor/route binding, caller-selected return projection, fail-closed unsupported routing, canonical `manifest_receipt_id`, replay, and reconstruction.

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

The prior candidate head had become 7 commits behind current `main`, producing a GitHub `mergeable=false` report even though the candidate and main-side changed paths did not overlap. This was repaired without rewriting candidate semantics by creating merge commit `b53fb8c26688c8ea02ac336c5b876b3e6aa189cb` with the validated candidate as first parent and current main `c7666cf37ba8561e85298bc88d50d152aa565965` as second parent. The merge tree uses current-main state plus the exact ten candidate blobs.

Post-repair comparison:

```text
base: main@c7666cf37ba8561e85298bc88d50d152aa565965
head: b53fb8c26688c8ea02ac336c5b876b3e6aa189cb
status: ahead
ahead_by: 16
behind_by: 0
merge_base: c7666cf37ba8561e85298bc88d50d152aa565965
PR mergeable: true
changed files: exactly 10 intended candidate files
```

Candidate control files remain:

```text
pyproject.toml
VERSION.json
RELEASE_NOTES_1.3.0.md
scripts/check_component_version.py
docs/SDK_1_3_0_SUCCESSOR_RELEASE_MIRROR_HANDOFF.md
.github/workflows/component-version-validation.yml
```

README maintenance remains incorporated and current.

## Exact-head validation after merge-base repair

Exact PR #165 head `b53fb8c26688c8ea02ac336c5b876b3e6aa189cb`:

```text
SDK Component Version Validation 34355771475 PASS
SDK Package Artifact Validation 34355771348 PASS
Release Dependency Alignment 34355771409 PASS
External Framework Public Submission 34355771364 PASS
Evaluator Manifest Source Validation 34355771441 PASS
Evaluator Contract Console Validation 34355771315 PASS
SDK Production Manifold Governance Validation 34355771382 PASS
Portable Package Source Validation 34355771396 PASS
Portable Release Index 34355771447 PASS
Manifest Builder Source Validation 34355771439 PASS
MCP Source Validation 34355771329 PASS
SDK Output-Boundary Proof Validation 34355771324 PASS
Connect my LLM Source Validation 34355771408 PASS
Communication Edge SDK Demo Validation 34355771365 PASS
Anonymous Governed Runtime Install 34355771357 FAIL_CLOSED_EXPECTED
```

Exact anonymous-install failure remains:

```text
materialize exact SDK source: PASS
pip install -e .[governed-test]: FAIL
pip error: No matching distribution found for stegverse-stegcore==0.3.0
package identity verification: SKIPPED
ELAN Test 1 execution: SKIPPED
complete governed result verification: SKIPPED
```

This proves the merge-base repair introduced no observed SDK source regression. The first current public-distribution blocker remains authentic publication of `stegverse-stegcore 0.3.0`. Private repository visibility is not the observed failure mode. Do not weaken the anonymous gate or infer Master Records publication status merely because pip stops at the first missing package.

## Release boundary

PR #165 remains DRAFT despite being mergeable and source-valid. Source validation and mergeability are not release publication.

Actual `v1.3.0` freeze/publication requires:

```text
exact candidate freeze reconciliation
TVC successor policy updated to the new SDK coordinate
current TV/TVC GRANTED release authorization
required SKAP double-interlock resident evidence
immutable GitHub tag/release
Trusted Publisher PyPI provenance
anonymous governed-runtime install PASS
ELAN Test 1 custody/replay/reconstruction PASS
```

The live TVC release-credential task remains `BLOCKED_DEPENDENCY` / `REQUESTED_NOT_GRANTED`; no tag or release is created now.

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
  - validate and merge the evaluator-bias remediation after PR/check evidence
  - keep PR #165 draft while public package/release gate is unsatisfied
  - after authentic public distributions exist, rerun Anonymous Governed Runtime Install and ELAN E2E
  - require Event-3 continuity evidence before treating separate-session silence as the intended S2 condition
  - freeze exact 1.3.0 coordinate only through canonical release reconciliation

StegVerse-Labs/StegCore:
  - authentic immutable/public publication of stegverse-stegcore 0.3.0 under canonical release gate

master-records/orchestration:
  - authentic immutable/public publication of stegverse-master-records 0.2.0 under canonical release gate

StegVerse-Labs/Site:
  - Site-owned admitted SDK preview/backend contract propagation after repository orchestration admits it

StegVerse-Labs/admissibility-wiki:
  - Worker D-owned processor-generic interoperability doctrine propagation

GCAT-BCAT-Engine/Publisher: none now
StegVerse-002/stegguardian-wiki: none now
```

## Current status

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
ELAN evaluator-bias remediation: SOURCE_CHANGES_ON_BRANCH / REVALIDATION_PENDING
SDK 1.3.0 source candidate: EXACT_HEAD_SOURCE_VALIDATED_MERGEABLE_DRAFT_PR_165
merge-base regression: RESOLVED
SDK public distribution rewrite: INCORPORATED_IN_PR_165
SDK README correction: INCORPORATED_IN_PR_165
first proven anonymous-install blocker: stegverse-stegcore==0.3.0 NOT PUBLISHED
Site completion predicate: FALSE / MACHINE_OWNED
admissibility completion predicate: FALSE / WORKER_OWNED
manual user work: NONE
```
