# SDK Evaluator Governance Posture Manifest Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `STRUCTURED_AUTHORITY_BASIS_VALIDATED_MERGED_RUNTIME_PROOF_PENDING`

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

Canonical StegCore authority-basis resolution is now merged. The initial resolver entered through PR #219 and the UNKNOWN-versus-FALSE completeness correction through PR #221. Its resolver:

- binds actor identity plus exact action / target / scope / evaluation instant;
- consumes frozen authority/delegation assertions;
- preserves role label as context only;
- returns ALLOW / DENY / FAIL_CLOSED current-basis facts;
- never issues authority, verifies TVC credentials, or interprets role policy;
- leaves TV/TVC and Interlock/InTr authority boundaries unchanged.

The merged SDK integration includes:

```text
stegverse/authority_basis_bridge.py
build_authority_bound_evaluator_governance_manifest(...)
tests/test_evaluator_authority_basis_bridge.py
.github/workflows/sdk-structured-authority-basis.yml
README.md structured authority/delegation contract
```

The structured SDK path rejects pre-authored `actor_authority_current` and `delegation_current` values. It invokes an injected canonical resolver, binds only its currentness facts into the exact governance request, and preserves both the original structured request and a non-authorizing resolution binding as manifest evidence.

Validated public claim boundary:

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

## Historical comparative-experiment notes

The baseline and observed-silence evidence sets remain separate immutable experiment evidence. PR #197 and PR #177 are already merged historical evidence. Future silence tests should continue distinguishing observed non-emission from missing transport, timeout, refusal, incapacity, or contextual response without preassigning intent. The current parent-goal remaining predicate is the authentic live/private-runtime proof stated in the final closeout section below.

## Manual work

None.


## Structured authority completeness correction — 2026-09-17

Follow-up review found an unknown-versus-false edge in the first structured resolver contract. A non-matching assertion set cannot establish that authority is absent unless that set is known to be complete for the candidate under test.

StegCore patch PR #221 adds explicit `authority_basis_complete` and `delegation_basis_complete` declarations. Matching current evidence may establish TRUE. If no match exists and the relevant basis is incomplete, the resolver must return UNKNOWN / FAIL_CLOSED. Only a declared complete basis may support FALSE / DENY for no candidate-covering authority or delegation.

The SDK closeout branch now requires those completeness fields, verifies that the canonical resolver returns the same completeness values, preserves them in the binding, and tests that incomplete authority basis may remain `actor_authority_current = null` without being coerced to false.

StegCore exact completeness head `df03835dfa8046da190521d7ef55ece9634a576a` passed Authority Basis Resolution Validation run `35288540217`, StegVerse 001/002 validation, and package-version identity validation. PR #221 merged with expected-head protection as `f45d52cb62db29418d88752fe38f68e9bcc3cf12`. The SDK completeness bridge and tests passed the SDK Structured Authority Basis Validation and adjacent evaluator/manifest/package lanes at exact heads `bad170ad43a6a7c85dc2850b74c6be0de1c3afcf` and `ededb14d9d22a2b201189f660b80f90b57d13b7f`; PR #254 then merged as `16d4bf1e40b4eac7313b3399e48ab880a6f53001` and final source-contract closeout PR #255 merged as `ca5b349b76a3548a385aa65299d8b08664feedaa`.


## Final structured-authority source closeout — 2026-09-17

StegCore completeness correction PR #221 merged as `f45d52cb62db29418d88752fe38f68e9bcc3cf12`; its canonical handoff closeout merged as `dae6c564d361d515f71aaecedbade1652f40cb12`.

SDK PR #254 exact head `ededb14d9d22a2b201189f660b80f90b57d13b7f` passed all triggered lanes, including SDK Structured Authority Basis Validation run `35288636196`, Evaluator Governance Posture Manifest Validation, Evaluator Manifest Source Validation, Manifest Builder Source Validation, Evaluator Contract Console Validation, SDK Package Artifact Validation, Publisher return binding, workspace probe, and shared-doc/provider integration validation. PR #254 merged with expected-head protection as `16d4bf1e40b4eac7313b3399e48ab880a6f53001`.

The structured role/authority source claim is therefore valid at the merged source-contract level:

```text
role label alone -> never authority
matching current scoped structured authority basis -> may establish actor_authority_current = true
incomplete no-match authority/delegation basis -> UNKNOWN / FAIL_CLOSED
complete no-match current authority/delegation basis -> false / DENY
SDK -> preserves evidence + invokes canonical resolver + binds returned currentness facts
SDK -> does not issue authority, verify protected credentials, or implement role policy
TV/TVC -> credential/scoped-authority issuance authority
Interlock/InTr -> governed transition authority
```

