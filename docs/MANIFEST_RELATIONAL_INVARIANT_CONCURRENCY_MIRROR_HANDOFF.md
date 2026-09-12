# Manifest relational invariant concurrency mirror handoff

Updated: 2026-09-11
Goal Task ID: `SDK-MANIFEST-RELATIONAL-INVARIANT-CONCURRENCY-004`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Issue: `StegVerse-org/StegVerse-SDK#215`
Status: `ACTIVE / DETERMINISTIC CONCURRENCY CONFORMANCE IMPLEMENTED / EXACT-HEAD VALIDATION PENDING`

## Goal

Verify an existing StegVerse manifest invariant rather than invent a new one:

> Before governance evaluation, the submitted manifest already declares/binds its source data and any governance-relevant source-native relationships it chooses to expose.

Universal InTr/SDK transport must preserve those manifested semantics without deriving relationships from arrival order, shared adapter use, common source framework, or concurrency.

## Canonical interpretation

Two simultaneous submissions from MIR are two distinct manifested governance objects even when they share:

- `source_framework = MIR`;
- one adapter family;
- one `processing.capability = governance`;
- one installed route;
- one Universal InTr transport protocol.

They remain distinct through their exact `source_output_id`, source-native payload or payload commitment, payload hash, candidate hash, canonical manifest hash, request identity, governance-state binding, and any relationship declarations already carried by the manifested source data.

```text
same transport protocol != same manifest
same source framework != same source output
same adapter family != same governance object
concurrent arrival != declared relationship
shared subject != inferred dependency
```

## Relationship custody

This task does not add a generic relationship ontology to `stegverse.ingress-manifest.v1`.

The generic ingress contract already preserves source-native semantic custody. A relational source may manifest its own relational representation inside the exact payload it submits. StegVerse binds and carries that source-native object unchanged into processor input; governance may evaluate a proposition about or in relation to that manifested data, but the SDK must not rewrite the source's relationship semantics.

A source-native relationship mutation therefore changes the committed payload and canonical manifest identity. It cannot silently alias the original manifested request.

## Deterministic concurrency fixture

`tests/test_manifest_relational_invariant_concurrency.py` creates two MIR-like manifests that share the same framework, adapter/processor class, and installed route while declaring different source outputs and different source-native relationships.

The suite verifies:

1. both manifests may be converted concurrently;
2. both resolve through the same installed governance route;
3. each retains a distinct source output ID;
4. each retains a distinct canonical manifest hash and request ID;
5. each retains its own governance state-binding hash;
6. exact source data and relationship declarations survive conversion into `input.input_data.payload` unchanged;
7. a manifest with no declared relationship remains relation-empty even while processed concurrently with a related manifest;
8. changing a relationship changes payload commitment, canonical manifest identity, and request identity;
9. reversing arrival order does not change either manifest's semantics or request identity.

## Boundary

These tests prove deterministic source-preservation/concurrency behavior in the SDK conversion layer only. They do not prove:

- authentic sovereign concurrent execution;
- an MIR production connection;
- an InTr resident dispatcher handling ten live connections simultaneously;
- any governance result;
- any credential, runtime, custody, or transition authority from CI.

The next runtime-facing layer should preserve the same invariant when multiple manifested requests are staged and admitted through Universal InTr.

## Completion predicates

- [x] existing invariant identified without schema reinvention;
- [x] MIR-like concurrent fixture implemented;
- [x] source-native relationships preserved unchanged;
- [x] no relationship inferred from concurrency;
- [x] relationship mutation changes exact manifested identity;
- [x] arrival-order independence asserted;
- [ ] exact-head dedicated CI PASS;
- [ ] SDK package validation PASS;
- [ ] merge;
- [ ] Site Interlock/InTr documentation cross-reference updated as a separate bounded follow-up if needed.
