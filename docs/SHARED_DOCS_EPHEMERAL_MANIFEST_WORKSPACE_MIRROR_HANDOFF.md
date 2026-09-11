# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / CONSENT + RESEAL SOURCE RECONCILED / SDK VALIDATION PASS / AUTHENTIC RESIDENT EXECUTION NEXT`

## Canonical architecture

```text
source-native external resource observation
  -> stegverse.ingress-manifest.v1
  -> stegverse.state-transition-evidence.v1
  -> external Interlock/InTr binding
  -> organization federation boundary
  -> registry-selected INTERNAL_ENDPOINT
  -> provider-neutral WorkSpace resource consumer
  -> runtime-supplied active probe executor when PROBE_REQUIRED
  -> TVC one-device external-collaboration owner-consent surface
       -> exact external-collaboration client-secret SKAP purpose
       -> provider-native authorization-code exchange
       -> external-collaboration refresh/session custody
       -> dedicated resident vault ref/provider slot
  -> exact provider-file metadata probe with durable pre-provider replay consumption
  -> SDK secret-free TVC evidence bridge
  -> active-probe engine re-derives readiness from complete predicate state
```

Canonical external-resource rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
Personal-KV OAuth client-secret seal purpose != external-collaboration OAuth client-secret seal purpose
KV _System/Workspace/** observation != authoritative external Shared Doc proof
TVC/provider/broker evidence != readiness authority
source/CI/merge != authentic resident execution
```

## Completed implementation chain

- SDK PR #174 — state-transition evidence — merged `ee8f7023d74d70fa762e3982776c27c1e372a1f7`.
- SDK PR #176 — canonical ingress -> external Interlock binding — merged `7047e67d21173e800f78d4468519dba87992b16d`.
- StegVerse-org/.github PR #9 — generic INTERNAL_ENDPOINT dispatch — merged `d8baefb8674ebed00bbbf9784c54e092a5b1a04d`.
- SDK PR #179 — provider-neutral WorkSpace resource consumer — merged `07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c`.
- StegVerse-org/.github PR #10 — WorkSpace endpoint binding — merged `b851996afc5c5323d0d0db970dd46e511bd36338`.
- SDK PR #181 — provider-neutral active-probe execution — merged `5c8a3c0246a0ae48e498c10f85d9eee0a2d1ba2c`.
- SDK PR #182 — TVC provider evidence bridge — merged `43519567d036d1d87d5866ae825ffee54acec08f`.
- TVC PR #381 — Personal-KV `_System/Workspace/**` semantic probe only — merged `bcf872cf0ce24a2cc653aabdaa8b25c34d0e4402`.
- SDK PR #184 — WorkSpace-specific TVC result bridge — merged `97b2a5f018a261dc27370448fa1eb73644418d66`.
- TVC PR #383 — distinct external-collaboration consent/session class — merged `ccbeae7ab03c23045b92db3a293b562422980cac`; validation `34549493296` PASS.
- stegfin-governance PR #95 — distinct external-collaboration resident vault ref/provider slot — merged `35a058488c0a2a3dddeafdb59befcd19488e3c2a`.
- TVC PR #384 — distinct external-collaboration SKAP refresh custody, consent controller, and vault-session consumer — merged `b7e8fd3f3f498e2cae6efb01c511a68d6ab7bd8c`; validation `34550176643` PASS.
- stegfin-governance PR #96 — exact external-file metadata probe broker extension with durable pre-provider replay consumption — merged `66c1abbcc74a0a53fe6436b1fa003759acacaad6`; validations `34551171043`, `34551171019`, `34551171073`, `34551171066` PASS.
- TVC PR #385 — exact external-file probe lease/runtime — merged `4a3cc09dc5e85c051b9820dd83f6b2373e6316a7`; validation `34551154748` PASS.
- SDK PR #186 — external-collaboration TVC result bridge support — merged `f2f9a7f385477c8096a50fc223333240060e0a2f`; validations `34551543442`, `34551543443`, `34551543452`, `34551543495` PASS.
- TVC PR #390 — canonical one-current-device external-collaboration Google owner-consent activation plus distinct client-secret SKAP use purpose — merged `4c6df450b5a5925f74672e273d64b87d3e459808`; final validations `34552694050` and `34552694044` PASS.
- TVC PR #395 — reconciled later HTTP/listener/public-route layers back to PR #390 authority, removed Personal-KV client-secret adapter reuse, fixed the canonical callback path, and made callback/begin/health query handling fail closed — merged `7451550d2d0506a5c091853805db22ad5211fd1b`; final validation `34553560515` PASS.
- Service Gateway machine owner `StegVerse-org/LLM-adapter#72` transfer comment `5628280311` was corrected to the PR #390 callback/purpose after #395 merged; no competing Gateway branch was opened from this lane.
- TVC PR #397 — resident-only purpose-to-purpose SKAP reseal from an existing Personal-KV Google client-secret ciphertext into `google_drive.external_collaboration.client_secret`, with no plaintext CLI/environment input and no source ciphertext mutation — merged `15f2e1afc9bb65d506241f3c9f0a4ce4bec1f46c`; final validation `34553843142` PASS.
- SDK PR #188 reconciles this handoff and canonical task record with TVC #395/#397. Exact reconciliation head `c7b23897c144710aa4bce4767868d624fcf50d82` passed Generic Manifest Downstream Contract `34554036793`, Manifest Builder Source `34554036710`, WorkSpace TVC Provider Probe Bridge `34554036705`, and WorkSpace Active Probe `34554036706`.

TVC PR #382 and stegfin-governance PR #94 remain intentionally closed/unmerged after authority reconciliation. TVC PR #380 remains closed/unmerged as superseded by the distinct external-collaboration chain.

## External-collaboration provider contract

Credential class: `TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001`  
Purpose: `EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY`  
OAuth state purpose prefix: `extcollab.*`  
Canonical callback: `https://stegverse.org/tvc/google-drive/external-collaboration/callback`  
OAuth client-secret SKAP purpose: `google_drive.external_collaboration.client_secret`  
Personal-KV client-secret purpose: `google_drive.personal_kv.client_secret`  
Session schema: `stegverse.tvc.google-drive-external-collaboration-access-session/v1`  
Refresh SKAP purpose: `google_drive.external_collaboration.refresh`  
Vault ref: `vault://tvc/providers/google-drive/external-collaboration-session`  
Provider key: `google_drive_external_collaboration`  
Operation: `external_collaboration_resource_probe`  
WorkSpace binding: `wsprobe_*`  
TVC result: `stegverse.tvc.external-collaboration-google-drive-probe-result/v1`  
Broker observation: `stegverse.tvc.google-drive-external-collaboration-metadata-probe/v1`

The browser-facing owner-presence surface exposes only a Google authorization URL and secret-free receipts. Authorization code, OAuth client secret, access token, refresh token, and broker session remain transient inside TV/TVC processing. `second_user_operated_device_required=false` remains explicit.

## Purpose-specific client-secret custody transition

PR #397 resolves the source gap without broadening consent authority. The existing Personal-KV sealed object cannot simply be relabeled because purpose is part of the cryptographic AAD. The resident-only transition performs:

```text
existing Personal-KV custody receipt
-> verify current resident-seal liveness
-> callback-only resolve under google_drive.personal_kv.client_secret
-> transient mutable bytes inside TVC resident process
-> immediate reseal under google_drive.external_collaboration.client_secret
-> ciphertext-only persist + exact readback
-> 0600 target custody receipt
-> mutable plaintext zeroization
```

There is no `--client-secret` argument and no environment-secret input. The Personal-KV source ciphertext is not modified or retired. If the target receipt already exists, the operation fails before resolving source plaintext. Source/CI proves this algorithm only; it does not prove the production source object, key liveness, or target ciphertext exists.

## SDK bridge rule

SDK PR #186 validates the exact external result/broker schemas, `wsprobe_*`, provider file ID, reason digest, credential class/purpose, metadata-only/read-only posture, no mutation, no credential return, and durable pre-provider replay evidence. It produces an ordinary canonical active-probe result without a readiness decision. The active-probe engine alone recomputes readiness after exact reason matching and complete predicate evaluation.

## Current proof boundary

```text
Generic ingress + Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Generic WorkSpace consumer + org endpoint: IMPLEMENTED / VALIDATED / MERGED
Active-probe execution: IMPLEMENTED / VALIDATED / MERGED
External-collaboration consent/session class: IMPLEMENTED / VALIDATED / MERGED
External-collaboration refresh/session custody source: IMPLEMENTED / VALIDATED / MERGED
External-collaboration vault-agent ref/provider slot: IMPLEMENTED / VALIDATED / MERGED
Exact external-file TVC lease/runtime: IMPLEMENTED / VALIDATED / MERGED
Exact external-file durable broker operation: IMPLEMENTED / VALIDATED / MERGED
SDK external-collaboration provider-result bridge: IMPLEMENTED / VALIDATED / MERGED
One-device owner-consent activation source: IMPLEMENTED / VALIDATED / MERGED
External-collaboration OAuth client-secret use source: IMPLEMENTED / VALIDATED / MERGED
Canonical HTTP/listener/route reconciliation: IMPLEMENTED / VALIDATED / MERGED
Purpose-specific client-secret reseal source: IMPLEMENTED / VALIDATED / MERGED
SDK canonical-record reconciliation: VALIDATED / MERGE PENDING
Authentic Personal-KV source client-secret ciphertext available on resident: NOT PROVEN
Authentic resident-seal liveness for reseal execution: NOT PROVEN
Authentic external-collaboration client-secret SKAP ciphertext custody: NOT PROVEN
Authentic resident consent-listener installation/health: NOT PROVEN
Authentic public stegverse.org callback route: NOT PROVEN
Authentic owner-present external-collaboration consent: NOT PROVEN
Authentic active external-collaboration session: NOT PROVEN
Authentic authoritative provider-file probe: NOT PROVEN
Shared Docs live synchronization/content refresh: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records authentic custody/reconstruction: NOT PROVEN
One-device authentic end-to-end execution: NOT PROVEN
```

Source/CI/merge must not be promoted into provider/runtime/custody proof.

## Sovereign route ownership

The existing machine-owned Service Gateway `StegVerse-org/LLM-adapter#72` owns public routing. This SDK lane must not create a competing gateway. Its corrected contract is:

```text
GET https://stegverse.org/tvc/external-collaboration/google-drive/consent/begin
GET https://stegverse.org/tvc/google-drive/external-collaboration/callback
GET https://stegverse.org/tvc/external-collaboration/google-drive/consent/health
same-host upstream: http://127.0.0.1:8786
```

CMC-029 WebPKI HTTP-01 remains the sovereign `stegverse.org` TLS path. Cloudflare, Render, and Vercel are not required. G18 terminalization is not a downstream gate.

## README review

`README.md` remains accurate. The SDK remains a non-authorizing client/integration surface; this update records internal TV/TVC custody/runtime prerequisites rather than a newly observable SDK capability. TVC README must change only when the owner-consent route is authentically public/reachable.

## Next executable sequence

1. Merge SDK PR #188 only if this handoff-bearing head remains green.
2. On the existing authorized TVC resident lane, observe whether the target external-collaboration client-secret custody receipt already exists. If it exists, validate it rather than overwriting it.
3. If the target is absent, verify the existing Personal-KV source custody receipt and current resident-seal liveness, then execute the merged PR #397 reseal exactly once. Retain the secret-free reseal receipt and exact target custody/readback evidence.
4. Prove `GoogleDriveExternalCollaborationClientSecretUse` can resolve the new target only inside its bounded callback without plaintext export.
5. Install/start the merged resident consent listener on `127.0.0.1:8786` through the existing TVC resident execution owner and retain health evidence.
6. Let machine-owned Service Gateway #72 implement the corrected three-route contract; do not create a competing Gateway. Use CMC-029 for the sovereign `stegverse.org` certificate and independently verify public HTTPS reachability.
7. Only after client-secret custody and callback reachability are proven, initiate owner-present Google consent on the current iPhone.
8. Execute one authentic exact provider-file metadata probe and retain the secret-free TVC result plus durable broker-use receipt.
9. Feed the exact result through SDK #186 and the active-probe engine; verify `PROBE_REQUIRED -> READY` only when the named unresolved predicate is actually satisfied and no other applicable predicate remains unresolved.
10. Continue `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY`, retaining MIR reporting, independent Master Records custody/reconstruction, and one-current-device evidence.

## Human action

None yet. No client-secret re-entry is intended if the existing Personal-KV sealed object is authentically present and valid. Do not initiate Google consent until purpose-specific custody and sovereign callback reachability are authentically proven ready.
