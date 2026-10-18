# SDK #484 T6 — Universal Entry Validator Mirror Handoff

Status (2026-10-17): MERGED + CI_VALIDATED source (#506 `d4d0f2d`, #516 `579998a`); governed migration T6-001 = StegCore DENY; T6-002 not yet filed. Canonical owner `SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001`, COSV `60200000013002`. Sections below 2026-10-17 are chronology; the reconciliation at the end supersedes them.

## Scope
This draft PR modifies only the SDK universal-entry-envelope validator, not the StegCore recreation gate or AI Registry validators. The existing universal entry schema remains the sole source of field constraints. Schema validation uses Draft202012Validator explicitly; a schema violation yields deterministic FAIL_CLOSED reporting without bypassing invariant validation. Valid packets retain PASS behavior.

## Validation
Regression tests cover missing routing, invalid routing type, and the valid sample packet. Run exact-head CI including the full test-suite ratchet. No baseline weakening, new dependencies, external receiver, or new governance authority is permitted. T1 Registry reconciliation is required before any governed transition or merge.

## Coordination
Independent from T2 PR #505's pinned Organization boundary. T5 TV/TVC provenance must authenticate the final SDK source head. Interlock/InTr and Organization ledger remain runtime authority; these source tests do not establish ALLOW or Organization Master Records evidence.

## Verified exact-head CI (2026-10-13)
SDK PR #506 head ec9a638f733d7a65690a56256d60a7f0107366d3: six completed GitHub Actions workflows, all successful including Test suite ratchet. Source-only validation; not a runtime authorization or T1 registration. T2 PR #505 head 4544ba4922d2d9a40fb2292a0ef6552d6a23cd70: thirty completed workflows, all successful. StegCore T6 PR #254 head c6b411228470252ae065b03db9b08fd55564d496: two completed workflows, both successful. No merges performed. Issue #484 explicitly distinguishes non-authorizing source merges from governed migrations requiring canonical T1 registration. The remaining adapter target `benchmarks/svg_native_source_adapter.py` could not be located on SDK main during this pass; do not invent or silently replace it.

## 2026-10-17 reconciliation (supersedes the stale lines above)

- **Merged, not draft.** #506 merged at `d4d0f2d`. #516 merged at `579998a`.
- **No `jsonschema`.** #516 moved `scripts/verify_universal_entry_envelope.py` to the SDK-native validator (`stegverse/structural_validator_candidate.py`, loaded by path). The "uses Draft202012Validator" line above no longer holds. `tests/test_t6_universal_entry_validator.py` carries its differential mutation tests.
- **T1 registered.** `SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001`, COSV `60200000013002` (`StegVerse-Labs/.github` #3181).
- **T6-001 governed attempt: DENY.**
  - Path: StegVerse-org intake (#159) → StegCore `steggate.evaluate_admissibility`, which returned **DENY** `signal.inputs_incomplete`.
  - Labs receipt: `103ce892`. StegVerse-org closure: `8fe9d362` (ORGANIZATION_EGRESS_CLOSED).
  - Failed predicates:
    - missing authenticated grant;
    - missing TV/TVC source provenance;
    - stale actor authority and delegation;
    - owner approval not bound.
- **T6-002 next attempt.** It needs three things:
  - **WorkerCoordinator claim for TASK-2026-0014.** The request is a durable queue entry. Its event-ephemeral consumption is open as `StegVerse-Labs/.github` #3211, which needs no resident machine.
  - **T5 provenance.** The TVC lane is proposed as item A5 on `StegVerse-Labs/TVC#488`.
  - **Owner approval.** It must be bound to the T6-002 candidate hash (SDK#484 RESPONSE-041).
- **Master Records.** Reconstruction is non-gating downstream evidence, never a predicate.
- **Missing adapter target.** `benchmarks/svg_native_source_adapter.py` lives in StegCore, not the SDK (SDK#484 comment 6167499524).
