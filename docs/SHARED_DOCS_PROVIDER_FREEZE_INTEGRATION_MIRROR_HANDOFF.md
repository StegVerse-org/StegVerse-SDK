# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-11
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / PROVIDER BINDING + TVC VERSION SEAM MERGED / CONTENT-INTEGRITY OBSERVATION NEXT`

## Goal

Integrate the merged provider-neutral multiparty freeze state machine with Shared Docs provider observations and admitted document mutations without transferring provider, governance, custody, or execution authority.

## Merged evidence

Parent Shared Docs freeze source merged at:

```text
d505e937dd9f5e531c56427d7477e026789e4769
```

Provider-neutral freeze binding SDK PR `#209` merged at:

```text
5d3c882eb975720651bfac7f2b08dc3f4da4cdfc
```

Exact head `0a685e673293a5e8738c7a6fc841827b7cc49d15` passed:

- Shared Docs Provider Freeze Integration Validation `34635628063`;
- SDK Package Artifact Validation `34635628245`.

TVC provider-version evidence seam SDK PR `#210` merged at:

```text
6eab366b96474b5146e51da7d4062b5a061cb707
```

Exact head `abc58f07832356cbf19cb0a64b9942d85565d42d` passed:

- WorkSpace TVC Provider Probe Bridge Validation `34635986800`;
- SDK Package Artifact Validation `34635986945`;
- Shared Docs Provider Freeze Integration Validation `34635987038`.

## Current implemented contract

The SDK now has provider-neutral evidence-only Shared Docs freeze binding and an explicit TVC-backed intake seam.

A provider observation binds:

```text
provider
provider_document_id
provider_version_id
content_digest
observed_at
observation_ref
provider_authority = TV/TVC
provider_mutation_performed = false
authority_effect = NONE_EVIDENCE_ONLY
observation_sha256
```

The binding attaches that exact observation to Shared Docs `document_id + revision_id + review_epoch + content_digest` and records `TV/TVC` as provider authority and `Interlock/InTr` as transition authority. The binding grants neither authority.

Freeze-state projection is metadata-only:

```text
reviewed_bytes_mutated = false
provider_write_performed = false
authority_effect = NONE_METADATA_PROJECTION_ONLY
```

An admitted provider-observed content mutation may create a successor only when provider identity/document identity are unchanged, provider version advances, reviewed-content digest changes, and an explicit admitted `Interlock/InTr` transition reference is supplied. The prior frozen revision remains immutable provenance; the successor starts `REVIEW_OPEN` with no inherited freeze receipts.

## TVC evidence seam

The existing `stegverse/tvc_provider_probe_bridge.py` now validates the nested Google Drive resource observation and preserves exact provider `version` as `provider_version_id`.

If an exact `provider_content_sha256` is supplied by TVC/provider evidence, it is projected. If it is absent, `provider_observation_from_active_probe()` fails closed with `provider content SHA-256 unavailable for exact freeze binding`.

The SDK MUST NOT infer reviewed-content identity from mutable metadata, file names, timestamps, provider version labels, MD5 metadata, or the hash of the metadata observation itself.

## Remaining content-integrity work

The current shipped external-collaboration Google Drive probe is metadata-only. It can prove provider resource identity/version and read-only reachability, but it does not yet produce the exact canonical SHA-256 of reviewed content required for a freeze binding.

The next implementation step is therefore a separate read-only TV/TVC provider content-integrity operation that:

1. binds the same provider document ID and provider version;
2. uses an explicitly versioned canonical content profile;
3. computes SHA-256 inside the non-exportable provider/vault execution path;
4. returns only the secret-free digest/profile/version evidence needed by Shared Docs;
5. performs no provider mutation and transfers no provider authority;
6. fails `CONTENT_DIGEST_UNAVAILABLE` for unsupported provider content types rather than substituting metadata-derived hashes;
7. remains operable from the one current user device with no second user-operated machine.

For Google-native documents, no canonical export representation is assumed yet; the content profile must be explicitly defined before those bytes can satisfy exact freeze binding. For ordinary downloadable files, exact downloaded bytes can be a candidate profile once implemented and validated.

## Proof classes

Source validation, provider metadata observation, provider content-integrity observation, provider mutation, resident execution, and external provider synchronization remain separate proof classes. None may be promoted into another without corresponding evidence.

## Current next action

Implement and validate the bounded TV/TVC read-only content-integrity observation contract, beginning with exact-byte downloadable Google Drive resources. Do not claim authentic content-integrity observation until a real provider result supplies the same document/version plus exact canonical SHA-256.
