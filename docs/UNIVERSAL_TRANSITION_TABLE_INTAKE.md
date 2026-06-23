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

## Optional Commitment Candidate input

```text
commitment_candidate.json
```

The Commitment Candidate, also called an Execution Authority Request, is non-authorizing by design.

It must declare:

```text
candidate_type == COMMITMENT_CANDIDATE
authorizing == false
inherits_review_authority == false
implies_standing == false
requires_fresh_standing_determination == true
```

It presents a reviewed transition at a crossing point for a fresh standing determination. It does not approve execution, inherit review authority, or create standing.

## Commitment Candidate required fields

```text
bounded_scope
actor
target
action
review_ref
evidence_refs
policy_context
delegation_context
validity_window
execution_context
recoverability_profile
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

If a Commitment Candidate is supplied, it must also pass the non-authorizing invariant checks.

## Output

```text
manifest
intake_receipt
route_eligibility_receipt
```

When a Commitment Candidate is supplied, output also includes:

```text
commitment_candidate_receipt
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
commit-time standing determination
execution approval
```
