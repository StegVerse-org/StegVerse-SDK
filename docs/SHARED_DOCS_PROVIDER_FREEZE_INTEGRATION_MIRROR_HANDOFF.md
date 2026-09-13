# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-12
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / REUSABLE COMPONENT MODEL RECONCILED / AUTHENTIC PROVIDER OBSERVATION NEXT`

## Goal

Integrate Shared Docs multiparty freeze with provider observations and admitted document mutations while preserving TV/TVC provider authority, Interlock/InTr transition authority, immutable prior revision provenance, and one-current-device operation.

## Reusable Task Component Model reconciliation

The Goal Task identity and COSV remain unchanged. The deterministic decomposition signals exceed the STOP-SCOPE-GROWTH threshold, so no additional task-specific orchestration may be added before reuse composition is applied.

Canonical profile:

`StegVerse-Labs/.github:data/goal-task-component-profiles/SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001.json`

Canonical evaluation:

`StegVerse-Labs/.github:data/goal-task-componentization-evaluations/SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001.json`

Selected reusable/canonical components are intentionally narrower than the maximal transport chain:

1. `RTC-MANIFEST-001` — exact provider observation request manifest plus task/COSV/provider-target binding.
2. Existing sovereign resident runtime-observation surface — authentic resident visitation/receipt only; no authority minted.
3. Existing TV/TVC Google Drive content-integrity lease/runtime plus steggfin non-exportable provider operation — bounded read-only exact-byte observation.
4. `RTC-ROUNDTRIP-003` — one provider request/response cycle per observed provider revision.
5. `RTC-SDK-RETURN-006` — normalize the authentic provider result into the SDK provider-observation/freeze-binding seam.
6. `RTC-EVIDENCE-CUSTODY-004` — Master Records custody/readback/reconstruction for completion evidence.
7. `RTC-INTERLOCK-INTR-TRANSPORT-008` — conditional only when an observed edit must create an admitted successor Shared Docs revision.

Not selected: Publisher projection, StegVerse final egress, far-side final transition. They are not required for this Goal Task's current provider-freeze integration semantics.

The already-merged `.github` consumer `control/resident-execution-request.d/consume-shared-docs-provider-content-integrity.py` is now bounded as a task-specific translator/compatibility shim. It must not be extended into a parallel resident scheduler, credential/session owner, provider runtime, evidence engine, Interlock/InTr transition engine, or custody/reconstruction system.

No genuinely new reusable capability was discovered: provider content-integrity observation already exists canonically in TVC/stegfin; SDK normalization already exists; runtime observation, Interlock/InTr, WorkerCoordinator, and Master Records retain their existing ownership.

## Canonical authority map

- Task Registry: coordination only.
- WorkerCoordinator: claim/fence authority when execution claim/fence is required.
- KV/SKAP Vault: sole user-verification authority; no device-local user verification is introduced.
- StegOS device: interchangeable transport/execution node only.
- TV/TVC: credential/session/provider-operation authority.
- Interlock/InTr: governed state-transition/admission authority for successor-revision transitions.
- Master Records: observed-reality custody/readback/reconstruction.
- HeartBeat: timing, freshness, liveness, correlation, and observability only.
- GitHub: source/evidence coordination only; no runtime authority.

## Merged source chain

- Shared Docs freeze source: `d505e937dd9f5e531c56427d7477e026789e4769`.
- SDK provider-neutral freeze binding PR #209: `5d3c882eb975720651bfac7f2b08dc3f4da4cdfc`.
- SDK TVC provider-version/fail-closed digest seam PR #210: `6eab366b96474b5146e51da7d4062b5a061cb707`.
- TVC Shared Docs content-integrity lease/runtime PR #414: `2b8183cfbc148617a6ea714f2c2e6fb293004615`.
- steggfin-governance bounded provider/vault content-integrity operation PR #98: `6c26a15cbc72bb79167ed5abf7d82b00a7cb7a9c`.
- `.github` resident content-integrity translator PR #1571: `27f4f33abdccaf3427151f5d81eb4c972678b448`.

Exact-head validation before those merges remains source validation only and does not substitute for runtime evidence.

## Provider content-integrity profile

The canonical operation remains:

```text
provider: google_drive_external_collaboration
operation: external_collaboration_content_integrity
content_profile: google-drive.downloaded-bytes.v1
credential authority: TV/TVC
provider mutation: prohibited
secret export: prohibited
```

For an ordinary downloadable provider resource, TV/TVC captures provider version, performs the bounded exact-byte read inside the non-exportable path, computes SHA-256, rechecks provider version, and returns only secret-free provider document/version/content-profile/content-SHA evidence. Unsupported or unstable content remains `CONTENT_DIGEST_UNAVAILABLE`; metadata must not be substituted for reviewed-content SHA-256.

## Existing SDK freeze intake

The SDK binds authentic provider observations to exact Shared Docs `document_id + revision_id + review_epoch + content_digest`. Freeze-state projection remains metadata-only and does not mutate reviewed bytes. An admitted provider-observed edit may create a successor revision only through the conditional Interlock/InTr component; prior frozen provenance remains immutable.

## Goal-specific remaining predicates

- `PROVIDER_DOCUMENT_ID_BOUND_TO_LOGICAL_DOCUMENT`
- `PROVIDER_VERSION_BOUND_TO_IMMUTABLE_REVISION`
- `PROVIDER_CONTENT_DIGEST_BOUND_TO_FREEZE_REVISION`
- `FREEZE_METADATA_PROJECTION_DOES_NOT_MUTATE_REVIEWED_BYTES`
- `ADMITTED_EDIT_CREATES_SUCCESSOR_REVISION`
- `STALE_PROVIDER_REVISION_FREEZE_REJECTED`
- `PRIOR_FROZEN_PROVIDER_REVISION_PROVENANCE_PRESERVED`
- `PROVIDER_MUTATION_AUTHORITY_REMAINS_TV_TVC`
- `GOVERNED_TRANSITION_AUTHORITY_REMAINS_INTERLOCK_INTR`
- `ONE_CURRENT_DEVICE_OPERATION_PRESERVED`

## Runtime/evidence state

Source construction and validation exist for the provider-integrity path, but authentic resident execution, TV/TVC provider operation, exact provider version/content SHA evidence for the selected invocation, SDK binding of that authentic result, Master Records custody/reconstruction, and any conditional Interlock/InTr successor-revision transition remain separately evidenced requirements.

The previously selected real downloadable provider target remains `Global_Interlock_InTr_Node_Test.txt` (`provider_file_id=1uTDq29Q5gEmnqY18u8JCRPlUBGkCYqOE`). The old request PR #1575 is historical source evidence but is not the continuation owner because its branch diverged from main before this component reconciliation.

## Current next action

After the component-profile/task-record reconciliation validates and merges, rematerialize the exact read-only provider request as Goal Task-specific configuration on current `.github` main without adding a new orchestration layer. Then invoke it through the existing resident dispatcher + TV/TVC reusable path, retain the authentic document/version/`google-drive.downloaded-bytes.v1`/SHA-256 evidence, pass it through the existing SDK return/freeze-binding seam, and submit required evidence to Master Records. Use Interlock/InTr only if an observed provider edit requires a successor-revision transition. No second user-operated device is permitted.
