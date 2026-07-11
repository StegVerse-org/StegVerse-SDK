# SDK-to-SPE Commitment Intake

## Purpose

This contract converts an SDK-origin `DECLARED` transition candidate into a deterministic, non-authorizing Commitment Candidate envelope for `StegVerse-Labs/Standing-Proof-Engine`.

The SDK does not decide standing. It presents a bounded candidate for a fresh standing determination.

## Input Boundary

Required SDK transition posture:

```text
origin.origin_class = SDK_INPUT
lifecycle_state = DECLARED
governance.admissibility_result = PENDING
governance.commit_time_validity = PENDING
execution.action_ref = null
continuity.final_receipt_id = null
```

## Commitment Candidate Boundary

The generated candidate must state:

```text
candidate_type = COMMITMENT_CANDIDATE
authorizing = false
inherits_review_authority = false
implies_standing = false
requires_fresh_standing_determination = true
```

Required contextual fields are preserved or supplied explicitly:

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

## SPE Intake Envelope

The transport-neutral envelope contains:

```text
schema_version
destination_repo
route_purpose
package_id
transition_id
run_id
candidate_hash
candidate
authority
expected_result
receipt_required
envelope_hash
```

Expected SPE results are bounded to:

```text
ALLOW
DENY
FAIL_CLOSED
```

An `ALLOW` result establishes only the standing expressed by the returned SPE receipt and does not independently execute the requested action.

## Determinism

Both `candidate_hash` and `envelope_hash` are SHA-256 hashes over canonical JSON with sorted keys and compact separators.

## Local Verification

```bash
python -m unittest tests.test_spe_commitment_intake
```

The existing SDK workflow should discover this test through its current test surface. No new workflow is required.

## Boundary Statements

```text
SDK construction is not SPE standing.
SPE standing is not execution.
Receipt generation is not Master-Records installation.
Routing to SPE is not delegation.
A Commitment Candidate does not inherit reviewer authority.
```
