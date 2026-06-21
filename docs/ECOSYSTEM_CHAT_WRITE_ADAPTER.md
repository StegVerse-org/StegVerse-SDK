# Ecosystem Chat Write Adapter

## Purpose

This interface evaluates a persistence plan and returns a write result.

The default adapter performs no external write.

## Public helper

```python
from stegverse.ecosystem_chat_write_adapter import write_with_adapter

result = write_with_adapter(persistence_plan)
```

## Result shape

```text
write_complete
write_id
adapter_name
receipt_id
errors
```

## Default behavior

```text
adapter_name: DISABLED_ECOSYSTEM_CHAT_WRITE_ADAPTER
write_complete: false
write_id: null
```

## Boundary

A completed write requires an explicitly injected adapter.

A future production adapter must prove destination, receipt_id, and write result before `write_complete` may be true.
