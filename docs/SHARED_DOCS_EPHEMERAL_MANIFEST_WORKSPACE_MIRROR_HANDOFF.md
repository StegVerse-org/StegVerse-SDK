# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / GENERIC MANIFEST-TO-INTR BRIDGE MERGED / WORKSPACE RESOURCE CONSUMER PENDING`

## Completed implementation chain

### State-transition evidence

SDK PR #174 merged at `ee8f7023d74d70fa762e3982776c27c1e372a1f7`.

It added provider-neutral `stegverse.state-transition-evidence.v1` under the existing `stegverse.ingress-manifest.v1` `extensions` boundary. Unknown applicability, unresolved applicable evidence, open ambiguity, or discovered unresolved unknowns force `PROBE_REQUIRED`; contradictory `READY` claims fail closed.

### Canonical ingress to external Interlock binding

SDK PR #176 merged at `7047e67d21173e800f78d4468519dba87992b16d`.

It added:

```text
stegverse/external_interlock_ingress_binding.py
tests/test_external_interlock_ingress_binding.py
```

The adapter validates the exact ingress wire manifest, hash-binds that exact object, and places it inside the existing `stegverse.external_organization.interaction_manifest.v1` transport/control artifact.

The separation is now executable source behavior:

```text
external interaction manifest = transport/control artifact
stegverse.ingress-manifest.v1 = universal manifested-data artifact
stegverse.state-transition-evidence.v1 = state evidence inside canonical ingress
```

The request records:

```text
authority_transfer: false
sdk_mints_intr_receipt: false
sdk_claims_delivery: false
canonical_ingress_grants_transport_authority: false
```

A `PROBE_REQUIRED` state survives transport binding without promotion. Nested-ingress tampering, binding tampering, interaction-manifest tampering, operation mismatch, and authority-field mutation fail validation.

### Validation repairs

The first PR #176 source-validation run failed because the new tests were pytest-style functions while the workflow invoked `python -m unittest`; unittest discovered zero tests. The tests were converted to the repository's unittest convention.

The next run exposed a substantive serialization bug: the adapter nested the enriched return value of `validate_ingress_manifest()`, which contains validator-derived internal fields that are not legal caller-supplied top-level wire fields. The adapter was corrected to validate the submitted wire object but transport/hash-bind the exact valid wire manifest itself. Derived validation state is not serialized back into the universal envelope.

Final exact-head evidence before merge:

```text
PR #176 exact head: 913f652d5ebd3c4479ba64b31316916d60ba92dc
Manifest Builder Source Validation 34536379000: SUCCESS
SDK Package Artifact Validation 34536379094: SUCCESS
PR mergeable before merge: true
merge: SUCCESS
merge SHA: 7047e67d21173e800f78d4468519dba87992b16d
```

README review remains current: this SDK adapter introduced no new public processing capability identifier, runtime route, universal manifest field, user-facing WorkSpace surface, or runtime claim. Existing README semantics already document generic manifested-data processing and Interlock separation. README must change when an externally observable WorkSpace capability/surface is introduced.

## Cross-repository runtime dispatch repair

Tracing the organization federation path found a real genericity defect in `StegVerse-org/.github`.

`org-kernel/kernel.py::dispatch` already selected registered `INTERNAL_ENDPOINT` services generically, but production `org-boundary/runtime/process_boundary.py` executed a configured `endpoint_adapter` only when the service ID was exactly `stegverse-org.stegverse-sdk`.

StegVerse-org/.github PR #9 removed that service-ID special case and merged at `d8baefb8674ebed00bbbf9784c54e092a5b1a04d` after `Internal Endpoint Dispatch Validation` run `34536206284` succeeded.

The production boundary processor now executes any registry-declared `INTERNAL_ENDPOINT` adapter while requiring the adapter path to resolve inside the organization repository root. Unknown services, missing adapters, external-path adapters, and failed adapters remain fail-closed. README and `docs/ORG_FEDERATION_GENERIC_ENDPOINT_ADAPTER_MIRROR_HANDOFF.md` were maintained in that repository.

This means a future WorkSpace endpoint can use the existing service registry + Interlock/InTr organization boundary without adding another service-ID branch to the boundary processor.

