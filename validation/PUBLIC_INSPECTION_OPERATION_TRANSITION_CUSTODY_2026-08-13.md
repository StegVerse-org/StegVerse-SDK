# Public Inspection Replay/Reconstruction Transition Custody — 2026-08-13

Status: STATIC CONTRACT INSTALLED; INTEGRATED MASTER RECORDS EXECUTION NOT YET CLAIMED.

Replay and reconstruction are operations requested through the SDK for a specific `manifest_receipt_id`. Although neither operation mutates the original exact run or re-executes its consequence, the operation itself traverses ecosystem state transitions that must be recorded in Master Records before the requested artifact is returned.

Required chains:

```text
REPLAY      REQUESTED -> SOURCE_RESOLVED -> EVALUATED -> RETURNED
RECONSTRUCT REQUESTED -> SOURCE_RESOLVED -> ARTIFACT_DERIVED -> RETURNED
```

The SDK now reports success only when each transition has a `RECORDED` Master Records organization record; otherwise it fails closed. The returned artifact includes the operation ID and Master Records operation receipts.

Integrated validation depends on the matching Master Records operation-event routes being merged and exercised through the canonical organization-record service.
