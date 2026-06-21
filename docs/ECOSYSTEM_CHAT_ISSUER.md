# Ecosystem Chat Issuer Interface

## Purpose

This document records the governed issuer interface for Ecosystem Chat.

## Default behavior

```text
issuer_name: DISABLED_ECOSYSTEM_CHAT_ISSUER
issued: false
receipt_id: null
```

## Public helper

```python
from stegverse.ecosystem_chat_issuer import issue_with_governed_issuer

result = issue_with_governed_issuer(receipt_decision)
```

## Boundary

The default issuer fails closed.

A non-null receipt identifier requires an explicitly injected issuer.

## Next integration target

Connect a governed issuer implementation and prove it with tests before enabling production receipt identifiers.
