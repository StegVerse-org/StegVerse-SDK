# SDK Test One Manifest Builder Purpose Worker Handoff

Goal Task ID: `SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001`
Parent Goal Task ID: `SDK-TT-PURPOSE-BOUND-WORKER-CONSOLE-001`
COSV ID: `71000000111111`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `ACTIVE / MANIFEST-BUILDER INGRESS MERGED / AUTHENTIC RESIDENT PROOF PENDING`

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


## Manifest Builder Test One merge — 2026-09-19

SDK PR #276 merged as `a3a2039f907fe6499f32b79c7112c6be9495f5a4`.

Validated exact PR head: `572b91544ecf6ca5856fb7637db506c1b9bb5306`.

The dedicated `TT Purpose-Bound Worker Console Validation` run `35480600026` passed the actual evaluator-style console path:

```text
source-native evaluator input
-> stegverse manifest build
-> processing.capability=purpose_bound_worker
-> published installed route stegverse.route.purpose-bound-worker.v1
-> stegverse run-manifest
-> manifest-derived TT worker request
-> MATERIALIZED
-> INVOCATION_STARTED
-> TASK_COMPLETED
-> RETIRED
-> records_only=true
-> worker_live_after_close=false
```

Manifest Builder Source Validation `35480599985` and Evaluator Manifest Source Validation `35480599958` also passed at the same exact head.

This closes the SDK/source ingress defect identified during Test One preparation: the evaluator no longer supplies a separate worker request or uses the retired direct worker-lifecycle shortcut for this experiment. The manifest is the sole variable experiment input after builder construction. Authentic resident WorkerCoordinator claim/fence, TV/TVC warrant-policy, Interlock/InTr admission, StegAgents resident execution, and Master Records transition closures remain unpromoted until retained runtime receipts exist.
