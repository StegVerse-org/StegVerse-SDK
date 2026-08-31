# IW Matrix Falsifier Mirror Handoff

Updated: 2026-08-31

## Scope and authority

```text
goal_id: SDK-IW-MATRIX-FALSIFIERS-004
repository: StegVerse-org/StegVerse-SDK
canonical_branch: main
implementation_branch: test/iw-matrix-falsifiers-20260831
parent_handoff: STEGVERSE_SDK_MIRROR_HANDOFF.md
predecessor_handoffs:
  - ADMISSIBILITY_COMPOSITION_MIRROR_HANDOFF.md
  - EXECUTION_BOUNDARY_EVIDENCE_MIRROR_HANDOFF.md
SDK_role: non-authorizing falsification/conformance surface
canonical_execution_authority: external to SDK
status: VALIDATED_READY_FOR_MERGE
```

## Goal

Make two coupled-manifold falsifiers executable through the SDK without moving governance authority into the SDK.

### IW-FALSIFIER-001 — Temporal Order Dependence

Hold G/E/A/IW and the governed candidate set constant while varying only lane arrival/processing order. If the committed Action changes and order is not an explicit governed matrix input, temporal progression has become an undeclared governance variable.

Invariant:

```text
same governed matrix inputs + same candidate set + different arrival order
MUST NOT produce different committed Action
unless order is explicitly represented as a governed input.
```

### IW-FALSIFIER-002 — Irreversible Early Commit / Coupled-Manifold Omission

A1 and A2 are individually lane-admissible. Governance-relevant coupled information exists before A1 crosses the Action boundary, but is absent from A1's local lane view. Full G/E/A/IW resolution over the same Action state uniquely yields A3. If A1 nevertheless crosses the irreversible Action boundary, the architecture is falsified.

Invariant:

```text
perfect lane-local correctness does not imply Action correctness.
A lane MUST NOT cross the Action boundary before the relevant coupled manifold is resolved.
```

## Required surfaces

```text
stegverse/iw_matrix_falsifier.py
tests/test_iw_matrix_falsifier.py
.github/workflows/iw-matrix-falsifier-validation.yml
tasks/SDK-IW-MATRIX-FALSIFIERS-004.json
IW_MATRIX_FALSIFIER_MIRROR_HANDOFF.md
```

## Authority boundary

```text
sdk_evidence_is_execution_authority == false
sdk_falsifier_is_commit_authority == false
sdk_test_result_is_runtime_activation == false
github_actions_is_runtime_authority == false
```

The SDK may prove that a supplied architecture trace violates or preserves the falsifier invariants. It does not execute the governed actions.

## Completion gates

```text
implementation: COMPLETE
focused tests: PASS (6/6)
workflow validation: PASS
  IW Matrix Falsifier Validation: run 33404519933 / Python 3.9, 3.11, 3.12 SUCCESS
  SDK Package Artifact Validation (Non-Authorizing): run 33404519845 SUCCESS
merge: PENDING
cross-repository propagation assessment: PENDING
```

## Observed test results

```text
IW-FALSIFIER-001 positive falsification:
  same declared governed input + same candidate set
  different non-governed arrival order
  different committed Action
  => FAIL_TEMPORAL_ORDER_DEPENDENCE

IW-FALSIFIER-001 controls:
  explicit governed order may legitimately affect outcome
  same matrix-resolved Action across arrival orders does not falsify

IW-FALSIFIER-002 positive falsification:
  lane-local checks all pass
  coupled information existed within declared scope before boundary
  A1 crosses irreversible Action boundary
  unique matrix solution = A3
  A1 != A3
  => FAIL_IRREVERSIBLE_EARLY_COMMIT

IW-FALSIFIER-002 controls:
  information that did not exist before boundary is not used as a falsifier
  lane Action matching unique matrix Action does not falsify
```

These are SDK-local architecture-trace falsifiers. They validate the test semantics and implementation, not a live external architecture run.
