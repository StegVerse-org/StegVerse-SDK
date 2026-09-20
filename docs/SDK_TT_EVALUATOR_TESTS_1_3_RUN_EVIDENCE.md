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

## Evaluator identity and interface

The evaluator for Tests 1-3 is Rigel Randolph. Because the evaluator is operating from an iPhone and does not have a practical local console surface, ChatGPT operated the SDK interface on the evaluator's behalf. The evidentiary role is therefore evaluator-directed SDK interaction, not an independent third-party evaluator and not GitHub Actions acting as evaluator.

The interface used must remain exactly within the public SDK surface that the evaluator could invoke from a conventional console. ChatGPT may enter commands and retrieve outputs on the evaluator's behalf, but may not substitute internal resident scripts, private acceptance runners, hidden parameters, privileged repository-only entrypoints, or other execution paths unavailable at the SDK interface.

All three tests were executed using only the same public SDK pattern presented to the evaluator:

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

## Screenshot and visual-evidence contract

The subsequent evidence publication must show only pertinent SDK-interface screenshots from the evaluator-directed run. Required views are the exact stages that matter to understanding and independently checking the test: source-native input, processor request / preregistered expectations, completed manifest, resolved route or processing declaration, run-manifest invocation, returned result, ordered lifecycle receipts, terminal records-only / retired state, and retained artifact or provenance identity where pertinent.

Generic CI dashboards, decorative diagrams, unrelated repository pages, or substitute screenshots are not evidence views for these tests. If a contemporaneous interface screenshot is unavailable and a view is reconstructed from exact retained JSON, it must be explicitly labeled as a post-run reconstructed evidence view and must reproduce only the retained artifact content without adding inferred transitions or states.

## Evidence boundary

This file records evaluator-directed SDK runs and the artifacts returned to Rigel Randolph as evaluator. ChatGPT operated the console/interface on the evaluator's behalf because of the evaluator's iPhone-only constraint. GitHub Actions provided execution/validation transport for the SDK commands; it was not the evaluator and does not become StegVerse transition authority. The evidentiary claim is exactly that the evaluator-directed use of the installed SDK surface can build and run these manifests through the public Manifest Builder and generic manifest executor.

The retained manifest/result artifacts and exact pertinent SDK-interface captures are the source material for the subsequent ELAN-style visual evidence documentation.
