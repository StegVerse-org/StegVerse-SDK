# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / ORGANIZATION-LOCAL ENDPOINT BINDING MERGED / ACTIVE PROBE VALIDATION PENDING`

## Canonical architecture

```text
source-native external resource observation
  -> stegverse.ingress-manifest.v1
       -> stegverse.state-transition-evidence.v1
  -> stegverse.external-interlock-ingress-binding.v1
  -> external interaction transport/control manifest
  -> organization federation packet/frame
  -> federation gateway / InTr ingress
  -> registry-selected INTERNAL_ENDPOINT
  -> registry-declared organization-local endpoint_adapter
  -> provider-neutral WorkSpace resource consumer
  -> runtime-supplied active probe executor when current represented state is PROBE_REQUIRED
```

The universal ingress manifest remains the manifested-data artifact. External interaction manifests remain transport/control artifacts. State-transition evidence and probe evidence remain non-authorizing. Provider observations do not become governance authority, InTr receipt authority, MIR custody, or Master Records custody.

## Completed implementation chain

```text
SDK PR #174: state-transition evidence MERGED at ee8f7023d74d70fa762e3982776c27c1e372a1f7
SDK PR #176: canonical ingress -> external Interlock binding MERGED at 7047e67d21173e800f78d4468519dba87992b16d
StegVerse-org/.github PR #9: provider-neutral INTERNAL_ENDPOINT dispatch MERGED at d8baefb8674ebed00bbbf9784c54e092a5b1a04d
SDK PR #178: collision-prevention coordination rule MERGED at 8a2dfe07294daacaa5d44d4777e94def182d8d78
SDK PR #179: provider-neutral WorkSpace resource consumer MERGED at 07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c
StegVerse-org/.github PR #10: organization-local WorkSpace endpoint binding MERGED at b851996afc5c5323d0d0db970dd46e511bd36338
```

PR #10 exact validated head `7fb6783ec7bbfbdc249dfdba45b7c454ae0beed4` passed:

```text
WorkSpace Internal Endpoint Binding Validation 34545811959: PASS
Internal Endpoint Dispatch Validation 34545811830: PASS
```

The organization registry now exposes `stegverse-org.workspace-resource-consumer` as an `INTERNAL_ENDPOINT` using `resident-runtime/workspace_resource_consumer_adapter.py`. The adapter is organization-local and delegates projection semantics to the installed canonical SDK consumer rather than copying that logic into the boundary repository.

## Provider-neutral WorkSpace consumer contract

Source:

```text
stegverse/workspace_resource_consumer.py
stegverse/active_probe_execution.py
tests/test_workspace_resource_consumer.py
tests/test_active_probe_execution.py
```

Supported lifecycle operations remain:

```text
OBSERVE
MATERIALIZE
REFRESH
REVOKE
EXPIRE
DESTROY
```

`MATERIALIZE` and `REFRESH` require derived transition readiness `READY`. Without a runtime probe executor, `PROBE_REQUIRED` fails closed. `REVOKE`, `EXPIRE`, and `DESTROY` remain available for teardown even after readiness degrades.

## Active probe candidate

SDK PR #181 implements provider-neutral active probe execution.

The probe executor is supplied by the runtime integration layer and is never read from caller manifest data. Each returned probe result must:

```text
profile: stegverse.active-probe-result.v1
bind the exact derived probe reason
carry observed_at
carry evidence_ref
carry source
outcome: SATISFIED or UNRESOLVED
authority_effect: NONE
```

Successful probe evidence can resolve only represented unresolved predicate/applicability/ambiguity/discovered-unknown state. The code then removes prior derived readiness fields and invokes the canonical state-transition normalizer again. Therefore neither caller data nor probe output can directly assign READY.

Current regression coverage requires:

```text
PROBE_REQUIRED + SATISFIED runtime probe -> canonical re-derivation may become READY
UNRESOLVED probe -> remains fail-closed
probe authority_effect != NONE -> rejected
probe reason mismatch -> rejected
already READY -> probe executor not invoked
```

This is source/CI evidence only. No authentic external provider probe has executed yet.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence profile: IMPLEMENTED / VALIDATED / MERGED
Canonical ingress -> external Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Registry-driven INTERNAL_ENDPOINT adapter dispatch: IMPLEMENTED / VALIDATED / MERGED
Provider-neutral WorkSpace resource consumer: IMPLEMENTED / VALIDATED / MERGED
Organization-local consumer binding: IMPLEMENTED / VALIDATED / MERGED
Active provider-neutral probe execution source: IMPLEMENTED / VALIDATION PENDING IN PR #181
Authentic external-provider probe: NOT PROVEN
Shared Docs live synchronization runtime: NOT PROVEN
StegOS/StegNode ephemeral projection runtime: NOT PROVEN
MIR transition reporting: NOT PROVEN
MIR external witness/OTS: TO-BUILD
Master Records authentic custody/reconstruction: NOT PROVEN
Expiry/revocation authentic runtime enforcement: NOT PROVEN
One-device authentic end-to-end execution: NOT PROVEN
```

No source, CI, request construction, or provider observation is to be promoted into an authentic runtime claim.

## Controlling WorkSpace invariants

```text
Anything that changes is a state transition.
Source content remains authoritative under the external system.
WorkSpace/StegOS projection is ephemeral and bounded.
Live synchronization exists only while current admission remains valid.
Ephemeral content does not imply ephemeral transition history.
MIR and Master Records retain distinct custody/authority roles.
Required behavior must remain complete on one current mobile device.
Caller assertion cannot satisfy a current probe requirement.
Probe evidence does not confer authority.
```

Expiry, renewal, revocation, edit observation, synchronization, probe result, authorization change, projection creation, refresh, and destruction are state transitions.

## README maintenance

README was reviewed for this source unit. The active-probe implementation does not introduce a new public processing capability identifier, universal ingress class, CLI/runtime route, or user-facing WorkSpace product surface. Existing README language already states that state-transition evidence itself does not execute a probe and that `PROBE_REQUIRED` is fail-closed. A README source change becomes required when an externally observable WorkSpace/provider probe surface is introduced.

## Next executable sequence

1. Validate and merge SDK PR #181.
2. Reconcile canonical SDK handoff/task registry with PR #181 merge evidence.
3. Bind a real external-provider probe adapter under explicit provider consent/authority.
4. Execute controlled `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY` transitions.
5. Retain MIR transition reporting and independent Master Records custody/reconstruction evidence.
6. Verify the entire path on one current mobile device.
7. Only after authentic runtime evidence exists, claim Shared Docs/StegOS WorkSpace runtime behavior.

## Human action

None is required for provider-neutral active-probe source work. External-provider authorization/consent becomes relevant only when authentic provider-backed execution begins.
