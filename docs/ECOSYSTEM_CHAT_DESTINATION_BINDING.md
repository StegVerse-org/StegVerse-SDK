# Ecosystem Chat Destination Binding

## Purpose

This contract records the destination binding required before production writes are considered ready.

The default binding is disabled.

## Public helper

```python
from stegverse.ecosystem_chat_destination_binding import build_destination_binding

binding = build_destination_binding(config).to_dict()
```

## Shape

```text
binding_status
binding_hash
destination_name
destination_type
errors
```

## States

```text
DESTINATION_DISABLED
DESTINATION_READY
```

## Allowed destination types

```text
master-records
local-test
```

## Boundary

A ready binding does not perform a write.

It only identifies the configured destination and creates a stable binding hash.

A production write adapter must require a ready destination binding before accepting a write.
