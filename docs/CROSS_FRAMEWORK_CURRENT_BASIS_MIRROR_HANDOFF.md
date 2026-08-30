# Cross-Framework Current-Basis Mirror Handoff

Updated: 2026-08-29

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
freeze/review pull request: #94
execution integration branch: feat/cross-framework-v04-execution-20260829
frozen-source branch: test/cross-framework-current-basis-manifest-draft-20260828
manifest: inspection/examples/cross-framework-current-basis-request.draft.json
vector schema: stegverse.cross-framework-current-basis-vector.v0.4
state: EXACT_V0_4_FROZEN / COMMON_EXECUTION_WINDOW_OPEN
```

This file is the authoritative continuation record for the cross-framework current-basis comparison lane. Live repository state and exact artifact hashes supersede prior conversation claims and stale v0.2/v0.3 review state.

## Governing temporal receipt model

```text
S0 declaration
-> freeze exact S0 + transition definition + neutral S1 observed inputs + derivation rule + comparison boundary
-> execute architecture A and architecture B independently
-> each architecture derives its own native evaluation representation
-> observe each S1 and current-basis determination
-> establish whether each observed S1 transitioned from the exact frozen S0
-> only then bind the corresponding S0->S1 transition receipt
-> retain custody/replay/reconstruction evidence
-> compare result semantics, not internals
```

S0 may be declared before execution. It does not become receipt-bearing for the S0->S1 transition until S1 is observed and the relationship is established. Independently pre-existing evidence may be frozen as an input when a proposition explicitly depends on that evidence; that is separate from the post-observation transition receipt.

## Exact v0.4 identity

```text
manifest correction commit: 5a21fc6bdf4a94cfd6c4a4f369a1ba8b86721909
manifest Git blob SHA-1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
regression-test commit: 2c389a042d0eebd87abdd47a0b311b32ba1ac97b
external exact-v0.4 approval: APPROVED_FOR_HASH_FREEZE
approval scope: EXACT_UNCHANGED_JSON_IDENTITY_ONLY
freeze state: NOT YET FROZEN
```

The exact JSON itself MUST NOT be modified after this approval. Its embedded `DRAFT_PRE_FREEZE` label is part of the approved byte identity and therefore remains a snapshot label. The actual freeze transition, when eligible, must be recorded in a separate attestation/evidence record bound to the exact approved hash rather than by mutating the approved JSON.

## v0.4 execution-input correction

External pre-freeze review of v0.3 accepted the temporal receipt correction but identified a remaining ambiguity: architecture-native fields such as `actor_authority_current`, `policy_current`, `delegation_current`, `evidence_current`, and `validity_window_open` could be read as pre-establishing the present-standing/current-basis conclusion that each architecture is supposed to determine independently.

v0.4 removes those native currentness booleans from the common frozen artifact. The common input freezes neutral S1 observed-input facts only. Each architecture independently derives any native currentness/authority/continuity fields required by its own evaluation model. Those derivations are architecture-specific intermediate evidence, not common pre-established conclusions.

## External approval received

Richard Colimon reviewed the exact v0.4 identity through the external review channel and stated that the v0.4 correction resolves the remaining pre-freeze concern. He also confirmed that:

- the common artifact now supplies neutral S1 observed-input facts without pre-establishing architecture-native currentness, authority, delegation, evidence-currentness, validity-window, continuity, or present-standing conclusions;
- each architecture must derive those independently from the same frozen facts before determining current basis;
- material change remains distinct from established invalidation;
- the S0->S1 transition receipt remains post-observation evidence;
- neither architecture may consume the other's result before its own run completes.

He explicitly approved the exact identity:

```text
SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
Git blob SHA-1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
APPROVED FOR HASH/FREEZE
```

Approval applies only to that exact unchanged JSON identity.

Machine-readable approval/freeze-gate evidence:

```text
evidence/evaluator/cross-framework-current-basis-freeze-gate-2026-08-29.json
```

## Regression guards

```text
tests/test_cross_framework_current_basis_manifest.py
.github/workflows/evaluator-manifest-source-validation.yml
```

The v0.4 regression test requires:

- no `steggate_request` or equivalent native currentness booleans in the common comparison input;
- no `actor_authority_current`, `policy_current`, `delegation_current`, `evidence_current`, or `validity_window_open` strings in the common input;
- S0 remains non-receipt-bearing for S0->S1 before S1 observation;
- transition receipt remains post-observation evidence;
- `current_basis_status` remains `TO_BE_DETERMINED_BY_EACH_ARCHITECTURE`;
- architecture-native currentness fields are independently derived, not common conclusions;
- known-invalidation evidence remains distinct from the transition receipt.

## Current completion gates

```text
v0.4 semantic correction: IMPLEMENTED
v0.4 exact JSON artifact: IMPLEMENTED
v0.4 deterministic review PDF: IMPLEMENTED / 5 ACTUAL PAGES
v0.4 regression guard: IMPLEMENTED
external exact-v0.4 review: APPROVED_FOR_HASH_FREEZE
source validation: PENDING OBSERVABLE RESULT
StegVerse owner freeze attestation: PENDING AFTER SOURCE VALIDATION
freeze: NO
independent architecture execution: NO
transition receipts: NO / correctly post-observation only
custody/replay/reconstruction: NO
result comparison: NO
```

No GitHub Actions workflow run is observable for the current v0.4 branch head, and no Actions pass is claimed. Instead, the exact approved manifest bytes were deterministically validated against the installed v0.4 regression invariants and identity checks; that source-validation evidence is recorded separately.

## Next actions

1. Obtain an observable source-validation result for the exact v0.4 manifest identity.
2. If source validation passes, record StegVerse owner freeze attestation against SHA-256 `07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f` without modifying the approved JSON.
3. Mark that exact identity FROZEN in separate evidence/attestation.
4. Open the agreed execution window.
5. Execute both architectures independently against the same exact frozen identity.
6. Observe S1 independently and only then mint/bind each S0->S1 transition receipt.
7. Preserve Master Records custody/replay/reconstruction evidence and compare semantic results.

## Downstream propagation

After v0.4 source validation passes and the exact identity is frozen, re-check only pertinent projections/contracts in:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-002/stegguardian-wiki
```

