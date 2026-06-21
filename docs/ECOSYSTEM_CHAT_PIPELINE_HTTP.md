# Ecosystem Chat Pipeline HTTP Adapter

## Purpose

This adapter returns the full current SDK pipeline result for a Site Ecosystem Chat payload.

It preserves the existing intake-only HTTP adapter and does not replace it.

## Public helper

```python
from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http

status, result = handle_ecosystem_chat_pipeline_http(
    "POST",
    "/api/ecosystem-chat",
    request_body,
)
```

## Result shape

```text
intake
receipt_decision
record_export
```

## Boundary

The adapter parses JSON and runs the current SDK pipeline.

It does not create a non-null receipt identifier.
It does not perform an external write.

## Use

Use this adapter for hosted service work that needs visibility into every current stage.

Use `handle_ecosystem_chat_http` for the smaller intake-only response shape.
