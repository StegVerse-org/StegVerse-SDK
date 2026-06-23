# Universal Transition Table Intake

The universal transition-table intake adapter accepts a verified package produced by `StegVerse-org/universal-transition-table-test-path` and binds it at the SDK boundary.

It does not execute ingestion, sandbox, runtime, or production trust-kernel paths.

## Import

```python
from stegverse.universal_transition_table_intake import handle_universal_transition_table_package
```

or:

```python
from stegverse import handle_universal_transition_table_package
```

## Required inputs

```text
transition_test_package.json
expected_result.json
machine_replay_packet.json
```

## Accepted package condition

The adapter accepts only when:

```text
expected_construction_status == CONSTRUCTED
expected_route_eligibility == true
sdk_route_eligible == true
blocked_reasons is empty
human_readable_result_required == true
machine_replay_required == true
receipt_requirements is present
```

## Output

```text
manifest
intake_receipt
route_eligibility_receipt
```

## Non-scope

```text
live ingestion
live sandbox
runtime execution
production trust-kernel enforcement
external endorsement
compatibility recognition
publication authorization
```
