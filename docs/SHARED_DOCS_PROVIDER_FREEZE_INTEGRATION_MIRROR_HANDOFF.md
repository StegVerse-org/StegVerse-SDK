# Shared Docs Provider Freeze Integration Mirror Handoff

Updated: 2026-09-11
Goal Task ID: `SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001`
Parent Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Status: `ACTIVE / SUCCESSOR STAGED`

## Goal

Integrate the merged provider-neutral multiparty freeze state machine with Shared Docs provider observations and admitted document mutations without transferring provider, governance, custody, or execution authority.

## Starting evidence

Parent source implementation is merged on SDK `main` at:

```text
d505e937dd9f5e531c56427d7477e026789e4769
```

Parent exact-head validation includes dedicated Shared Docs freeze run `34568759924` PASS plus all applicable SDK lanes PASS.

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

## Proof classes

Source adapter validation, provider observation, provider mutation, resident execution, and external provider synchronization are separate evidence classes. A source test or provider metadata read MUST NOT be promoted into proof that the provider enforced a freeze or performed an edit.

## Initial next action

Inspect the current Shared Docs / external-collaboration provider adapter surfaces in the SDK and TVC, choose the minimal integration seam, then implement a provider-neutral binding with deterministic fixtures before attempting any authentic provider mutation.
