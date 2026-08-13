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
SDK-PUBLIC-INSPECTION-CUSTODY-REPLAY-005: INSTALLED_PENDING_INTEGRATED_VALIDATION_MERGE
```

No person-specific evaluator route is canonical.

## Governing invariant

```text
every ecosystem state transition is recorded in Master Records
successful governed SDK run without Master Records custody: PROHIBITED
successful replay/reconstruction return without operation-transition custody: PROHIBITED
caller return projection may suppress Master Records custody: FALSE
```

A preparation-only operation that stops before governance remains non-authorizing and may report `NOT_RUN` / `NOT_CLAIMED`.

## Custody-backed governed public inspection runtime

`stegverse/public_inspection_runtime.py` requires the admitted Master Records endpoint before governed execution. It runs canonical StegCore, derives the canonical `manifest_receipt_id`, submits the exact-run package, and returns the governed result only after Master Records reports `RECORDED`.

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

## Option 1 — replay

Replay is operational:

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

The original exact-run record is not mutated and the original consequence executor is never invoked. However, satisfying a replay request traverses new ecosystem states, so the operation is itself custodied:

```text
REQUESTED
-> SOURCE_RESOLVED
-> EVALUATED
-> RETURNED
```

Each transition receives an append-only Master Records operation receipt linked to the source `manifest_receipt_id` and `operation_id`. The SDK does not return the replay artifact unless all four transitions report `RECORDED`.

## Option 2 — reconstruction

Reconstruction is operational:

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

The original consequence is not re-executed and the original exact-run record is not rewritten. The reconstruction operation itself is new ecosystem history and is custodied:

```text
REQUESTED
-> SOURCE_RESOLVED
-> ARTIFACT_DERIVED
-> RETURNED
```

The SDK returns the reconstruction artifact only after all operation transitions are recorded in Master Records.

## Critical distinction

```text
original exact run immutable: true
original consequence reexecuted by replay/reconstruction: false
replay/reconstruction produce ecosystem operation state transitions: true
those operation transitions recorded in Master Records: required
```

## Public PR boundary

A public PR is a visible declarative request/discussion record. PR-supplied code is not evaluator/runtime authority. Receipt locators and replay/reconstruction operation receipts may be posted back only after the corresponding Master Records custody exists.

## Cross-repository ownership

```text
LLM transport/translation: StegVerse-org/LLM-adapter
Canonical governance/exact-run semantics: StegVerse-Labs/StegCore
Exact-run + operation-transition custody/reconstruction: master-records/orchestration
```

## Remaining cross-repository work

```text
1. merge/validate the matching Master Records operation-transition custody routes;
2. validate SDK run/replay/reconstruct end-to-end against canonical_custody_app;
3. route canonical `stegverse governance` options 1/2 directly to these executable operations;
4. reconcile LLM-adapter to the same custody-before-return invariant;
5. prove shared/live Master Records transport after repository-wide storage/readiness gates are satisfied.
```

## Release state

This custody/replay/reconstruction correction is not yet tagged/released. Do not propagate release or evaluator-ready claims until integrated validation, merge, and applicable release gates are satisfied.
