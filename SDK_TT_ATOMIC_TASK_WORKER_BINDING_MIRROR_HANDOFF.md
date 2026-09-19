# SDK TT Atomic Task-Worker Binding Mirror Handoff

Updated: 2026-09-19
Goal Task ID: `SDK-TT-ATOMIC-TASK-WORKER-BINDING-001`
Parent Goal Task ID: `SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001`
COSV ID: `20010000110000`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `ACTIVE / CHECKED_OUT / TEST 2 SOURCE IMPLEMENTED VALIDATION PENDING`

## Objective

Provide an externally replayable semantic proof that, for the tested executable-task class, task activation and creation/binding of the task-specific worker are one constitutive transition.

```text
HANDOFF_READY task T + manifest-governed capability M
-> ACTIVATE(T)+CREATE_AND_BIND(W,T)
-> evidence closure
-> INVOCATION_STARTED
-> TASK_COMPLETED
-> CLOSE(T)+RETIRE(W,T)
-> records-only reconstruction
```

Test 1 remains unchanged.

## Positive invariants

The pre-state has T registered as HANDOFF_READY with no task-specific claim or worker instance. The constitutive transition simultaneously produces ACTIVE T, fresh deterministic claim/fence state, and newly created W with reciprocal `W.bound_task_id=T`. The manifest constrains capability and task-bound authority. Invocation chains to the constitutive receipt. The result remains bound to T/W. Closeout moves T to CLOSED and W to RETIRED with no continued task-bound authority and no callable/executor retained.

## Falsification cases

The SDK must fail closed for:

1. ACTIVE without worker.
2. Worker without ACTIVE task.
3. Mismatched reciprocal task/worker binding.
4. Pre-activation worker creation.
5. Invocation before combined transition closure.
6. Manifest capability/authority boundary violation.
7. Completed task with bound worker still live.
8. Records-only packet retaining executor/callable state.

## External replay

```bash
python -m unittest tests.test_atomic_task_worker_binding -v
stegverse task-worker-binding --input inspection/examples/tt-atomic-task-worker-binding.example.json
```

The fixture and hashing are deterministic. A later closeout must record the immutable merged source commit and exact expected hashes.

## Evidence boundary

This is a source/local semantic test only. It does not claim WorkerCoordinator, TV/TVC, Interlock/InTr, resident runtime, or Master Records execution. Those belong to the later authentic seam test.
