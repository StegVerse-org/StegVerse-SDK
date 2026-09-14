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

## MIR PR #71 round-trip continuity

When the exact Publisher return contains `roundtrip_binding.profile = stegverse.publisher.mir-roundtrip-binding/v1`, `assemble_publisher_return()` requires the **original** `stegverse.sdk.downstream-completion-capsule/v1` as an independent input. The MIR return fails closed unless the Publisher-carried capsule exactly equals that original capsule and remains bound to the original admitted manifest.

The verifier independently requires:

- Goal Task ID `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`;
- COSV ID `50000000100000`;
- Publisher transition `PUBLISHER_ARTIFACT_RETURN_PRODUCED` with `publisher_transition_observed = true`;
- original manifest SHA-256 matching the capsule `manifest_hash`;
- original manifest `completion` object matching the capsule `completion` exactly;
- recomputed completion SHA-256 matching the capsule `completion_hash`;
- `response_to` and `retained_packet_sha256` matching the original capsule;
- the complete Publisher-carried downstream completion capsule matching the original SDK capsule exactly;
- carried SDK processor state `SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED` with `processor_result_observed = true`;
- Publisher return schema, source-export identity/hash, generation ID, and artifact-manifest SHA-256 matching the exact Publisher return envelope;
- all post-Publisher downstream predicates still false in the Publisher-carried binding;
- `authority_effect = NONE` throughout.

The resulting SDK object records `sdk_return_binding_observed = true` as the source-level return-assembly transition it represents, while final StegVerse egress, Interlock/InTr egress, far-side transition, authentic external MIR substitution, and communication completion remain false.

Legacy/non-MIR Publisher returns remain supported without a completion-capsule argument. Supplying only one side of the MIR pair (a Publisher round-trip binding without its original SDK capsule, or an SDK capsule without a Publisher round-trip binding) fails closed.

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
- `sdk_return_binding_observed = true`;
- for MIR returns, a deterministic `mir_roundtrip` summary binding the Publisher round-trip object and original SDK completion capsule;
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
authentic_external_mir_endpoint_substitution_observed = false
communication_complete = false
authority_effect = NONE
```

Any mutation attempting to promote those predicates is rejected by `verify_publisher_return_binding()`.

The next runtime owner is the manifest-declared final StegVerse-side egress surface. For framework paths that is the existing LLM Adapter exact-response egress path; no duplicate LLM Adapter or InTr transport is authorized by this module.

## Implementation

```text
stegverse/publisher_return_binding.py
tests/test_publisher_return_binding.py
docs/MIR_SDK_RETURN_ASSEMBLY_CONTINUITY_MIRROR_HANDOFF.md
```

Source validation does not prove Publisher runtime execution, SDK runtime assembly against a live MIR packet, LLM Adapter traversal, Interlock/InTr egress, far-side transition, authentic external MIR substitution, release, deployment, or communication completion.
