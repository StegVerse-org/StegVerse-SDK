# Manifest Builder Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
workstream: SDK-MANIFEST-BUILDER-001
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This scoped handoff records the completed user/framework-facing Manifest Builder over the merged generic `stegverse.ingress-manifest.v1` contract.

## Goal

Provide a convenience layer that accepts source-native data, a selected installed processing class, and a desired return depth, then constructs and validates a canonical ingress manifest without changing source semantics or inventing processor-specific governance evidence.

## Required invariants

```text
source payload semantic custody remains external
payload class != processing class
builder construction != governance decision
builder validation != authority
missing governance evidence is never synthesized
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
-> existing option 0B ingress/runtime
```

Primary CLI:

```bash
stegverse manifest build --input <source.json> --governance-request <request.json> --source-framework <name> --source-output-id <id> --return-depth result+evidence --output <manifest.json>
```

## Preflight determination

- Existing scoped handoff inspected: `GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md`.
- Existing builder implementation search found no canonical `build_manifest` / `manifest_builder` implementation on `main` before this workstream.
- Existing 0B route/runtime/schema reused; no duplicate evaluator or governance engine introduced.
- README impact was REQUIRED because this adds a public user-facing SDK construction interface and CLI capability; README was updated in the same change set.
- No new console-script entry point was needed; the builder is integrated under the existing `stegverse` command.

## Implemented files

```text
stegverse/manifest_builder.py
stegverse/evaluator_console.py
tests/test_manifest_builder.py
tests/test_governance_navigation.py
README.md
.github/workflows/manifest-builder-source-validation.yml
MANIFEST_BUILDER_MIRROR_HANDOFF.md
tasks/SDK-MANIFEST-BUILDER-001.json
StegVerse-Labs/.github:control/task-vectors/SDK-MANIFEST-BUILDER-001.json
```

The navigation-test change is a whitespace-insensitive assertion correction for an already-valid wrapped guidance sentence; it changes no runtime or governance semantics.

## Completion evidence

```text
PR: #125
merge: f2d85e17ca50146f4234585561868d5b8818d1a4
validated head: 59cd46dab52aa73293fd60d34b15ab08eb21299a

Manifest Builder Source Validation (Non-Authorizing)
run: 34278909616
job: 102238648212
result: SUCCESS
builder tests: 5/5 PASS
canonical ingress compatibility tests: PASS

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

An initial focused run exposed an unrelated brittle whitespace assertion in `tests.test_governance_navigation`; the assertion was corrected to normalize wrapped whitespace, then the complete focused validation passed. No production source behavior was changed to mask that test failure.

## COSV registration

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

The vector follows the canonical `task.v1` position order `L R U I V G O C M T B E A P` and is evidence-bound to this completed workstream.

## Completion predicates

```text
Python build_manifest API exists: PASS
CLI manifest build path exists: PASS
payload preserved at JSON value level: PASS
candidate taken only from complete processor request: PASS
hashes deterministic: PASS
installed route selected explicitly: PASS
return-depth aliases deterministic: PASS
built output passes validate_external_manifest(): PASS
missing processor evidence fails closed: PASS
README documents public usage: PASS
focused tests: PASS
existing ingress/navigation tests: PASS
package artifact build/install/smoke: PASS
PR merged to main: PASS
COSV registered: PASS
```

## Current readiness

```text
SDK-MANIFEST-BUILDER-001: COMPLETE_VALIDATED_MERGED
current installed builder processing class: governance
current downstream submission path: option 0B
additional processor classes installed by this workstream: NONE
new credential authority introduced: FALSE
new runtime authority introduced: FALSE
```

The SDK is ready for an external framework to build a source-native manifest with `build_manifest(...)` or `stegverse manifest build ...`, then submit that output through the existing governed 0B path. Actual governance execution still depends on the complete processor-specific governance request and the existing sovereign runtime/custody path; the builder does not fabricate either.
