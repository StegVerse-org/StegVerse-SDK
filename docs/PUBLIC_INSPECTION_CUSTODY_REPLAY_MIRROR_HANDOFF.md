# Public Inspection Custody / Replay Mirror Handoff

## Authority

```text
goal_id: SDK-PUBLIC-INSPECTION-CUSTODY-REPLAY-005
repository: StegVerse-org/StegVerse-SDK
branch: feat/inspection-custody
parent_handoff: docs/PUBLIC_INSPECTION_GOVERNED_TEST_RUNTIME_MIRROR_HANDOFF.md
repository_handoff: SDK_MIRROR_HANDOFF.md
implementation_state: INSTALLED_PENDING_INTEGRATED_VALIDATION_MERGE
release_state: NOT_RELEASED
```

## Goal

Enforce the ecosystem invariant that every state transition required by SDK run, replay, and reconstruction is retained in the local run store before the corresponding artifact is returned (the store is the SDK-internal local run record (`stegverse/local_run_record.py`; non-authoritative: authority_effect NONE, completes_transition false; not Master Records authority or custody); Master Records is not a gate, and sovereign completion requires a verified organization-ledger readback, `stegverse/organization_ledger_evidence.py`).

## Governed-run ordering

```text
public inspection request
-> bounded validation
-> canonical StegCore AdmissibilityRequest
-> canonical run_manifested_transaction
-> complete hash-chained transition trajectory
-> canonical manifest_receipt_id
-> write exact-run evidence package to the SDK-internal local run record (stegverse/local_run_record.py; non-authoritative)
-> require custody_status: RECORDED
-> return governed result
```

## Replay operation custody

Input: `manifest_receipt_id`.

The original run remains immutable and its consequence executor is never invoked. The replay request itself creates a new observable ecosystem trajectory:

```text
REQUESTED
-> SOURCE_RESOLVED
-> EVALUATED
-> RETURNED
```

Each transition is appended to the SDK-internal local run record (non-authoritative; authority_effect NONE) under a distinct replay `operation_id`, hash-linked in sequence, and assigned an operation-event receipt. The SDK fails closed if any transition cannot be recorded. Only after `RETURNED` is recorded may the replay artifact be returned to the caller.

## Reconstruction operation custody

Input: `manifest_receipt_id`.

The original consequence is not re-executed and the original retained exact-run package is not mutated. The reconstruction request still creates new ecosystem states:

```text
REQUESTED
-> SOURCE_RESOLVED
-> ARTIFACT_DERIVED
-> RETURNED
```

Those transitions are likewise recorded in the same local run store before the reconstruction artifact is returned.

## Correct boundary

```text
read-only with respect to original record != no ecosystem transition
original_record_mutated: false
consequence_reexecuted: false
operation_transition_custody: required
```

## Cross-repository dependency

The sovereign lane no longer calls a `master-records/orchestration` operation-event API; operation events are written to the SDK-internal local run record (`stegverse/local_run_record.py`, `LocalRunRecordStore.record_operation_event`). The Master Records HTTP routes below are used only by the production-lane runtime (`stegverse/production_validation_runtime.py`) for downstream, non-gating recording and readback of released records; they are not authority or custody:

```text
POST /api/master-records/manifest-receipts/{manifest_receipt_id}/operations
GET  /api/master-records/manifest-receipts/{manifest_receipt_id}/operations/{operation_id}
```

The SDK-internal local run record assigns operation event IDs, sequencing and hash linkage for the local lane (authority_effect NONE, completes_transition false); the Organization keeps its ledger record and owns custody. The SDK fails closed if the local row cannot be written, but a written local row is never a completion: sovereign completion comes only from a verified organization-ledger readback.

## Validation gate

Before merge/release claim:

```text
1. SDK-internal local run record operation-event implementation/tests PASS (tests/test_local_run_record.py).
2. The local run record writes and reads operation events (`record_operation_event`, `reconstruct`) at the caller-supplied location.
3. One governed TEST returns only after its exact-run evidence is written to the local run record; that local row is evidence, not completion.
4. Replay records REQUESTED/SOURCE_RESOLVED/EVALUATED/RETURNED and then returns artifact.
5. Reconstruction records REQUESTED/SOURCE_RESOLVED/ARTIFACT_DERIVED/RETURNED and then returns artifact.
6. Original exact-run hash is unchanged after both operations.
7. Original consequence is not re-executed.
8. SDK tests and integrated authenticated round trip PASS.
```

No release, evaluator-ready receipt, or production activation claim is authorized until applicable validation evidence exists.
