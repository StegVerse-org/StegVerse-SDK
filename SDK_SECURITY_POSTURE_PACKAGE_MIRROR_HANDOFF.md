# SDK Security Posture Package Mirror Handoff

Updated: 2026-09-10

```text
goal_id: FEDERAL-HEALTH-PII-EXCEEDANCE-HARDENING-001
child_task: SDK-SECURITY-POSTURE-PACKAGE-001
repository: StegVerse-org/StegVerse-SDK
credential_authority: TV/TVC
github_runtime_authority: NONE
heartbeat_execution_authority: false
model_output_authority: NONE
```

## Purpose

Package a concrete security posture for SDK use now while allowing monotonic posture upgrades as StegVerse hardening improves.

The posture is deliberately separate from source-native payload semantics, processor selection, evaluator preregistration, and governance evidence. Selecting a posture cannot alter experimental observations or create evaluation-specific evidence fields.

```text
source-native data
+ processor request
+ optional evaluator declaration
+ security posture reference
-> SDK manifest
-> runtime posture attestation
-> fail closed unless selected posture is satisfied
-> normal processor/InTr path only after admission
```

## Initial posture

```text
posture_id: stegverse.security.health-pii-high.v1
version: 1
classification: PII / ePHI / sensitive-health-data
```

Required controls include minimum-necessary manifesting, exact field and purpose scope, approved sink binding, payload digest binding, encryption in transit and at rest, audit receipts, pseudonymous subject identifiers, <=24h or stronger retention, automatic disposition, fresh runtime roots, predecessor-authority rejection, TV/TVC credentials only, no GitHub runtime authority, and no Heartbeat-granted execution authority.

Explicit prohibitions include undeclared secondary use, model training, advertising, data sale, undeclared sinks, raw sensitive data in audit receipts, and runtime secret inheritance.

## Upgrade contract

A caller pins an explicit posture ID/version and digest. New stronger profiles are added under new immutable IDs such as `stegverse.security.health-pii-high.v2`; existing profile semantics are not silently rewritten.

```text
v1 request + v1-capable runtime -> admissible
v1 request + stronger v2-capable runtime -> admissible if v1 remains satisfied
v2 request + only-v1 runtime -> fail closed
unknown posture -> fail closed
silent downgrade -> forbidden
```

A posture upgrade therefore does not require rewriting historical manifests. Replays resolve the original posture ID/digest; new submissions can select the stronger profile.

## ELAN / experiment non-interference

The SDK attaches only a posture reference and digest under `extensions.security_posture`. It does not inject the posture's control list into source-native test data, evaluator fields, governance-request fields, or experiment-visible evidence declarations. This preserves the existing SDK rule that governance-specific or test-specific fields are not universal manifest requirements.

## Current source

```text
stegverse/security_posture.py
tests/test_security_posture.py
SDK_SECURITY_POSTURE_PACKAGE_MIRROR_HANDOFF.md
```

## Next integration

Bind the selected posture digest to the exact payload/manifest digest at the Interlock/InTr boundary under `INTR-SENSITIVE-DATA-MANIFEST-PAYLOAD-BINDING-001`, then expose an SDK CLI/API admission surface that can consume runtime posture attestations without moving authority into the SDK.
