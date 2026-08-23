# Portable Governance Verifier Mirror Handoff

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
issue: #61
role: independent non-authorizing verifier for the portable interlock -> SPE -> StegGate evidence path
```

Live repository state, issue/PR state, workflow evidence, and downstream canonical handoffs supersede this prose.

## Goal
Allow a developer, observer, external framework, or StegVerse module to verify a governed evidence bundle without trusting the application that produced it and without running a second governance evaluator.

## Contract

Input schema:
`stegverse.portable-governance-verification-bundle.v1`

Current stages:
- `PRE_STEGGATE`: verifies exact ingress interlock, SDK->SPE envelope, deterministic SPE receipt, identity continuity, and the non-authorizing canonical StegGate request candidate.
- `POST_RETURN`: additionally requires a valid reciprocal interlock return. This stage is structurally supported but cannot be claimed as end-to-end production proof until real canonical StegGate/consequence/return evidence exists.

## Verification performed
- validates the merged interlock ingress contract;
- recomputes candidate and envelope hashes;
- recomputes SPE standing receipt hash;
- verifies package_id / transition_id / run_id continuity;
- recomputes the StegGate bridge hash;
- verifies the bridge binds the exact ingress interlock and SPE receipt/candidate/envelope hashes;
- verifies the bridge remains `decision=PENDING` and non-authorizing;
- for `POST_RETURN`, validates reciprocal interlock return and exact ingress binding;
- emits a deterministic verification report with no authority.

## Explicit non-claims
The verifier does not:
- mint standing;
- decide admissibility;
- call StegCore;
- authorize or perform execution;
- mint governance/continuity receipts;
- install Master Records custody;
- establish truth of participant claims;
- make a `PRE_STEGGATE` bundle equivalent to completed production governance.

## Why this is portable
The verifier consumes only published bundle objects and deterministic hashing/contract rules. It does not require the producing application, provider secrets, a particular UI, or a special demo backend. The same verifier is intended for internal StegVerse modules and external interlock participants.

## Collision boundary
StegCore PR #141 remains active on transaction receipts/reconstruction and is not modified by this SDK slice. Canonical StegGate decision evidence and Master Records custody remain downstream authorities.

## Completion boundary
This source slice is complete only after exact-head SDK package validation and merge. Full portable verification is not complete until a real `POST_RETURN` bundle contains canonical StegGate decision/consequence evidence, reciprocal participant acknowledgement, Master Records preservation, and replay/reconstruction PASS.
