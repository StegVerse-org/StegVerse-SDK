# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-11
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / PROVIDER-NEUTRAL BINDING IMPLEMENTED / VALIDATION PENDING`

## Goal

Integrate the merged provider-neutral multiparty freeze state machine with Shared Docs provider observations and admitted document mutations without transferring provider, governance, custody, or execution authority.

## Starting evidence

Parent source implementation is merged on SDK `main` at:

```text
d505e937dd9f5e531c56427d7477e026789e4769
```

Parent exact-head validation includes dedicated Shared Docs freeze run `34568759924` PASS plus all applicable SDK lanes PASS.

## Provider seam inspection

The existing SDK provider seam is `stegverse/tvc_provider_probe_bridge.py`. It already consumes secret-free TVC-owned Google Drive evidence and explicitly preserves these constraints:

- credential authority remains `TV/TVC`;
- SDK does not obtain provider credentials or execute provider operations in the bridge;
- provider results are evidence-only;
- external collaboration metadata probes are read-only and may not assign readiness;
- provider mutation authority is not transferred.

That seam is suitable for authentic provider observations later, but its present external-collaboration result does not expose the immutable provider-version + canonical SHA-256 reviewed-content tuple required by Shared Docs freeze binding. The minimal integration therefore adds a provider-neutral binding contract first rather than weakening the existing probe schema or inferring a revision from mutable provider metadata.

## Implemented provider-neutral binding

Branch `shared-docs-provider-freeze-integration-001` adds:

```text
stegverse/shared_docs_provider_freeze.py
tests/test_shared_docs_provider_freeze.py
.github/workflows/shared-docs-provider-freeze-validation.yml
```

The provider observation contract binds:

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

The revision binding then binds that observation to exact Shared Docs `document_id + revision_id + review_epoch + content_digest` and records `TV/TVC` as provider authority and `Interlock/InTr` as transition authority. The binding itself grants neither authority.

Freeze-state projection is metadata-only and explicitly records:

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

The source tests cover:

- deterministic provider observation hashing;
- exact provider-version/revision/content-digest binding;
- content-digest mismatch rejection;
- metadata projection without byte mutation/provider write;
- admitted edit -> unfrozen successor while frozen prior is preserved;
- required Interlock/InTr admission reference;
- same provider-version replay rejection;
- provider-document identity-change rejection;
- base Shared Docs freeze-state regression validation.

## Proof classes

Source adapter validation, provider observation, provider mutation, resident execution, and external provider synchronization are separate evidence classes. A source test or provider metadata read MUST NOT be promoted into proof that the provider enforced a freeze or performed an edit.

## Current next action

Open/validate the SDK implementation PR. If deterministic source validation passes, merge only the provider-neutral binding. Authentic provider observation is the following proof class and must supply an exact provider version plus canonical reviewed-content SHA-256 without introducing a second user-operated device or transferring provider authority away from TV/TVC.
