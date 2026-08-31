# IW Cross-System Falsifier Mirror Handoff

Updated: 2026-08-31

## Scope and authority

```text
goal_id: SDK-IW-CROSS-SYSTEM-FIXTURE-005
issue: StegVerse-org/StegVerse-SDK#114
repository: StegVerse-org/StegVerse-SDK
canonical_branch: main
implementation_branch: test/iw-cross-system-fixture-20260831
parent_handoff: IW_MATRIX_FALSIFIER_MIRROR_HANDOFF.md
status: CLAIMED_FOR_IMPLEMENTATION_AND_VALIDATION
SDK_role: non-authorizing neutral test fixture + result evaluator
```

## Goal

Provide one neutral, machine-readable falsifier suite that can be executed independently by StegVerse and an external runtime-governance architecture, with the SDK evaluating only the returned observations.

## Required surfaces

```text
inspection/examples/iw-cross-system-falsifier-suite-v0.1.json
scripts/run_iw_cross_system_falsifier_suite.py
tests/test_iw_cross_system_falsifier_suite.py
.github/workflows/iw-matrix-falsifier-validation.yml
tasks/SDK-IW-CROSS-SYSTEM-FIXTURE-005.json
IW_CROSS_SYSTEM_FALSIFIER_MIRROR_HANDOFF.md
```

## Neutrality constraints

```text
fixture_is_execution_authority == false
sdk_runner_is_governance_authority == false
counterpart_result_must_be_independently_produced == true
counterpart_result_consumed_before_own_run == false
test_oracle_is_not_architecture_output == true
```

The fixture freezes the test conditions and oracle. Each architecture supplies its own observed Action outcomes. The SDK runner rejects altered arrival-order inputs rather than silently evaluating a different experiment.

## Test cases

### IW-FALSIFIER-001

Two runs use the same governed-input identity and candidate-set identity while reversing only arrival order. The test falsifies an architecture if the committed Action varies and order is not an explicit governed input.

### IW-FALSIFIER-002

The test declares A3 as the agreed unique matrix oracle for a case in which the coupled information exists within declared scope before the irreversible Action boundary. An architecture is falsified if its lane commits a different Action.

## Completion gates

```text
fixture: IMPLEMENTED
runner: IMPLEMENTED
focused tests: IMPLEMENTED / NOT YET HOSTED-VALIDATED
workflow integration: PENDING
merge: PENDING
external independent execution: PENDING / outside SDK-local source completion
```
