# Provider Usage Event Handoff

## Active goal

```text
Goal: ingest adapter-owned provider usage events into SDK transition and session usage contracts
Upstream: StegVerse-org/LLM-adapter PR 48
Upstream merge: 623dbefca7c18d4838d423434aeeb4ede04eceb1
Module: stegverse/provider_usage_ingest.py
Fixture: examples/provider_usage_event.json
Tests: tests/test_provider_usage_ingest.py
Authority posture: ingestion_is_not_authority
Manual user action required: false
State: IMPLEMENTED_PENDING_CANONICAL_VALIDATION
```

## Completion boundary

The goal is complete when the SDK independently validates the adapter event hash and non-authority boundary, projects measurements into `TransitionUsageEvent`, preserves provider ownership and return-to-origin receipt requirements, aggregates the projected event without converting usage into value or authority, passes the existing Python 3.9/3.11/3.12 SDK validation matrix, and merges to `main`.

## Successor goal

After merge, bind the projected SDK transition usage event into a deterministic session usage receipt and optional Master-Records custody handoff while preserving:

```text
sdk_validation_is_execution == false
aggregation_is_authority == false
session_receipt_is_custody == false
custody_is_authority == false
```
