# MIR Site SDK processing handoff mirror handoff

Updated: 2026-09-14
Goal Task ID: `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`
COSV ID: `50000000100000`
Source Site PR: `StegVerse-Labs/Site#1319`
Source Site merge: `StegVerse-Labs/Site@7c2d19649a8ad52520e45a76b4a0009a22f2e0df`
SDK branch: `mir-site-sdk-handoff-processing`
Status: `ACTIVE / SDK MANIFEST-SELECTED PROCESSING BINDING OPEN`

## Purpose

Consume the Site-emitted `stegverse.site.sdk-processing-handoff/v1` packet as the transition input for the SDK-owned manifest-selected processor path.

The Site handoff is a bridge from already-admitted Site return state to SDK processing. It carries the admitted manifest object, manifest hash, `response_to` correlation, `retained_packet_sha256`, retained packet schema, `STEGVERSE_RETURN_EXIT` receipt, `SDK_EVALUATOR_INGRESS_ADMITTED` state, and Node `EXTERNAL_COUNTERPART_RETURN_ADMITTED` receipt.

## Boundary

This SDK work does not create a MIR-specific processor, transport, scheduler, credential path, Publisher stage, SDK return binding, egress mechanism, Interlock/InTr egress, far-side final receipt, or authentic external MIR endpoint substitution.

## Implemented on branch

`stegverse/site_sdk_processing_handoff.py` validates the Site handoff and binds its admitted manifest into the existing manifest-selected SDK route/runtime path.

Validation requires:

- schema `stegverse.site.sdk-processing-handoff/v1`;
- authority effect `NONE`;
- admitted manifest object;
- manifest hash matching the supplied manifest;
- stable `response_to` correlation;
- retained packet hash and retained packet wrapper schema;
- `STEGVERSE_RETURN_EXIT` receipt bound to the same manifest hash and `response_to`;
- `SDK_EVALUATOR_INGRESS_ADMITTED` state;
- Node `EXTERNAL_COUNTERPART_RETURN_ADMITTED` receipt when present;
- next transition `EXECUTE_MANIFEST_SELECTED_SDK_PROCESSING_AFTER_EVALUATOR_INGRESS`.

`execute_site_sdk_processing_handoff(...)` then calls the existing SDK `run_external_manifest(...)` path. That path resolves the manifest-selected route through `external_manifest_to_public_request(...)` and executes the selected runtime binding. Processing selection grants no authority.

## Current transition truth

```text
Site-to-SDK handoff packet: implemented on SDK branch
SDK handoff validation: implemented on SDK branch
SDK manifest-selected processing execution: implemented on SDK branch, pending PR validation/merge
Master Records custody/readback when requested: not claimed by this branch
Publisher transition when declared: not claimed by this branch
SDK return binding: not claimed by this branch
final StegVerse-side governed egress: not claimed by this branch
Interlock/InTr egress: not claimed by this branch
far-side final transition/caller receipt: not claimed by this branch
authentic external MIR endpoint substitution: not claimed by this branch
```

## Next after this branch

After validation and merge, reconcile the parent MIR handoff and canonical task record to mark only SDK manifest-selected processing from the Site handoff as implemented/validated/merged. Then continue to declared custody/Publisher and return/egress stages without creating MIR-specific mechanisms.