This does not close the parent goal. The canonical remaining predicate is still authentic SDK-to-live StegOS/InTr posture-bound governance execution evidence. Public distribution of the private StegCore resolver is also not claimed by these source merges.


## Governance Reference Graph reconciliation — 2026-09-18

The structured-role investigation generalized beyond HITL. A human hierarchy is one
instance of a broader requirement: a manifested input may need to carry a graph of
governance-relevant references spanning humans, AI systems, services, devices,
organizations, roles, datasets, sensors, credentials, constraints, provenance,
supervision, escalation, delegation context, and quorum/policy-shape references.

The SDK representation boundary is now defined as a generic **Governance Reference
Graph (GRG)** rather than a human-specific hierarchy contract.

Canonical SDK responsibilities:

```text
validate graph structure
preserve typed nodes and relationships
preserve applicability, evidence, basis and constraint references
preserve scoped coverage/completeness
hash-bind graph independently
bind graph into canonical manifest
preserve unknown/domain-specific relation types as non-authorizing evidence
```

Explicit non-responsibilities:

```text
hierarchy does not grant authority
graph composition does not grant authority
unknown relations do not grant authority
SDK validation does not resolve governance
SDK does not infer actor_authority_current or delegation_current from graph position
SDK does not verify protected credentials
SDK does not perform governed transitions
```

The smallest SDK integration surface is:

```text
stegverse/governance_reference_graph.py
stegverse/manifest_builder.py
stegverse/evaluator_manifest_builder.py
stegverse/__init__.py
docs/GOVERNANCE_REFERENCE_GRAPH.md
tests/test_governance_reference_graph.py
validation/governance_reference_graph_console.py
```

The graph is carried under `extensions.governance_reference_graph`. It has its
own `graph_sha256` and is also covered by the canonical manifest hash. The
Manifest Builder accepts it through Python and through
`--governance-reference-graph <file.json>`. Evaluator-safe builders accept the
same optional graph without mixing it into evaluator preregistration or directly
into the canonical StegGate request.

Coverage/completeness follows the existing structured-authority truth rule:
absence from an incomplete relationship basis is not converted to FALSE. Scoped
coverage records therefore carry an explicit `complete` boolean.

This does not replace the merged StegCore authority-basis resolver. That resolver
remains the canonical leaf authority/delegation currentness seam. Existing
StegCore policy shapes remain the canonical structural semantics for quorum,
guardian, veto, time-lock, and escalation. The GRG may reference those shapes but
does not reimplement them.

Authority boundaries remain:

```text
SDK -> graph representation, validation, transport and hash binding
StegCore/StegGate -> recognized governance semantics and admissibility
TV/TVC -> protected credential/scoped-authority issuance and verification
Interlock/InTr -> governed transition authority
```

The included console validation uses a generic external-framework fixture with
AI supervision, human escalation, evidence provenance, a quorum constraint
reference, scoped incomplete authority coverage, and an unknown framework-native
relationship. Required assertions are that all graph structure survives the
manifest, the graph and manifest hashes are bound, hierarchy/composition/unknown
relations grant no authority, and the graph does not silently populate
`actor_authority_current` or `delegation_current`.

Console/public inspection surfaces are now explicit:

```text
stegverse governance-graph
stegverse governance-graph --schema
stegverse governance-graph --example
stegverse governance-graph --all
python -m stegverse governance-graph --all
```

The console example is deliberately HITL-shaped for readability but marks HITL as an example projection rather than the canonical schema. The generic contract remains applicable to human hierarchy, agent supervision, provenance, constraint references, scoped authority evidence, and domain-specific relationships.

Repository-native validation on branch head `b85ce413d58fc9eafcc5794659932d62f5a1820c` passed:

```text
Manifest Builder Source Validation: run 35340670238 PASS
  tests/test_governance_reference_graph.py: 7 passed
  validation/governance_reference_graph_console.py: GOVERNANCE_REFERENCE_GRAPH_CONSOLE_PASS
  actor_authority_current: null
  delegation_current: null
  hierarchy_grants_authority: false
  sdk_resolves_governance: false
  external_manifest_grants_authority: false

Evaluator Manifest Source Validation: run 35340670250 PASS
Evaluator Contract Console Validation: run 35340670256 PASS
  stegverse governance-graph: PASS
  stegverse governance-graph --schema: PASS
  stegverse governance-graph --example: PASS
  stegverse governance-graph --all: PASS
  python -m stegverse governance-graph --all: PASS
  console/release-set suite: 12 passed

SDK Structured Authority Basis Validation: run 35340670243 PASS
External Framework Public Submission Validation: run 35340670304 PASS
SDK Package Artifact Validation: run 35340670345 PASS
```

