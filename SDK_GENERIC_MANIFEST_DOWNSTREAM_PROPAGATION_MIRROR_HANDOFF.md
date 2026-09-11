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
coordination_state: ACTIVE
```

This handoff is the canonical SDK root for processor-generic downstream propagation and the WorkSpace/external-collaboration continuation. The current Task Registry truth is `StegVerse-Labs/.github:data/canonical-task-records/SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003.json`; the portable resident-dispatch mirror is `StegVerse-Labs/.github:docs/SDK_WORKSPACE_EXTERNAL_COLLAB_PORTABLE_DISPATCH_MIRROR_HANDOFF.md`.

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

## Merged implementation / validation state

The previously documented WorkSpace/external-collaboration source chain through SDK #189, TVC #397, and StegVerse-Labs/.github #1370 remains merged and valid. Subsequent canonical coordination has advanced further:

- SDK #195 merged at `2c88e7079e92c129eb10ca47093c1e5ed423911a`; External Collaboration Authentic Runtime Proof Contract Validation run `34557481930` PASS. The contract requires resident source custody and resident-seal liveness before authentic reseal consumption/target custody, and requires target custody plus sovereign callback reachability before owner-present Google consent.
- StegVerse-Labs/.github #1382 merged the resident consent-listener dispatcher source. Source/merge is not a consumption receipt and is not callback reachability proof.
- StegVerse-Labs/.github #1393 merged at `312a31976bf5e794aa3912c2aa2c9ce0016c1102` from source head `cab250db7895e13fe63721d72497a64be020d0e0`, repairing the portable exact-dispatch path for the already-owned resident selectors. Exact validation runs `34558793611`, `34558793613`, `34558793653`, and `34558793622` passed.
- #1393 forwards only the documented non-secret consent-listener inputs (`STEGVERSE_GOOGLE_DRIVE_CLIENT_ID`, `STEGVERSE_OWNER_BINDING_DIGEST`, `STEGVERSE_STEGFIN_SOURCE_ROOT`). It does not create GitHub runtime authority, a hosted fallback, a second resident executor, or credential authority.

README review: current public SDK semantics remain accurate. These changes alter resident dispatch/evidence coordination only; they do not introduce a new public SDK capability identifier, universal ingress class, CLI route, or user-facing WorkSpace product surface.

## External-collaboration authority boundary

```text
credential class: TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001
purpose: EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY
provider slot: google_drive_external_collaboration
vault ref: vault://tvc/providers/google-drive/external-collaboration-session
client-secret SKAP purpose: google_drive.external_collaboration.client_secret
operation: external_collaboration_resource_probe
binding prefix: wsprobe_
public callback: https://stegverse.org/tvc/google-drive/external-collaboration/callback
client-secret public ingress: https://stegverse.org/v1/skap/google-drive/external-collaboration/client-secret/ingress
Service Gateway owner: StegVerse-org/LLM-adapter#72
canonical resident carrier: StegVerse-Labs/.github:docs/CANONICAL_RESIDENT_CARRIER_MIRROR_HANDOFF.md
```

Controlling rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
Personal-KV client-secret custody != external-collaboration client-secret custody
KV _System/Workspace/** observation != authoritative external Shared Docs proof
source/CI/merge != authentic runtime proof
GitHub runtime authority = NONE
third-party/hosted fallback = FALSE
```

Machine-owned Service Gateway #72 remains the sole owner of the exact external-collaboration sovereign route implementation/runtime proof. Do not create a competing gateway, tunnel, callback implementation, or third-party runtime dependency.

## Authentic runtime proof ordering

`docs/EXTERNAL_COLLAB_AUTHENTIC_RUNTIME_PROOF_CONTRACT.md` remains authoritative. The required evidence order is:

```text
authorized-resident Personal-KV source custody
+ current resident-seal liveness/private-key availability
-> authentic resident #1370 reseal consumption
-> exact external-collaboration target client-secret custody/readback
-> sovereign stegverse.org ingress + exact resident callback/listener reachability
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
Authentic-runtime proof contract including SDK #195 ordering: IMPLEMENTED / VALIDATED / MERGED
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

Reuse evidence from these lanes. Do not seize their components or infer runtime execution from merge/CI.

## Next executable sequence

1. Search the canonical resident evidence path for an authentic secret-free `RESIDENT-EXEC-SDK-WORKSPACE-EXTCOLLAB-CLIENT-SECRET-RESEAL-001` consumption receipt produced after the #1393 portable exact-dispatch repair.
2. Branch only on the authentic resident result:
   - `TARGET_ALREADY_PRESENT`: validate exact target-purpose client-secret custody/readback without overwrite.
   - `BLOCKED`: remediate the exact reported resident prerequisite through its canonical owner (source Personal-KV custody, resident seal/private-key liveness, TVC source materialization, or root resident execution).
   - `COMPLETED`: retain the secret-free reseal result and exact target custody/readback evidence; do not infer consent or provider contact.
3. Observe the existing resident consent-listener selector and machine-owned Service Gateway #72. Require authentic `stegverse.org` ingress and exact callback/listener reachability evidence.
4. Only after target custody and callback reachability are proven, execute owner-present Google consent on the current iPhone.
5. Execute one exact authoritative external provider-file metadata probe and feed only the secret-free result/use evidence through the SDK bridge and active-probe engine.
6. Complete lifecycle/MIR reporting, Master Records custody/reconstruction, one-current-device proof, downstream propagation, and public-distribution evidence.

## Current status

```text
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
COSV: 71000000100110
SDK #195: MERGED / EXACT CONTRACT VALIDATION PASS
StegVerse-Labs/.github #1382: MERGED resident consent-listener dispatcher source
StegVerse-Labs/.github #1393: MERGED / EXACT VALIDATION PASS / portable exact-dispatch repaired
resident reseal consumption receipt: NOT OBSERVED
resident consent-listener consumption receipt: NOT OBSERVED
authentic target client-secret custody: NOT PROVEN
authentic sovereign callback reachability: NOT PROVEN
authentic owner-present Google consent: NOT PROVEN
authentic provider probe: NOT PROVEN
propagation complete: FALSE
manual user work required now: NONE
```
