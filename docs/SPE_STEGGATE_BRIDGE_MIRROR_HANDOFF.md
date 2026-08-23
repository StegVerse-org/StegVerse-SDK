# SPE to StegGate Bridge Mirror Handoff

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
issue: #61
role: non-authorizing SDK bridge from verified SPE standing return to canonical StegGate request candidate
```

Live default-branch state, issue/PR state, workflow evidence, and downstream authority-owner records supersede this prose.

## Goal
Consume the exact SDK->SPE intake envelope and deterministic SPE standing receipt, independently verify their identity/hash bindings and currentness, preserve the #65 interlock identity, and construct a canonical StegGate request candidate without converting standing into execution authority.

## Canonical order

```text
interlocked participant/module state
  -> SDK commitment candidate/envelope
  -> SPE fresh-standing receipt
  -> this bridge verifies envelope + receipt + currentness
  -> non-authorizing canonical StegGate request candidate
  -> StegCore canonical runtime evaluates later
```

## Files

```text
stegverse/spe_steggate_bridge.py
schemas/spe_steggate_bridge.v1.schema.json
tests/test_spe_steggate_bridge.py
docs/SPE_STEGGATE_BRIDGE_MIRROR_HANDOFF.md
```

Schema: `stegverse.sdk.spe-steggate-bridge.v1`.

## Verified inputs

The bridge independently reconstructs and verifies:

- SDK commitment candidate hash;
- SDK SPE envelope hash;
- SPE standing receipt hash;
- package_id;
- transition_id;
- run_id;
- candidate_hash;
- envelope_hash;
- SPE non-authority flags;
- SPE next-boundary semantics.

The receipt algorithm matches the current SPE `stegverse.spe.sdk_commitment_intake.v0.1` contract: SHA-256 over deterministic sorted compact JSON of the receipt core, excluding `receipt_hash` itself.

## Currentness

The SPE receipt binds the exact SDK envelope, and that envelope binds the candidate `validity_window`. The bridge evaluates `not_before` / `not_after` against an explicit timezone-aware `observed_at`.

A stale or not-yet-valid standing result cannot progress. The caller may not inject `consent_or_standing_current`; that predicate is derived only from the verified SPE ALLOW result plus the bound validity window.

## Progression semantics

Only current `standing_result=ALLOW` may produce a StegGate request candidate.

```text
ALLOW + current -> request candidate with decision=PENDING
DENY            -> no StegGate progression
FAIL_CLOSED     -> no StegGate progression
stale/future    -> no StegGate progression
hash mismatch   -> fail closed
identity mismatch -> fail closed
```

SPE ALLOW remains standing evidence only. It does not authorize execution.

## Interlock binding

The bridge requires the #65 interlock context to preserve:

```text
package_id
transition_id
run_id
participant_id
ingress_interlock_hash
```

Package/transition/run identity must exactly match the SDK/SPE envelope. The interlock hash uses the public `sha256:<hex>` form while current SDK/SPE internal receipt hashes retain their existing 64-hex format.

## Canonical StegGate candidate

The emitted candidate binds:

- runtime identity `stegverse:steggate:canonical:three-layer:v1`;
- permission/admissibility contract `PA-001@1.0.0`;
- verified current SPE standing as `consent_or_standing_current=true`;
- caller-supplied remaining present-tense permission/admissibility predicates as candidate facts, not SDK decisions;
- the current StegCore `ThreeLayerRequest` structural fields;
- deterministic `three_layer_request_hash`;
- `decision=PENDING`.

The SDK does not call `evaluate_three_layer` and does not decide admissibility.

## Authority invariants

```text
sdk_authority = NONE
spe_execution_authority = NONE
steggate_decision_authority = CANONICAL_RUNTIME_ONLY
execution_authorized = false
master_records_custody_claimed = false
```

## Collision boundary

Active StegCore PR #141 remains untouched. This SDK bridge does not mutate StegCore transaction lifecycle, receipt provider, capability-context, bounded executor, return ingestion, discovery, or Master Records handoff paths.

A later StegCore bridge must consume this exact standing/interlock binding after #141 is reconciled and must fail closed on missing/stale/mismatched standing where standing is required.

## Completion boundary

This source slice is complete only after focused tests and the existing SDK package workflow validate the exact PR head and the PR is merged.

Full #61 remains open until canonical StegCore actually consumes the exact verified standing binding, bounded consequence occurs only after canonical ALLOW, return ingestion preserves the evidence, Master Records reconstruction/replay passes, and portable independent verification succeeds.
