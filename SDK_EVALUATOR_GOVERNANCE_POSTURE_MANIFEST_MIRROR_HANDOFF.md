# SDK Evaluator Governance Posture Manifest Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `IMPLEMENTED_VALIDATED_AWAITING_MERGE`

## Objective

Integrate evaluator-facing SDK manifest construction with the current governance processor route and the authoritative Interlock/InTr security-posture request contract without adding evaluator-specific evidence fields or allowing the SDK to resolve final posture.

## Implemented separation

```text
source-native evaluator data
+ governance processor request
+ optional evaluator preregistration declaration
+ optional SDK security-posture request inputs
-> canonical ingress manifest
-> governance route
-> Interlock/InTr authoritative posture resolution
```

The evaluator declaration remains outside `extensions.stegverse_governance_request`. The security-posture request remains outside governance evidence and carries only non-authorizing request inputs. The evaluator composition layer does not derive `automatic_posture`, `effective_posture`, posture instance identity, or posture digest.

## Source

```text
stegverse/security_posture_request.py
stegverse/evaluator_manifest_builder.py
tests/test_evaluator_manifest_builder.py
.github/workflows/evaluator-governance-posture-manifest.yml
```

The existing processor-generic `stegverse.manifest_builder.build_manifest()` remains the canonical manifest constructor. `build_evaluator_governance_manifest()` composes the independent evaluator inputs around that builder rather than adding experiment-specific requirements to the universal manifest contract.

## Posture request contract

```text
schema = stegverse.sdk.security-posture-request.v1
selection_present = true|false
selected_tier = SECURE|HIGH|HIGHEST|null
organization_minimum_tier = SECURE|HIGH|HIGHEST
data_class = optional source classification
channel = optional transport channel
authority_effect = NONE_REQUEST_INPUT_ONLY
```

When `selection_present=false`, `selected_tier` must be absent/null. The SDK therefore cannot recreate the pre-StegOS-#325 fabricated SECURE selection behavior. Interlock/InTr determines the automatic floor and effective posture.

## Validation

PR #172 exact head before this handoff reconciliation: `a31f99ea247b99bbbb8e2ca146e5e16bff690269`.

```text
Evaluator Governance Posture Manifest Validation run 34517464907: PASS
- five evaluator/posture separation and negative tests: PASS
- existing Manifest Builder regression tests: PASS

SDK Package Artifact Validation run 34517464750: PASS
- exact wheel build/install/smoke validation: PASS
- non-authorizing package boundary retained: PASS
```

An earlier workflow attempt failed only because the workflow imported the package before installing its normal `requests` dependency; after adding `python -m pip install -e .`, the actual evaluator integration tests ran. A subsequent single test failure was an assertion-text mismatch (`non-authorizing` vs canonical `sdk_posture_request_must_be_non_authorizing`); the implementation correctly rejected the authorizing request and only the test expectation was corrected.

## Completion predicates

- source-native payload unchanged: PASS;
- governance processor request complete and separate: PASS;
- evaluator declaration remains preregistration metadata only: PASS;
- SDK posture request remains non-authorizing and separate: PASS;
- no local effective-posture resolution by evaluator manifest builder: PASS;
- explicit and no-selection posture semantics represented without local policy resolution: PASS;
- malformed/authorizing/contradictory posture input fails closed: PASS;
- package artifact compatibility: PASS.

## README review

The existing README already documents the processor-generic Manifest Builder, governance request separation, evaluator-defined manifests, and preregistration non-interference. This child adds a dedicated canonical handoff for the new posture-request input so the universal README contract is not rewritten into an evaluator-specific schema.

## Remaining boundary

Source integration and CI do not prove a live evaluator execution through the new StegOS Interlock/InTr resolver. Runtime evaluator proof should submit a manifest produced by this composition layer, observe an InTr-resolved posture instance bound to the exact task/payload/transition request, then retain governance/custody/replay/reconstruction evidence without predefining favorable experimental observations.

## Manual work

None.
