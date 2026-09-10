# SDK Evaluator Governance Posture Manifest Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `SOURCE_INTEGRATION_COMPLETE_RUNTIME_PROOF_PENDING`

## Objective

Integrate evaluator-facing SDK manifest construction with the governance processor and authoritative Interlock/InTr security-posture contract without adding evaluator-specific evidence fields or allowing the SDK to resolve final posture.

## Implemented path

```text
source-native evaluator data
+ governance processor request
+ optional evaluator preregistration declaration
+ optional SDK security-posture request inputs
-> canonical ingress manifest
-> exact governance transition request
-> authoritative Interlock/InTr posture resolver
-> exact task + payload SHA-256 + transition-request SHA-256 binding verification
-> unchanged governance request execution
-> posture binding + governance result + normal replay/reconstruction
```

The evaluator declaration remains outside `extensions.stegverse_governance_request`. The posture request remains outside governance evidence and carries only non-authorizing request inputs. The SDK never derives authoritative automatic/effective posture or mints a posture instance.

## Source

```text
stegverse/security_posture_request.py
stegverse/evaluator_manifest_builder.py
stegverse/intr_posture_runtime_bridge.py
stegverse/evaluator_governance_runtime.py
stegverse/external_framework_runner.py
stegverse/public_inspection.py
scripts/run_elan_manifest_governance_evidence_test.py
tests/test_evaluator_manifest_builder.py
tests/test_intr_posture_runtime_bridge.py
tests/test_intr_posture_runtime_crossrepo.py
tests/test_external_framework_posture_runtime.py
tests/fixtures/stegos_intr_security_posture_resolution_84ddc96e.py
.github/workflows/evaluator-governance-posture-manifest.yml
.github/workflows/evaluator-governance-runtime-binding.yml
.github/workflows/elan-governance-evidence-test.yml
```

## One-command evaluator surface

`stegverse external-run` accepts `--security-posture-request`. In `--prepare-only` mode the request is retained without posture resolution. During execution, a posture-bearing manifest requires the canonical StegOS Interlock/InTr resolver (`stegos.intr_security_posture_resolution.resolve_task_security_posture`) or an explicitly injected resolver callback for deterministic testing. Missing resolver fails closed.

Posture-free external-run preserves the prior `governance_ingress_runtime.run_external_manifest` compatibility path.

## Binding invariants

- posture request schema: `stegverse.sdk.security-posture-request.v1`;
- `selection_present=false` cannot carry a selected tier;
- SDK does not compute automatic/effective posture;
- resolver output must identify `INTERLOCK_INTR` as resolution authority;
- returned posture instance must bind the exact task ID;
- returned posture instance must bind the exact payload SHA-256;
- returned posture instance must bind the exact transition-request SHA-256;
- the governance request executed after resolution is the unchanged request whose digest was supplied to InTr;
- evaluator preregistration remains outside governance decision evidence.

## Validation and merge evidence

Manifest-builder composition PR #172 merged at `7aaf0ea4a3a4b133941a8b16ffd410817746a6ee`.

Runtime binding PR #173 merged at `b9beedcbbed3b09ed7620ac6de6f51788c6567a1` after exact-head `c5d41998bb39f9af1bb127a0e74b1c8bffd50dd4` passed:

```text
Evaluator Governance Runtime Binding Validation 34522799912: PASS
Manifest Builder Source Validation 34522799896: PASS
External Framework Public Submission Validation 34522799991: PASS
SDK Package Artifact Validation 34522800019: PASS
```

The StegOS compatibility fixture is an exact test-only snapshot of `StegVerse-Labs/StegOS@84ddc96e38d6a5156becd91fb49da7dd14047bca`, source path `stegos/intr_security_posture_resolution.py`, Git blob `e7f1e89abad89008f5dbba736621bbd23a294aa0`. Runtime code still imports the live `stegos` module and does not execute the snapshot.

## 2026-09-10 ÉLAN evidence execution

PR #177 (`sdk-evaluator-governance-posture-test-evidence-001`) executes the source-native ÉLAN Test Trace Events 1 and 2. Event 3 remains explicitly `NOT_SUBMITTED`; no synthetic silence event is introduced. The evaluator declaration leaves `expected_observation` null.

The evidence harness emits exact files for each state boundary and uploads them as a GitHub Actions artifact. Run `34539775942` on head `8ce364370813e47fe7b787e9db1b6a09dbfa4f46` established:

```text
SOURCE_NATIVE_CAPTURED: PASS
GOVERNANCE_REQUEST_DECLARED: PASS
POSTURE_REQUEST_DECLARED_NON_AUTHORIZING: PASS
MANIFEST_BUILT_VALIDATED: PASS
GOVERNANCE_TRANSITION_REQUEST_MATERIALIZED: PASS
INTR_POSTURE_BOUND_TEST_DOUBLE: PASS
GOVERNANCE_EXECUTION: FAIL_CLOSED_MISSING_CANONICAL_RUNTIME_PACKAGES
```

The run preserved 13 evidence files. Important exact artifact hashes from that run include:

```text
04-manifest.json
  sha256:1f2b204fc55a22fe0ba533a1825d2bc11a8a1427d70fa8191776c71f4c323bc3
05-transition-request.json
  sha256:3d06812c7d1c1967cdded761c1245db4cc4587b275c5944b6de89bb0ac67909b
06-intr-posture-binding.json
  sha256:9c0df3c370b6a1927af25e8318bc2ea38e0608e6f5eeb3bed2451c11a1a429a1
```

An earlier run exposed a contract skew where `governance_ingress_runtime` emitted `execution_provenance.processor_capability` while `public_inspection` rejected that field. PR #177 repairs the validator to accept and bound processor capability in execution provenance. The next run passed that validator boundary and reached canonical runtime component loading.

The current execution failure is not an ÉLAN payload or manifest validation failure. The runner cannot materialize the canonical governed runtime because `stegverse-stegcore` is not yet available from the public package index. This matches `SDK_PUBLIC_DISTRIBUTION_PRIVACY_MIRROR_HANDOFF.md`, where exact public `stegverse-stegcore==0.3.0` publication remains pending the TV/TVC release gate. The evidence test does not bypass that release gate with protected-source credentials.

## README review

The README documents the Manifest Builder, `stegverse external-run`, evaluator-defined manifests, processor-specific governance request separation, evaluator preregistration non-interference, and caller-selected return projection. PR #177 adds a bounded evidence-test note so the new test artifact path and its fail-closed runtime-publication boundary are discoverable without making ÉLAN semantics part of the generic SDK contract.

## Remaining evidence boundary

The current test has authentic SDK source execution through completed manifest, governance transition request, and deterministic InTr binding. It has **not** executed the canonical StegCore governance runtime because the exact public governed-runtime distributions are not yet materialized in the clean runner, and it has not used live StegOS/InTr.

Remaining predicates are:

```text
1 exact immutable stegverse-stegcore / Master Records public distribution publication through the canonical TV/TVC release chain
2 clean-environment governed runtime materialization
3 same source-native ÉLAN manifest executed through canonical governance
4 live StegOS/InTr posture instance retained with exact task/payload/transition bindings
5 governance result + manifest receipt + Master Records custody retained
6 replay retained
7 reconstruction retained
```

CI/test-double compatibility does not prove the live runtime predicates.

## Manual work

None.
