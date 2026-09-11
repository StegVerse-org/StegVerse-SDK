# SDK Generic Manifest Downstream Propagation Mirror Handoff

Updated: 2026-09-10

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
source_goal: SDK-PROCESSOR-GENERIC-MANIFEST-002
source_cosv: 71000000100110
continuation_goal: SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003
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

## WorkSpace / external-collaboration implementation chain

```text
SDK #174 state-transition evidence: MERGED ee8f7023d74d70fa762e3982776c27c1e372a1f7
SDK #176 canonical ingress -> external Interlock binding: MERGED 7047e67d21173e800f78d4468519dba87992b16d
StegVerse-org/.github #9 generic INTERNAL_ENDPOINT dispatch: MERGED d8baefb8674ebed00bbbf9784c54e092a5b1a04d
SDK #179 provider-neutral WorkSpace resource consumer: MERGED 07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c
StegVerse-org/.github #10 WorkSpace endpoint binding: MERGED b851996afc5c5323d0d0db970dd46e511bd36338
SDK #181 provider-neutral active-probe execution: MERGED 5c8a3c0246a0ae48e498c10f85d9eee0a2d1ba2c
SDK #182 secret-free TVC provider evidence bridge: MERGED 43519567d036d1d87d5866ae825ffee54acec08f
TVC #381 Personal-KV _System/Workspace/** semantic probe: MERGED bcf872cf0ce24a2cc653aabdaa8b25c34d0e4402 / KV-SCOPED ONLY
SDK #184 WorkSpace-specific TVC result bridge: MERGED 97b2a5f018a261dc27370448fa1eb73644418d66
TVC #383 distinct external-collaboration consent/session class: MERGED ccbeae7ab03c23045b92db3a293b562422980cac
stegfin-governance #95 distinct external-collaboration vault ref/provider slot: MERGED 35a058488c0a2a3dddeafdb59befcd19488e3c2a
TVC #384 distinct external-collaboration SKAP refresh/session custody: MERGED b7e8fd3f3f498e2cae6efb01c511a68d6ab7bd8c
stegfin-governance #96 exact metadata-only provider probe + durable pre-provider replay: MERGED 66c1abbcc74a0a53fe6436b1fa003759acacaad6
TVC #385 exact external-file probe lease/runtime: MERGED 4a3cc09dc5e85c051b9820dd83f6b2373e6316a7
SDK #186 external-collaboration TVC result bridge: MERGED f2f9a7f385477c8096a50fc223333240060e0a2f
```

SDK #186 exact-head validations all passed:

```text
WorkSpace TVC Provider Probe Bridge Validation 34551543442: PASS
SDK Package Artifact Validation 34551543443: PASS
Manifest Builder Source Validation 34551543452: PASS
WorkSpace Active Probe Validation 34551543495: PASS
```

Two noncanonical attempts remain intentionally closed and unmerged: TVC #382 and stegfin-governance #94. They attempted to reuse Personal-KV consent for arbitrary external collaborative files. That model is prohibited.

TVC #380 is also closed unmerged as superseded. Its Personal-KV reuse premise cannot govern independently controlled external collaborative resources.

## External-collaboration boundary

```text
credential class: TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001
purpose: EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY
OAuth state purpose: extcollab.*
provider slot: google_drive_external_collaboration
vault ref: vault://tvc/providers/google-drive/external-collaboration-session
operation: external_collaboration_resource_probe
binding prefix: wsprobe_
TVC result: stegverse.tvc.external-collaboration-google-drive-probe-result/v1
broker observation: stegverse.tvc.google-drive-external-collaboration-metadata-probe/v1
```

Controlling rules:

```text
technical token reach != consent authority
Personal-KV consent != external-collaboration consent
KV _System/Workspace/** observation != authoritative external Shared Doc proof
TVC/provider/broker evidence != readiness authority
```

The exact provider probe binds one provider file ID and one active-probe reason, is single-use with lease duration <=300 seconds, performs metadata GET only, downloads no document content, exports no credential material, grants no provider mutation authority, and cannot assign readiness. Durable replay is consumed before provider invocation. The SDK validates the exact result and projects only non-authorizing active-probe evidence; the active-probe engine recomputes readiness after complete predicate evaluation.

## Current proof boundary

```text
Generic ingress + Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Generic WorkSpace consumer + organization endpoint: IMPLEMENTED / VALIDATED / MERGED
Active-probe execution: IMPLEMENTED / VALIDATED / MERGED
Personal-KV WorkSpace semantic probe: IMPLEMENTED / VALIDATED / MERGED / KV-SCOPED ONLY
External-collaboration consent/session class: IMPLEMENTED / VALIDATED / MERGED
External-collaboration SKAP refresh/session custody: IMPLEMENTED / VALIDATED / MERGED
External-collaboration resident vault ref/provider slot: IMPLEMENTED / VALIDATED / MERGED
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

Source, CI, merge, or request construction must not be promoted into provider/runtime proof.

## Public runtime distribution boundary

```text
StegCore public distribution: stegverse-stegcore
StegCore target version: 0.3.0
StegCore rename PR #197: MERGED
Master Records public distribution: stegverse-master-records
Master Records target version: 0.2.0
Master Records Trusted Publishing PR #85: MERGED
SDK successor PR #165: SOURCE_CANDIDATE / DRAFT
SDK successor version: 1.3.0
first proven anonymous-install blocker: stegverse-stegcore==0.3.0 NOT PUBLISHED
release/tag/publication claim: NONE
```

Actual SDK 1.3.0 release still requires TV/TVC release authorization, required SKAP evidence, immutable tag/release, public Trusted Publisher provenance, anonymous governed-runtime install PASS, and ELAN custody/replay/reconstruction PASS. Do not weaken the anonymous installation gate.

## Downstream ownership

```text
StegVerse-Labs/Site: REQUIRED / MACHINE_OWNED / completion FALSE
StegVerse-Labs/admissibility-wiki: REQUIRED / Worker D OWNED / completion FALSE
GCAT-BCAT-Engine/Publisher: NO_DIRECT_CONTRACT_CHANGE
StegVerse-002/stegguardian-wiki: NO_DIRECT_CONTRACT_CHANGE
```

External sessions must not duplicate Site or Worker D-owned implementation.

## Next executable sequence

1. Determine whether a correctly scoped external-collaboration Google owner session is already authentically active. Do not infer this from source or CI.
2. If absent, execute owner-present consent through the distinct external-collaboration controller on the current device.
3. Execute one authentic exact provider-file metadata probe through the merged TVC lease/runtime and durable broker; retain the secret-free result/use receipt.
4. Feed that exact result through the SDK bridge and active-probe engine; verify `PROBE_REQUIRED -> READY` only when the named predicate is actually satisfied and no other applicable predicate remains unresolved.
5. Continue the authoritative-provider `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY` lifecycle.
6. Retain MIR transition reporting, independent Master Records custody/reconstruction, and one-current-device evidence.
7. Continue observing Site/Worker D and public-runtime publication dependencies without colliding with their owners.

## Current status

```text
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
COSV: 71000000100110
propagation complete: FALSE
authentic owner-present external-collaboration consent: NOT PROVEN
authentic provider probe: NOT PROVEN
manual user work required now: NONE
```

## README maintenance

Root README remains current for the source units above. They do not introduce a new public processing capability identifier, universal ingress class, public CLI/runtime route, or user-facing WorkSpace surface. README must change when an externally observable Shared Docs/WorkSpace workflow is introduced.
