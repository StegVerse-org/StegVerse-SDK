# Cross-Framework Current-Basis Mirror Handoff

Updated: 2026-08-29

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
pull request: #94
branch: test/cross-framework-current-basis-manifest-draft-20260828
manifest: inspection/examples/cross-framework-current-basis-request.draft.json
vector schema: stegverse.cross-framework-current-basis-vector.v0.3
state: DRAFT_PRE_FREEZE / SOURCE_VALIDATION_PENDING
```

This scoped handoff is the authoritative continuation record for the cross-framework current-basis comparison lane. Live repository state and exact artifact hashes supersede stale conversation or earlier handoff claims for this lane.

## Correct temporal receipt model

The test must not require a transition receipt before the transition has been observed.

```text
S0 declaration
-> freeze exact S0 + transition definition + S1 observation definition + comparison boundary
-> execute architecture A and architecture B independently
-> observe each S1
-> establish whether each observed S1 transitioned from the exact frozen S0
-> only then bind the corresponding S0->S1 transition receipt
-> retain custody/replay/reconstruction evidence
-> compare result semantics, not internal implementation details
```

An S0 state can be declared and frozen before execution. It does not become receipt-bearing for the S0->S1 transition until S1 is observed and the relationship is established. A transition receipt is therefore post-observation evidence, never a pre-execution input for the transition it proves.

Independently pre-existing evidence may still be frozen as an input when the proposition explicitly depends on that prior evidence. That is different from pre-minting the transition receipt under test.

## Correction applied

Previous v0.2 manifest identity:

```text
revision: c9b8935309e69d3a6f70e4ad4ef5dd55fb8a9aac
blob: 2dd0468779975d18ad53dfe400e1d2fcf83650c3
sha256: a7d8f6b5d09fc894f92634e5ee31e82b3297fb453c315160b04aeb28f73b515d
external review: APPROVED_FOR_HASH_FREEZE
```

That approval is now stale because v0.3 materially corrects receipt timing semantics.

Current v0.3 manifest identity:

```text
source correction commit: 910442aa274fdcc8c720b6ae46367295e5c2a895
blob: 79f1e26a1c34beb0d4d43342d14ea99c5d600bc0
sha256: ad863e73112c4bd7295cebaa456471335a68f0b7733b80aff6ef167b15e881f4
freeze state: DRAFT_PRE_FREEZE
external exact-revision approval: PENDING_REREVIEW
```

Machine-readable correction evidence:

```text
evidence/evaluator/cross-framework-current-basis-freeze-gate-2026-08-29.json
```

The prior `bind_actual_s0_valid_state_receipt_or_equivalent` blocker is explicitly superseded and invalid.

## Installed regression guard

```text
tests/test_cross_framework_current_basis_manifest.py
.github/workflows/evaluator-manifest-source-validation.yml
```

The regression test requires:

- S0 is not transition-receipt-bearing before S1 observation;
- no `prior_receipt_ref` is present in S0;
- the runtime continuity input does not claim a verified previous transition receipt;
- the S0->S1 receipt is explicitly post-observation evidence;
- the pre-freeze requirements prohibit requiring that receipt before S1 exists;
- the post-observation requirements require binding the receipt only after observation;
- independently pre-existing known-invalidation evidence remains distinguishable from the control transition's own later receipt.

## Current completion gates

```text
semantic correction: IMPLEMENTED
machine-readable correction evidence: IMPLEMENTED
regression test: IMPLEMENTED
workflow integration: IMPLEMENTED
source validation: PENDING_OBSERVABLE_RESULT
external exact-v0.3 rereview: PENDING
freeze: NO
independent architecture execution: NO
transition receipts: NO / correctly post-observation only
custody/replay/reconstruction: NO
result comparison: NO
```

## Next actions

1. Observe the evaluator-manifest source-validation result for the current v0.3 branch head.
2. If source validation passes, present the exact v0.3 manifest/hash for external exact-revision rereview.
3. If approved unchanged, record StegVerse owner freeze attestation against the same exact manifest hash.
4. Transition only that exact artifact to FROZEN.
5. Execute both architectures independently against the same frozen definition.
6. Observe each S1 and only then mint/bind its S0->S1 transition receipt.
7. Preserve ordinary Master Records custody/replay/reconstruction evidence and compare semantic results.

## Downstream propagation

After v0.3 passes source validation and exact external rereview, re-check and update only pertinent projections/contracts in:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-002/stegguardian-wiki
```

Do not propagate the stale v0.2 pre-observation receipt requirement.

## Authority boundary

```text
GitHub source validation != runtime authority
manifest declaration != execution authority
freeze != execution
transition receipt != pre-execution authority
post-observation receipt != retroactive permission
Master Records custody != admissibility
TV/TVC remains credential authority
```
