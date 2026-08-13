# Public Inspection Custody / Replay Mirror Handoff

## Authority

```text
goal_id: SDK-PUBLIC-INSPECTION-CUSTODY-REPLAY-005
repository: StegVerse-org/StegVerse-SDK
branch: feat/inspection-custody
parent_handoff: docs/PUBLIC_INSPECTION_GOVERNED_TEST_RUNTIME_MIRROR_HANDOFF.md
repository_handoff: SDK_MIRROR_HANDOFF.md
implementation_state: INSTALLED_PENDING_VALIDATION_MERGE
release_state: NOT_RELEASED
```

## Goal

Enforce the ecosystem invariant that every governed SDK state transition is retained in Master Records, and make SDK replay/reconstruction actual callable operations rather than documentation-only promises.

## Installed implementation

```text
stegverse/public_inspection_runtime.py
tests/test_public_inspection_runtime.py
README.md
docs/SDK_CONSOLE.md
docs/PUBLIC_INSPECTION_ENTRY.md
docs/PUBLIC_INSPECTION_GOVERNED_TEST_RUNTIME_MIRROR_HANDOFF.md
SDK_MIRROR_HANDOFF.md
```

## Governed-run ordering

```text
public inspection request
-> bounded validation
-> canonical StegCore AdmissibilityRequest
-> canonical run_manifested_transaction
-> complete hash-chained transition trajectory
-> canonical manifest_receipt_id
-> build_master_records_submission
-> POST canonical exact-run evidence package to Master Records
-> require custody_status: RECORDED
-> return governed result to caller
```

The runtime preflights Master Records before governance and fails closed if custody cannot be configured or confirmed. The TEST consequence executor remains side-effect-free; governance transitions are still ecosystem state transitions and therefore require custody.

## Replay

```text
input: manifest_receipt_id
source: Master Records exact-run evidence package
operation: canonical StegCore admissibility re-evaluation only
consequence executor: NEVER INVOKED
original Master Record mutation: NONE
```

Replay compares original/replayed disposition and candidate identity and reports deterministic comparison fields.

## Reconstruction

```text
input: manifest_receipt_id
source: Master Records canonical reconstruction route
consequence reexecution: FALSE
original Master Record mutation: NONE
```

## Read-only boundary

Replay and reconstruction intentionally do not create new ecosystem state. They query retained state and derive comparisons without mutation. Therefore they do not require a second custody write merely for being read.

If a future replay/reconstruction mode creates persisted derived artifacts, approvals, decisions, consequences, or other ecosystem mutations, those new states must be separately retained in Master Records before that future mode may report success.

## Validation gate

Required before merge/release claim:

```text
1. SDK unit/contract tests PASS.
2. Canonical StegCore dependency installs from the pinned revision.
3. Canonical master-records/orchestration local custody service starts.
4. One governed TEST produces custody_status RECORDED.
5. Returned manifest_receipt_id resolves through Master Records to the same immutable run.
6. Replay reads that retained request, does not invoke consequence, and deterministic comparison is inspectable.
7. Reconstruction returns persisted-vs-derived evidence and consequence_reexecuted false.
8. Original retained record hash is unchanged before/after replay and reconstruction.
```

No release, evaluator-ready receipt, or production activation claim is authorized until the applicable validation evidence exists.
