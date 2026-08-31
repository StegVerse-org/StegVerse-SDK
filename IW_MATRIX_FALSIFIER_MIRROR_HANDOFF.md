# IW Matrix Falsifier Mirror Handoff

Updated: 2026-08-31

## Scope and authority

```text
goal_id: SDK-IW-MATRIX-FALSIFIERS-004
repository: StegVerse-org/StegVerse-SDK
canonical_branch: main
implementation_branch: test/iw-matrix-sdk-integration-20260831
parent_handoff: STEGVERSE_SDK_MIRROR_HANDOFF.md
predecessor_handoffs:
  - ADMISSIBILITY_COMPOSITION_MIRROR_HANDOFF.md
  - EXECUTION_BOUNDARY_EVIDENCE_MIRROR_HANDOFF.md
SDK_role: non-authorizing falsification/conformance surface
canonical_execution_authority: external to SDK
status: MERGED_BASELINE_WITH_INTEGRATION_TESTS_PENDING_VALIDATION
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
merge: BASELINE MERGED via PR #112 / squash 7816670f691a84ea3d4ea97ec16e77a324891700
integration extension merge: PENDING
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


## SDK-native integration extension

The first falsifier slice validated architecture-trace semantics. The successor integration tests now exercise the existing SDK admissibility, composition, and execution-boundary implementations directly.

Added surface:

```text
tests/test_iw_matrix_sdk_integration.py
```

The integration test asserts three additional properties:

1. a real SDK single-lane boundary evaluation can return `PERMIT_CONSEQUENCE` for A1 while the real n>1 composition evaluator fails closed for A1+A2 because no governed joint relation exists;
2. reversing component arrival order does not change the joint governance classification where order is not a governed input; and
3. once the consequence is already irreversible, the execution-boundary evaluator correctly treats re-assessment as too late rather than retroactively restoring governance correctness.

These tests remain non-authorizing and do not claim a live external irreversible action was executed.
