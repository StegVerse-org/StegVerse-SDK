# SDK Compiled-State Governance Matrix Mirror Handoff

Goal Task ID: `SDK-COMPILED-STATE-GOVERNANCE-MATRIX-001`
Parent Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `ACTIVE`

## Objective

Validate the final single-lane governance decision boundary after upstream sensing, context compilation, interpretation, purpose-profile application, and constraint preparation have already produced the parameters supplied to this experiment.

This experiment does not infer intent, responsiveness, cause, medical meaning, law-enforcement meaning, conversational meaning, or any other upstream interpretation. Those facts or interpretations are inputs already established before this boundary.

## Canonical test distinction

```text
CASE A — NO SIGNAL / NOT SUBMITTED
Event 3 has not been supplied as an observed state after Event 2.
Expected governance result: DENY / signal.inputs_incomplete

CASE B — OBSERVED SILENCE
Event 3 is supplied explicitly as the observed state transition from Event 2:
Event 2 ACTIVE_CONVERSATION_WITH_EMISSION_POSSIBLE
  -> observation window closes without emission
Event 3 NON_EMISSION_OBSERVED
Expected governance result: ALLOW / ok
```

Silence is not missing evidence. Missing evidence is not silence.

## Upstream boundary

Everything required to interpret the world before this decision point is outside this experiment and must already be compiled into the supplied parameters. The single-lane experiment consumes those parameters and must not reach backward and reinterpret them.

## Preserved predecessor evidence

PR #177 merged the predecessor experiment stack to main at `77732ef42505cb801cb4a60e10d8d3f9cb73deff` after exact-head `dfa6a7feeb72d90a6d327fbabd74f8b7f2164757` passed all four observed workflows. PR #197 supplied the controlled observed-silence comparison into that stack.

## Current implementation

`scripts/run_compiled_state_governance_matrix_test.py` builds two manifests from already-compiled input. In the silence case, Event 3 contains `predecessor_event: 2`, `state_transition.from_event: 2`, and transition target `NON_EMISSION_OBSERVED`. In the no-signal case, Event 3 remains `NOT_SUBMITTED` and is declared missing.

The governance evaluator code is unchanged between cases.

## Manual work

None.
