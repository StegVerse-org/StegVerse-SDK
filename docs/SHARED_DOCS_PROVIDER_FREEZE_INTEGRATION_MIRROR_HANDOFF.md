# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-12
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / REUSABLE COMPONENT MODEL RECONCILED / AUTHENTIC PROVIDER OBSERVATION NEXT`

## Goal

Integrate Shared Docs multiparty freeze with provider observations and admitted document mutations while preserving TV/TVC provider authority, Interlock/InTr transition authority, immutable prior revision provenance, and one-current-device operation.

## Reusable Task Component Model reconciliation

The Goal Task identity and COSV remain unchanged. Canonical component profile: `StegVerse-Labs/.github:data/goal-task-component-profiles/SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001.json`.

Selected components/canonical owners:
1. `RTC-MANIFEST-001` for exact provider request manifest + task/COSV/provider-target binding.
2. `GLOBAL-RUNTIME-EVIDENCE-MEASUREMENT-001` for authentic resident/runtime observation.
3. Existing TV/TVC provider content-integrity runtime plus steggfin non-exportable provider operation.
4. `RTC-ROUNDTRIP-003` for provider request/response correlation.
5. `RTC-SDK-RETURN-006` for provider-result normalization into Shared Docs freeze intake.
6. `RTC-EVIDENCE-CUSTODY-004` for Master Records custody/readback/reconstruction.
7. `RTC-INTERLOCK-INTR-TRANSPORT-008` only when an observed edit requires a successor-revision transition.

Not selected: Publisher projection, StegVerse final egress, far-side final transition, terminal cleanup/entropy recovery.

The already-merged `.github` consumer `control/resident-execution-request.d/consume-shared-docs-provider-content-integrity.py` is bounded to task-specific translation/compatibility only and must not become a duplicate scheduler, credential/session owner, provider runtime, evidence engine, transition engine, or custody plane.

No genuinely new reusable capability was discovered.

## Authority map

- Task Registry: coordination only.
- WorkerCoordinator: claim/fence authority.
- KV/SKAP Vault: sole user-verification authority.
- StegOS device: interchangeable transport/execution node only.
- TV/TVC: credential/session/provider-operation authority.
- Interlock/InTr: governed transition/admission authority.
- Master Records: observed-reality custody/readback/reconstruction.
- HeartBeat: timing/freshness/liveness/correlation/observability only.
- GitHub: source/evidence coordination only.

## Merged source chain

- Shared Docs freeze source: `d505e937dd9f5e531c56427d7477e026789e4769`.
- SDK provider-neutral freeze binding PR #209: `5d3c882eb975720651bfac7f2b08dc3f4da4cdfc`.
- SDK TVC provider-version/fail-closed digest seam PR #210: `6eab366b96474b5146e51da7d4062b5a061cb707`.
- TVC Shared Docs content-integrity lease/runtime PR #414: `2b8183cfbc148617a6ea714f2c2e6fb293004615`.
- steggfin-governance bounded provider/vault content-integrity operation PR #98: `6c26a15cbc72bb79167ed5abf7d82b00a7cb7a9c`.
- `.github` resident content-integrity translator PR #1571: `27f4f33abdccaf3427151f5d81eb4c972678b448`.

## Provider content-integrity profile

```text
provider: google_drive_external_collaboration
operation: external_collaboration_content_integrity
content_profile: google-drive.downloaded-bytes.v1
credential authority: TV/TVC
provider mutation: prohibited
secret export: prohibited
```

For an ordinary downloadable provider resource, TV/TVC captures provider version, performs the bounded exact-byte read inside the non-exportable path, computes SHA-256, rechecks provider version, and returns only secret-free provider document/version/content-profile/content-SHA evidence. Unsupported or unstable content remains `CONTENT_DIGEST_UNAVAILABLE`; metadata must not substitute for reviewed-content SHA-256.

## Existing SDK freeze intake

The SDK binds authentic provider observations to exact Shared Docs `document_id + revision_id + review_epoch + content_digest`. Freeze-state projection remains metadata-only and does not mutate reviewed bytes. A provider-observed edit may create a successor revision only through Interlock/InTr; prior frozen provenance remains immutable.

## Runtime/evidence state

Source construction/validation exists. Still pending as authentic evidence: resident execution; WorkerCoordinator claim/fence when required; TV/TVC provider credential/session use; provider content-integrity execution; exact provider version/content SHA for the selected invocation; SDK binding of that authentic result; Master Records custody/reconstruction; and any conditional Interlock/InTr successor-revision transition.

The selected real downloadable provider target remains `Global_Interlock_InTr_Node_Test.txt` (`provider_file_id=1uTDq29Q5gEmnqY18u8JCRPlUBGkCYqOE`). Historical PR #1575 is not the continuation owner because its branch diverged before component reconciliation.

## Goal-specific completion predicates

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

## Current next action

After component-profile/task-record reconciliation merges, rematerialize the exact read-only provider request as Goal Task-specific configuration on current `.github` main without adding a new orchestration layer. Then invoke it through the existing resident observation + TV/TVC path, retain authentic document/version/`google-drive.downloaded-bytes.v1`/SHA-256 evidence, normalize through the SDK seam, and submit required evidence to Master Records. Use Interlock/InTr only if an observed edit requires a successor-revision transition. No second user-operated device is permitted.
