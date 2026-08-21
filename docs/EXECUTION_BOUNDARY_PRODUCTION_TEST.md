# SDK Execution-Boundary Production Test

Updated: 2026-08-21

## Purpose

This is the minimum consequential `n=1` falsification test discussed for a bounded production or qualified-client trajectory.

It tests one claim only:

```text
historical authorization does not establish continuing admissibility;
a consequence is admissible only if the materially relevant observable state
at the execution boundary establishes current admissibility.
```

The SDK helper is evidence-producing and non-authorizing. Actual consequential execution must remain on the canonical StegCore/StegGate/Master Records path.

## Prerequisites

Use SDK `main` at or after merge commit:

```text
3a17d9e04b3457914d752684d43cd57c2ab1a361
```

Validated source evidence:

```text
PR #53
Execution Boundary Evidence Validation: 32507900821 SUCCESS
SDK Package Artifact Validation (Non-Authorizing): 32507900887 SUCCESS
```

## Minimal test shape

1. Select one bounded candidate transition with a consequence that remains safely alterable at the final evaluation boundary.
2. Evaluate and retain its initial admissibility result.
3. Preserve the original authority source.
4. Introduce or observe one materially relevant state transition.
5. Record that transition with causal continuity evidence.
6. Re-evaluate the same candidate transition immediately before consequence.
7. Submit the initial result, intervening transition evidence, boundary result, and observed consequence state to the SDK execution-boundary evaluator.
8. Preserve the SDK result together with canonical MR/MRR/MRO execution/replay/reconstruction evidence.

## Python API

```python
from stegverse import (
    EXECUTION_BOUNDARY_CASE_SCHEMA,
    evaluate_admissibility_packet,
    evaluate_execution_boundary_case,
)
```

Create an initial tester packet for the candidate transition and evaluate it with `evaluate_admissibility_packet(..., strict=True)`. The `test_object.object_id` must equal the candidate transition id used in the execution-boundary case.

After a materially relevant state change, generate a fresh admissibility result for that same candidate and same authority source.

Then evaluate:

```python
case = {
    "schema": EXECUTION_BOUNDARY_CASE_SCHEMA,
    "case_id": "CASE-PROD-001",
    "candidate_transition": {
        "transition_id": "T-CANDIDATE"
    },
    "initial_admissibility": initial_result,
    "intervening_transitions": [
        {
            "transition_id": "ENV-1",
            "from_state_hash": "sha256:<state-before>",
            "to_state_hash": "sha256:<state-after>",
            "materially_relevant": True,
            "observed": True,
            "observed_at": "<observation-time-or-canonical-order-marker>"
        }
    ],
    "boundary_admissibility": boundary_result,
    "consequence": {
        "status": "pending",
        "alterable_at_boundary": True
    }
}

result = evaluate_execution_boundary_case(case)
```

## Expected determinations

```text
PERMIT_CONSEQUENCE
  Current admissibility is independently established at the boundary.

PREVENT_CONSEQUENCE
  Initial authority remains valid, but the fresh boundary evaluation no longer establishes admissibility.

FAIL_CLOSED
  Identity, receipt integrity, observation, causal continuity, authority constancy, or pre-irreversibility evidence is insufficient.
```

## Falsification outcomes

```text
PASS_MINIMUM_N1_BOUNDARY_CASE
  Evidence is complete and the consequence conforms to the boundary disposition.

FAIL_CONSEQUENCE_NONCONFORMANCE
  The consequence occurred or was prevented contrary to the boundary disposition.

INDETERMINATE_EVIDENCE_BOUNDARY
  The submitted evidence cannot establish the execution boundary.
```

## Evidence to retain

The production packet must preserve enough information for an independent verifier to answer:

```text
what was permitted
what materially changed
what the system observed
when / at what canonical ordering boundary reassessment occurred
whether the original authority remained applicable
what the boundary determination was
what execution disposition followed
whether the consequence conformed
```

Retain together:

```text
initial admissibility result + local receipt hash
material transition evidence and state hashes
fresh boundary admissibility result + local receipt hash
execution-boundary SDK result + local receipt hash
canonical manifest / receipt identifiers
Master Records MRR checkpoint custody
Master Records MR exact-run custody
return MRR custody
replay result
reconstruction result
observed consequence evidence
```

## Success criterion for the advised experiment

The strongest negative test is:

```text
initial result: admissible
original authority: unchanged
material state transition: observed and causally continuous
boundary result: no longer admissible
SDK disposition: PREVENT_CONSEQUENCE
actual consequence: prevented / blocked / not executed
falsification outcome: PASS_MINIMUM_N1_BOUNDARY_CASE
```

A deliberately executed consequence after `PREVENT_CONSEQUENCE` must be recorded as:

```text
FAIL_CONSEQUENCE_NONCONFORMANCE
```

That failure is useful evidence; it falsifies the claim that governance remained effective through consequence.

## Boundary of this test

This is intentionally the minimum linear `n=1` production test. It does not claim to solve generalized manifold governance, concurrent causal neighborhoods, logical-heartbeat dependency semantics, or manifold-local actuator admissibility. Those are broader extensions. This test remains valuable because any generalized system must reduce correctly to this minimum case.

## Credential and authority constraints

```text
credential authority: TV/TVC
GitHub runtime authority: NONE
non-TV/TVC runtime secret/token required: FALSE
SDK helper grants execution authority: FALSE
```
