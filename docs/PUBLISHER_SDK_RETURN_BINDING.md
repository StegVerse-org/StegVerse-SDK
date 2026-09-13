# Publisher -> SDK return binding

## Purpose

This contract implements the narrow SDK seam between an existing Publisher exact-byte artifact return and the manifest-declared final StegVerse-side egress transition.

It does not create a new Publisher format, a new transport, a new processor, or a new authority surface.

Canonical sequence:

```text
Publisher stegverse.publisher.artifact-return/v1
-> SDK exact-byte verification
-> bind to original manifest_receipt_id
-> bind to completion.initiator
-> bind to return_projection
-> bind to completion.egress
-> READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION
-> existing manifest-declared egress surface
-> Interlock/InTr
-> far-side transition
```

For external-framework paths the manifest-declared final StegVerse-side surface is normally `LLM_ADAPTER`. The binding layer does not invoke the LLM Adapter or Interlock/InTr itself.

## Reused Publisher contract

Publisher already returns canonical exact bytes under:

```text
stegverse.publisher.artifact-return/v1
```

The SDK verifies that return without importing or reimplementing Publisher execution. Required boundaries include:

- canonical JSON exact bytes;
- `authority_effect = NONE`;
- publication/release/execution authorization all false;
- each embedded artifact's decoded bytes match its declared SHA-256 and length;
- each artifact digest matches the Publisher artifact manifest.

Publisher therefore remains presentation/evidence assembly only.

## SDK binding object

`assemble_publisher_return()` emits:

```text
stegverse.sdk.publisher-return-binding/v1
```

The binding contains:

- original `manifest_receipt_id`;
- deterministic SHA-256 of the original admitted complete manifest supplied to assembly;
- exact `completion.initiator` identity/correlation;
- original `return_projection`;
- Publisher transfer/generation/source-export identities;
- SHA-256 of the exact Publisher return bytes;
- rendered artifact digest/length bindings;
- the manifest-declared final StegVerse-side egress surface;
- `INTERLOCK_INTR` transport requirement;
- `far_side_transition_required = true`;
- deterministic SDK binding digest.

## Fail-closed state boundary

Successful SDK assembly means only:

```text
READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION
```

The object is forced to retain:

```text
final_stegverse_transition_observed = false
interlock_intr_egress_observed = false
far_side_transition_observed = false
communication_complete = false
authority_effect = NONE
```

Any mutation attempting to promote those predicates is rejected by `verify_publisher_return_binding()`.

The next runtime owner is the manifest-declared final StegVerse-side egress surface. For framework paths that is the existing LLM Adapter exact-response egress path; no duplicate LLM Adapter or InTr transport is authorized by this module.

## Implementation

```text
stegverse/publisher_return_binding.py
tests/test_publisher_return_binding.py
```

Source validation does not prove Publisher runtime execution, SDK runtime assembly, LLM Adapter traversal, Interlock/InTr egress, or the far-side transition.
