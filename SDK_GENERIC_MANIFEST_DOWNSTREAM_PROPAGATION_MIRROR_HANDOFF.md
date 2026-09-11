# SDK Generic Manifest Downstream Propagation Mirror Handoff

Updated: 2026-09-11

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
source_goal: SDK-PROCESSOR-GENERIC-MANIFEST-002
continuation_goal: SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003
COSV: 71000000100110
credential_authority: TV/TVC
GitHub runtime authority: NONE
coordination_state: ACTIVE
legacy_task_state_invariant: DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
canonical_public_base: https://stegverse.org/
current_ecosystem_chat_route: https://stegverse.org/ecosystem-chat.html
```

This is the canonical SDK root handoff for processor-generic downstream propagation and the WorkSpace/external-collaboration continuation. Current Task Registry truth is `StegVerse-Labs/.github:data/canonical-task-records/SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003.json`. Runtime proof remains task-specific and cannot be inferred from repository source or CI.

## Canonical semantics

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance-specific fields are not universal manifest requirements
unsupported or uninstalled processor/route execution fails closed
```

The currently installed processor remains governance on `stegverse.route.canonical-governed.v1`; processor-specific request state remains under `extensions.stegverse_governance_request`.

## Reconciled source / validation state

The previously documented implementation chain through SDK #195, TVC #397, `.github` #1370/#1382/#1393, and SDK #196 remains merged and valid.

- SDK #196 merged `e55c0e415759a3f2baf2d553f403a3729719f891`; exact-head validations `34560810500`, `34560810440`, and `34560810392` passed.
- `.github` #1402 merged `c2d03c776895ab99fa99ed49ca7c9ca9256d45cf`, retaining the fail-closed observation that neither exact resident consumption receipt had been observed and no authorized remote runtime was online.
- `StegVerse-org/LLM-adapter` #332 merged `9ab7e019eaf694f20c978ce65ad7a2d5c886010a` from exact head `5d199cfc11be410f03c884cd70278d81d956c9f5`; exact-head validation runs `34563524745`, `34563524752`, and `34563524742` passed.
- SDK #199 merged `19db2775b6dbcd361f8329b6b0710699f4467462` from exact head `f8ed8260f965da5655780f6e4949c0799d2ac67e`; exact-head validation runs `34566917409`, `34566917412`, and `34566917413` passed, reconciling the WorkSpace child handoff to the Gateway source completion.

README review remains current: these changes reconcile coordination and source/runtime-proof boundaries only; they do not add a new public SDK capability identifier, universal ingress class, CLI route, or user-facing WorkSpace product surface.

## External-collaboration authority boundary

```text
credential class: TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001
purpose: EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY
provider slot: google_drive_external_collaboration
vault ref: vault://tvc/providers/google-drive/external-collaboration-session
client-secret SKAP purpose: google_drive.external_collaboration.client_secret
operation: external_collaboration_resource_probe
binding prefix: wsprobe_
public begin: https://stegverse.org/tvc/external-collaboration/google-drive/consent/begin
public callback: https://stegverse.org/tvc/google-drive/external-collaboration/callback
public health: https://stegverse.org/tvc/external-collaboration/google-drive/consent/health
client-secret public ingress: https://stegverse.org/v1/skap/google-drive/external-collaboration/client-secret/ingress
same-host listener upstream: http://127.0.0.1:8786
Service Gateway owner: StegVerse-org/LLM-adapter#72
canonical resident carrier: StegVerse-Labs/.github:docs/CANONICAL_RESIDENT_CARRIER_MIRROR_HANDOFF.md
```

