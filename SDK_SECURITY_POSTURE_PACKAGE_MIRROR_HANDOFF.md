# SDK Security Posture Package Mirror Handoff

Updated: 2026-09-10

```text
goal_id: FEDERAL-HEALTH-PII-EXCEEDANCE-HARDENING-001
child_task: SDK-SECURITY-POSTURE-PACKAGE-001
continuation_child: SDK-TASK-SCOPED-EPHEMERAL-POSTURE-002
repository: StegVerse-org/StegVerse-SDK
credential_authority: TV/TVC
github_runtime_authority: NONE
heartbeat_execution_authority: false
model_output_authority: NONE
```

## Purpose

Package concrete security postures for SDK use while allowing monotonic posture upgrades as StegVerse hardening improves. Posture is instantiated for the task being executed rather than treated as a permanent SDK-wide mode.

The posture remains separate from source-native payload semantics, processor selection, evaluator preregistration, and governance evidence. Selecting or elevating a posture cannot alter experimental observations or create evaluation-specific evidence fields.

```text
source-native data
+ processor request
+ optional evaluator declaration
+ evaluator requested security tier
+ evaluator organization minimum tier
+ data-class minimum tier
+ channel minimum tier
-> strongest applicable posture selected
-> task-scoped ephemeral posture instance
-> runtime posture attestation
-> fail closed unless effective posture is satisfied
-> normal processor/InTr path only after admission
```

## Current tiers

```text
SECURE  -> stegverse.security.secure.v1
HIGH    -> stegverse.security.high.v1
HIGHEST -> stegverse.security.health-pii-high.v1
```

The effective posture is the strongest applicable floor. A caller can request stronger security but cannot lower an organization, data-class, or channel minimum.

```text
requested SECURE + org SECURE + general SDK task -> SECURE
requested SECURE + org HIGH -> HIGH
requested SECURE + PII -> HIGH
requested SECURE + ePHI -> HIGHEST
any request + KV-SKAP or SKAP-KV -> HIGHEST
```

## KV / SKAP invariant

`KV-SKAP` and `SKAP-KV` are hard-pinned to the HIGHEST tier. This floor is not evaluator-selectable and cannot be downgraded by an SDK request. KV/SKAP therefore uses the strongest currently packaged posture while normal SDK evaluators can select SECURE through HIGHEST subject to their organization's minimum and the data/task floor.

## Ephemeral task posture instance

A posture instance is bound to exactly one task and has a bounded lifetime. Current default maximum lifetime is one hour, with a 15-minute normal task instance supported. The instance is explicitly non-transferable and cannot be reused across tasks.

```text
posture definition: durable immutable versioned policy
posture instance: ephemeral task-scoped realization
instance binds: task_id + posture_id + posture digest + effective tier + data class + channel + issued_at + expires_at
instance reuse across tasks: forbidden
expired instance: fail closed
silent downgrade: forbidden
```

The task posture is admission evidence only. It creates no execution, transition, credential, or governance authority.

## HIGHEST current controls

`stegverse.security.health-pii-high.v1` requires minimum-necessary manifesting, exact field and purpose scope, approved sink binding, payload digest binding, encryption in transit and at rest, audit receipts, pseudonymous subject identifiers, <=24h or stronger retention, automatic disposition, fresh runtime roots, predecessor-authority rejection, TV/TVC credentials only, no GitHub runtime authority, and no Heartbeat-granted execution authority.

Explicit prohibitions include undeclared secondary use, model training, advertising, data sale, undeclared sinks, raw sensitive data in audit receipts, and runtime secret inheritance.

## Upgrade contract

Posture definitions are immutable. Stronger future controls are published as new posture versions. Organization and channel floors can then move upward to the newer version without rewriting historical task evidence.

```text
historical v1 instance -> resolves exact v1 digest for replay
new HIGHEST v2 available -> new tasks may instantiate v2
organization floor upgraded to v2 -> v1-only runtime fails closed
KV-SKAP floor upgraded to v2 -> all new KV-SKAP instances require v2
```

## ELAN / experiment non-interference

The SDK attaches only posture reference/instance metadata under the security-posture extension. It does not inject posture controls into source-native test data, evaluator fields, governance-request fields, or experiment-visible evidence declarations. Evaluator security requirements therefore constrain the processing environment without biasing the experiment under evaluation.

## Current source

```text
stegverse/security_posture.py
tests/test_security_posture.py
SDK_SECURITY_POSTURE_PACKAGE_MIRROR_HANDOFF.md
```

## Next integration

Bind the selected task posture instance and posture digest to the exact payload/manifest digest at the Interlock/InTr boundary under `INTR-SENSITIVE-DATA-MANIFEST-PAYLOAD-BINDING-001`, then expose SDK CLI/API inputs for requested tier and organization minimum while retaining automatic mandatory elevation for data/channel floors.
