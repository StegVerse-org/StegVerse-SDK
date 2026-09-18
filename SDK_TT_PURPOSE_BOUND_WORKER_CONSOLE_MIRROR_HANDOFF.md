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