The console integration fixture preserved AI supervision, human escalation, evidence provenance, a canonical quorum constraint reference, incomplete authority coverage, and an unknown external-framework relationship while leaving current authority/delegation unresolved. This proves the graph is represented and hash-bound without silently becoming an SDK authority resolver.

This GRG work is source-contract work only. It does not satisfy the parent task's
remaining authentic SDK-to-live StegOS/InTr execution predicate.


## Governance Reference Graph console/source closeout — 2026-09-18

The generic Governance Reference Graph representation and its console discovery surface are now merged on SDK main.

Final public/source integration:

```text
PR #257 -> initial GRG manifest/builder/evaluator integration
merge: 9a0970cdbf3a7f7eef3dcf754a1fb00398b23721

PR #258 -> console/public contract exposure and validation closeout
exact validated head: fde1c6bd04141d02c802c642717d174e44df5359
merge: ace3adf88068929b4b0e56f9880b209b3e2178ad
Evaluator Contract Console Validation: run 35340811339 PASS
Manifest Builder Source Validation: run 35340811283 PASS
Evaluator Manifest Source Validation: run 35340811323 PASS
Evaluator Governance Posture Manifest Validation: run 35340811316 PASS
SDK Structured Authority Basis Validation: run 35340811205 PASS
SDK Package Artifact Validation: run 35340811374 PASS
```

The exact console validation exercised:

```text
stegverse governance-graph
stegverse governance-graph --schema
stegverse governance-graph --example
stegverse governance-graph --all
python -m stegverse governance-graph --all
python validation/governance_reference_graph_console.py
```

Observed assertions included:

```text
contract = stegverse.governance-reference-graph.v1
authority_effect = NONE_REPRESENTATION_ONLY
unknown_relations_grant_authority = false
hierarchy_grants_authority = false
sdk_resolves_governance = false
actor_authority_current = null
delegation_current = null
external_manifest_grants_authority = false
console integration status = GOVERNANCE_REFERENCE_GRAPH_CONSOLE_PASS
console/release-set test suite = 12 passed
```

This closes the requested SDK documentation/internal-surface/console-expression work for the GRG source contract. It does not close the parent runtime predicate and does not claim that arbitrary graph relations are already projected by live StegCore/Interlock execution.


## HGAI Muhammad-facing GRG example — 2026-09-18

A final HGAI-facing example has been prepared against the merged generic GRG source contract.

Repository surfaces:

```text
docs/HGAI_GOVERNANCE_REFERENCE_GRAPH_EXAMPLE.md
inspection/examples/hgai-governance-reference-graph.json
```

The example maps a realistic HITL chain:

```text
AI analyst -> SUPERVISED_BY -> human reviewer
human reviewer -> ESCALATES_TO -> supervising reviewer
supervising reviewer -> ESCALATES_TO -> final decision authority
AI analyst -> DERIVED_FROM -> case evidence set
final decision authority -> REQUIRES_CONSTRAINT -> stegcore:policy-shape:quorum
final decision authority -> HAS_SCOPED_AUTHORITY -> case evidence set
```

The authority-coverage record is deliberately incomplete, preserving UNKNOWN/fail-closed behavior for a no-match rather than manufacturing FALSE. The example explicitly states that the hierarchy and `HAS_SCOPED_AUTHORITY` relation are represented evidence/context only; canonical current authority remains an exact actor/action/target/scope/time determination by the StegCore authority-basis resolver.

No live graph projection is claimed. The parent remaining predicate remains authentic SDK-to-live StegOS/InTr posture-bound governance execution evidence.


## HGAI GRG example validation closeout — 2026-09-18

The HGAI example source/test package merged through PR #260 as `58178b7af65263b4c9ccd81aaa215b659741a6b1` after exact-head validation at `cb42b7399802e3c1610aaf79d557f12a6b89a6dc`.

Exact-head validation passed:

```text
Evaluator Manifest Source Validation: run 35370782309 PASS
Manifest Builder Source Validation: run 35370782437 PASS
Evaluator Contract Console Validation: run 35370782515 PASS
SDK Structured Authority Basis Validation: run 35370782424 PASS
Evaluator Governance Posture Manifest Validation: run 35370782316 PASS
Publisher SDK Return Binding Validation: run 35370782458 PASS
External Collaboration Authentic Runtime Proof Contract Validation: run 35370782467 PASS
WorkSpace Active Probe Validation: run 35370782390 PASS
Shared Docs Multiparty Freeze Validation: run 35370782339 PASS
Shared Docs Provider Freeze Integration Validation: run 35370782385 PASS
```

The machine-readable fixture is therefore validated against the generic GRG parser/hash contract. This does not advance the parent runtime predicate: authentic SDK-to-live StegOS/InTr posture-bound governance execution evidence remains unproven.
