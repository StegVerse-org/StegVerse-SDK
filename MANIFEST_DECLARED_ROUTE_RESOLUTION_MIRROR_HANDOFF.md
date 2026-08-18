# Manifest-Declared Route Resolution Mirror Handoff

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
canonical_branch: main
credential_authority: TV/TVC
GitHub runtime authority: NONE
person-specific route: NONE
```

## Goal

A preformatted `stegverse.ingress-manifest.v1` establishes its intended route. SDK validation must recognize that route, reject unsupported/uninstalled/conflicting declarations, bind the governance-relevant system state to the resolved route, and execute through that route without silently substituting another route.

## Installed contract

The 0B manifest declares its route at:

```text
extensions.stegverse_route
```

Current installed route identifier:

```text
stegverse.route.canonical-governed.v1
```

The declaration contains the exact published route tuple:

```text
route_id
lane_class
routing_surface
containment
sandbox_required
external_consequence_enabled
```

Current executable canonical tuple:

```text
route_id: stegverse.route.canonical-governed.v1
lane_class: PRODUCTION_VALIDATION
routing_surface: CANONICAL_PRODUCTION
containment: PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE
sandbox_required: false
external_consequence_enabled: false
```

Resolution behavior:

```text
recognized + installed + exact tuple -> RESOLVE
unknown route_id -> REJECT
known route with conflicting tuple -> REJECT
published route without installed runtime binding -> REJECT
missing 0B route declaration -> REJECT
route substitution -> PROHIBITED
```

`stegverse/route_resolution.py` owns evaluator-neutral route recognition. The registry currently exposes only the route whose runtime binding is installed. Adding a future route requires an explicit published tuple plus installed runtime binding; a manifest cannot create one dynamically.

## State binding

The route resolver binds the governance-relevant state carried by the submitted canonical StegGate request. The state-binding digest covers:

```text
candidate
judgment
signal
execution
capability
continuity
approval
permission_present
```

Non-decision `declared_context` additions do not alter the governance-state digest.

The accepted 0B public request carries:

```text
execution_provenance.route_id
execution_provenance.route_declaration_hash
execution_provenance.state_binding_hash
input.route_binding
```

The sovereign runtime independently re-resolves the declared route and recomputes the state-binding hash before execution. A mismatch fails closed.

## Execution and retained evidence

For the currently installed route, successful resolution selects the existing `core_lite.default_validation_route` runtime binding. The runtime does not choose that route merely because it is the default; it selects it only after the manifest declaration resolves to the published route that owns that binding.

Retained exact-run metadata/result surfaces include:

```text
declared_route_id
route_declaration_hash
state_binding_hash
route_substitution_permitted: false
route_substitution_occurred: false
```

The route identity/state binding are retained in StegCore transaction metadata and exact-run route linkage without creating route, custody, release, or execution authority.

## Backward compatibility

Existing 0A public-inspection requests may omit `route_id` because older request files already declare the route tuple through `execution_provenance`. The runtime accepts that legacy representation only when the tuple resolves uniquely to one published installed route. Ambiguous or unmatched tuples fail closed.

External 0B manifests do not receive that compatibility shortcut: they must explicitly declare the route under `extensions.stegverse_route`.

## Implementation

```text
PR: #49
merge: dc2da6dc4ff079f48dfee92dd9fe3f488f3409ac
route resolver: stegverse/route_resolution.py
0B binding: stegverse/governance_ingress_runtime.py
runtime enforcement: stegverse/sovereign_validation_runtime.py
public request validation: stegverse/public_inspection.py
request schema: inspection/request.schema.json
focused tests: tests/test_route_resolution.py
focused ingress tests: tests/test_governance_ingress_runtime.py
```

## Validation

Exact PR head:

```text
6c5f545bdda307a0355c615737694e043a40b6fc
```

Non-authorizing source validation:

```text
Evaluator Manifest Source Validation
run: 32195184770
result: SUCCESS

MCP Source Validation
run: 32195184754
result: SUCCESS
```

The evaluator-manifest lane validates route-resolution tests, 0B ingress tests, existing public-inspection bindings, CLI ingress, evaluator-boundary behavior, and module compilation. These source checks do not constitute external-run, release, custody, or evaluator authority.

## Status

```text
manifest-declared route recognition: COMPLETE_VALIDATED_MERGED
unsupported/conflicting route rejection: COMPLETE_VALIDATED_MERGED
governance-state route binding: COMPLETE_VALIDATED_MERGED
runtime route re-resolution: COMPLETE_VALIDATED_MERGED
silent route substitution: PROHIBITED_AND_TESTED
external exact-run evidence: PRODUCED_WHEN_AN_EXTERNAL_MANIFEST_IS_RUN
release/tag state: SEPARATE_FROM_INGRESS_SOURCE_COMPLETION
```

No external evaluator-specific route, processor, capability, or repository identifier was introduced.
