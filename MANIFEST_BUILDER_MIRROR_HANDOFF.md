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

This scoped handoff records the completed user/framework-facing Manifest Builder over `stegverse.ingress-manifest.v1` and its validated compatibility with the processor-generic manifest correction.

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

The currently installed builder capability remains `governance`. The builder emits the caller-facing `processing` block separately from `extensions.stegverse_route`, verifies that the route registry binds that route to the selected processing capability, and validates output with the processor-generic `validate_ingress_manifest()` contract.

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

## Processor-generic correction completion

```text
correction_task: SDK-PROCESSOR-GENERIC-MANIFEST-002
PR: #126
validated_head: 771a28c7428c2adc92823b10f9bf031ecf2f710f
merge: cb53cb0304efbd21e5a5700677c4f3fb8ef7b874
builder source: COMPLETE_MERGED
builder tests: COMPLETE_VALIDATED
README: COMPLETE_MERGED
validation: PASS
manual user work: NONE
```

Correction validation:

```text
Manifest Builder Source Validation: 34280687649 SUCCESS
Evaluator Manifest Source Validation: 34280687697 SUCCESS
Evaluator Contract Console Validation: 34280687650 SUCCESS
SDK Package Artifact Validation: 34280687651 SUCCESS
builder tests: 5/5 PASS
processor-generic manifest tests: 8/8 PASS
wheel build/install/smoke: PASS
```

Correction assertions for the builder:

```text
build_manifest emits processing.capability=governance: PASS
build_manifest emits processing.route_id matching extensions.stegverse_route.route_id: PASS
installed route registry processor_capability must match requested process: PASS
builder uses processor-generic validate_ingress_manifest(): PASS
source-native payload remains unchanged at JSON value level: PASS
governance candidate remains sourced only from complete processor_request: PASS
missing governance evidence fails closed: PASS
return-depth aliases remain deterministic: PASS
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

The original builder task remains complete. The processor-generic correction is a separate completed workstream and does not reopen or erase that historical completion evidence.

## Current readiness

```text
SDK-MANIFEST-BUILDER-001: COMPLETE_VALIDATED_MERGED
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
current installed builder processing capability: governance
current downstream submission path: option 0B
additional processor capabilities installed by correction: NONE
new credential authority introduced: FALSE
new runtime authority introduced: FALSE
processor-generic correction merge state: COMPLETE
```

The SDK builder remains the simple user-facing façade while `stegverse.ingress-manifest.v1` is structurally processor-generic beneath it. Actual governance execution still depends on the complete governance request and existing sovereign runtime/custody path; the builder does not fabricate either.


## Manifest-time capability resolution — 2026-09-28

Manifest intake no longer equates "not installed" with terminal unsupported input. The requested processing capability is classified before route construction:

- ONLINE: installed admitted route exists; build the normal canonical manifest and continue to run-manifest.
- OFFLINE: capability is known but its route/runtime is unavailable; emit an active workaround-selection contract with solution_required=true and preserve the original processor request. This follows the ecosystem blocker-resolution invariant: unavailability is a solution-selection transition, not permission to wait.
- UNKNOWN_CAPABILITY: no known capability binding exists; emit a user-requested capability-development/deployment request that first discovers an existing equivalent, otherwise defines the capability/profile contract, develops it within existing SDK authority, validates/deploys it through existing release authority, and retries the original user request.

Classification and development requests grant no execution, credential, deployment, or transition authority. Actual deployment remains governed by the existing owners/TV-TVC/release path. The original user request is retained as the obligation being resolved.


## Customer-local and ecosystem-connected peer routes — 2026-10-04

The portability review demonstrated one bounded construction gap after the general customer-local route had already merged: the public Manifest Builder exposed only one governance route mapping even though two published governance routes serve different execution contexts.

The builder now exposes compatible governance routes as peers and accepts an explicit `execution_context`:

- `CUSTOMER_LOCAL -> stegverse.route.customer-local-governed.v1`
- `ECOSYSTEM_CONNECTED -> stegverse.route.canonical-governed.v1`

The CLI exposes the same contract as `stegverse manifest build --execution-context ...`. `ECOSYSTEM_CONNECTED` remains the backward-compatible default for existing callers; it is not a priority declaration. The selected route is retained identically in `processing.route_id` and `extensions.stegverse_route.route_id`. Both compatible routes are exposed in Manifest Builder evidence with `automatic_substitution_permitted=false`.

Route availability is independent. `runtime_installed` proves only that the SDK binding is installed. The builder records operational availability as requiring execution-context evidence rather than inferring it. Ecosystem unavailability therefore cannot silently become local execution, and local unavailability is not inferred from ecosystem state. Acquisition/download failure, package/install integrity failure, and installation-location unavailability remain evidence owned by their existing acquisition/install/location contracts; this builder creates no duplicate detector or availability authority.

Customer-local `run-manifest` still correctly fails closed with `CUSTOMER_LOCAL_HOST_BINDINGS_REQUIRED` unless the integrating customer supplies the independently trusted verifier, precommit recorder, bounded executor and result recorder through the existing programmatic customer-local runtime. No gateway, credential route, second SDK, hosted dependency, or authority plane is created.
