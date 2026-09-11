# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / EXTERNAL-COLLAB CONSENT CLASS MERGED / SEALED SESSION + EXACT PROVIDER PROBE BINDING NEXT`

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
  -> TVC provider evidence path
       -> consent/session class appropriate to the authoritative external resource
       -> non-exportable TV/TVC/SKAP custody + vault broker
       -> exact provider-resource probe
  -> SDK secret-free TVC provider evidence bridge
```

The canonical external-resource rule is now explicit:

```text
technical token reach != consent authority
Personal-KV consent != arbitrary external-collaboration consent
KV `_System/Workspace/**` observation != proof of the authoritative external Shared Doc
```

A provider token or OAuth scope must not be reused outside the consent-purpose/credential class that authorized its use merely because the provider would technically accept the request.

## Completed implementation chain

```text
SDK PR #174: state-transition evidence MERGED at ee8f7023d74d70fa762e3982776c27c1e372a1f7
SDK PR #176: canonical ingress -> external Interlock binding MERGED at 7047e67d21173e800f78d4468519dba87992b16d
StegVerse-org/.github PR #9: generic INTERNAL_ENDPOINT dispatch MERGED at d8baefb8674ebed00bbbf9784c54e092a5b1a04d
SDK PR #178: collision-prevention coordination MERGED at 8a2dfe07294daacaa5d44d4777e94def182d8d78
SDK PR #179: provider-neutral WorkSpace resource consumer MERGED at 07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c
StegVerse-org/.github PR #10: WorkSpace endpoint binding MERGED at b851996afc5c5323d0d0db970dd46e511bd36338
SDK PR #181: provider-neutral active probe execution MERGED at 5c8a3c0246a0ae48e498c10f85d9eee0a2d1ba2c
SDK PR #182: TVC Google Drive result evidence bridge MERGED at 43519567d036d1d87d5866ae825ffee54acec08f
TVC PR #381: Personal-KV `_System/Workspace/**` WorkSpace semantic probe adapter MERGED at bcf872cf0ce24a2cc653aabdaa8b25c34d0e4402
SDK PR #184: WorkSpace-specific TVC result bridge support MERGED at 97b2a5f018a261dc27370448fa1eb73644418d66
TVC PR #383: distinct external-collaboration Google Drive owner-session class MERGED at ccbeae7ab03c23045b92db3a293b562422980cac
```

Validation evidence includes:

```text
TVC WorkSpace Google Drive Probe Validation 34548963700: PASS
SDK WorkSpace TVC Provider Probe Bridge Validation 34549046178: PASS
SDK Package Artifact Validation 34549046169: PASS
TVC PR #383 exact validated head: 0e3e2fa0272bb747438ee0f9a996546629d1427d
TVC Credential Model Consistency Validation 34549493296: PASS
```

## Correct interpretation of TVC PR #381

PR #381 exposes:

```text
request: stegverse.tvc.workspace-google-drive-probe-request/v1
result:  stegverse.tvc.workspace-google-drive-probe-result/v1
scope:   ["_System/Workspace/**"]
underlying credential class: TVC-PERSONAL-KV-GOOGLE-DRIVE-OWNER-SESSION-037
underlying binding class: kvpb_*
```

It composes over the already-admitted Personal-KV `personal_kv_materialize` read primitive. That is valid and useful for content already within the authoritative Personal-KV `_System/Workspace/**` boundary.

It is **not** evidence that an independently controlled external Shared Doc is authorized, observed, or synchronized. Copying or projecting an external document into KV cannot substitute for probing the authoritative external resource when the experiment requires external-system authority and live provider state.

## External-collaboration consent correction

Inspection after PR #381 showed that the existing owner session is explicitly credential class:

```text
TVC-PERSONAL-KV-GOOGLE-DRIVE-OWNER-SESSION-037
```

Even though its provider scope is Google `drive.readonly`, using it for arbitrary external collaborative resources would broaden the consent purpose. Two draft attempts to do so were therefore closed without merge:

```text
StegVerse-Labs/TVC PR #382: CLOSED / NOT MERGED
StegVerse-Labs/stegfin-governance PR #94: CLOSED / NOT MERGED
```

They are not capability evidence.

TVC PR #383 then implemented the corrected model with distinct credential class:

```text
TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001
purpose: EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY
broker session schema: stegverse.tvc.google-drive-external-collaboration-access-session/v1
OAuth state purpose binding: extcollab.*
```

PR #383 reuses the same Google OAuth transport and protected refresh-store interfaces; it does not create a second OAuth implementation. The distinction is consent/policy/session identity, not duplicated provider machinery.

Its source preserves exact `drive.readonly`, StegVerse HTTPS callback restrictions, protected refresh custody, secret-free receipts, non-mutation, and distinct lifecycle identity through authorization completion, refresh, and revocation.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence: IMPLEMENTED / VALIDATED / MERGED
Ingress -> external Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Generic INTERNAL_ENDPOINT dispatch: IMPLEMENTED / VALIDATED / MERGED
WorkSpace resource consumer: IMPLEMENTED / VALIDATED / MERGED
Organization-local WorkSpace endpoint binding: IMPLEMENTED / VALIDATED / MERGED
Provider-neutral active probe execution: IMPLEMENTED / VALIDATED / MERGED
TVC Personal-KV `_System/Workspace/**` probe adapter: IMPLEMENTED / VALIDATED / MERGED / KV-SCOPED ONLY
SDK WorkSpace-specific TVC provider evidence bridge: IMPLEMENTED / VALIDATED / MERGED
External-collaboration Google Drive consent/session class: IMPLEMENTED / VALIDATED / MERGED
External-collaboration sealed resident access-session materialization: NOT YET BOUND
External-collaboration vault-agent secret reference: NOT YET BOUND
External-collaboration exact provider-file probe lease/broker operation: NOT YET BOUND
Authentic owner-present external-collaboration Google consent: NOT PROVEN
Authentic authoritative Shared Docs provider probe: NOT PROVEN
Shared Docs live synchronization: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records authentic custody/reconstruction: NOT PROVEN
One-device authentic end-to-end execution: NOT PROVEN
```

Source, CI, merge, Personal-KV observation, or technical provider-token scope must not be promoted into external Shared Docs runtime proof.

## State-transition model

Document Share is treated as an ordinary governed abstract. A live edit, autosave, recipient/share change, authorization change, consent/session activation, refresh, revocation, expiry, projection creation, synchronization, or destruction is a candidate state transition. Interlock/InTr evaluates the complete applicable governance matrix for that transition context before the resultant state is admitted. Authority is one governed attribute within that matrix, not a fixed property assigned by component class.

## Next executable sequence

1. Bind `stegverse.tvc.google-drive-external-collaboration-access-session/v1` into the existing TV/TVC/SKAP protected-session materialization path under a distinct non-exportable vault reference.
2. Add an exact external-resource read/probe lease and resident broker operation that accepts only that external-collaboration session class; do not fall back to `personal_kv_materialize`, `kvpb_*`, or Personal-KV root/scope semantics.
3. Bind provider file identity + active-probe reason and retain secret-free provider metadata/state evidence with durable single-use replay protection.
4. Execute owner-present consent only after those source/admission boundaries are validated.
5. Execute one authentic authoritative external Shared Docs provider probe and feed the result through the merged SDK TVC evidence bridge/active-probe engine; verify `PROBE_REQUIRED -> READY` only when the exact unresolved predicate is satisfied.
6. Execute the Shared Docs lifecycle: `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY`.
7. Retain state-transition sequence, MIR reporting, independent Master Records custody/reconstruction evidence, and prove the complete flow on one current mobile device.

## Human action

None for the next source/custody/broker-binding work. Owner-present Google authorization is required only when the authentic external-collaboration session is activated and no correctly scoped current session exists.
