# SDK Evaluator Governance Posture Manifest Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Repository: `StegVerse-org/StegVerse-SDK`
Status: `ACTIVE_IMPLEMENTATION`

## Objective

Integrate evaluator-facing SDK manifest construction with the current governance processor route and the authoritative Interlock/InTr security-posture request contract without adding evaluator-specific evidence fields or allowing the SDK to resolve final posture.

## Required separation

```text
source-native evaluator data
+ governance processor request
+ optional evaluator preregistration declaration
+ optional SDK security-posture request inputs
-> canonical ingress manifest
-> governance route
-> Interlock/InTr authoritative posture resolution
```

The evaluator declaration remains outside `extensions.stegverse_governance_request`. The security-posture request remains outside governance evidence and carries only non-authorizing request inputs. The Manifest Builder must not derive `automatic_posture`, `effective_posture`, posture instance identity, or posture digest.

## Expected posture request

```text
schema = stegverse.sdk.security-posture-request.v1
selection_present = true|false
selected_tier = SECURE|HIGH|HIGHEST|null
organization_minimum_tier = SECURE|HIGH|HIGHEST
data_class = optional source classification
channel = optional transport channel
authority_effect = NONE_REQUEST_INPUT_ONLY
```

When `selection_present=false`, the builder must not fabricate an explicit selected tier. Interlock/InTr determines the automatic floor and effective posture.

## Completion predicates

- source-native payload unchanged;
- governance processor request remains complete and separate;
- evaluator declaration remains preregistration metadata only;
- SDK posture request remains non-authorizing and separate;
- no local effective-posture resolution by the Manifest Builder;
- prepare-only evaluator submission works with governance + posture request;
- negative tests reject malformed or internally contradictory posture request inputs.

## Manual work

None.
