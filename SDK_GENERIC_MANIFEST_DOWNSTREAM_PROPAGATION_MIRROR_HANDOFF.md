# SDK Generic Manifest Downstream Propagation Mirror Handoff

Updated: 2026-09-10

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
coordination_state: DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
```

This handoff is the canonical root for processor-generic downstream propagation, public governed-runtime distribution remediation, and the WorkSpace continuation at `docs/SHARED_DOCS_EPHEMERAL_MANIFEST_WORKSPACE_MIRROR_HANDOFF.md`.

## Canonical processor-generic semantics

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance-specific fields are not universal manifest requirements
unsupported or uninstalled processor/route execution fails closed
```

The current executable processor remains governance on `stegverse.route.canonical-governed.v1`; processor-specific governance request state remains under `extensions.stegverse_governance_request`.

## Current merged WorkSpace / external-collaboration chain

The source/CI chain is merged and validated through:

- SDK #174 state-transition evidence.
- SDK #176 canonical ingress -> external Interlock binding.
- StegVerse-org/.github #9 generic INTERNAL_ENDPOINT dispatch.
- SDK #179 provider-neutral WorkSpace resource consumer.
- StegVerse-org/.github #10 WorkSpace endpoint binding.
- SDK #181 provider-neutral active-probe execution.
- SDK #182 secret-free TVC provider-evidence bridge.
- TVC #381 KV-scoped `_System/Workspace/**` semantic probe only; not authoritative external Shared Docs proof.
- SDK #184 WorkSpace-specific TVC result bridge.
- TVC #383 distinct external-collaboration consent/session class.
- stegfin-governance #95 distinct external-collaboration vault ref/provider slot.
- TVC #384 distinct external-collaboration SKAP refresh/session custody.
- stegfin-governance #96 exact metadata-only provider probe plus durable pre-provider replay consumption.
- TVC #385 exact external-file probe lease/runtime.
- SDK #186 external-collaboration TVC result bridge.
- stegfin-governance #97 exact external-collaboration session readiness, merged `712dbdb325eef9e2cbadf0ca4b714b12592b30bf`; exact-head runs `34552662298`, `34552662375`, `34552662249`, and `34552662285` PASS.
- TVC #390 one-current-device external-collaboration owner-consent composition plus distinct OAuth client-secret SKAP purpose.
- TVC #394 purpose-specific current-iPhone -> SKAP ciphertext ingress source.
- TVC #395 canonical HTTP/listener/public-route reconciliation to PR #390 authority and corrected callback path.
- TVC #396 exact external-collaboration client-secret ingress route, corrected before merge to use the existing sovereign `https://stegverse.org` Service Gateway plus canonical resident InTr carrier with no Cloudflare/third-party tunnel runtime; merged `bff7bbbb58bb474cbe44e148b2061a14351de84e`; corrected exact-head `99f34171adec7edf334e6e42a3fc2ab2e8526ef3`; runs `34554831422` and `34554828811` PASS.
- TVC #397 resident-only purpose-specific Google client-secret ciphertext reseal into `google_drive.external_collaboration.client_secret`.
- StegVerse-Labs/.github #1370 resident request/consumer + canonical dispatcher binding for the TVC #397 reseal; merged `de09dcb3f74c19e3f891704f4db33db915ee61c6` after exact-head `a3d8002180c5ea8dddc51d735c6541da6dd272f3` passed deterministic repository, heartbeat worker, organization control-plane, dedicated reseal, cross-framework, and DeepSeek regression workflows (`34555121000`, `34555121027`, `34555121010`, `34555121049`, `34555121264`, `34555120999`).
- SDK #189 authentic external-collaboration runtime proof contract, merged at `ce67583e6e42eced35716f8460176f6c9e892f66` after exact-head validation PASS.

SDK #189 exact head `da11a4f77c5085bd3d9e9c07b28d252ac3a671f2` passed:

```text
External Collaboration Authentic Runtime Proof Contract Validation 34554329799: PASS
Generic Manifest Downstream Contract Validation 34554329833: PASS
Manifest Builder Source Validation 34554329801: PASS
```

README review remains current. The present changes are internal evidence/runtime contracts and do not introduce a new public SDK capability identifier, universal ingress class, CLI/runtime route, or user-facing WorkSpace product surface.

## External-collaboration authority boundary

