# External Collaboration Authentic Runtime Proof Contract

Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`  
COSV ID: `71000000100110`  
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`  
WorkSpace handoff: `docs/SHARED_DOCS_EPHEMERAL_MANIFEST_WORKSPACE_MIRROR_HANDOFF.md`

## Purpose

This contract defines the minimum evidence required to promote the merged external-collaboration source chain from source/CI proof to authentic resident/provider-runtime proof. It does not itself activate credentials, assert owner consent, assign WorkSpace readiness, or substitute repository evidence for resident/provider execution.

## Required authentic pre-consent evidence

A qualifying proof bundle MUST first bind all of the following to the same resident lineage before owner-present external-collaboration consent is attempted:

1. authorized-resident source custody for the already-sealed Personal-KV Google client-secret object, without exposing plaintext or a secret-derived hash;
2. current resident-seal activation/liveness plus the resident private-key availability required by the TV/TVC reseal source;
3. the exact resident reseal request `RESIDENT-EXEC-SDK-WORKSPACE-EXTCOLLAB-CLIENT-SECRET-RESEAL-001` and selector `sdk_workspace_external_collab_client_secret_reseal` as consumed by the existing sovereign resident dispatcher;
4. authentic resident consumption evidence at `receipts/sovereign-host/sdk-workspace-external-collab-client-secret-reseal.latest.json` showing `COMPLETED` or `TARGET_ALREADY_PRESENT`; `BLOCKED`, source merge, CI, or dispatcher registration alone is not custody proof;
5. exact target ciphertext custody/readback for SKAP purpose `google_drive.external_collaboration.client_secret`, with no target overwrite when custody already exists;
6. the canonical sovereign public ingress `https://stegverse.org/v1/skap/google-drive/external-collaboration/client-secret/ingress` bound through the existing Service Gateway owner and canonical resident InTr carrier to the exact loopback receiver, with `third_party_tunnel_runtime_required: false`;
7. resident callback/listener health and reachability for `https://stegverse.org/tvc/google-drive/external-collaboration/callback` before any owner-present authorization begins.

These predicates are ordered prerequisites. A public route, source file, merge, test, or provider-independent readiness observation may not be promoted into proof of resident client-secret custody or callback reachability.

## Required authentic provider evidence

Only after the pre-consent evidence above is satisfied, a qualifying proof bundle MUST bind all of the following to the same execution lineage:

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
- Personal-KV client-secret custody was not directly reused as external-collaboration client-secret custody; any target purpose materialization used the governed purpose-specific reseal or the exact governed ingress path.
- No provider credential, OAuth client secret, refresh token, access token, token hash, client-secret hash, or equivalent secret was returned to the browser, SDK, evidence artifact, or GitHub.
- No third-party tunnel runtime was required to establish the sovereign client-secret ingress or callback route.
- Provider mutation authority was not granted or exercised.
- Provider/TVC/broker output did not assign WorkSpace readiness.
- Caller assertions did not directly transition `PROBE_REQUIRED` to `READY`.
- A consumed lease could not be replayed after a failed, uncertain, or completed provider invocation.
- Repository/CI success was not used as a substitute for resident custody, callback reachability, owner-present authorization, or provider execution.

## Completion rule

Authentic external-collaboration provider proof is satisfied only when the full pre-consent and provider evidence lineage above is retained and independently reconstructable. Until then, the canonical status remains `AUTHENTIC RESIDENT CUSTODY / OWNER-PRESENT EXECUTION / PROVIDER PROBE NOT PROVEN` as applicable to the first unsatisfied predicate.

This document is an evidence contract only. It carries `authority_effect: NONE`.
