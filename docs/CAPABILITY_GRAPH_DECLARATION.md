# Manifest-declared capability graphs

## What this changes

`capability_resolution.classify_capability` resolves one capability against the
installed route table. `manifest_builder.build_manifest` then binds that single
capability through one branch of a fixed per-capability chain, and
`processing.capability` carries a scalar. A submitting framework that needs
several capabilities has no way to state that, and widening the reachable set
means editing the SDK rather than declaring anything.

`stegverse/capability_graph.py` lets the manifest declare the set. The
declaration names a root capability, every capability the submission needs, and
the `requires` edges between them:

```json
{
  "schema": "stegverse.capability-graph.v1",
  "graph_id": "acme-ingest-v1",
  "root_capability": "governance",
  "declared_capabilities": ["governance", "stegbrowser"],
  "requires": {"governance": ["stegbrowser"]}
}
```

`resolve_declared_capabilities` walks the closure from the root and classifies
every member through the existing `classify_capability`. The admitted set is
that closure and nothing wider.

## Declaration is not creation

A declaration cannot bring a capability into existence. Every member still has
to resolve to an installed route, and the SDK never substitutes one that does
not:

```text
every member ONLINE            -> DECLARED_CLOSURE_RESOLVED
any member unknown to the SDK  -> CLOSURE_MEMBER_UNKNOWN_CAPABILITY
                                  + one capability-development request per member
any member installed but down  -> CLOSURE_MEMBER_OFFLINE
```

The unknown case is the expansion path, and it reuses the contract that already
existed for a scalar capability: `capability_development_request` preserves the
original request, states `request_granted_authority: False`, and ends at
`RETRY_ORIGINAL_USER_MANIFEST_REQUEST`. An external framework declaring a
capability StegVerse has not built gets an obligation to build it, never an
admission.

## Declaring a capability does not declare what it needs

The closure walk is fail-closed in both directions, and both defects are
reported as verdicts a submitter can receipt rather than raised:

```text
requires reaches a capability the declaration omitted
  -> UNDECLARED_REQUIREMENT_REACHED
a declared capability the root never reaches
  -> DECLARED_CAPABILITY_NOT_REACHED_FROM_ROOT
requires edges form a cycle
  -> REQUIREMENT_CYCLE_DETECTED
```

The first is the separability invariant applied to capabilities: an admitted
capability never implies its components are admitted, so the edge has to be
declared, and the component has to resolve on its own. The second is the same
rule read the other way — excess declaration is a defect, so a submitter cannot
park an extra capability in the declaration and have the closure carry it in.

## Bound to the declaration that produced it

A resolution carries the declaration it was computed from:

```text
coverage.covers_graph_id
coverage.covers_root_capability
coverage.covers_declaration_sha256
```

so a closure resolved for one declaration is not a resolution for another, in
the same way a joint relation is bound to the composition it backs. Component
ids follow that convention too: member `c` of graph `G` is `"G:c"`, which is
what `closure_component_ids` returns, so a resolved closure can be handed to
composition coverage as a declared component set.

## Authority

Resolution is source-only and non-authorizing throughout
(`authority_effect: NONE_RESOLUTION_ONLY`):

```text
declaration_creates_capability: false
closure_membership_grants_execution: false
resolution_grants_authority: false
wider_closure_admits_undeclared_member: false
sdk_substitutes_unresolved_member: false
```

It installs nothing, binds no route, substitutes no route, and observes no
runtime. Route recognition stays with `MANIFEST_DECLARED_ROUTE_RESOLUTION`, and
transition authority stays with Interlock/InTr.

## Builder binding

`build_manifest(..., capability_graph=...)` is optional and additive, mirroring
`governance_reference_graph`. When supplied:

- the graph root must equal the declared `process`, or the call raises — the
  manifest may not declare two different things;
- an unresolved closure returns
  `state: CAPABILITY_CLOSURE_UNRESOLVED` and no manifest at all;
- a resolved closure is bound at `extensions.capability_graph`.

Omitting it leaves existing scalar behavior untouched.
