# SDK Test One Manifest Builder Purpose Worker Handoff

Goal Task ID: `SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001`
Parent Goal Task ID: `SDK-TT-PURPOSE-BOUND-WORKER-CONSOLE-001`
COSV ID: `71000000111111`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `ACTIVE / MANIFEST-BUILDER INGRESS REPAIR`

## Objective

Make Test One enter the SDK exactly like an ordinary manifested evaluator test. The evaluator supplies source-native input and a processor request to the existing Manifest Builder. The builder emits the canonical `stegverse.ingress-manifest.v1`, selects the published `purpose_bound_worker` route, and the SDK executes only the runtime binding declared by that validated route.

No direct `worker-lifecycle --input` request is authoritative for this experiment. No second worker-request file is accepted by the processor. The canonical TT worker request is derived from the validated manifest.

## Test One definition

One purpose-bound worker, one compute unit, derived maximum lifetime 15 seconds:

```text
expected_task_execution          6
known_delay                      1
inferred_unknown_delay_reserve   2
records_decomposition            3
safety_reserve                   3
----------------------------------
derived maximum lifetime        15
```

Purpose completion may retire the worker earlier.

## Evaluator console path

```bash
stegverse manifest build \
  --input inspection/examples/sdk-test1-source.json \
  --processor-request inspection/examples/sdk-test1-purpose-worker.processor-request.json \
  --source-framework external_evaluator \
  --source-output-id sdk-test-one-001 \
  --process purpose_bound_worker \
  --return-depth full-trace \
  --output /tmp/sdk-test1.manifest.json

stegverse run-manifest \
  --manifest /tmp/sdk-test1.manifest.json \
  --output /tmp/sdk-test1.result.json
```

The first command is the sole construction path. The second command validates that manifest, resolves its published installed route, and invokes only the declared runtime binding.

## Evidence boundary

This SDK branch proves manifest-driven construction and SDK processor execution. It does not by itself promote authentic WorkerCoordinator, TV/TVC, Interlock/InTr, resident StegAgents, or canonical Master Records runtime predicates. Those remain owned by the active runtime-proof goal and must be promoted only from authentic retained receipts.
