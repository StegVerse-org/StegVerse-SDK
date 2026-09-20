# SDK Evaluator Tests 1-3 — Run Evidence

## Evidence identity

- PR: #278
- Validated exact head: `58bd1ba4413fb04877e59ad0b1b262dfea688314`
- Merge commit: `88805e46e7764da7083402a3515066c4e50de000`
- Workflow: `TT Evaluator Manifest Tests 1-3`
- Workflow run: `35481650008`
- Retained artifact: `sdk-evaluator-tests-1-3-evidence`
- Artifact ID: `10595688669`
- Artifact ZIP SHA-256: `01e0bbb2fb6397c00dac8d5ae286af7e7f333c86de47c50e41f8f23c6f9b4f56`
- Retained files: three canonical manifests + three returned results.

## Evaluator contract

All three tests were executed using only the same public SDK pattern available to an evaluator:

```text
source-native JSON
+ processor-request JSON
-> stegverse manifest build
-> canonical stegverse.ingress-manifest.v1
-> stegverse run-manifest
-> result JSON
```

No direct worker CLI, GitHub-internal acceptance runner, resident control script, second-device path, hidden runtime parameter, or task-specific privileged invocation was part of the evaluator test sequence.

The source-native payload is supplied through Manifest Builder input. Processor requests declare processing semantics and preregistered evidence expectations; they do not duplicate the source payload.

## Reuse

Test 1 uses the installed `purpose_bound_worker` manifest processor.

Tests 2 and 3 reuse the same installed `atomic_task_worker` manifest processor and differ only in their evaluator-declared scenario and preregistered expectation.

All three use the same generic `stegverse run-manifest` dispatcher, which resolves the installed runtime binding from the validated manifest route.

## Test 1

Processor: `purpose_bound_worker`

Command shape:

```text
stegverse manifest build --input <source> --processor-request <test1-request> --process purpose_bound_worker --return-depth full-trace --output <manifest>
stegverse run-manifest --manifest <manifest> --output <result>
```

Observed assertions:

- preregistered evidence expectations satisfied
- no missing expected evidence fields
- lifecycle: `MATERIALIZED -> INVOCATION_STARTED -> TASK_COMPLETED -> RETIRED`
- records-only final packet: true
- worker live after close: false

Console marker: `SDK_TEST1_EVALUATOR_MANIFEST_PASS`

## Test 2

Processor: `atomic_task_worker`

Scenario: `TEST_2_ATOMIC_TASK_WORKER_BINDING`

Observed assertions:

- preregistered evidence expectations satisfied
- constitutive transition: `ACTIVATE_TASK_AND_CREATE_BIND_WORKER`
- invocation follows constitutive transition
- task result bound to the same task/worker lineage
- terminal transition: `CLOSE_TASK_AND_RETIRE_WORKER`
- records-only final packet: true
- worker live after close: false

Console marker: `SDK_TEST2_EVALUATOR_MANIFEST_PASS`

## Test 3

Processor: `atomic_task_worker`

Scenario: `TEST_3_RICHARD_SHORT_LIVED_ACTOR_SEAM`

Observed assertions:

- same evaluator-visible SDK path as Test 2
- preregistered evidence expectations satisfied
- same constitutive task/worker transition family
- records-only final packet: true
- worker live after close: false
- continued task-bound authority after retirement: false

Console marker: `SDK_TEST3_EVALUATOR_MANIFEST_PASS`

## Evidence boundary

This file records the completed evaluator-visible SDK runs and the artifacts they returned. It does not convert GitHub Actions into StegVerse runtime authority and does not claim a hidden resident execution path. The evidentiary claim is exactly that an evaluator using the installed SDK surface can build and run these manifests through the same public Manifest Builder and generic manifest executor.

The retained manifest/result artifacts are the source material for the subsequent ELAN-style visual evidence documentation.
