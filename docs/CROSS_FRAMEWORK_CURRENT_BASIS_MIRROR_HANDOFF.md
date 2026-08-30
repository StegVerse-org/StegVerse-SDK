# Cross-Framework Current-Basis Mirror Handoff

Updated: 2026-08-29

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
pull request: #94
branch: test/cross-framework-current-basis-manifest-draft-20260828
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


## Authentic StegVerse execution harness — prepared 2026-08-29

Issue: #106.

Installed source:
```text
scripts/run_cross_framework_current_basis_v04.py
tests/test_cross_framework_current_basis_execution.py
```

The harness consumes only the exact frozen v0.4 manifest bytes, verifies SHA-256 `07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f`, calls canonical merged `stegcore.current_basis` for native derivation/evaluation, then passes the derived canonical request into the existing sovereign validation runtime. It does not place architecture-native currentness fields into the frozen common manifest and does not consume counterpart results before completion.

After the canonical run returns Master Records custody, the harness records S1 observation, then creates the S0->S1 post-observation evidence receipt, then invokes canonical replay and reconstruction. Only if all gates are observed does it write `RUN_COMPLETE.json` with the flags required by the external result packager.

Expected result directory:
`evidence/evaluator/cross-framework-current-basis-v0.4-result/`

Source validation of this harness does not equal authentic sovereign execution. The execution goal remains open until that directory is produced by the canonical sovereign path and the retained custody/replay/reconstruction evidence verifies.


## Superseding execution/publication state — 2026-08-30

This section supersedes stale earlier completion-gate text that still described freeze/source validation as pending.

```text
exact v0.4 manifest: FROZEN
source validation: PASS
StegVerse owner freeze attestation: FROZEN
common execution window: OPEN
SDK authentic harness: MERGED / VALIDATED
StegCore native derivation: MERGED / VALIDATED
resident request/consumer: MERGED / VALIDATED
resident refresh consumer materialization: MERGED / VALIDATED
canonical local source-root discovery: MERGED / VALIDATED
exact experiment-critical resident source-blob guard: MERGED / VALIDATED
Site frozen v0.4 projection: MERGED / PUBLICLY OBSERVED
authentic resident request consumption: NOT OBSERVED
StegVerse S1: NOT OBSERVED
post-observation S0->S1 receipt: NOT OBSERVED
Master Records custody/replay/reconstruction for the authentic run: NOT OBSERVED
RUN_COMPLETE.json: NOT OBSERVED
result packet publication: NOT YET ELIGIBLE
```

Resident/runtime source evidence:
- `StegVerse-Labs/.github#500` / merge `0c45dfc7e413c5da8fcc89f33637e1783a6eb558`
- `StegVerse-Labs/.github#511` / merge `6d03c0d3d41f45ac91b740c091f16b7ddf9097bf`
- `StegVerse-Labs/.github#518` / merge `c379903b25ebf369ba3aaf7b295d6a725e9d6ec8`
- Site public verification run `33294523117`, attempt 2, job `99211964506`: PASS.

The remaining experiment transition is therefore authentic sovereign execution, not further specification freeze or Site publication work.

## Result publication hardening — 2026-08-30

Issue #108 hardens the non-authorizing result distribution gate. A successful result packet must now include the complete expected evidence set:

```text
STEGVERSE_RESULT.json
S1_OBSERVATION.json
S0_S1_TRANSITION_RECEIPT.json
REPLAY.json
RECONSTRUCTION.json
RUN_COMPLETE.json
```

In addition to the original completion flags and frozen manifest identity, publication now requires:

```text
counterpart_result_consumed_before_completion=false
external_side_effect=false
github_actions_runtime_authority=false
manifest_receipt_id present
S1 observation bound to frozen v0.4
S1 counterpart isolation preserved
transition receipt bound to frozen v0.4
transition receipt timing=POST_OBSERVATION
RUN_COMPLETE transition_receipt_hash matches retained receipt
replay operation_transition_custody_status=RECORDED
reconstruction operation_transition_custody_status=RECORDED
```

This means the desired successful GitHub Actions artifact link cannot be produced from a partial, architecture-cross-contaminated, pre-observation, or externally consequential packet. GitHub Actions remains verification/distribution only.


## PR retirement / execution-only continuation — 2026-08-30

Historical working PRs have been retired after their canonical content was reconciled onto current main:

```text
PR #94: CLOSED / SUPERSEDED_BY_EXACT_V0_4_FROZEN_MAIN
PR #99: CLOSED / SUPERSEDED_BY_CURRENT_MAIN_EXECUTION_HARNESS
issue #106: OPEN / AUTHENTIC_EXECUTION_EVIDENCE_ONLY
manifest blob: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
SDK execution harness merge: 2b1ae25662aaade5033e6bacac98d9ba5233fdee
StegCore native derivation merge: e80e927616750a88ad7fc88f4017fc496474f1e4
known scoped scaffolding/stubs: 0
```

Closing #94/#99 is source-branch housekeeping only. It does not represent execution.

The remaining #106 completion evidence is exactly:

```text
authentic independent StegVerse execution
-> S1 observed
-> post-observation S0->S1 receipt bound
-> Master Records custody
-> replay custody
-> reconstruction custody
-> RUN_COMPLETE.json
-> fail-closed result packet verification/publication
```

Until those artifacts exist, result publication remains ineligible and no successful external-result Action may be represented as available.
