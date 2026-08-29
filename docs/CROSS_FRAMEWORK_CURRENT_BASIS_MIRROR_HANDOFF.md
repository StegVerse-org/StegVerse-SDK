# Cross-Framework Current-Basis Mirror Handoff

Updated: 2026-08-29

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
pull request: #94
branch: test/cross-framework-current-basis-manifest-draft-20260828
manifest: inspection/examples/cross-framework-current-basis-request.draft.json
vector schema: stegverse.cross-framework-current-basis-vector.v0.4
state: DRAFT_PRE_FREEZE / EXACT-REVISION REREVIEW REQUIRED
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

S0 may be declared and frozen before execution. It does not become receipt-bearing for the S0->S1 transition until S1 is observed and the relationship is established. Independently pre-existing evidence may be frozen as an input when a proposition explicitly depends on that evidence; that is separate from the post-observation transition receipt.

## v0.4 execution-input correction

External pre-freeze review of v0.3 accepted the temporal receipt correction but identified a remaining ambiguity: architecture-native fields such as `actor_authority_current`, `policy_current`, `delegation_current`, `evidence_current`, and `validity_window_open` could be read as pre-establishing the present-standing/current-basis conclusion that each architecture is supposed to determine independently.

v0.4 removes those native currentness booleans from the common frozen artifact. The common input now freezes neutral S1 observed-input facts only. Each architecture must independently derive any native currentness/authority/continuity fields required by its own evaluation model. Those derivations are architecture-specific intermediate evidence, not common pre-established conclusions.

```text
v0.4 manifest correction commit: 5a21fc6bdf4a94cfd6c4a4f369a1ba8b86721909
v0.4 manifest Git blob SHA-1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
v0.4 manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
v0.4 regression-test commit: 2c389a042d0eebd87abdd47a0b311b32ba1ac97b
freeze state: DRAFT_PRE_FREEZE
external exact-v0.4 approval: PENDING
```

## Regression guards

```text
tests/test_cross_framework_current_basis_manifest.py
.github/workflows/evaluator-manifest-source-validation.yml
```

The v0.4 regression test now requires:

- no `steggate_request` or equivalent native currentness booleans in the common frozen comparison input;
- no `actor_authority_current`, `policy_current`, `delegation_current`, `evidence_current`, or `validity_window_open` strings in the common input;
- S0 remains non-receipt-bearing for S0->S1 before S1 observation;
- transition receipt remains post-observation evidence;
- `current_basis_status` remains `TO_BE_DETERMINED_BY_EACH_ARCHITECTURE`;
- architecture-native currentness fields are independently derived, not common conclusions;
- known-invalidation evidence remains distinct from the transition receipt.

## Review history

```text
v0.2: external approval received; superseded by temporal receipt correction
v0.3: temporal receipt correction externally accepted; hash/freeze approval held on execution-input ambiguity
v0.4: execution-input ambiguity corrected; exact-revision rereview required
```

No prior approval is inherited across the material v0.4 manifest change.

## Current completion gates

```text
v0.4 semantic correction: IMPLEMENTED
v0.4 exact JSON artifact: IMPLEMENTED
v0.4 deterministic review PDF: IMPLEMENTED / 5 ACTUAL PAGES
v0.4 regression guard: IMPLEMENTED
source validation: PENDING OBSERVABLE RESULT
external exact-v0.4 review: PENDING
freeze: NO
independent architecture execution: NO
transition receipts: NO / correctly post-observation only
custody/replay/reconstruction: NO
result comparison: NO
```

## Next actions

1. Observe source validation for the v0.4 branch head.
2. Send the exact v0.4 review artifact identified by SHA-256 `07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f` for external exact-revision review.
3. If approved unchanged, record the StegVerse owner freeze attestation against the same exact JSON identity.
4. Transition only that exact artifact to FROZEN.
5. Open the agreed execution window and execute both architectures independently.
6. Observe S1 independently and only then mint/bind each S0->S1 transition receipt.
7. Preserve Master Records custody/replay/reconstruction evidence and compare semantic results.

## Downstream propagation

After v0.4 passes source validation and exact external review, re-check only pertinent projections/contracts in:

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
