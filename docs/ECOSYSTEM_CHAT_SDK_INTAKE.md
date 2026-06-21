# Ecosystem Chat SDK Intake

## Purpose

This SDK intake path accepts the completed Site-side Ecosystem Chat form payload.

The accepted payload must preserve three layers:

```text
fields
manifest
receipt_window
```

## Current state

```text
Validator: installed
Backend handler: installed
HTTP adapter: installed
Minimal tests: installed
Receipt issuance: not installed
Hosted service endpoint: not installed
```

## Validator

```python
from stegverse.ecosystem_chat_intake import validate_ecosystem_chat_payload

result = validate_ecosystem_chat_payload(payload).to_dict()
```

## Backend handler

```python
from stegverse.ecosystem_chat_backend import handle_ecosystem_chat_submission

response = handle_ecosystem_chat_submission(payload)
```

## HTTP adapter

```python
from stegverse.ecosystem_chat_http import handle_ecosystem_chat_http

status, response = handle_ecosystem_chat_http(
    "POST",
    "/api/ecosystem-chat",
    request_body,
)
```

The response shape is:

```text
accepted
routed_module
receipt_id
next_action
errors
```

`receipt_id` remains `None` in this pre-receipt stage.

## Acceptance rule

The SDK accepts only payloads where:

1. `fields`, `manifest`, and `receipt_window` are all present;
2. manifest values derive from the submitted fields;
3. receipt-window values derive from the submitted fields;
4. closed-choice values are within the allowed SDK vocabulary;
5. Site does not claim receipt issuance;
6. the manifest is correct at submission time;
7. correctness errors are empty.

## Next step

Mount `handle_ecosystem_chat_http(method, path, body)` in a hosted service and connect receipt issuance only after the governed SDK-side receipt authority is installed.
