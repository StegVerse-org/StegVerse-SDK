# SDK Evaluator Governance Posture Manifest Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `STRUCTURED_AUTHORITY_BASIS_COMPLETENESS_PATCH_PENDING`

## Objective

Prove the local SDK experiment path from ÉLAN-shaped source data through canonical manifest construction, exact governance transition construction, Interlock/InTr posture binding, governance consumption, returned governed result, route evidence, exact-run custody, replay, and reconstruction without third-party evaluator execution or public package publication; then compare two Event 3 representations under the same governance evaluator.

## Structured role/authority reconciliation — 2026-09-17

A focused SDK console test showed that role-shaped data was preserved and state-bound but not independently resolved: manually supplied `actor_authority_current` / `delegation_current` booleans controlled the canonical three-layer outcome, while a structured role hierarchy did not.

Cross-repository reconciliation established:

```text
StegCore three-layer + StegGate:
  consume already-resolved current authority/delegation facts

StegCore current commit boundary:
  independently checks represented authority status, target binding, time validity, evidence currentness

StegCore correctability schemas:
  authority/delegation records exist but are correction-domain records, not a generic organization-role resolver

StegEntity:
  domain-specific role-transition enforcement, not a general external role hierarchy

Ecosystem-Delegation:
  evaluates whether authority may be delegated under HPS standing, not whether a role label currently holds arbitrary organizational authority

StegOS:
  node authority-class enforcement, not a general organization-role resolver

TV/TVC:
  protected scoped credential/authority issuance and verification authority
```

Therefore there was no existing general canonical role resolver simply missing from the SDK. The needed seam is a non-authorizing **structured authority-basis resolution** that derives the current authority/delegation facts StegGate already consumes. That resolver belongs with StegCore decision-state preparation, not as an SDK authority engine.

Supporting StegCore implementation is staged in PR #219 on `sdk-authority-basis-resolution-001`. Its resolver:

- binds actor identity plus exact action / target / scope / evaluation instant;
- consumes frozen authority/delegation assertions;
- preserves role label as context only;
- returns ALLOW / DENY / FAIL_CLOSED current-basis facts;
- never issues authority, verifies TVC credentials, or interprets role policy;
- leaves TV/TVC and Interlock/InTr authority boundaries unchanged.

The SDK branch `sdk-structured-authority-basis-001` adds:

```text
stegverse/authority_basis_bridge.py
build_authority_bound_evaluator_governance_manifest(...)
tests/test_evaluator_authority_basis_bridge.py
.github/workflows/sdk-structured-authority-basis.yml
README.md structured authority/delegation contract
```

The structured SDK path rejects pre-authored `actor_authority_current` and `delegation_current` values. It invokes an injected canonical resolver, binds only its currentness facts into the exact governance request, and preserves both the original structured request and a non-authorizing resolution binding as manifest evidence.

Public claim boundary after validation:

```text
StegVerse can independently evaluate whether supplied structured authority/delegation evidence
establishes current authority for the exact actor/action/target/scope at the declared evaluation time.

StegVerse does not infer that a role label itself grants authority.
The SDK does not issue authority or verify protected credentials.
TV/TVC remains protected credential/scoped-authority issuance authority.
Interlock/InTr remains governed transition authority.
```

Validation evidence now exists for the source composition:

```text
StegCore resolver PR: #219
StegCore exact validated head: acf210f073a8d4350f56642b1ac6119fc68fbe52
StegCore focused resolver validation: run 35287845446 PASS
StegCore merge: 1c045362726fd7ede0af3c1d6afb960d8dff70b8
StegCore handoff closeout merge: e3be88294b0583d8b3c781b7547a4d2e5b1ad112

SDK PR: #253
SDK preliminary validated head: d0b8ac7f4c5064f758978734e519a467040b7b42
SDK preliminary Structured Authority Basis Validation: run 35288090021 PASS
SDK final exact validated head: 926eed7dfee115ee714959042a1c9f3b39078e4f
SDK final Structured Authority Basis Validation: run 35288182438 PASS
Evaluator Manifest Source Validation: PASS
Evaluator Governance Posture Manifest Validation: PASS
Manifest Builder Source Validation: PASS
Evaluator Contract Console Validation: PASS
SDK Package Artifact Validation: PASS
```

The first focused SDK attempt failed only because public SDK CI could not clone the private StegCore repository through pip. That was not converted into a false runtime dependency: the private-source package extra and same-process cross-org test were removed. The canonical resolver is independently validated in StegCore; the public SDK validates its injected resolver contract and binding behavior without vendoring or duplicating authority semantics.

PR #253 merged to SDK main as `5702fed1f9feaee1bca308f01e3d9d44ad8b2f1f`. The structured authority-basis contract and SDK binding are therefore merged canonical source behavior. Public distribution of the canonical StegCore resolver is a separate distribution concern; this change does not claim that the resolver is newly available as a public package.

## Baseline run: Event 3 not submitted

The original source trace explicitly said Event 3 was silence but had not yet been submitted. The baseline SDK test correctly did not synthesize that future event and represented its absence as:

```text
signal.missing_inputs = ["event_3:not_submitted"]
```

Observed baseline result:

