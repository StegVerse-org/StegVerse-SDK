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
- TVC #390 one-current-device external-collaboration owner-consent composition plus distinct OAuth client-secret SKAP purpose.
- TVC #395 canonical HTTP/listener/public-route reconciliation to PR #390 authority and corrected callback path.
- TVC #397 resident-only purpose-specific Google client-secret ciphertext reseal into `google_drive.external_collaboration.client_secret`.
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
```

Controlling rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
Personal-KV client-secret custody != external-collaboration client-secret custody
KV _System/Workspace/** observation != authoritative external Shared Doc proof
TVC/provider/broker evidence != readiness authority
source/CI/merge != authentic runtime proof
```

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

## Current proof boundary

```text
Generic ingress + Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Generic WorkSpace consumer + organization endpoint: IMPLEMENTED / VALIDATED / MERGED
Active-probe execution: IMPLEMENTED / VALIDATED / MERGED
External-collaboration consent/session source: IMPLEMENTED / VALIDATED / MERGED
External-collaboration SKAP refresh/session custody source: IMPLEMENTED / VALIDATED / MERGED
External-collaboration exact provider probe source: IMPLEMENTED / VALIDATED / MERGED
SDK external-collaboration provider-result bridge: IMPLEMENTED / VALIDATED / MERGED
One-device activation source: IMPLEMENTED / VALIDATED / MERGED
Client-secret purpose-specific reseal source: IMPLEMENTED / VALIDATED / MERGED
Authentic-runtime proof contract: IMPLEMENTED / VALIDATED / MERGED
External-collaboration client-secret ciphertext custody on authorized resident: NOT PROVEN
Authorized-resident Personal-KV source client-secret custody: NOT PROVEN
Resident seal liveness for reseal: NOT PROVEN
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
StegVerse-Labs/.github #1370: resident dispatcher path for external-collab client-secret reseal
StegVerse-Labs/TVC #396: dedicated zero-credential resident InTr carrier for external-collab client-secret ingress
```

Do not open competing implementations for those owned lanes. Reuse their evidence and only reconcile it here after merge/validation/runtime proof.

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

1. Let the machine-owned resident reseal/ingress lanes complete without collision: StegVerse-Labs/.github #1370 and TVC #396.
2. Reconcile their exact merge and validation evidence into this handoff and the task record.
3. On the authorized TVC resident, determine whether exact external-collaboration client-secret custody already exists; if absent, prove source Personal-KV client-secret custody plus resident seal liveness and execute the merged purpose-specific reseal exactly once.
4. Retain the secret-free reseal receipt plus exact target custody/readback evidence.
5. Install/start the merged TVC resident consent listener on `127.0.0.1:8786` through the existing resident execution owner and retain authentic health/callback reachability evidence.
6. Only then execute owner-present Google consent on the current iPhone.
7. Execute one authentic exact external provider-file metadata probe and feed the secret-free result through the SDK bridge/active-probe engine.
8. Complete authoritative-provider lifecycle, MIR transition reporting, independent Master Records custody/reconstruction, and one-current-device proof.
9. Continue observing Site/Worker D and public-runtime publication dependencies without taking over their owned implementation lanes.

## Current status

```text
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
COSV: 71000000100110
SDK #189: MERGED / EXACT-HEAD VALIDATED
propagation complete: FALSE
authentic owner-present external-collaboration consent: NOT PROVEN
authentic provider probe: NOT PROVEN
manual user work required now: NONE
```
