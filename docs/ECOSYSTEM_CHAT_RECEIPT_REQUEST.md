# Ecosystem Chat Receipt Request

## Purpose

This document records the pre-issuance receipt request object for Ecosystem Chat SDK intake.

The request object is deterministic and hash-bound to the submitted payload.

It does not issue a proof receipt.

## Builder

```python
from stegverse.ecosystem_chat_receipt_request import build_ecosystem_chat_receipt_request

request = build_ecosystem_chat_receipt_request(payload).to_dict()
```

## Shape

```text
request_hash
routed_module
accepted
receipt_authority_installed
receipt_issuance_enabled
receipt_id
errors
```

## Current state

```text
request_hash: sha256 over canonical JSON payload
receipt_authority_installed: false
receipt_issuance_enabled: false
receipt_id: null
```

## Boundary

A receipt request is not a proof receipt.

It is the object that a future governed receipt engine may evaluate before issuing a non-null receipt identifier.

## Next integration target

Use this request object as the input to the governed receipt engine, then hand the resulting receipt record to master-records only after receipt creation is proven by tests.
