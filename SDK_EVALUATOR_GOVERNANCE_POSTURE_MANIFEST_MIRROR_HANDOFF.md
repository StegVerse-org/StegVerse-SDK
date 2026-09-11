# SDK Evaluator Governance Posture Manifest Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `SOURCE_INTEGRATION_COMPLETE_LOCAL_BOUNDARY_PROOF_IN_PROGRESS`

## Objective

Establish the local SDK -> governance boundary using source-native test data, the canonical manifest builder, exact governance transition construction, and Interlock/InTr posture binding without introducing third-party evaluator execution, public-distribution acquisition, or evaluator-specific evidence contamination.

The local test is intentionally earlier than third-party evaluator compatibility. No third party is executing the ÉLAN test in this lane. ÉLAN Events 1 and 2 are source-native test material used by the local SDK only.

## Local boundary under test

```text
source-native local test data
+ governance processor request
+ optional evaluator-style declaration retained as metadata only
+ optional SDK security-posture request inputs
-> canonical ingress manifest
-> exact governance transition request
-> injected local Interlock/InTr posture resolver
-> exact task + payload SHA-256 + transition-request SHA-256 binding verification
-> explicit SDK_TO_GOVERNANCE boundary handoff
-> READY_FOR_GOVERNANCE_CONSUMPTION
```

At this stage the test MUST NOT imply:

```text
third-party evaluator execution
public package publication/acquisition
live deployed StegOS runtime proof
governance consumption
StegCore execution
Master Records custody
replay
reconstruction
```

Those are downstream tests after this boundary is established.

## Source

```text
stegverse/security_posture_request.py
stegverse/evaluator_manifest_builder.py
stegverse/intr_posture_runtime_bridge.py
stegverse/local_governance_boundary.py
stegverse/evaluator_governance_runtime.py
stegverse/external_framework_runner.py
stegverse/public_inspection.py
scripts/run_elan_manifest_governance_evidence_test.py
tests/test_evaluator_manifest_builder.py
tests/test_intr_posture_runtime_bridge.py
tests/test_intr_posture_runtime_crossrepo.py
tests/test_external_framework_posture_runtime.py
tests/test_local_governance_boundary.py
tests/fixtures/stegos_intr_security_posture_resolution_84ddc96e.py
.github/workflows/evaluator-governance-posture-manifest.yml
.github/workflows/evaluator-governance-runtime-binding.yml
.github/workflows/elan-governance-evidence-test.yml
```

## Existing runtime integration

Manifest-builder composition PR #172 merged at `7aaf0ea4a3a4b133941a8b16ffd410817746a6ee`.

Runtime binding PR #173 merged at `b9beedcbbed3b09ed7620ac6de6f51788c6567a1` after exact-head `c5d41998bb39f9af1bb127a0e74b1c8bffd50dd4` passed:

```text
Evaluator Governance Runtime Binding Validation 34522799912: PASS
Manifest Builder Source Validation 34522799896: PASS
External Framework Public Submission Validation 34522799991: PASS
SDK Package Artifact Validation 34522800019: PASS
```

The StegOS compatibility fixture is an exact test-only snapshot of `StegVerse-Labs/StegOS@84ddc96e38d6a5156becd91fb49da7dd14047bca`, source path `stegos/intr_security_posture_resolution.py`, Git blob `e7f1e89abad89008f5dbba736621bbd23a294aa0`. It is compatibility evidence only. Local boundary execution uses an explicitly injected deterministic resolver callback.

## Binding invariants

- posture request schema: `stegverse.sdk.security-posture-request.v1`;
- `selection_present=false` cannot carry a selected tier;
- SDK does not compute automatic/effective posture;
- resolver output identifies `INTERLOCK_INTR` as resolution authority;
- returned posture instance binds the exact task ID;
- returned posture instance binds the exact payload SHA-256;
- returned posture instance binds the exact transition-request SHA-256;
- the exact transition request placed at the governance boundary is unchanged after binding;
- evaluator-style WHAT/HOW/WHY metadata is not a governance decision input;
- boundary preparation grants no governance/execution authority.

## Correction of 2026-09-10 test framing

PR #177 initially attempted to continue from successful manifest/InTr construction directly into `run_external_framework`, which caused the CI harness to attempt public governed-runtime package acquisition. That conflated two separate local tests:

```text
A. SDK -> governance boundary establishment
B. full local governance-runtime execution
```

For the current lane only A is in scope.

The earlier run `34539775942` remains useful diagnostic evidence because it proved manifest construction, transition construction, and deterministic InTr binding and exposed a genuine `processor_capability` validator skew. PR #177 repaired that skew. However, the later missing-package failure is no longer treated as a blocker for this boundary test because package publication/acquisition is outside the scope of establishing A.

## Corrected local evidence harness

PR #177 now adds `stegverse/local_governance_boundary.py`. It emits:

```text
schema: stegverse.sdk.local-governance-boundary/v1
boundary: SDK_TO_GOVERNANCE
boundary_state: READY_FOR_GOVERNANCE_CONSUMPTION
execution_scope: LOCAL_SDK_BOUNDARY_TEST
exact_request_preserved: true
governance_execution_performed: false
governance_result_claimed: false
external_package_materialization_required: false
third_party_evaluator_execution: false
authority_effect: NONE
```

The revised test sequence is:

```text
SOURCE_NATIVE_CAPTURED
-> LOCAL_GOVERNANCE_REQUEST_DECLARED
-> POSTURE_REQUEST_DECLARED_NON_AUTHORIZING
-> MANIFEST_BUILT_VALIDATED
-> GOVERNANCE_TRANSITION_REQUEST_MATERIALIZED
-> LOCAL_INTR_POSTURE_BINDING_VERIFIED
-> SDK_TO_GOVERNANCE_BOUNDARY_READY
-> GOVERNANCE_CONSUMPTION_NOT_EXECUTED_IN_THIS_BOUNDARY_TEST
```

The workflow installs only the current SDK source plus pytest. It does not install `stegverse-stegcore`, Core-Lite, Master Records, or any other external governed-runtime distribution.

## Relationship to StegOS/Node and state-transition protocols

Universal InTr transport and the inter-Entity epistemic/state-transition protocol remain relevant to the shape of the boundary, but they do not enlarge the current test scope. The local SDK test establishes the exact manifested handoff and its non-authorizing InTr/posture binding. Governance-side consumption is the next integration test.

Transport receipt, posture binding, semantic incorporation, governance admission, execution, custody, replay, and reconstruction remain distinct states. No downstream state is inferred merely because the SDK boundary artifact exists.

## README reconciliation

README must distinguish the new local SDK -> governance boundary test from the existing full local governed-runtime test. The full governed-runtime section may continue to describe its canonical runtime dependencies; those dependencies are not prerequisites for the earlier boundary-establishment test.

## Remaining evidence boundary

For this goal's immediate local boundary lane:

```text
1 execute exact-head revised local-only workflow
2 retain exact manifest, transition request, InTr binding, and SDK_TO_GOVERNANCE handoff artifact
3 verify focused regression tests
4 generate screenshots only from the revised local-only evidence
5 reconcile README wording
6 merge PR #177 only after exact-head validation
```

After this is green, the next separate integration step is governance-side consumption of the exact handoff artifact. Third-party evaluator execution remains later still.

## Manual work

None.
