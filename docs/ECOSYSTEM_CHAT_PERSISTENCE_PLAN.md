# Ecosystem Chat Persistence Plan

## Purpose

This module creates a deterministic plan for future persistence of an Ecosystem Chat record export.

It does not perform an external write.

## Public helper

```python
from stegverse.ecosystem_chat_persistence_plan import build_persistence_plan

plan = build_persistence_plan(record_export).to_dict()
```

## Shape

```text
persistence_status
persistence_hash
receipt_id
export_hash
external_write_complete
errors
```

## States

```text
PERSISTENCE_PENDING: receipt_id and export_hash are present
PERSISTENCE_BLOCKED: receipt_id or export_hash is missing, or export errors exist
```

## Boundary

`external_write_complete` remains `false`.

A future write adapter must consume a pending persistence plan and prove the write before this field may become true.
