# SDK TT Purpose-Bound Worker Console Mirror Handoff

Goal Task ID: `SDK-TT-PURPOSE-BOUND-WORKER-CONSOLE-001`
Parent Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Repository: `StegVerse-org/StegVerse-SDK`
COSV ID: `71000000101111`
Status: `ACTIVE / HANDOFF CREATED / LOCAL CONSOLE IMPLEMENTATION IN PROGRESS`

## Objective

Demonstrate, through the public/local SDK console, the minimum source-level lifecycle in which one declared TT transition cell carries a bounded purpose, produces exactly one purpose-bound worker specification, invokes one arbitrary tracked local task, records ordered lifecycle evidence, retires the worker, and returns a records-only packet.

This lane is deliberately narrower than authentic StegOS/InTr runtime materialization. It tests the construction semantics and evidence shape without claiming live resident execution, credential issuance, or Interlock/InTr transition authority.

## Required demonstration

```text
single TT transition cell
-> declared purpose
-> required capability
-> purpose-bound worker specification
-> worker materialization event
-> bounded task invocation
-> task result
-> worker retirement event
-> records-only packet
```

The worker is not the durable object. The durable output is the transition/lifecycle evidence packet.

## Initial arbitrary task

Use a deterministic local task so the console test is independently reproducible without a hosted model or external provider:

```text
purpose: analyze a supplied text payload for a tracked integrity summary
capability: text.integrity_summary
result: SHA-256 + UTF-8 byte count + word count
```

The task is intentionally arbitrary. Its role is to prove lifecycle construction, invocation, ordering, and records-only decomposition rather than model intelligence.

## Required invariants

```text
purpose != authority
lineage != authority
worker materialization != execution success
execution success != continued authority
worker retirement removes live worker state
records-only packet retains no callable/executor object
unsupported capability fails closed
lifecycle ordering is explicit and hash-bound
local console proof != live StegOS/InTr runtime proof
```

## Console target

```bash
stegverse worker-lifecycle --input inspection/examples/tt-purpose-worker.example.json
```

The returned JSON must expose at minimum:

```text
transition_cell_hash
purpose
worker_spec
lifecycle_receipts
task_result
task_result_hash
records_only
worker_live_after_close
runtime_binding_state
authority_effect
```

Expected source/local values:

```text
records_only: true
worker_live_after_close: false
runtime_binding_state: LOCAL_SEMANTIC_DEMONSTRATION_ONLY
authority_effect: NONE
```

## Completion boundary

Source/local completion requires the console path, tests, README/console documentation, and this handoff to merge with exact-head validation.

Do not claim the full StegVerse worker-lifecycle problem solved from this test. Authentic proof still requires the existing live StegOS/InTr/runtime path to materialize and execute a bounded worker under current authority, retain authentic receipts, retire/transform it, and preserve/reconstruct the resulting history.

## Implementation checkpoint — 2026-09-18

The local source path is implemented on branch `sdk-tt-purpose-bound-worker-console-001` with:

```text
stegverse/purpose_bound_worker.py
tests/test_purpose_bound_worker_console.py
inspection/examples/tt-purpose-worker.example.json
stegverse worker-lifecycle --input ...
.github/workflows/tt-purpose-bound-worker-console.yml
```

The initial arbitrary tracked purpose uses `text.integrity_summary`. The worker is deterministically specified from the transition cell/purpose/capability, the task is invoked only after `MATERIALIZED`, the result is hash-bound, `RETIRED` is the terminal lifecycle receipt, and the returned object is a records-only packet with no live worker state.

This checkpoint remains unvalidated until exact-head console/unit CI passes and the implementation merges.


## Exact-head local-console validation — 2026-09-18

PR `#266` source head `802f9ce2c640f8b5b415645af9aed6a3b8d11c0c` passed dedicated workflow run `35384743742` / job `105728900561`.

Validated execution steps:

```text
python -m unittest tests.test_purpose_bound_worker_console -v: PASS
stegverse worker-lifecycle --input inspection/examples/tt-purpose-worker.example.json: PASS
records_only == true: PASS
worker_live_after_close == false: PASS
runtime_binding_state == LOCAL_SEMANTIC_DEMONSTRATION_ONLY: PASS
```

Adjacent SDK validation at the same head also passed Evaluator Contract Console, Manifest Builder, Evaluator Manifest, Structured Authority Basis, External Framework Public Submission, SDK Package Artifact, WorkSpace Active Probe, Shared Docs Provider Freeze, Publisher SDK Return Binding, External Collaboration Runtime Contract, and Portable Package Source lanes.

Evidence boundary remains unchanged: this is an authentic execution of the SDK local-console implementation, but not authentic resident StegOS/InTr worker materialization or a live AI-model inference run.
