# Ecosystem Chat Record Export Candidate

## Purpose

This document records the deterministic export candidate produced after Ecosystem Chat receipt evaluation.

The export candidate does not perform an external write.

## Builder

```python
from stegverse.ecosystem_chat_record_export import build_record_export_candidate

candidate = build_record_export_candidate(payload).to_dict()
```

## Shape

```text
export_status
export_hash
request_hash
receipt_id
external_write_complete
errors
```

## Current states

```text
EXPORT_PENDING: receipt evaluation has no errors, but receipt_id is still null
EXPORT_BLOCKED: receipt evaluation has errors
external_write_complete: false
```

## Boundary

This is a pre-handoff candidate only.

It may be used later by a governed persistence integration after a non-null receipt exists and the external destination is connected.