Controlling rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
Personal-KV client-secret custody != external-collaboration client-secret custody
KV _System/Workspace/** observation != authoritative external Shared Doc proof
source/CI/merge != authentic runtime proof
GitHub runtime authority = NONE
third-party/hosted fallback = FALSE
```

Machine-owned Service Gateway #72 remains the sole owner of the sovereign public-route implementation/runtime proof. PR #332 now provides the exact three bounded GET routes through the existing Gateway with fixed loopback upstream, callback query-key admission, environment-proxy bypass, no redirect following, bounded response-header forwarding, and fail-closed listener-unreachable behavior. It does not prove listener health, public HTTPS/TLS reachability, custody, consent, provider contact, or WorkSpace readiness.

## Authentic runtime proof ordering

`docs/EXTERNAL_COLLAB_AUTHENTIC_RUNTIME_PROOF_CONTRACT.md` remains authoritative:

```text
authorized-resident Personal-KV source custody
+ current resident-seal liveness/private-key availability
-> authentic RESIDENT-EXEC-SDK-WORKSPACE-EXTCOLLAB-CLIENT-SECRET-RESEAL-001 consumption
-> exact external-collaboration target client-secret custody/readback
-> authentic resident consent-listener health
-> sovereign stegverse.org ingress + exact callback/listener reachability
-> owner-present external-collaboration Google consent/session
-> exact provider-file metadata probe + durable replay/use evidence
-> SDK normalization / active-probe predicate re-evaluation
-> lifecycle/MIR reporting
-> independent Master Records custody/reconstruction
-> one-current-device end-to-end evidence
```

Repository validation carries `authority_effect: NONE` and cannot satisfy any authentic runtime predicate.

## Current proof boundary

```text
Generic ingress + Interlock binding: IMPLEMENTED / VALIDATED / MERGED
WorkSpace consumer / endpoint / active-probe source: IMPLEMENTED / VALIDATED / MERGED
External-collaboration consent/session + provider probe source: IMPLEMENTED / VALIDATED / MERGED
Purpose-specific client-secret ingress/reseal source: IMPLEMENTED / VALIDATED / MERGED
Resident reseal dispatcher source (#1370): IMPLEMENTED / VALIDATED / MERGED
Resident consent-listener dispatcher source (#1382): IMPLEMENTED / VALIDATED / MERGED
Portable exact-dispatch repair (#1393): IMPLEMENTED / VALIDATED / MERGED
Service Gateway external-collaboration route source (#332): IMPLEMENTED / VALIDATED / MERGED
SDK root/child reconciliation (#196/#199): IMPLEMENTED / VALIDATED / MERGED
Authorized-resident Personal-KV source client-secret custody: NOT PROVEN
Resident seal liveness/private-key availability for reseal: NOT PROVEN
Authentic resident reseal consumption receipt: NOT OBSERVED
Authentic resident consent-listener consumption receipt: NOT OBSERVED
External-collaboration target client-secret custody/readback: NOT PROVEN
Authentic sovereign public ingress/callback reachability: NOT PROVEN
Authentic owner-present external-collaboration consent: NOT PROVEN
Authentic authoritative provider-file probe: NOT PROVEN
SDK active-probe complete predicate re-evaluation: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records authentic custody/reconstruction: NOT PROVEN
One-current-device authentic end-to-end execution: NOT PROVEN
Downstream propagation complete: FALSE
Public distributions complete: FALSE
```

## Collision prevention

```text
StegVerse-Labs/Site: REQUIRED / MACHINE_OWNED
StegVerse-Labs/admissibility-wiki: REQUIRED / WORKER_OWNED
StegVerse-org/LLM-adapter#72: MACHINE_OWNED sovereign Gateway/runtime proof
StegVerse-Labs/.github resident dispatcher: EXISTING CANONICAL EXECUTOR PATH
GitHub Actions: VALIDATION / EVIDENCE TRANSPORT ONLY
```

Reuse these lanes. Do not create a competing Gateway, tunnel, reverse proxy, WorkerCoordinator, resident executor, scheduler, credential path, or hosted fallback.

## Next executable sequence

1. Observe the existing authorized resident consume `sdk_workspace_external_collab_client_secret_reseal`; accept only authentic `TARGET_ALREADY_PRESENT`, `COMPLETED`, or exact `BLOCKED` receipt evidence.
2. Independently observe `sdk_workspace_external_collab_consent_listener`; accept only authentic `SERVICE_ALREADY_HEALTHY`, `COMPLETED` with exact loopback health, or exact `BLOCKED` evidence.
3. For `BLOCKED`, remediate only the exact resident prerequisite through its canonical owner; do not create a substitute executor.
4. After target-purpose custody/readback and listener health exist, require authentic sovereign `stegverse.org` ingress/callback reachability through Service Gateway #72.
5. Only after custody and callback reachability are proven, perform owner-present Google consent on the current iPhone.
6. Execute one exact authoritative provider-file metadata probe, feed only secret-free result/use evidence through the SDK bridge/active-probe engine, then complete MIR, Master Records, one-current-device proof, downstream propagation, and public-distribution evidence.

## Current status

```text
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
COSV: 71000000100110
SDK #196: MERGED / EXACT VALIDATION PASS
SDK #199: MERGED / EXACT VALIDATION PASS
LLM-adapter #332: MERGED / EXACT VALIDATION PASS / exact Gateway routes source-complete
resident reseal consumption receipt: NOT OBSERVED
resident consent-listener consumption receipt: NOT OBSERVED
authorized remote runtime online: NOT OBSERVED
authentic target client-secret custody: NOT PROVEN
authentic sovereign callback reachability: NOT PROVEN
authentic owner-present Google consent: NOT PROVEN
authentic provider probe: NOT PROVEN
propagation complete: FALSE
public distributions complete: FALSE
manual user work required now: NONE
```
