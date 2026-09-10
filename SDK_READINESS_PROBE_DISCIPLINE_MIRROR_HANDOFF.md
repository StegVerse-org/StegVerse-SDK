# SDK Readiness Probe Discipline Mirror Handoff

## Canonical identity

```text
Goal Task ID: SDK-READINESS-PROBE-DISCIPLINE-004
Parent Goal Task ID: SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003
Repository: StegVerse-org/StegVerse-SDK
Branch: sdk-readiness-probe-discipline-004
Status: ACTIVE
```

## Defect

External evaluation exposed an invalid composition: successful SDK/source-governance preparation can be true while end-to-end execution readiness is still unsupported. A narrower satisfied predicate must never be promoted into broader READY state.

## Required state discipline

Readiness is cumulative over every currently identified applicable predicate. A predicate may be SATISFIED, UNSATISFIED, UNKNOWN, or NOT_APPLICABLE. READY is permitted only when every identified applicable predicate is SATISFIED and there is no unresolved ambiguity affecting applicability or evidence.

Unknown unknowns cannot be enumerated before discovery. Once discovered they become known predicates and are immediately incorporated into the readiness set before any later READY classification.

Ambiguity that can affect readiness produces PROBE_REQUIRED, not READY. A probe may be system-side or UI-side, but reclassification requires durable probe evidence identifying the predicate, observation, evidence reference, and observation time.

## State ordering

```text
BLOCKED       := at least one applicable predicate is UNSATISFIED
PROBE_REQUIRED:= no known blocker, but at least one applicable predicate is UNKNOWN or applicability/evidence ambiguity can affect readiness
READY         := every identified applicable predicate is SATISFIED and no readiness-affecting ambiguity remains
```

BLOCKED dominates PROBE_REQUIRED; PROBE_REQUIRED dominates READY.

## Implementation scope

- Add a reusable SDK readiness evaluator independent of governance decision semantics.
- Require explicit predicate records and durable probe evidence for UNKNOWN -> SATISFIED/UNSATISFIED transitions.
- Reject direct READY claims when unresolved UNKNOWN predicates or ambiguity exist.
- Preserve source-governance success as a predicate, never as an end-to-end readiness synonym.
- Add regression tests for the external evaluator failure mode.
- Maintain README with the readiness/probe contract.

## Completion predicate

COMPLETE requires source tests proving cumulative predicate evaluation, ambiguity-to-PROBE_REQUIRED behavior, durable probe-evidence transition validation, and prevention of SDK/source-governance success from independently yielding end-to-end READY; canonical task/registry/handoff and README must be reconciled.