## Current executable path

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
```

Every layer through endpoint-adapter selection now has an executable source path. What remains missing for WorkSpace is the actual provider-neutral resource/projection consumer behind that adapter and authentic external-provider execution evidence.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence profile: IMPLEMENTED / VALIDATED / MERGED
Fail-closed READY vs PROBE_REQUIRED derivation: IMPLEMENTED / VALIDATED / MERGED
Canonical ingress -> external Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Registry-driven organization INTERNAL_ENDPOINT adapter dispatch: IMPLEMENTED / VALIDATED / MERGED
External Interlock bootstrap: EXISTS / NON-TRANSPORT
Federation gateway transport implementation: EXISTS
Generic WorkSpace external-resource consumer: NOT YET IMPLEMENTED
Active probe execution for WorkSpace predicates: NOT YET IMPLEMENTED
Shared Docs live synchronization runtime: NOT PROVEN
StegOS/StegNode ephemeral projection runtime for Shared Docs: NOT PROVEN
MIR transition reporting for this experiment: NOT PROVEN
MIR external witness/OTS: TO-BUILD
Master Records authentic custody/reconstruction for this experiment: NOT PROVEN
Expiry/revocation runtime enforcement for WorkSpace: NOT PROVEN
One-device authentic end-to-end execution: NOT PROVEN
```

No source, CI, request construction, or provider observation is to be promoted into an authentic runtime claim.

## Controlling WorkSpace invariants

```text
Anything that changes is a state transition.
source content remains authoritative under the external system.
WorkSpace/StegOS projection is ephemeral and bounded.
live synchronization exists only while current admission remains valid.
ephemeral content does not imply ephemeral transition history.
MIR and Master Records retain distinct custody/authority roles.
required behavior must remain complete on one current mobile device.
```

Expiry, renewal, revocation, edit observation, synchronization, probe result, authorization change, projection creation, refresh, and destruction are state transitions.

## Session collision-prevention coordination

Canonical coordination rule: `docs/SESSION_COLLISION_COORDINATION_RULE.md`.

Before progressing any coincident session or narrower task that overlaps this lane, reconcile it against the GitHub Task Registry and the applicable broader/global handoff. When the broader/global task owns the remaining overlapping scope and all unique work/evidence from the narrower session has been durably transferred, that narrower session/task must transition to `INACTIVE`, identify the controlling Global Task ID and Handoff Task ID, and stop progressing the work.

Required disposition:

```text
STATUS: INACTIVE
coordinated_with_global_task_id: <canonical broader/global Goal Task ID>
coordinated_with_handoff_task_id: <canonical broader/global *_MIRROR_HANDOFF.md path>
work_progression_allowed: false
```

`INACTIVE` means coordination ownership moved; it does not mean the underlying work is complete. The controlling global task may remain `ACTIVE`. A coincident session must not continue simply because it can still access its branch, prompt history, or prior handoff. Re-activation requires explicit canonical ownership transfer or decomposition into a genuinely separate canonical Goal Task ID.

## Next executable target

Do not introduce a Shared Docs-specific API or service schema unless actual provider inspection proves an adapter is required.

The next source unit should be a provider-neutral organization-local external-resource endpoint adapter/consumer that:

1. consumes the already-bound canonical ingress object;
2. rejects `PROBE_REQUIRED` for materialization until an explicit probe result resolves the represented condition;
3. supports bounded lifecycle operations needed by the experiment (`OBSERVE`, `MATERIALIZE`, `REFRESH`, `REVOKE`/`EXPIRE`, `DESTROY`) without claiming provider behavior;
4. records deterministic resource/projection bindings and prior/new state references;
5. provides hooks/interfaces for authentic provider read/refresh/revoke operations rather than embedding Shared Docs semantics;
6. leaves InTr receipt minting, governance/admission authority, MIR custody, and Master Records custody with their owning systems;
7. can later be driven through the one-device experiment path.

After that source consumer is validated, bind the authentic external provider adapter and perform the controlled live-edit + probe + expiry/revocation + teardown test.

## Human action

None is required for the next provider-neutral source implementation. Richard Whitney's participation becomes necessary only when authentic Shared Docs access/consent is required for the live provider-backed experiment.
