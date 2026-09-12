# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-11
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / CONTENT-INTEGRITY SOURCE MERGED / AUTHENTIC PROVIDER OBSERVATION NEXT`

## Goal

Integrate Shared Docs multiparty freeze with provider observations and admitted document mutations while preserving TV/TVC provider authority, Interlock/InTr transition authority, immutable prior revision provenance, and one-current-device operation.

## Merged source chain

- Shared Docs freeze source: `d505e937dd9f5e531c56427d7477e026789e4769`.
- SDK provider-neutral freeze binding PR #209: `5d3c882eb975720651bfac7f2b08dc3f4da4cdfc`.
- SDK TVC provider-version/fail-closed digest seam PR #210: `6eab366b96474b5146e51da7d4062b5a061cb707`.
- TVC Shared Docs content-integrity lease/runtime PR #414: `2b8183cfbc148617a6ea714f2c2e6fb293004615`.
- steggfin-governance bounded provider/vault content-integrity operation PR #98: `6c26a15cbc72bb79167ed5abf7d82b00a7cb7a9c`.

Exact-head validation before merge:

- TVC External Collaboration Google Drive Content Integrity Validation `34670605754`: PASS.
- steggfin External Collaboration Google Drive Content Integrity Validation `34670598778`: PASS.
- steggfin External Collaboration Google Drive Probe Broker Validation `34670598802`: PASS.
- steggfin Validate StegWallet governance `34670598790`: PASS.
- steggfin Validate Governance `34670598880`: PASS.
- steggfin iOS first-passkey PREPARE validation `34670598883`: PASS.

## Implemented content-integrity profile

The source now defines a separate read-only provider operation:

```text
provider: google_drive_external_collaboration
operation: external_collaboration_content_integrity
content_profile: google-drive.downloaded-bytes.v1
credential authority: TV/TVC
provider mutation: prohibited
secret export: prohibited
```

For ordinary downloadable Google Drive resources, the provider/vault path:

1. reads provider metadata and captures the exact provider version;
2. rejects Google-native resources because no canonical export profile is defined yet;
3. downloads the exact bounded file bytes inside the non-exportable provider path;
4. computes SHA-256 over those exact bytes;
5. re-reads provider metadata and rejects the observation if the provider version changed during the bounded read;
6. returns only secret-free document/version/content-profile/content-SHA evidence.

Unsupported or unstable content fails `CONTENT_DIGEST_UNAVAILABLE`; metadata hashes, file names, timestamps, MD5 values, and provider version labels are never substituted for exact reviewed-content SHA-256.

TVC issues a separate single-use purpose-bound lease and returns secret-free evidence containing the same provider document identity, provider version, `provider_content_sha256`, and canonical content profile. No provider authority is transferred to SDK or Shared Docs.

## Existing SDK freeze intake

The SDK binds provider observations to exact Shared Docs `document_id + revision_id + review_epoch + content_digest`. Freeze-state projection remains metadata-only and does not mutate reviewed bytes. An admitted provider-observed edit may create a successor revision only with an explicit Interlock/InTr transition reference; prior frozen provenance remains immutable.

## Proof classes

Source validation, authentic provider content-integrity observation, resident execution, provider mutation, provider-side freeze enforcement, and external synchronization remain distinct. The merged source does **not** prove that a real provider document has yet been read through this new operation.

## Current next action

Materialize an authentic TV/TVC content-integrity observation on the existing resident/provider path for a downloadable Shared Docs resource and retain the secret-free result showing the same provider document ID + provider version + `google-drive.downloaded-bytes.v1` + exact SHA-256. Feed that authentic result through the existing SDK Shared Docs provider observation seam and bind it to an immutable revision. If no qualifying downloadable provider resource is available, preserve `CONTENT_DIGEST_UNAVAILABLE` rather than synthesizing evidence. No second user-operated device is permitted.
