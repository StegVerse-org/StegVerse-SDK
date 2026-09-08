# Manifest Builder Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
branch: sdk-manifest-builder-001
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
workstream: SDK-MANIFEST-BUILDER-001
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This scoped handoff controls implementation of the user/framework-facing Manifest Builder over the already-merged generic `stegverse.ingress-manifest.v1` contract.

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

CLI target:

```bash
stegverse manifest build --input <source.json> --governance-request <request.json> --source-framework <name> --source-output-id <id> --return-depth result+evidence --output <manifest.json>
```

## Preflight

- Existing scoped handoff inspected: `GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md`.
- Existing builder implementation search: no canonical `build_manifest` / `manifest_builder` implementation found on `main`.
- Existing 0B route/runtime/schema reused; no duplicate evaluator or governance engine permitted.
- README impact: REQUIRED because this adds a public user-facing SDK construction interface and CLI capability. README must be updated in the same change set.
- `pyproject.toml` impact: REQUIRED only if a new console script is added; prefer integration under existing `stegverse` command to avoid redundant entry points.

## Completion predicates

```text
Python build_manifest API exists
CLI manifest build path exists
payload is preserved byte-equivalent at JSON value level
candidate is taken only from complete processor request
hashes are deterministic
installed route is selected explicitly
return-depth aliases map deterministically to canonical return_projection
built output passes validate_external_manifest()
missing processor evidence fails closed
README documents public usage
focused tests PASS
existing ingress/navigation tests PASS
PR merged to main
```
