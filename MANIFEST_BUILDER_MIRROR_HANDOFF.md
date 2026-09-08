# Manifest Builder Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
workstream: SDK-MANIFEST-BUILDER-001
processor_generic_correction: SDK-PROCESSOR-GENERIC-MANIFEST-002
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This scoped handoff records the completed user/framework-facing Manifest Builder over `stegverse.ingress-manifest.v1` and its compatibility with the processor-generic manifest correction.

## Goal

Provide a convenience layer that accepts source-native data, a selected installed processing capability, complete processor-specific evidence for that capability, and a desired return depth, then constructs and validates a canonical ingress manifest without changing source semantics or inventing processor-specific evidence.

## Required invariants

```text
source payload semantic custody remains external
payload class != processing capability
processing capability != runtime route
builder construction != governance decision
builder validation != authority
missing processor evidence is never synthesized
return depth != canonical custody depth
GitHub runtime authority: NONE
credential authority: TV/TVC
```

## User contract

```text
source data + source identity
+ processing="governance"
+ complete processor_request
+ return_depth=(result-only | result+evidence | full-trace | locator-only)
-> build_manifest(...)
-> canonical stegverse.ingress-manifest.v1
-> processing.capability + processing.route_id
-> existing option 0B ingress/runtime
```

Primary CLI:

```bash
stegverse manifest build --input <source.json> --governance-request <request.json> --source-framework <name> --source-output-id <id> --return-depth result+evidence --output <manifest.json>
```

The currently installed builder capability remains `governance`. The builder now emits the caller-facing `processing` block separately from `extensions.stegverse_route`, verifies that the route registry binds that route to the selected processing capability, and validates output with the processor-generic `validate_ingress_manifest()` contract.

## Original completion evidence — SDK-MANIFEST-BUILDER-001

```text
PR: #125
merge: f2d85e17ca50146f4234585561868d5b8818d1a4
validated head: 59cd46dab52aa73293fd60d34b15ab08eb21299a

Manifest Builder Source Validation (Non-Authorizing)
run: 34278909616
job: 102238648212
result: SUCCESS
builder tests: 5/5 PASS

Evaluator Manifest Source Validation (Non-Authorizing)
run: 34278909631
result: SUCCESS

Evaluator Contract Console Validation
run: 34278909777
result: SUCCESS

SDK Package Artifact Validation (Non-Authorizing)
run: 34278909861
result: SUCCESS
wheel build/install/smoke test: PASS
```

## Processor-generic correction state

```text
correction_task: SDK-PROCESSOR-GENERIC-MANIFEST-002
branch: fix/processor-generic-manifest-contract
builder source: UPDATED_ON_BRANCH
builder tests: UPDATED_ON_BRANCH
README: UPDATED_ON_BRANCH
validation: PENDING_PR
merge: PENDING
manual user work: NONE
```

Correction assertions for the builder:

```text
build_manifest emits processing.capability=governance
build_manifest emits processing.route_id matching extensions.stegverse_route.route_id
installed route registry processor_capability must match requested process
builder uses processor-generic validate_ingress_manifest()
source-native payload remains unchanged at JSON value level
governance candidate remains sourced only from complete processor_request
missing governance evidence fails closed
return-depth aliases remain deterministic
builder grants authority: FALSE
```

## COSV registration — original builder task

```text
COSV profile: task.v1
COSV vector: 71000000100110
registry: StegVerse-Labs/.github/control/task-vectors/SDK-MANIFEST-BUILDER-001.json
canonical task record: tasks/SDK-MANIFEST-BUILDER-001.json
lifecycle: COMPLETE
archive_ready: TRUE
unassigned_work: 0
blockers: 0
evidence_complete: TRUE
activated: TRUE
propagated: FALSE
```

The original builder task remains complete. The processor-generic correction is a separate workstream and does not reopen or erase that historical completion evidence.

## Current readiness

```text
SDK-MANIFEST-BUILDER-001: COMPLETE_VALIDATED_MERGED
current installed builder processing capability: governance
current downstream submission path: option 0B
additional processor capabilities installed by correction: NONE
new credential authority introduced: FALSE
new runtime authority introduced: FALSE
processor-generic correction merge state: PENDING
```

After `SDK-PROCESSOR-GENERIC-MANIFEST-002` validates and merges, the SDK builder remains the simple user-facing façade while `stegverse.ingress-manifest.v1` becomes structurally processor-generic beneath it. Actual governance execution still depends on the complete governance request and existing sovereign runtime/custody path; the builder does not fabricate either.
