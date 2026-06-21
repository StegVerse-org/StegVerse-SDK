# Ecosystem Chat Receipt Authority

## Purpose

This document records the current receipt authority boundary for Ecosystem Chat SDK intake.

## Current state

```text
Receipt authority boundary: installed
Receipt issuing engine: pending
Hosted service endpoint: pending
```

## SDK status helper

```python
from stegverse.ecosystem_chat_receipt_authority import get_receipt_authority_status

status = get_receipt_authority_status()
```

Current helper values:

```text
authority_installed: false
receipt_issuance_enabled: false
authority_name: SDK_RECEIPT_AUTHORITY_PENDING
```

## Boundary

The SDK intake validator, backend handler, and HTTP adapter may validate and accept a Site-generated payload.

They do not create a proof receipt in the current stage.

A future governed receipt engine must be wired before any non-null receipt identifier is returned.

## Next integration target

Connect this boundary to the governed receipt engine, then add master-records handoff after receipt creation is proven by tests.
