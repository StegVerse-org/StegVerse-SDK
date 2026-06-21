# Ecosystem Chat Destination-Bound Write Adapter

## Purpose

This adapter requires a ready destination binding before a write adapter may complete.

It delegates to another adapter only after the binding check passes.

## Import

```python
from stegverse.ecosystem_chat_bound_write_adapter import DestinationBoundWriteAdapter
```

## Use

```python
binding = build_destination_binding(config).to_dict()
adapter = DestinationBoundWriteAdapter(binding, LocalEcosystemChatWriteAdapter())
```

## Write identifier shape

```text
<destination_name>:<delegate_write_id>
```

## Boundary

A missing or disabled destination binding blocks the write.

A ready binding does not itself prove external persistence; it only permits delegation to the configured write adapter.
