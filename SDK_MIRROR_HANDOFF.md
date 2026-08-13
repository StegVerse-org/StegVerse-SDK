# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
```

Live repository state, immutable commits, validation evidence, scoped mirror handoffs, and this file supersede prior chat claims.

## Goal inventory

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002: COMPLETE_STATIC_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-TEST-004: SUPERSEDED_BY_CUSTODY_BACKED_RUNTIME
SDK-PUBLIC-INSPECTION-CUSTODY-REPLAY-005: INSTALLED_PENDING_VALIDATION_MERGE
```

No person-specific evaluator route is canonical.

## Governing invariant

```text
every ecosystem state transition produced by a governed SDK run must be retained in Master Records
successful governed SDK run without Master Records custody: PROHIBITED
caller return projection may suppress Master Records custody: FALSE
```

A preparation-only operation is not an ecosystem state transition and may still stop before governance with `NOT_RUN` / `NOT_CLAIMED`.

## Custody-backed governed public inspection runtime

Current implementation:

```text
stegverse/public_inspection_runtime.py
```

The runtime now requires `MASTER_RECORDS_URL` and `MASTER_RECORDS_AUTH_TOKEN` (or equivalent explicit arguments) before it begins a governed TEST. It preflights the custody service, runs the canonical StegCore manifested-transaction path, derives the canonical `manifest_receipt_id`, builds the canonical Master Records submission through StegCore, and requires a `RECORDED` custody response before reporting success.

The canonical governance request itself is retained in the transaction manifest metadata so a later read-only replay can reconstruct the exact StegCore request from Master Records.

Canonical ordering:

```text
bounded inspection request
-> canonical StegCore AdmissibilityRequest
-> canonical manifested transaction
-> complete transition receipt chain
-> canonical manifest_receipt_id
-> full exact-run Master Records custody
-> custody_status: RECORDED
-> caller result
```

The TEST consequence executor remains side-effect-free, but the governance state transitions are real ecosystem transitions and therefore are custodied.

## Option 1 — replay

Replay is no longer guidance-only.

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

Replay:

```text
1. resolves the exact retained package from Master Records;
2. recovers the retained canonical governance request;
3. performs a pure canonical StegCore admissibility re-evaluation;
4. compares original vs replay disposition and candidate identity;
5. never invokes the consequence executor;
6. never mutates the original Master Record.
```

Because replay is implemented as a pure read/evaluation operation with no state mutation, it creates no new ecosystem state transition requiring a second custody write.

## Option 2 — reconstruction

Reconstruction is no longer guidance-only.

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

The SDK reads the canonical Master Records reconstruction route and requires `consequence_reexecuted: false`. The Master Records response preserves persisted historical evidence separately from reconstructed material and does not mutate the original exact-run record.

Because reconstruction is read-only, it creates no new ecosystem state transition.

## Public PR boundary

A public PR is a visible declarative request/discussion record. PR-supplied code is not used as evaluator/runtime authority. A receipt locator may be posted back to the PR only after the governed run has been recorded in Master Records.

## Isolated local custody

A tester may run the canonical `master-records/orchestration` custody application locally. This does not duplicate Master Records inside the SDK; it reuses the owning implementation. Local canonical custody is valid test custody but is not a claim of production activation.

## Cross-repository ownership

```text
LLM transport/translation: StegVerse-org/LLM-adapter
Canonical governance/exact-run semantics: StegVerse-Labs/StegCore
Exact-run custody/reconstruction: master-records/orchestration
```

## Remaining cross-repository work

```text
1. validate this SDK runtime against a canonical local Master Records service;
2. reconcile the LLM-adapter so its governed ingress uses the same custody-before-return invariant;
3. prove the shared/live Master Records transport once repository-wide storage/readiness gates are satisfied;
4. run the frozen external-evaluation cases only through this custody-backed path before describing their IDs as evaluator-ready.
```

## Release state

This custody/replay/reconstruction correction is not yet tagged/released. Do not propagate release claims until validation, merge, and release authority gates are satisfied.