Do not propagate stale v0.2/v0.3 pre-observation or pre-established-currentness semantics.

## Authority boundary

```text
GitHub source validation != runtime authority
manifest declaration != execution authority
freeze != execution
native derivation != common input conclusion
transition receipt != pre-execution authority
post-observation receipt != retroactive permission
Master Records custody != admissibility
TV/TVC remains credential authority
```
\n\n## Freeze / execution evidence\n\n```text\nevidence/evaluator/cross-framework-current-basis-v0.4-source-validation-2026-08-29.json\nevidence/evaluator/cross-framework-current-basis-v0.4-owner-freeze-attestation-2026-08-29.json\nevidence/evaluator/cross-framework-current-basis-v0.4-execution-window-2026-08-29.json\n```\n

## S0 semantics correction and live execution state — 2026-08-29

This section supersedes any earlier statement in this handoff that requires a historical or pre-existing S0 receipt for this test lane.

For this testing environment, absent explicitly supplied prior-state data, S0 is the declared initial state from which evaluation begins. The frozen test definition does not require a prior receipt to justify S0. The S0->S1 transition receipt is post-observation evidence and is bound only after S1 is observed and the transition relationship is established. If a future test explicitly supplies prior-state data, that prior state/transition/receipt becomes part of that test's evaluation context.

Current exact lane state:

```text
vector schema: stegverse.cross-framework-current-basis-vector.v0.4
manifest Git blob SHA-1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
source validation: PASS
authoritative source-validation evidence: evidence/evaluator/cross-framework-current-basis-v0.4-source-validation-2026-08-29.json
StegVerse owner freeze attestation: FROZEN
freeze evidence: evidence/evaluator/cross-framework-current-basis-v0.4-owner-freeze-attestation-2026-08-29.json
common execution window: OPEN
execution-window evidence: evidence/evaluator/cross-framework-current-basis-v0.4-execution-window-2026-08-29.json
execution permitted by specification freeze: true
runtime authority effect: NONE
```

The exact approved JSON must remain unchanged; its embedded `DRAFT_PRE_FREEZE` value is snapshot content within the approved byte identity, while the effective freeze is carried by the separate hash-bound attestation.

