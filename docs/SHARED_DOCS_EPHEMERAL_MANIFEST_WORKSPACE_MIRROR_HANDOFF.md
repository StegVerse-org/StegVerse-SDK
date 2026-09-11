# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / RESIDENT RESEAL + CONSENT-LISTENER REQUESTS MERGED / AUTHENTIC RESIDENT CONSUMPTION NEXT`

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

Canonical rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
Personal-KV OAuth client-secret seal purpose != external-collaboration OAuth client-secret seal purpose
KV _System/Workspace/** observation != authoritative external Shared Doc proof
TVC/provider/broker evidence != readiness authority
source/CI/merge != authentic resident execution
```

## Completed implementation chain

- SDK #174 state-transition evidence — merged `ee8f7023d74d70fa762e3982776c27c1e372a1f7`.
- SDK #176 canonical ingress -> external Interlock binding — merged `7047e67d21173e800f78d4468519dba87992b16d`.
- StegVerse-org/.github #9 generic INTERNAL_ENDPOINT dispatch — merged `d8baefb8674ebed00bbbf9784c54e092a5b1a04d`.
- SDK #179 provider-neutral WorkSpace consumer — merged `07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c`.
- StegVerse-org/.github #10 WorkSpace endpoint binding — merged `b851996afc5c5323d0d0db970dd46e511bd36338`.
- SDK #181 provider-neutral active-probe execution — merged `5c8a3c0246a0ae48e498c10f85d9eee0a2d1ba2c`.
- SDK #182 TVC provider evidence bridge — merged `43519567d036d1d87d5866ae825ffee54acec08f`.
- TVC #381 Personal-KV `_System/Workspace/**` semantic probe only — merged `bcf872cf0ce24a2cc653aabdaa8b25c34d0e4402`.
- SDK #184 WorkSpace-specific TVC result bridge — merged `97b2a5f018a261dc27370448fa1eb73644418d66`.
- TVC #383 distinct external-collaboration consent/session class — merged `ccbeae7ab03c23045b92db3a293b562422980cac`.
- stegfin-governance #95 distinct external-collaboration resident vault ref/provider slot — merged `35a058488c0a2a3dddeafdb59befcd19488e3c2a`.
- TVC #384 external-collaboration SKAP refresh custody, consent controller, vault-session consumer — merged `b7e8fd3f3f498e2cae6efb01c511a68d6ab7bd8c`.
- stegfin-governance #96 exact external-file metadata probe broker extension with durable pre-provider replay consumption — merged `66c1abbcc74a0a53fe6436b1fa003759acacaad6`.
- TVC #385 exact external-file probe lease/runtime — merged `4a3cc09dc5e85c051b9820dd83f6b2373e6316a7`.
- SDK #186 external-collaboration TVC result bridge — merged `f2f9a7f385477c8096a50fc223333240060e0a2f`.
- TVC #390 canonical one-current-device external-collaboration Google owner-consent activation plus distinct client-secret SKAP use purpose — merged `4c6df450b5a5925f74672e273d64b87d3e459808`.
- TVC #394 purpose-specific current-iPhone/browser-sealed SKAP ingress for `google_drive.external_collaboration.client_secret` — merged.
- TVC #395 canonical listener/public-route reconciliation to PR #390 semantics — merged `7451550d2d0506a5c091853805db22ad5211fd1b`.
- TVC #396 exact sovereign InTr carrier for the purpose-specific external-collaboration client-secret ingress — merged `bff7bbbb58bb474cbe44e148b2061a14351de84e`.
- TVC #397 resident-only purpose-to-purpose client-secret reseal into `google_drive.external_collaboration.client_secret` — merged `15f2e1afc9bb65d506241f3c9f0a4ce4bec1f46c`.
- Service Gateway owner `StegVerse-org/LLM-adapter#72` canonical transfer comment `5628280311` corrected to the PR #390 callback/purpose; no competing Gateway branch is authorized from this lane.
- StegVerse-Labs/.github #1370 resident reseal request/consumer + canonical dispatcher binding — merged `de09dcb3f74c19e3f891704f4db33db915ee61c6`.
- StegVerse-Labs/.github #1382 resident consent-listener installation/health request + consumer + canonical dispatcher binding — merged `f791bf2fa3eacfcdf7e9459916eec991293eb2c1`; exact final source head `fa560f09e7003b3a9d16e73c1390335c9dc726a1` passed listener `34558002459`, organization-control `34558002391`, Heartbeat `34558002427`, reseal regression `34558002497`, deterministic suite `34558002382`, cross-framework `34558002425`, and DeepSeek `34558002480`.
- SDK #188 WorkSpace external-collaboration consent/reseal reconciliation — MERGED.
- SDK #189 authentic external-collaboration runtime proof contract — MERGED at `ce67583e6e42eced35716f8460176f6c9e892f66`; exact-head validation runs `34554329799`, `34554329833`, `34554329801` PASS.
- SDK #190 root-handoff reconciliation of runtime proof gate/current machine-owned lanes — MERGED.
- SDK #193 later canonical reconciliation — MERGED `f5348c4de881ac8c66cb9b59b3fc0d6911266ad2`.

TVC #380/#382 and stegfin-governance #94 remain intentionally closed/unmerged where their earlier Personal-KV reuse premise conflicted with the canonical external-collaboration boundary.

## External-collaboration provider contract

Credential class: `TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001`  
Purpose: `EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY`  
OAuth state prefix: `extcollab.*`  
Canonical callback: `https://stegverse.org/tvc/google-drive/external-collaboration/callback`  
OAuth client-secret SKAP purpose: `google_drive.external_collaboration.client_secret`  
Refresh SKAP purpose: `google_drive.external_collaboration.refresh`  
Vault ref: `vault://tvc/providers/google-drive/external-collaboration-session`  
Provider key: `google_drive_external_collaboration`  
Operation: `external_collaboration_resource_probe`  
WorkSpace binding: `wsprobe_*`  
TVC result: `stegverse.tvc.external-collaboration-google-drive-probe-result/v1`  
Broker observation: `stegverse.tvc.google-drive-external-collaboration-metadata-probe/v1`

The browser receives only provider authorization transport and secret-free receipts. Authorization code, OAuth client secret, access token, refresh token, and broker session remain inside bounded TV/TVC processing. `second_user_operated_device_required=false` remains explicit.

## Client-secret custody paths

Two source-complete paths exist; runtime state selects one and must not duplicate custody:

```text
A. existing authentic Personal-KV ciphertext + current resident seal
   -> PR #397 resident-only purpose reseal
   -> .github #1370 exact resident request/consumer
   -> external-collaboration target ciphertext + custody receipt

B. no admissible reusable source custody
   -> PR #394 purpose-specific browser-sealed ingress
   -> PR #396 exact sovereign InTr carrier
   -> external-collaboration target ciphertext + chained receipts
```

Neither source path proves authentic target custody until executed on the authorized resident and independently read back/validated.

## Resident consent-listener path

The TVC listener source remains exact loopback `127.0.0.1:8786`. `.github #1382` now supplies an independent bounded resident request/consumer that:

- pins `scripts/install_external_collab_google_drive_consent_service.py` by Git blob `dae00dbec1a79d611a3184e185e04e6f29110348`;
- carries only `STEGVERSE_GOOGLE_DRIVE_CLIENT_ID`, `STEGVERSE_OWNER_BINDING_DIGEST`, and `STEGVERSE_STEGFIN_SOURCE_ROOT` as non-secret inputs;
- recognizes an already-healthy exact listener before installation;
- requires TVC resident root authority for installation;
- accepts completion only after exact loopback health reports the external-collaboration purpose and no credential/provider-contact/runtime-activation claim;
- grants no public HTTPS, Gateway, Google-consent, provider, credential, GitHub-token, HeartBeat, signing, broadcast, or readiness authority.

Expected resident receipt:

```text
receipts/sovereign-host/sdk-workspace-external-collab-consent-listener.latest.json
```

As of this reconciliation, that receipt was not observed in repository evidence or connected retained Drive evidence, so authentic listener installation/health remains unproven.

## Authentic runtime proof contract

SDK #189 defines the deterministic proof gate for the runtime phase. Authentic completion requires exact lineage across the dedicated credential class/session, purpose-specific custody, `wsprobe_*`, exact provider file/reason, durable replay consumption, secret-free TVC result, SDK evidence normalization, complete readiness re-evaluation, lifecycle transitions, MIR reporting, Master Records custody/reconstruction, and one-current-device continuity.

No caller assertion, provider result, source merge, or CI run may itself assign READY or satisfy runtime proof.

## Current proof boundary

```text
Generic ingress/Interlock/WorkSpace/active-probe chain: IMPLEMENTED / VALIDATED / MERGED
Dedicated external-collaboration consent/session/custody/probe source chain: IMPLEMENTED / VALIDATED / MERGED
Purpose-specific client-secret ingress + sovereign InTr carrier: IMPLEMENTED / VALIDATED / MERGED
Purpose-specific resident reseal source: IMPLEMENTED / VALIDATED / MERGED
Resident reseal dispatcher request/consumer: IMPLEMENTED / VALIDATED / MERGED
Resident consent-listener installer request/consumer: IMPLEMENTED / VALIDATED / MERGED
Authentic runtime proof contract: IMPLEMENTED / VALIDATED / MERGED
Authentic external-collaboration client-secret SKAP ciphertext custody: NOT PROVEN
Authentic source Personal-KV custody + resident-seal liveness for reseal: NOT PROVEN
Authentic reseal resident consumption receipt: NOT OBSERVED
Authentic purpose-specific InTr ingress execution: NOT PROVEN
Authentic consent-listener resident consumption receipt: NOT OBSERVED
Authentic resident consent listener installation/health on 127.0.0.1:8786: NOT PROVEN
Authentic public stegverse.org callback route / CMC-029 TLS: NOT PROVEN
Authentic owner-present external-collaboration consent: NOT PROVEN
Authentic active external-collaboration session: NOT PROVEN
Authentic authoritative provider-file probe: NOT PROVEN
Shared Docs live synchronization/content refresh: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records custody/reconstruction: NOT PROVEN
One-device end-to-end proof: NOT PROVEN
```

## Machine-owned lanes

Do not compete with current machine-owned owners:

- `StegVerse-org/LLM-adapter#72` — sovereign Service Gateway/native TLS path and corrected three-route consent contract.
- `StegVerse-Labs/.github` canonical resident dispatcher — selectors `sdk_workspace_external_collab_client_secret_reseal` and `sdk_workspace_external_collab_consent_listener` are now merged source requests awaiting authentic resident consumption.
- TVC runtime owners consuming the already-merged source units; no second resident runtime should be created.

Exact public route contract remains:

```text
GET https://stegverse.org/tvc/external-collaboration/google-drive/consent/begin
GET https://stegverse.org/tvc/google-drive/external-collaboration/callback
GET https://stegverse.org/tvc/external-collaboration/google-drive/consent/health
same-host upstream: http://127.0.0.1:8786
```

CMC-029 WebPKI HTTP-01 remains the sovereign `stegverse.org` TLS path. Cloudflare, Render, and Vercel are not required.

## Next executable sequence

1. Observe the existing sovereign resident dispatcher consume `sdk_workspace_external_collab_client_secret_reseal` and `sdk_workspace_external_collab_consent_listener`; do not create hosted substitutes or duplicate runtimes.
2. For reseal: if `TARGET_ALREADY_PRESENT`, validate exact target custody/readback without overwrite; if `BLOCKED`, remediate only the exact canonical prerequisite; if `COMPLETED`, retain the TV/TVC secret-free reseal result and target custody evidence.
3. For listener: accept only `SERVICE_ALREADY_HEALTHY` or `COMPLETED` with `loopback_health_verified=true`; if `BLOCKED`, remediate only the exact non-secret/source/root prerequisite.
4. Let machine-owned Service Gateway #72 implement the exact three-route contract and CMC-029 TLS path; independently verify public reachability with no callback-query leakage.
5. Only after custody and callback reachability are proven, execute owner-present Google consent on the current iPhone.
6. Execute one authentic exact provider-file metadata probe and retain the secret-free TVC result plus durable broker-use receipt.
7. Feed the exact result through the SDK bridge/active-probe engine and verify readiness changes only after complete applicable-predicate evaluation.
8. Continue `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY`, retaining MIR, Master Records reconstruction, and one-current-device evidence.

## README review

`README.md` remains accurate. No new public SDK capability is claimed until authentic public route/runtime evidence exists.

## Human action

None yet. Do not initiate Google consent until purpose-specific client-secret custody and sovereign callback reachability are authentically proven ready.
