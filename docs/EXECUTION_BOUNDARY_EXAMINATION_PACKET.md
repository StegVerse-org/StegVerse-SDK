# Execution-Boundary Examination Packet

Updated: 2026-08-22

## Purpose

This document defines the minimum reviewer-visible evidence interfaces for the first controlled-production `n=1` examination. It is intentionally narrower than the implementation surface.

The examiner receives enough evidence to independently determine the sequence and result without requiring disclosure of unrelated implementation details.

## Frozen fixture declaration

The packet begins with a signed or receipt-bound fixture declaration containing:

```text
fixture_id
candidate_id
candidate_action_type
payload_hash
target_id
authority_source_id
frozen_admissibility_predicates
material_state_variable
initial_required_state
intervening_state
execution_boundary_definition
concurrency_prohibited: true
```

The fixture declaration must be frozen before execution.

## Evidence interfaces

### E1 — initial admissibility

```text
candidate_id
authority_source_id
evaluation_time_or_order
admissibility_result
receipt_hash
relevant_state_hash
```

### E2 — material state transition

```text
transition_id
material_state_variable
from_state_hash
to_state_hash
from_state_value
to_state_value
materially_relevant: true
observed: true
observed_at_or_order
continuity_reference
```

### E3 — execution-boundary state observation

```text
candidate_id
target_id
boundary_state_hash
boundary_state_value
observation_time_or_order
consequence_alterable_at_boundary: true
```

### E4 — fresh boundary admissibility

```text
candidate_id
authority_source_id
evaluation_time_or_order
admissibility_result
receipt_hash
relevant_state_hash
```

The candidate and authority identifiers must match E1.

### E5 — SDK execution-boundary determination

```text
case_id
candidate_id
boundary_determination
execution_disposition
falsification_outcome
independently_reconstructable
receipt_hash
```

### E6 — canonical route and custody references

```text
canonical_manifest_id
manifest_receipt_id
Master Records checkpoint MRR reference
StegCore transaction reference
StegGate / commit-coherence determination reference
Master Records exact-run MR reference
return MRR reference
```

Identifiers may be opaque where necessary; they must remain sufficient for authorized independent verification.

### E7 — actual consequence observation

```text
target_id
candidate_id
expected_record_hash
record_present: true|false
observation_time_or_order
observation_receipt_or_hash
```

For the selected negative-control trajectory, the strongest conforming result is `record_present: false` after `PREVENT_CONSEQUENCE`.

### E8 — replay result

```text
manifest_receipt_id
replay_result
reexecution_occurred: false
receipt_or_hash
```

### E9 — reconstruction result

```text
manifest_receipt_id
reconstruction_result
sequence_established
boundary_determination_reconstructed
consequence_status_reconstructed
receipt_or_hash
```

## Examiner determination table

The examiner must be able to distinguish at least:

```text
PASS_MINIMUM_N1_BOUNDARY_CASE
  evidence complete; consequence conforms to boundary disposition

FAIL_CONSEQUENCE_NONCONFORMANCE
  actual consequence contradicts the retained boundary disposition

INDETERMINATE_EVIDENCE_BOUNDARY
  evidence does not establish the execution boundary or required continuity
```

No result is predeclared by the fixture.

## Minimum disclosure rule

Only evidence necessary to establish the claimed transition, boundary, disposition, custody, replay, reconstruction, and consequence is required.

The examiner does not require:

```text
unrelated source code
unrelated customer data
unrelated infrastructure configuration
unrelated credentials or secrets
internal model prompts
private implementation details not necessary to establish the evidence chain
```

## Integrity requirements

1. Candidate identity must remain stable from initial admission through boundary reassessment.
2. Authority source must remain stable.
3. Receipt hashes must validate.
4. The material state transition must be observed and causally linked.
5. Boundary evaluation must occur while the consequence remains alterable.
6. Canonical custody references must establish the actual route used.
7. Replay must not re-execute the original consequence.
8. Reconstruction must independently recover the material sequence and determination.

## Commercial scope boundary

The first paid examination may be scoped around exactly one execution of the frozen fixture. Expansion to concurrency, manifold governance, multiple simultaneous transitions, generalized heartbeat-relative dependencies, or additional actuator classes requires a separate scope.

## Authority constraints

```text
examination_authorizes_execution: false
SDK_authorizes_execution: false
credential_authority: TV/TVC
GitHub_runtime_authority: NONE
non_TV_TVC_secret_or_token_allowed: false
```
