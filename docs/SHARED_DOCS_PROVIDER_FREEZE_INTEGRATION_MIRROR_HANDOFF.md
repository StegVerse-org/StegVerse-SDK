# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-11
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / PROVIDER-NEUTRAL BINDING MERGED / TVC EVIDENCE SEAM IN VALIDATION`

## Goal

Integrate the merged provider-neutral multiparty freeze state machine with Shared Docs provider observations and admitted document mutations without transferring provider, governance, custody, or execution authority.

## Starting evidence

Parent source implementation is merged on SDK `main` at:

```text
d505e937dd9f5e531c56427d7477e026789e4769
```

Parent exact-head validation includes dedicated Shared Docs freeze run `34568759924` PASS plus all applicable SDK lanes PASS.

## Provider-neutral binding merge

SDK PR `#209` merged at:

```text
5d3c882eb975720651bfac7f2b08dc3f4da4cdfc
```

Its exact head `0a685e673293a5e8738c7a6fc841827b7cc49d15` passed:

- Shared Docs Provider Freeze Integration Validation `34635628063`;
- SDK Package Artifact Validation `34635628245`.

That merge establishes source-level provider observation/binding semantics only. It does not prove an authentic provider observation, provider mutation, provider-side freeze enforcement, resident execution, or external synchronization.

## Provider seam inspection

The existing SDK provider seam is `stegverse/tvc_provider_probe_bridge.py`. It consumes secret-free TVC-owned Google Drive evidence and preserves these constraints:

- credential authority remains `TV/TVC`;
- SDK does not obtain provider credentials or execute provider operations in the bridge;
- provider results are evidence-only;
- external collaboration probes are read-only and may not assign readiness;
- provider mutation authority is not transferred.

The current TVC external-collaboration broker observation already carries Google Drive `version` inside the nested provider observation. The SDK previously discarded that field when normalizing the probe. It does not currently carry a canonical SHA-256 of reviewed content.

## Current TVC evidence-seam implementation

Branch `shared-docs-provider-freeze-tvc-binding-001` now:

1. validates the nested TVC provider resource observation;
2. requires and projects exact `provider_version_id` from the TVC-backed Google Drive metadata result;
3. optionally projects `provider_content_sha256` only when that exact SHA-256 is actually present;
4. adds `provider_observation_from_active_probe()` as the Shared Docs intake seam;
5. fails closed when provider metadata has version/reachability but no exact reviewed-content SHA-256;
6. prohibits deriving a content hash from mutable metadata, names, timestamps, provider version labels, or observation hashes;
7. preserves `TV/TVC` provider authority and prohibits provider-operation authority transfer.

This means the already-shipped metadata probe can establish exact provider resource/version evidence, but cannot yet be promoted to an exact freeze binding unless a trustworthy content SHA-256 is also supplied by an admitted TVC/provider operation.

## Provider-neutral observation contract

The merged provider observation contract binds:

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

The revision binding binds that observation to exact Shared Docs `document_id + revision_id + review_epoch + content_digest` and records `TV/TVC` as provider authority and `Interlock/InTr` as transition authority. The binding itself grants neither authority.

Freeze-state projection is metadata-only and records:

```text
reviewed_bytes_mutated = false
provider_write_performed = false
authority_effect = NONE_METADATA_PROJECTION_ONLY
```

## Admitted edit semantics

A provider-observed content mutation may create a Shared Docs successor only when all of the following hold:

1. the current revision and prior provider binding agree exactly;
2. provider identity and provider document identity are unchanged;
3. provider version advances;
4. reviewed content digest changes;
5. an explicit admitted `Interlock/InTr` transition reference is supplied;
6. the new provider observation still declares `TV/TVC` provider authority and evidence-only posture.

The prior frozen revision remains immutable provenance. The successor starts `REVIEW_OPEN` with no inherited freeze receipts and binds the newly observed provider version/content digest.

## Integration requirements

1. Map provider document identity/version metadata to canonical logical `document_id` and immutable `revision_id` without treating provider mutable names as revision identity.
2. Bind exact provider-observed content digest to the freeze-state revision.
3. Accept reviewer freeze actions only for the exact current revision/digest/review epoch.
4. Project `REVIEW_OPEN`, `PARTIALLY_FROZEN`, and `FROZEN` as lifecycle metadata without silently changing reviewed document bytes.
5. When an admitted content mutation occurs, create a successor revision and reset reviewer freezes while retaining prior frozen provenance.
6. Reject stale/replayed reviewer freezes against superseded provider versions.
7. Preserve provider/TVC mutation authority and Interlock/InTr transition authority; the freeze module does not write provider content by itself.
8. Retain enough secret-free evidence for Master Records reconstruction of revision lineage and freeze receipts.
9. Preserve one-current-device operation; no second user-operated device is introduced.

## Deterministic fixture coverage

Tests now cover:

- deterministic provider observation hashing;
- exact provider-version/revision/content-digest binding;
- TVC-backed active-probe -> Shared Docs observation when exact content SHA-256 exists;
- explicit rejection of TVC metadata-only evidence when exact content SHA-256 is absent;
- content-digest mismatch rejection;
- metadata projection without byte mutation/provider write;
- admitted edit -> unfrozen successor while frozen prior is preserved;
- required Interlock/InTr admission reference;
- same provider-version replay rejection;
- provider-document identity-change rejection;
- TVC provider evidence bridge regression validation;
- base Shared Docs freeze-state regression validation.

## Proof classes

Source adapter validation, provider observation, provider content-integrity observation, provider mutation, resident execution, and external provider synchronization are separate evidence classes. A source test or provider metadata read MUST NOT be promoted into proof that the provider enforced a freeze or performed an edit.

## Current next action

Validate and merge the TVC evidence-seam SDK change if exact-head CI remains green. After that, the remaining provider-observation gap is narrow and explicit: TV/TVC must produce an admitted, secret-free exact reviewed-content SHA-256 tied to the same provider document/version. That digest must be computed from an explicitly defined canonical content profile rather than inferred from Google Drive metadata. No authentic content-integrity observation is claimed yet.
