# Labs patches prepared by Claude for StegVerse-Labs/.github

Claude sessions cannot push to `StegVerse-Labs/.github`, which is a dot-named repository. This branch carries patches for an LLM with Labs write access to apply with `git am`. This branch is never merged. authority_effect NONE.

| Patch | Applies on | Purpose | Coordination |
|---|---|---|---|
| 0002 | Labs main | Synthetic assessment demo docs (#3370) | KV checkpoints |
| 0003 | Labs main `62391b0` | Fixes the InTr `sdk-manifest-ingress` binding owner: `StegVerse-Labs/StegVerse-SDK` becomes `StegVerse-org/StegVerse-SDK` | StegVerse-org/StegVerse-SDK#566 |
| 0004 | Labs main `62391b0` (after #3372) | Collision evaluator guards every owner-held checkout state | StegVerse-org/StegVerse-SDK#556 |
| 0006 | Labs main `62391b0` | Ingress refuses a crossing whose payload does not recompute from the delivered manifest (`CROSSING_PAYLOAD_NOT_BOUND_TO_THE_DELIVERED_MANIFEST`). Existing test stubs now compute real digests; no assertion changed | StegVerse-org/StegVerse-SDK#556 |
| 0005 | PR #3375 head `45a670b` | Protocol v1 negatives run through the real `receive()`; expectations are generated from real output; spec gaps are recorded honestly; adds the non-gating n9 case | StegVerse-org/StegVerse-SDK#556 |

Verify with `sha256sum -c SHA256SUMS` before applying.

## Stacked series on Labs main `bbd84af` (recommended)

`series-on-bbd84af/` contains 0003, 0004, 0006 and 0005, rebased in that order onto Labs main `bbd84af`, which already includes #3372, #3375 and #3304. `0005` targets the merged #3375 code. Apply the whole series with `git am series-on-bbd84af/*.patch`. Regenerating `.stegverse/test-sets.json` after the series produces no diff.

## CURRENT: stacked series on Labs main `e0d2970` (supersedes earlier series and single patches)

`0003` is no longer needed: StegVerse-Labs/.github#3384 merged the binding-owner fix (`c356fd81`), and SDK #574 pins it. Apply in order with `git am series-on-e0d2970/*.patch`:

1. Collision evaluator: every owner-held checkout state guards.
2. Ingress binds the crossing to the delivered manifest's exact payload.
3. Protocol v1 negatives run through the real `receive()`; expectations are generated; adds n9 (non-gating).
4. Conformance fixtures: corrected the replay (`REDELIVERY_REPROCESSED_BEFORE_DEDUPLICATION`), sender-identity (`SUBMITTER_KV_SKAP_VERIFICATION_NOT_BOUND_AT_INGRESS`) and stale-head spec_gaps, and their owners. No gap waits on device attestation, which the invariants prohibit.
5. Ingress refuses a declared authority effect other than NONE before the crossing (`AUTHORITY_EFFECT_NOT_WARRANTED_AT_INGRESS`). No real manifest declares a non-NONE effect: 116 calls declare none and 20 declare NONE.

Design input for the remaining gaps: `design/INGRESS_GAP_OPTIONS_3369.md`.

Apply log (verified, not applied to Labs): applies cleanly with `git am` on Labs main `bbd84af`, `e0d2970`, `3d4c7c1` and `6b13c3a` (2026-10-29 13:05Z; touched test modules on `6b13c3a`: 136 passed, 90 subtests). Combined mbox sha256 `ce21e58b64d907666da3df53038b68addca5d525cfeb7c624b6b3e4ac40e7859`. Handoff for a Labs-write LLM: KV doc `1yMF4ldq6OQRBJtv5w5M2kwmW2CS1f0XP6ypxIU5Dahs`.
