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

Enforce the ecosystem invariant that every state transition required by SDK run, replay, and reconstruction is retained in Master Records before the corresponding artifact is returned.

## Governed-run ordering

```text
public inspection request
-> bounded validation
-> canonical StegCore AdmissibilityRequest
-> canonical run_manifested_transaction
-> complete hash-chained transition trajectory
-> canonical manifest_receipt_id
-> POST exact-run evidence package to Master Records
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

Each transition is appended to Master Records under a distinct replay `operation_id`, hash-linked in sequence, and assigned an operation-event receipt. The SDK fails closed if any transition cannot be recorded. Only after `RETURNED` is recorded may the replay artifact be returned to the caller.

## Reconstruction operation custody

Input: `manifest_receipt_id`.

The original consequence is not re-executed and the original retained exact-run package is not mutated. The reconstruction request still creates new ecosystem states:

```text
REQUESTED
-> SOURCE_RESOLVED
-> ARTIFACT_DERIVED
-> RETURNED
```

Those transitions are likewise recorded in Master Records before the reconstruction artifact is returned.

## Correct boundary

```text
read-only with respect to original record != no ecosystem transition
original_record_mutated: false
consequence_reexecuted: false
operation_transition_custody: required
```

## Cross-repository dependency

The SDK operation-event client requires the matching `master-records/orchestration` operation-event API:

```text
POST /api/master-records/manifest-receipts/{manifest_receipt_id}/operations
GET  /api/master-records/manifest-receipts/{manifest_receipt_id}/operations/{operation_id}
```

Master Records owns operation event IDs, sequencing, hash linkage, and durable custody. The SDK only requests custody and refuses to return success until `RECORDED` is confirmed.

## Validation gate

Before merge/release claim:

```text
1. Master Records operation-transition implementation/tests PASS.
2. Canonical custody app exposes operation POST/GET routes.
3. One governed TEST returns only after exact-run custody RECORDED.
4. Replay records REQUESTED/SOURCE_RESOLVED/EVALUATED/RETURNED and then returns artifact.
5. Reconstruction records REQUESTED/SOURCE_RESOLVED/ARTIFACT_DERIVED/RETURNED and then returns artifact.
6. Original exact-run hash is unchanged after both operations.
7. Original consequence is not re-executed.
8. SDK tests and integrated authenticated round trip PASS.
```

No release, evaluator-ready receipt, or production activation claim is authorized until applicable validation evidence exists.
