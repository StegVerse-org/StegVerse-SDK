# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / GENERIC RESOURCE CONSUMER IMPLEMENTED-VALIDATED-MERGED / ORGANIZATION-LOCAL ENDPOINT BINDING NEXT`

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

SDK PR #174 merged at `ee8f7023d74d70fa762e3982776c27c1e372a1f7`, adding provider-neutral `stegverse.state-transition-evidence.v1` with fail-closed `READY`/`PROBE_REQUIRED` derivation.

SDK PR #176 merged at `7047e67d21173e800f78d4468519dba87992b16d`, adding exact-wire canonical ingress to external Interlock binding. Validation runs `34536379000` and `34536379094` passed.

StegVerse-org/.github PR #9 merged at `d8baefb8674ebed00bbbf9784c54e092a5b1a04d` after Internal Endpoint Dispatch Validation `34536206284` passed, removing SDK-specific service-ID hardcoding from production organization endpoint dispatch and enforcing organization-root adapter containment.

SDK PR #178 merged at `8a2dfe07294daacaa5d44d4777e94def182d8d78`, establishing `docs/SESSION_COLLISION_COORDINATION_RULE.md`. A narrower/coincident session whose remaining scope is owned by a broader/global task must transfer unique evidence, transition to `INACTIVE`, identify the controlling Global Task ID and Handoff Task ID, and stop progressing overlapping work unless canonical ownership is explicitly transferred back.

SDK PR #179 merged at `07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c`, implementing the provider-neutral WorkSpace resource consumer. Exact validated head: `7a98cf776b13d90794cc330762bfd25761b8f501`.

PR #179 validation evidence:

```text
Manifest Builder Source Validation 34545309589: PASS
SDK Package Artifact Validation 34545309554: PASS
```

The package validation completed source materialization, build, exact wheel metadata verification, isolated wheel installation, and smoke validation successfully. The source validation ran the new WorkSpace consumer regression suite successfully.

## Provider-neutral WorkSpace consumer contract

Source:

```text
stegverse/workspace_resource_consumer.py
tests/test_workspace_resource_consumer.py
```

Supported lifecycle operations:

```text
OBSERVE
MATERIALIZE
REFRESH
REVOKE
EXPIRE
DESTROY
```

`MATERIALIZE` and `REFRESH` require transition readiness `READY`; `PROBE_REQUIRED` fails closed. `REVOKE`, `EXPIRE`, and `DESTROY` remain available for teardown even after readiness degrades to `PROBE_REQUIRED`.

An optional provider hook may return current provider observations. Provider-hook output remains evidence only and does not grant governance authority, mint an InTr receipt, or claim MIR or Master Records custody.

The output binds the canonical ingress hash, transition identity, prior/new state refs, prior projection ref, readiness/probe reasons, optional provider evidence, and a deterministic `projection_state_ref`.

README review remains current. The merged source unit introduced no new public processing capability identifier, universal ingress class, runtime route, or user-facing WorkSpace product surface. README must be updated when an externally observable WorkSpace capability/surface is introduced.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence profile: IMPLEMENTED / VALIDATED / MERGED
Canonical ingress -> external Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Registry-driven INTERNAL_ENDPOINT adapter dispatch: IMPLEMENTED / VALIDATED / MERGED
Provider-neutral WorkSpace resource consumer: IMPLEMENTED / VALIDATED / MERGED
Organization-local consumer binding: PENDING
Active provider probe execution: PENDING
External Interlock bootstrap: EXISTS / NON-TRANSPORT
Federation gateway transport implementation: EXISTS
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

1. Reconcile the StegVerse-org/.github endpoint-registry handoff before touching that repository, applying the collision-prevention rule.
2. Bind the merged generic consumer into the organization-local `INTERNAL_ENDPOINT` adapter slot without introducing a Shared Docs-specific universal schema.
3. Validate the organization-local adapter path and containment behavior.
4. Add active probe execution so `PROBE_REQUIRED` can be resolved by authentic current evidence rather than caller assertion.
5. Bind an authentic external-provider adapter for the controlled experiment.
6. Execute live `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY` transitions.
7. Retain MIR transition reporting and independent Master Records custody/reconstruction evidence.
8. Verify the entire path on one current mobile device.
9. Only after runtime evidence exists, claim Shared Docs/StegOS WorkSpace runtime behavior.

## Session handoff boundary

This session reached Goal Prompt Count 12 after PR #179 was implemented, validated, merged, and canonical reconciliation was prepared. Continue the same ACTIVE Goal Task ID in a new session from the organization-local endpoint binding step above. Do not open a parallel coincident session for the same binding work unless its ownership is explicitly separated in the Task Registry.

## Human action

None is required for organization-local consumer binding or provider-neutral active-probe source work. External-provider consent/access becomes required only when the provider-backed experiment reaches authentic live execution.