```text
governance_state: DENY
reason_code: signal.inputs_incomplete
executor_invoked: false
external_side_effect: false
```

Historical successful baseline run:

```text
workflow: ELAN Local SDK Governance Experiment
run: 34560172540
head: c6a8a29e404ddd7ed01dc706fcba3d4452e2fe17
artifact id: 10184019620
artifact digest: sha256:f804ace1f0eb965977d9ca6c3dab5d4cdc74ddf675bb3548c9a556b3d12f82c1
manifest receipt: MR-A6180341ED34E36D2682A37C398DC5D5031D398D9AE73007DD9333B712E1A68A
```

## Comparative rerun: Event 3 as observable silence

A second controlled local test preserves Events 1 and 2 and changes only the Event 3 representation. Event 3 is supplied as an observation with a bounded closed observation window:

```text
class: OBSERVATION
state_transition:
  from: ACTIVE_CONVERSATION_WITH_EMISSION_POSSIBLE
  to: NON_EMISSION_OBSERVED
emission_observed: false
observation_window:
  bounded: true
  state: CLOSED
intent: UNDETERMINED
semantic_interpretation: UNRESOLVED
```

The governance request admits the Events 1-3 evidence reference and sets:

```text
missing_inputs: []
```

No emotional meaning, motive, refusal, incapacity, or intent is inferred from silence.

### Exact successful comparative run

```text
PR: #197
branch: sdk-evaluator-governance-observed-silence-001
head: 9f708514e8ae3f42b098d1dadfa7713d661fa78d
workflow run: 34565096417
job: 103155480385
result: PASS
```

Exact-head workflow steps passed:

```text
Install current SDK source only: PASS
Focused local SDK boundary tests: PASS
Baseline ELAN governance experiment: PASS
Baseline missing-input assertions: PASS
Observed-silence ELAN governance experiment: PASS
Observed-silence state assertions: PASS
Controlled comparison assertions: PASS
Evidence inventory: PASS
Baseline artifact upload: PASS
Observed-silence artifact upload: PASS
```

Observed-silence artifact:

```text
name: elan-local-sdk-governance-observed-silence
artifact id: 10185708511
artifact digest: sha256:2b1a4114b727941787b251b92f08a2b86d1e5959d07eada9877d6bb0d8f2a68f
```

Rerun assertions proved:

```text
event_3_representation: OBSERVABLE_NON_EMISSION_STATE_TRANSITION
event_3_intent: UNDETERMINED
event_3_semantic_interpretation: UNRESOLVED
event_3_in_missing_inputs: false
boundary_consumed: true
governance_state: ALLOW
governance_reason: ok
executor_invoked: true
route_transition_count: 10
chain_verified: true
custody_status: RECORDED
replay_deterministic_match: true
reconstruction_chain_verified: true
result_returned: true
```

## Controlled comparison

```text
BASELINE
Event 3 = NOT_SUBMITTED -> signal.missing_inputs
Result = DENY / signal.inputs_incomplete

RERUN
Event 3 = admitted observable NON_EMISSION_OBSERVED state transition
Result = ALLOW / ok

Controlled difference = representation of Event 3
Governance evaluator code = unchanged
```

This comparison demonstrates that the local governance semantics can proceed when silence is presented as admitted observable state rather than as absent required evidence. It does not establish why the participant was silent, whether the silence carried a specific emotional meaning, or whether every future silence should be admissible. Those remain contextual evidence questions.

## Local governance continuation scope

`stegverse/local_governance_experiment.py` remains a test-only semantic snapshot of the exact pinned governed-test source basis:

```text
StegVerse-Labs/StegCore@ef38410505b0ef3e84148892b1d6e3cdef20f300
Data-Continuation/core-lite@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
master-records/orchestration@03312236c115bc814024d700810391340648601f
```

This proves local comparative experiment semantics and evidence-path behavior. It does not claim deployment of those private packages, a live cross-repository runtime instance, or third-party evaluator execution.

## Remaining work

```text
1 preserve the baseline and comparative rerun as separate immutable evidence sets
2 reconcile stacked PR #197 into PR #177 after exact-head review
3 keep live/private-package runtime proof as a separate predicate
4 use future silence tests to distinguish observed non-emission from missing transport, timeout, refusal, incapacity, or contextual response without preassigning intent
```

## Manual work

None.


## Structured authority completeness correction — 2026-09-17

Follow-up review found an unknown-versus-false edge in the first structured resolver contract. A non-matching assertion set cannot establish that authority is absent unless that set is known to be complete for the candidate under test.

StegCore patch PR #221 adds explicit `authority_basis_complete` and `delegation_basis_complete` declarations. Matching current evidence may establish TRUE. If no match exists and the relevant basis is incomplete, the resolver must return UNKNOWN / FAIL_CLOSED. Only a declared complete basis may support FALSE / DENY for no candidate-covering authority or delegation.

The SDK closeout branch now requires those completeness fields, verifies that the canonical resolver returns the same completeness values, preserves them in the binding, and tests that incomplete authority basis may remain `actor_authority_current = null` without being coerced to false.

The earlier PR #253 merge remains valid for role-label non-authority and resolver separation, but the final structured-authority public claim is held until the completeness patch validates and merges in both StegCore and SDK.
