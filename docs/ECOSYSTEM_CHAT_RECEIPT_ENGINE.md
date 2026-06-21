# Ecosystem Chat Receipt Engine Evaluator

## Purpose

This evaluator determines whether a Site-originated SDK intake payload is ready for receipt issuance.

It does not create proof receipts while receipt authority is pending.

## Inputs

The evaluator consumes the deterministic receipt request built from:

```text
fields
manifest
receipt_window
```

## Decisions

```text
ISSUANCE_PENDING
ISSUANCE_BLOCKED
```

## Current behavior

```text
Accepted SDK intake + disabled receipt authority -> ISSUANCE_PENDING
Rejected SDK intake -> ISSUANCE_BLOCKED
Receipt identifier -> null
```

## Public helper

```python
from stegverse.ecosystem_chat_receipt_engine import evaluate_ecosystem_chat_payload_for_receipt

decision = evaluate_ecosystem_chat_payload_for_receipt(payload)
```

## Boundary

A pending issuance decision is not a proof receipt.

A future governed receipt issuer must be connected before the evaluator can return a non-null receipt identifier.

## Next integration target

Wire the evaluator to the governed receipt issuer, then add master-records handoff after generated receipts are proven by tests.
