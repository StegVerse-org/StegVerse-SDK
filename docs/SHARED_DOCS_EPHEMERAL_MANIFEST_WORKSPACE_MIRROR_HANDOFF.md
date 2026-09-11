# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / GENERIC RESOURCE CONSUMER IMPLEMENTED IN PR #179 / VALIDATION AND RUNTIME BINDING PENDING`

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
```

The universal ingress manifest remains the manifested-data artifact. External interaction manifests remain transport/control artifacts. State-transition evidence remains non-authorizing evidence. Provider observations do not become governance authority, InTr receipt authority, MIR custody, or Master Records custody.

## Completed implementation chain

### State-transition evidence

SDK PR #174 merged at `ee8f7023d74d70fa762e3982776c27c1e372a1f7`.

It added provider-neutral `stegverse.state-transition-evidence.v1`. Unknown applicability, unresolved applicable evidence, open ambiguity, or discovered unresolved unknowns force `PROBE_REQUIRED`; contradictory `READY` claims fail closed.

### Canonical ingress to external Interlock binding

SDK PR #176 merged at `7047e67d21173e800f78d4468519dba87992b16d`.

The adapter validates and hash-binds the exact ingress wire object inside the existing external-organization transport/control artifact. Validator-derived state is not serialized back into the universal envelope.

Final validation evidence for PR #176:

```text
Manifest Builder Source Validation 34536379000: PASS
SDK Package Artifact Validation 34536379094: PASS
```

### Generic organization endpoint dispatch

StegVerse-org/.github PR #9 merged at `d8baefb8674ebed00bbbf9784c54e092a5b1a04d` after Internal Endpoint Dispatch Validation run `34536206284` passed.

Production organization boundary dispatch now executes any registry-declared `INTERNAL_ENDPOINT` adapter while enforcing organization-root containment. No SDK-specific service-ID branch is required for a WorkSpace consumer.

### Collision-prevention coordination

SDK PR #178 merged at `8a2dfe07294daacaa5d44d4777e94def182d8d78`.

Canonical rule: `docs/SESSION_COLLISION_COORDINATION_RULE.md`.

A narrower/coincident session whose remaining scope is owned by a broader/global task must transfer unique evidence, transition to `INACTIVE`, identify the controlling Global Task ID and Handoff Task ID, and stop progressing overlapping work unless canonical ownership is explicitly transferred back.

### Provider-neutral WorkSpace resource consumer

Current implementation PR: `StegVerse-org/StegVerse-SDK#179`.

Branch: `workspace-generic-resource-consumer`.

New source:

```text
stegverse/workspace_resource_consumer.py
tests/test_workspace_resource_consumer.py
```

Implemented source behavior:

```text
supported lifecycle operations:
  OBSERVE
  MATERIALIZE
  REFRESH
  REVOKE
  EXPIRE
  DESTROY

MATERIALIZE/REFRESH:
  require transition readiness == READY
  PROBE_REQUIRED -> fail closed

REVOKE/EXPIRE/DESTROY:
  remain available for teardown even when readiness becomes PROBE_REQUIRED

provider hook:
  optional provider-neutral callback
  returned value is provider evidence only
  grants no governance authority
  mints no InTr receipt
  claims no MIR custody
  claims no Master Records custody

projection state:
  deterministic canonical ingress hash
  transition identity
  prior/new state references
  prior projection reference
  derived readiness/probe reasons
  deterministic projection_state_ref
```

The source consumer does not claim provider I/O unless a provider hook actually executes, does not claim delivery, and does not promote source/CI behavior into runtime evidence.

README review: current README already documents the generic manifest/state-transition boundary and non-authorizing semantics. This source unit introduces no new public processing capability identifier, ingress class, runtime route, or user-facing WorkSpace product surface, so no README contract change is required at this stage. README must be updated when an externally observable WorkSpace capability/surface is introduced.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence profile: IMPLEMENTED / VALIDATED / MERGED
Canonical ingress -> external Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Registry-driven INTERNAL_ENDPOINT adapter dispatch: IMPLEMENTED / VALIDATED / MERGED
Provider-neutral WorkSpace resource consumer: IMPLEMENTED IN PR #179 / NOT YET MERGED
Consumer regression validation: PENDING PR #179 CI
External Interlock bootstrap: EXISTS / NON-TRANSPORT
Federation gateway transport implementation: EXISTS
Active provider probe execution: NOT YET IMPLEMENTED
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
```

Expiry, renewal, revocation, edit observation, synchronization, probe result, authorization change, projection creation, refresh, and destruction are state transitions.

## Next executable sequence

1. Complete PR #179 source validation and merge only on passing evidence.
2. Bind the generic consumer into the organization-local `INTERNAL_ENDPOINT` adapter slot without introducing a Shared Docs-specific universal schema.
3. Add active probe execution so a `PROBE_REQUIRED` condition can be resolved by authentic current evidence rather than caller assertion.
4. Bind an authentic external-provider adapter for the controlled experiment.
5. Execute live `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY` transitions.
6. Retain MIR transition reporting and independent Master Records custody/reconstruction evidence.
7. Verify the entire path on one current mobile device.
8. Only after runtime evidence exists, claim Shared Docs/StegOS WorkSpace runtime behavior.

## Human action

None is required for provider-neutral source validation or organization-local consumer binding. External-provider consent/access becomes required only when the provider-backed experiment reaches authentic live execution.
