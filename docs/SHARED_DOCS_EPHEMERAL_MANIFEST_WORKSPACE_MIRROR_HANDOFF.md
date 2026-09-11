# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-11
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
COSV: `71000000100110`
Status: `ACTIVE / GATEWAY SOURCE MERGED / AUTHENTIC RESIDENT CONSUMPTION + PUBLIC DISTRIBUTION NEXT`

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

The previously recorded source/validation chain through SDK #195, TVC #397, `.github` #1370/#1382/#1393, SDK #196, LLM-adapter #332, and SDK #199 remains merged and valid.

- `.github` #1393 merged `312a31976bf5e794aa3912c2aa2c9ce0016c1102`, carrying exact portable dispatch for `sdk_workspace_external_collab_client_secret_reseal` and `sdk_workspace_external_collab_consent_listener` without creating runtime authority.
- SDK #196 merged `e55c0e415759a3f2baf2d553f403a3729719f891`; exact-head SDK validations `34560810500`, `34560810440`, and `34560810392` passed.
- `.github` #1402 merged `c2d03c776895ab99fa99ed49ca7c9ca9256d45cf`, preserving the fail-closed observation that neither exact resident consumption receipt had been observed and the authorized remote runtime was offline.
- `StegVerse-org/LLM-adapter` #332 merged `9ab7e019eaf694f20c978ce65ad7a2d5c886010a` from exact head `5d199cfc11be410f03c884cd70278d81d956c9f5`. Exact-head runs `34563524745`, `34563524752`, and `34563524742` passed.
- SDK #199 merged `19db2775b6dbcd361f8329b6b0710699f4467462`, reconciling the merged Gateway source into the canonical SDK/task state; exact-head runs `34566917409`, `34566917412`, and `34566917413` passed.

LLM-adapter #332 implements the already-authorized three-route Service Gateway source contract:

```text
GET /tvc/external-collaboration/google-drive/consent/begin
GET /tvc/google-drive/external-collaboration/callback
GET /tvc/external-collaboration/google-drive/consent/health
same-host upstream: http://127.0.0.1:8786
```

The Gateway source is bounded to GET-only transport, exact callback query-key admission, direct loopback transport with environment proxies disabled, no redirect following, bounded response-header forwarding, and fail-closed listener-unreachable behavior. This proves source implementation/validation only; it does not prove listener health, native TLS adoption, public HTTPS reachability, client-secret custody, Google consent, provider contact, or WorkSpace readiness.

## Fresh authentic-runtime observation

A new reconciliation on 2026-09-11 rechecked all currently available authentic evidence channels:

- repository-tracked sovereign-host receipt paths: neither exact receipt present;
- connected retained Google Drive evidence: no exact reseal receipt and no exact listener receipt found;
- authorized remote resident-machine connector: no online device available.

Therefore source delivery remains distinct from resident execution. No client-secret custody, resident-seal liveness, listener health, public callback reachability, Google consent, provider execution, or one-device completion claim is made.

## Public distribution continuation

The canonical task record still identified `stegverse-stegcore==0.3.0_NOT_PUBLISHED` as the first proven public-distribution blocker. Fresh verification established:

```text
StegVerse-Labs/StegCore main source version: 0.3.0
exact release-ready source commit: 282f30e9e46efc3a8d0d867f48e08c3aa6534e22
public distribution name: stegverse-stegcore
required tag: v0.3.0
trusted-publishing workflow: .github/workflows/publish-pypi.yml
v0.3.0 tag observed: NO
GitHub Release v0.3.0 observed: NO
public stegverse-stegcore==0.3.0 observed: NO
```

Separate propagation-verification task `STEGCORE-PYPI-PROPAGATION-VERIFICATION-001` was created as `StegVerse-Labs/StegCore#203`. Its canonical handoff is `StegVerse-Labs/StegCore:docs/STEGCORE_PYPI_PROPAGATION_VERIFICATION_MIRROR_HANDOFF.md`, committed at `74237301e01a104f0470403d141abdcccdb82bc3`.

The available GitHub connector in this session exposes no GitHub Release creation mutation, so publication itself is not claimed. Once release `v0.3.0` is published against the exact release candidate commit, issue #203 owns verification of trusted publishing, public PyPI propagation, anonymous installation, downstream SDK install, and propagation checks for `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-Labs/stegguardian-wiki`.

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
StegCore public distribution release-ready: TRUE
StegCore v0.3.0 release published: FALSE
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
7. Feed the provider result through SDK normalization/active-probe predicate re-evaluation, then complete lifecycle/MIR, Master Records reconstruction, and one-device evidence.
8. Publish StegCore GitHub Release `v0.3.0` against exact commit `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`; issue #203 then verifies PyPI/public propagation and downstream consumers.
9. Reconcile all completed evidence into this goal and close downstream propagation only when both authentic runtime and public-distribution predicates are proven.

## Collision boundary

Do not create a competing resident runtime, Service Gateway, tunnel, callback implementation, credential path, hosted executor, Heartbeat execution authority, or alternate package publication mechanism. `StegVerse-org/LLM-adapter#72` remains the Gateway owner; TV/TVC remains credential/provider authority; StegCore's existing trusted-publishing workflow remains the public package publication path.

## README review

`README.md` remains accurate. The newly merged Gateway and release-readiness work changes source/distribution readiness but does not establish a new public runtime capability, so no README wording change is required at this stage.

## Human action

Two future owner actions are conditionally required, neither should be performed early:

1. For the public-distribution lane, publish GitHub Release `v0.3.0` in `StegVerse-Labs/StegCore` targeting exact commit `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`; use the existing Releases UI and make no source/code change.
2. Do not initiate Google consent until authentic target client-secret custody and sovereign callback reachability are both proven.
