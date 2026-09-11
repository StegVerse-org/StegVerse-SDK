# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-11
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
COSV: `71000000100110`
Status: `ACTIVE / GATEWAY SOURCE MERGED / AUTHENTIC RESIDENT CONSUMPTION NEXT`

## Canonical architecture

```text
source-native external resource observation
-> stegverse.ingress-manifest.v1
-> stegverse.state-transition-evidence.v1
-> external Interlock/InTr binding
-> organization federation boundary
-> provider-neutral WorkSpace consumer / active probe
-> TVC one-device external-collaboration consent/session/custody
-> exact provider-file metadata probe
-> SDK secret-free evidence bridge / readiness re-evaluation
```

Canonical authority rules remain unchanged:

```text
Task Registry = coordination only
WorkerCoordinator = claim/fence authority
Interlock/InTr = governed transition authority
TV/TVC = credential/provider authority
Master Records = observed reality / reconstruction authority
Service Gateway #72 = bounded sovereign HTTP ingress owner
GitHub Actions = validation/evidence transport only
GitHub runtime authority = NONE
hosted fallback = FALSE
second user-operated device required = FALSE
```

## Reconciled merged state

The previously recorded source/validation chain through SDK #195, TVC #397, `.github` #1370/#1382/#1393, and SDK #196 remains merged and valid.

- `.github` #1393 merged `312a31976bf5e794aa3912c2aa2c9ce0016c1102`, carrying exact portable dispatch for `sdk_workspace_external_collab_client_secret_reseal` and `sdk_workspace_external_collab_consent_listener` without creating runtime authority.
- SDK #196 merged `e55c0e415759a3f2baf2d553f403a3729719f891`; exact-head SDK validations `34560810500`, `34560810440`, and `34560810392` passed.
- `.github` #1402 merged `c2d03c776895ab99fa99ed49ca7c9ca9256d45cf`, preserving the fail-closed observation that neither exact resident consumption receipt had been observed and the authorized remote runtime was offline.
- `StegVerse-org/LLM-adapter` #332 merged `9ab7e019eaf694f20c978ce65ad7a2d5c886010a` from exact head `5d199cfc11be410f03c884cd70278d81d956c9f5`. Exact-head runs `34563524745`, `34563524752`, and `34563524742` passed.

LLM-adapter #332 implements the already-authorized three-route Service Gateway source contract:

```text
GET /tvc/external-collaboration/google-drive/consent/begin
GET /tvc/google-drive/external-collaboration/callback
GET /tvc/external-collaboration/google-drive/consent/health
same-host upstream: http://127.0.0.1:8786
```

The Gateway source is bounded to GET-only transport, exact callback query-key admission, direct loopback transport with environment proxies disabled, no redirect following, bounded response-header forwarding, and fail-closed listener-unreachable behavior. This proves source implementation/validation only; it does not prove listener health, native TLS adoption, public HTTPS reachability, client-secret custody, Google consent, provider contact, or WorkSpace readiness.

## Current proof boundary

```text
Generic ingress / Interlock / WorkSpace / active-probe source: MERGED / VALIDATED
External-collaboration consent/session/custody/probe source: MERGED / VALIDATED
Purpose-specific client-secret ingress/reseal source: MERGED / VALIDATED
Resident reseal dispatcher source: MERGED / VALIDATED
Resident consent-listener dispatcher source: MERGED / VALIDATED
Portable exact dispatch: MERGED / VALIDATED
Service Gateway three-route source: MERGED / VALIDATED
Authentic resident reseal receipt: NOT OBSERVED
Authentic resident listener receipt: NOT OBSERVED
Target external-collaboration client-secret custody/readback: NOT PROVEN
Resident listener health on 127.0.0.1:8786: NOT PROVEN
Sovereign stegverse.org callback/public HTTPS reachability: NOT PROVEN
Owner-present Google consent/session: NOT PROVEN
Authoritative provider-file probe: NOT PROVEN
SDK complete-predicate re-evaluation: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records reconstruction: NOT PROVEN
One-current-device end-to-end proof: NOT PROVEN
Downstream propagation complete: FALSE
Public distributions complete: FALSE
```

Expected resident receipts remain:

```text
receipts/sovereign-host/sdk-workspace-external-collab-client-secret-reseal.latest.json
receipts/sovereign-host/sdk-workspace-external-collab-consent-listener.latest.json
```

## Next executable sequence

1. Observe the existing authorized sovereign resident consume the two already-merged exact selectors; do not create a hosted substitute or duplicate resident runtime.
2. For reseal, accept only authentic `TARGET_ALREADY_PRESENT`, `COMPLETED`, or exact `BLOCKED`; validate target custody/readback without overwrite.
3. For listener, accept only authentic `SERVICE_ALREADY_HEALTHY`, `COMPLETED` with `loopback_health_verified=true`, or exact `BLOCKED`; remediate only the reported resident prerequisite.
4. After listener health, bind/observe the already-merged Service Gateway #332 source through the existing CMC-029/native-TLS `stegverse.org` runtime and independently prove the three public routes with no callback-query leakage.
5. Only after target client-secret custody and sovereign callback reachability are both proven, perform owner-present Google consent on the current iPhone.
6. Execute one exact authoritative provider-file metadata probe and retain secret-free durable replay/use evidence.
7. Feed the provider result through SDK normalization/active-probe predicate re-evaluation, then complete lifecycle/MIR, Master Records reconstruction, one-device evidence, downstream propagation, and public-distribution proof.

## Collision boundary

Do not create a competing resident runtime, Service Gateway, tunnel, callback implementation, credential path, hosted executor, or Heartbeat execution authority. `StegVerse-org/LLM-adapter#72` remains the Gateway owner and TV/TVC remains credential/provider authority.

## README review

`README.md` remains accurate. The newly merged Gateway work changes source readiness but does not establish a new public runtime capability, so no README wording change is required at this stage.

## Human action

None yet. Do not initiate Google consent until authentic target client-secret custody and sovereign callback reachability are both proven.
