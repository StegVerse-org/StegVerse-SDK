# MIR Site SDK processing handoff mirror handoff

Updated: 2026-09-14
Goal Task ID: `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`
COSV ID: `50000000100000`
Source Site PR: `StegVerse-Labs/Site#1319`
Source Site merge: `StegVerse-Labs/Site@7c2d19649a8ad52520e45a76b4a0009a22f2e0df`
SDK prior processing merge: `StegVerse-org/StegVerse-SDK@745f3aa6564d497eb51e2ac36c2b611cd5a995a4`
Repair issue: `StegVerse-org/StegVerse-SDK#239`
SDK repair PR: `StegVerse-org/StegVerse-SDK#240`
SDK repair exact head validated: `4114b75727746a40ca43e7ab4040abf1d45b22ad`
SDK repair validation: `SDK Package Artifact Validation (Non-Authorizing) #192: SUCCESS`
SDK completion capsule merge: `StegVerse-org/StegVerse-SDK@233632c35b0093166c16bdc660aa08e4ee1fe95a`
SDK post-merge handoff reconciliation: `StegVerse-org/StegVerse-SDK@183bc5b3ebc66c3f13a433b6b004e92a2bc0f80c`
Status: `MERGED / SDK COMPLETION CAPSULE CARRY-FORWARD IMPLEMENTED VALIDATED MERGED / DOWNSTREAM PUBLISHER AND EGRESS REMAIN`

## Purpose

Consume the Site-emitted `stegverse.site.sdk-processing-handoff/v1` packet as the transition input for the SDK-owned manifest-selected processor path.

The Site handoff is a bridge from already-admitted Site return state to SDK processing. It carries the admitted manifest object, manifest hash, `response_to` correlation, `retained_packet_sha256`, retained packet schema, `STEGVERSE_RETURN_EXIT` receipt, `SDK_EVALUATOR_INGRESS_ADMITTED` state, and Node `EXTERNAL_COUNTERPART_RETURN_ADMITTED` receipt.

## Boundary

This SDK work does not create a MIR-specific processor, transport, scheduler, credential path, Publisher stage, SDK return binding, egress mechanism, Interlock/InTr egress, far-side final receipt, or authentic external MIR endpoint substitution.

## Implemented previously

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

## Completion-capsule carry-forward merge

Issue `#239` identified that the SDK processing result was not a sufficient downstream transition input because it did not carry the admitted manifest object or normalized completion block forward.

PR `#240` adds `stegverse.sdk.downstream-completion-capsule/v1` to the SDK processing result. The capsule carries:

- the admitted manifest object;
- normalized `completion` block;
- `manifest_hash` bound to the same complete manifest bytes;
- `completion_hash`;
- `response_to` correlation;
- `retained_packet_sha256`;
- derived downstream declarations: Publisher required/not required, Publisher package profile, final StegVerse-side egress surface, Interlock/InTr egress requirement, and far-side transition requirement;
- `authority_effect = NONE`.

Fail-closed validation rejects missing completion, mutated completion after hash binding, non-SOUTH completion direction, non-Publisher Publisher stage, non-boolean Publisher requirement, non-Interlock/InTr egress transport, or missing far-side transition requirement.

The exact head `4114b75727746a40ca43e7ab4040abf1d45b22ad` was validated by `SDK Package Artifact Validation (Non-Authorizing) #192: SUCCESS` and squash-merged as `233632c35b0093166c16bdc660aa08e4ee1fe95a`.

## Current transition truth

```text
Site-to-SDK handoff packet: implemented and merged from Site
SDK handoff validation: implemented and merged
SDK manifest-selected processing execution: implemented and merged
SDK admitted manifest/completion carry-forward: implemented, validated, and merged
Master Records custody/readback when requested: not claimed by this branch
Publisher transition when declared: not claimed by this branch
SDK return binding: not claimed by this branch
final StegVerse-side governed egress: not claimed by this branch
Interlock/InTr egress: not claimed by this branch
far-side final transition/caller receipt: not claimed by this branch
authentic external MIR endpoint substitution: not claimed by this branch
```

## Next after this merge

Continue to declared custody/Publisher and return/egress stages without creating MIR-specific mechanisms. For MIR completion manifests that declare `completion.publisher.required = true`, Publisher issue `GCAT-BCAT-Engine/Publisher#70` owns exact `stegverse.publisher.artifact-return/v1` production/binding before SDK return assembly.

## Task registry linkage

The canonical parent task remains `ACTIVE` under Site issue `#1277`. This SDK handoff records only the completed SDK carry-forward predicate. It does not close the parent task because Publisher artifact-return, SDK return binding, final StegVerse-side egress, Interlock/InTr egress, far-side final receipt, and authentic external MIR substitution remain unclaimed.
