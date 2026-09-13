# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-12
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / COMPONENT MODEL RECONCILED / WORKERCOORDINATOR SOURCE BINDING MERGED / AUTHENTIC PROVIDER OBSERVATION NEXT`

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

The already-merged `.github` consumer `control/resident-execution-request.d/consume-shared-docs-provider-content-integrity.py` remains bounded to task-specific translation/compatibility only and does not become a duplicate scheduler, credential/session owner, provider runtime, evidence engine, transition engine, or custody plane.

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
- `.github` exact current provider-observation request PR #1681: `c542d9bbf2994654247124dfb8cb8df9ba1ded51`.
- `.github` WorkerCoordinator binding PR #1689: merge `f84c8a42e2ec063581c6c1eda0a5ff25313fb001`.

PR #1689 exact head `0510e175e7a677bb6e20fb1aeea7eec3eb5cebdc` passed Organization Control run `34735618438`, Heartbeat Worker Validation run `34735618529`, and Deterministic Repository Suite run `34735618452` before merge.

The WorkerCoordinator merge includes the executable handoff, process adapter, worker registry fragment, bounded cost basis, worker wrapper, Admissible Existence projection, COSV index shard, valid COSV machine record, and reconciled live-worker coverage. Source validation therefore no longer depends on adding a task-specific selector to the generic resident dispatcher or its portable exact-dispatch allowlist.

## Exact current provider request

Canonical `.github` source contains `control/resident-execution-request.d/shared-docs-provider-content-integrity-001.json`, binding the current Goal Task to `Global_Interlock_InTr_Node_Test.txt` using provider file ID `1uTDq29Q5gEmnqY18u8JCRPlUBGkCYqOE`, `google-drive.downloaded-bytes.v1`, read-only posture, no provider mutation, no credential material, and TV/TVC credential authority.

The request is source intent only. Its merge is not resident visitation, credential/session use, provider execution, or content-digest evidence.

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

Source construction is complete through the canonical WorkerCoordinator addressability path. Authentic runtime evidence is still required for: resident execution; WorkerCoordinator claim/fence; TV/TVC provider credential/session use; provider content-integrity execution; exact provider version/content SHA for the selected invocation; SDK binding of that authentic result; Master Records custody/reconstruction; and any conditional Interlock/InTr successor-revision transition.

No source merge, CI pass, workflow run, or registry record substitutes for those runtime observations.

## Runtime addressability boundary

The prior source-addressability plan to add `shared_docs_provider_content_integrity` to the generic resident dispatcher and portable exact-dispatch allowlist is superseded by the merged canonical WorkerCoordinator binding in `.github` PR #1689. No duplicate dispatcher or second execution plane is to be created.

The active path is now:

`canonical task record -> WorkerCoordinator claim/fence -> shared-docs provider content-integrity process adapter -> bounded worker -> existing TV/TVC content-integrity runtime -> secret-free provider observation receipt`.

That receipt then continues through the already-selected reusable evidence normalization/custody components and, only if an observed edit requires it, through Interlock/InTr for a successor-revision transition.

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

Use the canonical WorkerCoordinator path now merged in `.github` to claim/fence and execute one exact read-only provider observation on an eligible sovereign resident. Retain authentic document/version/`google-drive.downloaded-bytes.v1`/SHA-256 evidence, normalize it through the existing SDK seam, and submit required evidence to Master Records. Use Interlock/InTr only if the observed provider state requires a successor-revision transition. No second user-operated device is permitted.
