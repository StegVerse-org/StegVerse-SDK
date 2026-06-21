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
```

## Current boundary

The pipeline returns current stage outputs only.

It does not bypass intake validation.
It does not create a non-null receipt identifier by default.
It does not perform an external write.

## Next integration target

Inject a governed issuer implementation, then connect persistence only after issuer behavior is proven by tests.
