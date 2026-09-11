# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / EXTERNAL-COLLAB PROVIDER PROBE SOURCE CHAIN MERGED / AUTHENTIC OWNER-PRESENT EXECUTION NEXT`

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
  -> TVC external-collaboration consent/session
  -> distinct TV/TVC/SKAP custody + vault ref
  -> exact provider-file metadata probe with durable pre-provider replay consumption
  -> SDK secret-free TVC evidence bridge
  -> active-probe engine re-derives readiness from complete predicate state
```

Canonical external-resource rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
KV _System/Workspace/** observation != authoritative external Shared Doc proof
TVC/provider/broker evidence != readiness authority
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

TVC PR #382 and stegfin-governance PR #94 remain intentionally closed/unmerged after authority reconciliation. TVC PR #380 is also closed/unmerged as superseded by the distinct external-collaboration chain.

## External-collaboration provider contract

Credential class: `TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001`  
Purpose: `EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY`  
OAuth state purpose prefix: `extcollab.*`  
Session schema: `stegverse.tvc.google-drive-external-collaboration-access-session/v1`  
Vault ref: `vault://tvc/providers/google-drive/external-collaboration-session`  
Provider key: `google_drive_external_collaboration`  
Operation: `external_collaboration_resource_probe`  
WorkSpace binding: `wsprobe_*`  
TVC result: `stegverse.tvc.external-collaboration-google-drive-probe-result/v1`  
Broker observation: `stegverse.tvc.google-drive-external-collaboration-metadata-probe/v1`

The probe binds the exact provider file ID and active-probe reason, is single-use with lease duration <=300 seconds, performs metadata GET only, downloads no document content, exports no credential material, grants no provider mutation authority, and does not assign readiness. Durable replay is recorded before provider invocation so failed or uncertain provider calls cannot reuse the same lease after restart.

## SDK bridge rule

SDK PR #186 validates the exact external result/broker schemas, `wsprobe_*`, provider file ID, reason digest, credential class/purpose, metadata-only/read-only posture, no mutation, no credential return, and durable pre-provider replay evidence. It then produces an ordinary canonical active-probe result. It does not include a readiness decision. The active-probe engine alone recomputes readiness after exact reason matching and complete predicate evaluation.

## Current proof boundary

```text
Generic ingress + Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Generic WorkSpace consumer + org endpoint: IMPLEMENTED / VALIDATED / MERGED
Active-probe execution: IMPLEMENTED / VALIDATED / MERGED
Personal-KV WorkSpace probe: IMPLEMENTED / VALIDATED / MERGED / KV-SCOPED ONLY
External-collaboration consent/session class: IMPLEMENTED / VALIDATED / MERGED
External-collaboration SKAP refresh/session custody: IMPLEMENTED / VALIDATED / MERGED
External-collaboration vault-agent ref/provider slot: IMPLEMENTED / VALIDATED / MERGED
Exact external-file TVC lease/runtime: IMPLEMENTED / VALIDATED / MERGED
Exact external-file durable broker operation: IMPLEMENTED / VALIDATED / MERGED
SDK external-collaboration provider-result bridge: IMPLEMENTED / VALIDATED / MERGED
Authentic owner-present external-collaboration consent: NOT PROVEN
Authentic authoritative provider-file probe: NOT PROVEN
Shared Docs live synchronization/content refresh: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records authentic custody/reconstruction: NOT PROVEN
One-device authentic end-to-end execution: NOT PROVEN
```

Source/CI/merge must not be promoted into provider runtime proof.

## README review

`README.md` remains accurate for this source chain. The SDK remains a non-authorizing client/integration surface rather than credential, transport, or final-governance authority. README must be updated when an externally observable Shared Docs/WorkSpace workflow is introduced.

## Next executable sequence

1. Determine whether a correctly scoped external-collaboration Google owner session is already authentically active.
2. If no such session exists, execute owner-present consent through the distinct external-collaboration controller on the current device.
3. Execute one authentic exact provider-file metadata probe through the merged TVC lease/runtime and durable broker and retain the secret-free result/use receipt.
4. Feed the exact result through the SDK bridge and active-probe engine; verify `PROBE_REQUIRED -> READY` only when the named unresolved predicate is actually satisfied and no other applicable predicate remains unresolved.
5. Continue `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY` using the authoritative external resource, not a KV substitute.
6. Retain MIR reporting, independent Master Records custody/reconstruction, and one-current-device evidence.

## Human action

None for source/handoff reconciliation. Owner-present Google authorization is required only if no correctly scoped external-collaboration session already exists when authentic provider execution begins.