```text
credential class: TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001
purpose: EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY
OAuth state purpose: extcollab.*
provider slot: google_drive_external_collaboration
vault ref: vault://tvc/providers/google-drive/external-collaboration-session
client-secret SKAP purpose: google_drive.external_collaboration.client_secret
operation: external_collaboration_resource_probe
binding prefix: wsprobe_
public callback: https://stegverse.org/tvc/google-drive/external-collaboration/callback
client-secret public ingress: https://stegverse.org/v1/skap/google-drive/external-collaboration/client-secret/ingress
canonical resident carrier: StegVerse-Labs/.github:docs/CANONICAL_RESIDENT_CARRIER_MIRROR_HANDOFF.md
Service Gateway owner: StegVerse-org/LLM-adapter#72
```

Controlling rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
Personal-KV client-secret custody != external-collaboration client-secret custody
KV _System/Workspace/** observation != authoritative external Shared Doc proof
TVC/provider/broker evidence != readiness authority
source/CI/merge != authentic runtime proof
third-party tunnel availability != sovereign InTr route proof
```

PR #396 initially attempted to launch `cloudflared` and accept `*.trycloudflare.com`; that source was not merged. The merged correction launches no tunnel, reverse proxy, scheduler, gateway, or second resident carrier. It accepts only `https://stegverse.org`, observes exact local receiver `127.0.0.1:8767`, binds to machine-owned Service Gateway #72, and records `third_party_tunnel_runtime_required: false`.

## Authentic runtime proof gate

`docs/EXTERNAL_COLLAB_AUTHENTIC_RUNTIME_PROOF_CONTRACT.md` is the exact evidence contract. A qualifying lineage must bind:

```text
authentic resident source/client-secret custody + current resident seal liveness
-> purpose-specific ciphertext reseal when target custody is absent
-> exact external-collaboration client-secret target custody/readback
-> resident callback/listener reachability
-> owner-present external-collaboration consent/session
-> dedicated TV/TVC/SKAP provider slot/ref
-> fresh wsprobe_* binding + exact provider file ID + exact active-probe reason
-> single-use TVC lease + durable pre-provider replay consumption
-> authentic metadata-only/read-only provider response
-> secret-free TVC result + durable broker use receipt
-> SDK evidence normalization with no readiness assignment
-> full active-probe predicate re-evaluation
-> OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY
-> MIR transition reporting
-> independent Master Records custody/reconstruction
-> one-current-device continuity evidence
```

The proof contract carries `authority_effect: NONE`; passing repository validation is not runtime proof.

## Resident reseal execution boundary

StegVerse-Labs/.github #1370 now carries the already-merged TVC #397 source into the existing resident dispatcher without creating a second scheduler/WorkerCoordinator/heartbeat/runtime. Its consumer:

```text
selector: sdk_workspace_external_collab_client_secret_reseal
request: RESIDENT-EXEC-SDK-WORKSPACE-EXTCOLLAB-CLIENT-SECRET-RESEAL-001
credential authority: TV/TVC
GitHub runtime authority: NONE
source fetch over network: prohibited
target overwrite: prohibited
provider contact: none
```

The consumer observes the exact resident prerequisites and emits only a secret-free durable consumption receipt. `COMPLETED` or `TARGET_ALREADY_PRESENT` would be authentic resident evidence only when produced by the resident path. No such repository-relayed receipt has been observed yet. Therefore #1370 merge proves resident source carriage/dispatcher integration, not client-secret custody.

## Current proof boundary

```text
Generic ingress + Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Generic WorkSpace consumer + organization endpoint: IMPLEMENTED / VALIDATED / MERGED
Active-probe execution: IMPLEMENTED / VALIDATED / MERGED
External-collaboration consent/session source: IMPLEMENTED / VALIDATED / MERGED
External-collaboration SKAP refresh/session custody source: IMPLEMENTED / VALIDATED / MERGED
External-collaboration exact provider probe source: IMPLEMENTED / VALIDATED / MERGED
SDK external-collaboration provider-result bridge: IMPLEMENTED / VALIDATED / MERGED
Exact external-collaboration session readiness: IMPLEMENTED / VALIDATED / MERGED
One-device activation source: IMPLEMENTED / VALIDATED / MERGED
Purpose-specific client-secret ciphertext ingress source: IMPLEMENTED / VALIDATED / MERGED
Sovereign client-secret ingress route source: IMPLEMENTED / VALIDATED / MERGED
Client-secret purpose-specific reseal source: IMPLEMENTED / VALIDATED / MERGED
Resident reseal request/consumer/dispatcher binding: IMPLEMENTED / VALIDATED / MERGED
Authentic-runtime proof contract: IMPLEMENTED / VALIDATED / MERGED
External-collaboration client-secret ciphertext custody on authorized resident: NOT PROVEN
Authorized-resident Personal-KV source client-secret custody: NOT PROVEN
Resident seal liveness for reseal: NOT PROVEN
Authentic resident reseal consumption receipt: NOT OBSERVED
Authentic sovereign public route to exact 127.0.0.1:8767 receiver: NOT PROVEN
External-collaboration callback resident reachability: NOT PROVEN
Authentic owner-present external-collaboration consent: NOT PROVEN
Authentic authoritative provider-file probe: NOT PROVEN
Shared Docs live synchronization/content refresh: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records authentic custody/reconstruction: NOT PROVEN
One-device authentic end-to-end execution: NOT PROVEN
```

## Current ownership / collision prevention

```text
StegVerse-Labs/Site: REQUIRED / MACHINE_OWNED / completion FALSE
StegVerse-Labs/admissibility-wiki: REQUIRED / Worker D OWNED / completion FALSE
StegVerse-org/LLM-adapter#72: machine-owned corrected three-route callback/Gateway contract
StegVerse-Labs/.github #1370: MERGED resident dispatcher path for external-collab client-secret reseal
StegVerse-Labs/TVC #396: MERGED sovereign route observer/binding source for exact 8767 client-secret ingress
```

Do not open competing implementations for those owned lanes. Reuse their evidence and only reconcile authentic runtime evidence when it exists.

## Canonical public surfaces

```text
canonical public base: https://stegverse.org/
current Ecosystem Chat route: https://stegverse.org/ecosystem-chat.html
dedicated processor-generic public route: NOT YET OBSERVED
raw GitHub Pages URL is canonical public surface: FALSE
```

## Public runtime distribution boundary

```text
StegCore public distribution: stegverse-stegcore 0.3.0 / source rename merged / public publication still pending
Master Records public distribution: stegverse-master-records 0.2.0 / Trusted Publishing source merged / public publication still pending
SDK successor PR #165: 1.3.0 SOURCE_CANDIDATE
anonymous governed-runtime install: FAIL_CLOSED pending exact public distributions
release/tag/publication claim: NONE
```

## Next executable sequence

1. Observe the existing sovereign resident dispatcher consume merged #1370; do not create a hosted substitute or second resident executor.
2. If its receipt is `TARGET_ALREADY_PRESENT`, validate the existing external-collaboration target custody/readback without overwrite.
3. If its receipt is `BLOCKED`, remediate only the exact resident prerequisite through its canonical owner: TVC source materialization, Personal-KV source custody, resident-seal activation/liveness, resident private-key availability, or root resident execution.
4. If `COMPLETED`, retain the authentic secret-free reseal result and target custody/readback evidence; do not infer consent or provider contact.
5. Observe the machine-owned Service Gateway #72 bind the exact sovereign client-secret ingress and callback routes; retain authentic health/reachability evidence for `stegverse.org` and exact loopback receivers.
6. Only after target client-secret custody and callback reachability are proven, execute owner-present Google consent on the current iPhone.
7. Execute one authentic exact external provider-file metadata probe and feed the secret-free result through the SDK bridge/active-probe engine.
8. Complete authoritative-provider lifecycle, MIR transition reporting, independent Master Records custody/reconstruction, and one-current-device proof.
9. Continue observing Site/Worker D and public-runtime publication dependencies without taking over their owned implementation lanes.

## Current status

```text
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
COSV: 71000000100110
SDK #189: MERGED / EXACT-HEAD VALIDATED
stegfin-governance #97: MERGED / EXACT-HEAD VALIDATED
TVC #396 corrected sovereign source: MERGED / EXACT-HEAD VALIDATED
StegVerse-Labs/.github #1370 resident dispatcher path: MERGED / EXACT-HEAD VALIDATED
propagation complete: FALSE
authentic resident client-secret custody: NOT PROVEN
authentic owner-present external-collaboration consent: NOT PROVEN
authentic provider probe: NOT PROVEN
manual user work required now: NONE
```
