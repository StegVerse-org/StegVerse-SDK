# Ecosystem Chat SDK Pipeline

## Purpose

This pipeline composes the current SDK stages for one Site Ecosystem Chat payload.

## Public helper

```python
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline

result = run_ecosystem_chat_pipeline(payload)
```

## Result shape

```text
intake
receipt_decision
issuer_result
record_export
persistence_plan
destination_binding
write_result
```

## Current boundary

The pipeline returns current stage outputs only.

It does not bypass intake validation.
It does not create a non-null receipt identifier by default.
It does not perform an external write by default.
Destination binding is disabled unless `destination_config` is provided.

## Optional injection points

```text
issuer
write_adapter
destination_config
```

## Next integration target

Provide a production write adapter only after destination, receipt_id, and write result requirements are proven by tests.