The next legitimate machine step is independent StegVerse execution against that exact frozen identity, followed by S1 observation, post-observation S0->S1 receipt binding, custody/replay/reconstruction, and only then cross-framework semantic comparison. Neither architecture may consume the other's result before its own run completes.


## External result packet publication — prepared 2026-08-29

The completed authentic StegVerse run is intended to be shareable with the external evaluator as both a self-contained artifact packet and a successful GitHub Actions run whose attached artifacts reproduce the same packet.

Prepared surfaces:

```text
scripts/package_cross_framework_current_basis_results.py
.github/workflows/cross-framework-result-artifact-publication.yml
result input directory: evidence/evaluator/cross-framework-current-basis-v0.4-result/
completion sentinel: evidence/evaluator/cross-framework-current-basis-v0.4-result/RUN_COMPLETE.json
uploaded artifact name: cross-framework-current-basis-v0.4-results
retention: 90 days
```

Publication is fail-closed. The packet cannot be published as successful unless `RUN_COMPLETE.json` binds the exact frozen v0.4 SHA-256 and Git blob identity and asserts completed independent execution, S1 observation, post-observation transition-receipt binding, custody, replay, and reconstruction. The packager independently recomputes the frozen manifest SHA-256 and inventories every attached file with its own SHA-256.

GitHub Actions is distribution/verification only for this surface. It does not execute governance, mint the transition receipt, create runtime authority, or replace Master Records custody. The intended external handoff after authentic completion is: resultant packet + successful Actions-run link + attached `cross-framework-current-basis-v0.4-results` artifact.


## Execution integration continuation — 2026-08-29

The frozen v0.4 source identity remains unchanged and continues to be rooted in PR #94. A fresh execution-integration branch was created from current SDK main because the original freeze branch predates the merged evaluator Interlock/InTr ingress and cannot be cleanly synchronized without conflicts.

```text
execution branch: feat/cross-framework-v04-execution-20260829
current main parent: fdf15f110fd407c8c63943ab5bb1e2c43d032237
frozen manifest bytes: unchanged
frozen manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
frozen manifest Git blob: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
```

New execution surfaces on this branch:

```text
StegCore issue #161 / PR #162:
  src/stegcore/current_basis.py
  tests/test_current_basis.py

SDK:
  stegverse/current_basis.py
  stegverse/evaluator_review_intr.py -> current-basis surface
  stegverse/sovereign_validation_runtime.py -> derived native request support
  scripts/run_cross_framework_current_basis_v04.py
  tests/test_current_basis_sdk.py
  tests/test_cross_framework_current_basis_run.py
  tests/test_evaluator_review_intr.py
  pyproject.toml current-basis-test exact dependency set
```

The exact execution harness:
1. re-hashes the frozen manifest bytes and Git blob identity;
2. loads the unchanged neutral v0.4 vector;
3. asks canonical StegCore to derive its native AdmissibilityRequest;
4. sends that derived native request through the existing canonical SDK sovereign route while retaining the unchanged frozen manifest as the submitted comparison source;
5. requires canonical StegCore chain verification, transaction-identity continuity, and Master Records custody;
6. independently verifies the manifest/request/result binding tuple;
7. only after S1 observation creates the S0->S1 evidence receipt bound to the exact governed result and Master Records locator;
8. records reconstruction and replay as separately custodied operations and prohibits replay consequence re-execution;
9. writes RUN_COMPLETE.json only after all required evidence gates pass;
10. allows the already-prepared GitHub Actions publication workflow to verify/package the completed evidence without becoming runtime authority.

Current state:

```text
StegCore native derivation source: IMPLEMENTED ON PR #162 / VALIDATION PENDING
SDK thin client: IMPLEMENTED ON EXECUTION BRANCH
SDK InTr current-basis routing: IMPLEMENTED ON EXECUTION BRANCH
exact sovereign run harness: IMPLEMENTED ON EXECUTION BRANCH
source validation workflow integration: IMPLEMENTED ON EXECUTION BRANCH
authentic independent StegVerse run: NOT YET OBSERVED
RUN_COMPLETE.json: NOT PRESENT
artifact publication action: NOT YET ELIGIBLE
```
