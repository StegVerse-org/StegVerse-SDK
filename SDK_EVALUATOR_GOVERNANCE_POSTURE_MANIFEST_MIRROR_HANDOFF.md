# SDK Evaluator Governance Posture Manifest Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `LOCAL_SDK_TO_GOVERNANCE_BOUNDARY_PROVEN`

## Objective

Establish the local SDK -> governance boundary using source-native test data, the canonical manifest builder, exact governance transition construction, and Interlock/InTr posture binding without introducing third-party evaluator execution, public-distribution acquisition, or evaluator-specific evidence contamination.

The local test is intentionally earlier than third-party evaluator compatibility. No third party executes the ÉLAN test in this lane. ÉLAN Events 1 and 2 are source-native test material used by the local SDK only.

## Proven local boundary

```text
source-native local test data
+ governance processor request
+ evaluator-style declaration retained as metadata only
+ SDK security-posture request inputs
-> canonical ingress manifest
-> exact governance transition request
-> injected local Interlock/InTr posture resolver
-> exact task + payload SHA-256 + transition-request SHA-256 binding verification
-> explicit SDK_TO_GOVERNANCE boundary handoff
-> READY_FOR_GOVERNANCE_CONSUMPTION
```

The boundary proof does not imply governance consumption, StegCore execution, Master Records custody, replay, reconstruction, live deployed StegOS runtime proof, public package publication/acquisition, or third-party evaluator execution.

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

## Corrected test framing

PR #177 initially attempted to continue from successful manifest/InTr construction directly into `run_external_framework`, which conflated:

```text
A. SDK -> governance boundary establishment
B. full local governance-runtime execution
```

For this lane, A is now independently proven. The earlier run `34539775942` remains diagnostic only; it exposed a genuine `processor_capability` validator skew that PR #177 repairs, but its package-acquisition failure is not a blocker for boundary establishment.

## Exact successful boundary evidence

Current exact head before this handoff update: `9b3943934d1154a00c5cc87826bb3a0c00bd72de`.

Workflow:

```text
ELAN Local SDK Governance Boundary Test
run: 34553895610
job: local-boundary-test
result: PASS
```

The run passed:

```text
Install current SDK source only: PASS
Focused local SDK boundary tests: PASS
ÉLAN-shaped local SDK boundary evidence test: PASS
Evidence inventory: PASS
Artifact upload: PASS
```

Uploaded artifact:

```text
name: elan-local-sdk-governance-boundary-test
artifact id: 10181792404
artifact digest: sha256:888917ebf4a639ecb16b83ac899e09ca8083d3ca23c17cf0fc27046dd803cdf1
```

The artifact contains:

```text
00-source-native-input.json
01-governance-request.json
02-security-posture-request.json
03-evaluation-declaration.json
04-manifest.json
05-transition-request.json
06-intr-posture-binding.json
07-sdk-governance-boundary-handoff.json
08-state-transitions.json
09-summary.json
10-results-documentation.md
```

Observed state sequence:

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

Summary outcome:

```text
LOCAL_SDK_GOVERNANCE_BOUNDARY_PROVEN
boundary_state: READY_FOR_GOVERNANCE_CONSUMPTION
external_package_materialization_required: false
third_party_evaluator_execution: false
governance_execution_performed: false
```

## Third-party-view documentation

The screenshot set derived from run `34553895610` represents what a third-party SDK user would see at the SDK surface while preserving the actual local test semantics. It includes:

```text
1 Manifest Builder input
2 completed manifest
3 governance transition request
4 Interlock/InTr posture binding
5 SDK -> governance boundary READY
6 state-transition trace
```

No governance-result screenshot is produced from this run because governance did not consume the handoff. A later governance-consumption run must provide that evidence before any result screen is documented.

## Relationship to StegOS/Node and state-transition protocols

Universal InTr transport and the inter-Entity epistemic/state-transition protocol shape the boundary but do not enlarge the current test scope. Transport receipt, posture binding, semantic incorporation, governance admission, execution, custody, replay, and reconstruction remain distinct states. No downstream state is inferred merely because the SDK boundary artifact exists.

## Remaining work for this goal

```text
1 reconcile README wording so local boundary testing and full local governed-runtime testing are explicitly distinct
2 validate this exact newest handoff head
3 merge PR #177 when exact-head validation is green and branch/base are reconciled
4 create/continue the next integration lane for governance-side consumption of the exact READY_FOR_GOVERNANCE_CONSUMPTION artifact
5 only after governance consumption is proven, document governance decision/result/custody/replay/reconstruction screens
```

Third-party evaluator execution remains a later compatibility test after the SDK/governance boundary and governance-side consumer are established.

## Manual work

None.
