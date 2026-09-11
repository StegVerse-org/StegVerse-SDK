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
tests/test_evaluator_manifest_builder.py
tests/test_intr_posture_runtime_bridge.py
tests/test_intr_posture_runtime_crossrepo.py
tests/test_external_framework_posture_runtime.py
tests/fixtures/stegos_intr_security_posture_resolution_84ddc96e.py
.github/workflows/evaluator-governance-posture-manifest.yml
.github/workflows/evaluator-governance-runtime-binding.yml
```

## One-command evaluator surface

`stegverse external-run` now accepts `--security-posture-request`. In `--prepare-only` mode the request is retained without posture resolution. During execution, a posture-bearing manifest requires the canonical StegOS Interlock/InTr resolver (`stegos.intr_security_posture_resolution.resolve_task_security_posture`) or an explicitly injected resolver callback for deterministic testing. Missing resolver fails closed.

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
- SDK runtime bridge tests: PASS
- exact StegOS InTr compatibility snapshot test: PASS
- evaluator manifest + existing Manifest Builder regressions: PASS

Manifest Builder Source Validation 34522799896: PASS
External Framework Public Submission Validation 34522799991: PASS
SDK Package Artifact Validation 34522800019: PASS
```

The StegOS compatibility fixture is an exact test-only snapshot of `StegVerse-Labs/StegOS@84ddc96e38d6a5156becd91fb49da7dd14047bca`, source path `stegos/intr_security_posture_resolution.py`, Git blob `e7f1e89abad89008f5dbba736621bbd23a294aa0`. It exists only because the private StegOS repository cannot be anonymously cloned by SDK CI; runtime code still imports the live `stegos` module and does not execute the snapshot.

## README review

The existing README already documents the Manifest Builder, `stegverse external-run`, evaluator-defined manifests, processor-specific governance request separation, evaluator preregistration non-interference, and caller-selected return projection. The new `--security-posture-request` option is exposed by `stegverse external-run --help`; this handoff carries the detailed posture-runtime contract so the processor-generic README is not rewritten around one evaluator/security integration.

## Remaining evidence boundary

Source integration is complete and validated. The remaining predicate is authentic runtime evidence from a materialized environment containing both the SDK governed runtime and live StegOS Interlock/InTr resolver: submit one evaluator manifest, retain the returned InTr posture instance, verify its exact task/payload/transition bindings, then retain governance/custody/replay/reconstruction evidence. CI/snapshot compatibility does not by itself prove that authentic runtime event.

## Manual work

None.
