# External Collaboration Authentic Runtime Proof Contract

Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`  
COSV ID: `71000000100110`  
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`  
WorkSpace handoff: `docs/SHARED_DOCS_EPHEMERAL_MANIFEST_WORKSPACE_MIRROR_HANDOFF.md`

## Purpose

This contract defines the minimum evidence required to promote the merged external-collaboration source chain from source/CI proof to authentic provider-runtime proof. It does not itself activate credentials, assert owner consent, assign WorkSpace readiness, or substitute repository evidence for provider execution.

## Required authentic evidence

A qualifying proof bundle MUST bind all of the following to one execution lineage:

1. owner-present consent/session evidence for credential class `TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001` and purpose `EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY`;
2. the dedicated vault provider slot `google_drive_external_collaboration` and vault ref `vault://tvc/providers/google-drive/external-collaboration-session` without exporting credential material;
3. a fresh `wsprobe_*` binding, exact provider file ID, and exact active-probe reason/digest;
4. the single-use TVC lease and durable pre-provider replay-consumption evidence;
5. an authentic metadata-only/read-only provider response for the bound external file;
6. the secret-free TVC result and durable broker use receipt;
7. SDK bridge output showing evidence normalization only, with no readiness assignment;
8. active-probe engine output showing readiness was recomputed from complete predicate state;
9. state-transition evidence for `OBSERVE -> MATERIALIZE -> REFRESH`, followed by authorization/probe change and `REVOKE` or `EXPIRE`, then `DESTROY`;
10. MIR transition reporting and independent Master Records custody/reconstruction evidence;
11. one-current-device continuity evidence for the complete execution lineage.

## Required negative assertions

The proof bundle MUST demonstrate:

- Personal-KV authorization was not reused as external-collaboration consent.
- No provider credential, refresh token, access token, token hash, or equivalent secret was returned to the browser, SDK, evidence artifact, or GitHub.
- Provider mutation authority was not granted or exercised.
- Provider/TVC/broker output did not assign WorkSpace readiness.
- Caller assertions did not directly transition `PROBE_REQUIRED` to `READY`.
- A consumed lease could not be replayed after a failed, uncertain, or completed provider invocation.
- Repository/CI success was not used as a substitute for owner-present authorization or provider execution.

## Completion rule

Authentic external-collaboration provider proof is satisfied only when the evidence above is retained and independently reconstructable. Until then, the canonical status remains `AUTHENTIC OWNER-PRESENT EXECUTION / PROVIDER PROBE NOT PROVEN`.

This document is an evidence contract only. It carries `authority_effect: NONE`.
