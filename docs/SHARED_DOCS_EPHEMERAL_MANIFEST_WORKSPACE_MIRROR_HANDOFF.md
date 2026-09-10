# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Prior implementation: `PR #174 MERGED`
Prior merge SHA: `ee8f7023d74d70fa762e3982776c27c1e372a1f7`
Current branch: `workspace-generic-intr-binding-v2`
Status: `ACTIVE / GENERIC INGRESS-TO-INTR BINDING IMPLEMENTED / VALIDATION PENDING`

## Controlling architecture

The Shared Docs experiment reuses the existing generic-manifest + Interlock/InTr architecture. It does not create a bespoke Shared Docs API or caller-specific manifest class.

```text
entity
  -> source-native data
  -> stegverse.ingress-manifest.v1
       -> extensions.stegverse_state_transition
  -> external Interlock transport-control envelope
  -> InTr admitted ingress
  -> organization-local capability consumer
  -> bounded projection/output
```

The canonical `stegverse.ingress-manifest.v1` remains the universal manifested-data envelope. `stegverse.external_organization.interaction_manifest.v1` is transport/bootstrap control metadata only; it must not become a parallel universal payload schema.

Identity, relationship, credentials, current state, and requested capability may affect admissibility. They do not change the universal manifest class merely because the communicating entity differs.

## Completed prior source implementation

PR #174 merged `stegverse.state-transition-evidence.v1` under the existing ingress-manifest `extensions` boundary. Readiness is fail-closed:

```text
known applicable predicate + SATISFIED evidence -> may contribute to READY
known applicable predicate + unresolved evidence -> PROBE_REQUIRED
predicate applicability UNKNOWN -> PROBE_REQUIRED
open ambiguity -> PROBE_REQUIRED
open discovered unknown -> PROBE_REQUIRED
all represented applicable predicates satisfied + all ambiguity/discoveries resolved -> READY
caller READY contradicting derived state -> reject
```

The evidence profile grants no authority and preserves the rule that a genuinely unknown unknown can only become enforceable after discovery makes it known state.

Final PR #174 validation was green on the exact pre-merge head, and merge completed at `ee8f7023d74d70fa762e3982776c27c1e372a1f7`.

## Executable consumer trace

Cross-repository inspection located an actual organization-local receiver pattern in:

```text
StegVerse-002/.github
resident-runtime/self_characterization_surface.py
```

That surface:

- accepts an already-admitted InTr ingress envelope;
- validates request class, transport, destination, exact manifest bindings, and authority boundaries;
- resolves only its organization-local entity/principal binding;
- invokes the sovereign resident principal only after those checks;
- retains Master Records as required evidence/custody semantics.

It is intentionally operation-specific to self-characterization and is not itself a generic WorkSpace receiver. Its existence proves the transport-to-org-local-consumer pattern, not Shared Docs runtime completion.

The matching SDK producer-side bootstrap remains `stegverse/external_interlock_bootstrap.py`. It constructs request/control artifacts but explicitly does not perform transport, mint InTr receipts, transfer authority, or claim delivery.

## Current implementation: canonical ingress to external Interlock binding

The branch adds:

```text
stegverse/external_interlock_ingress_binding.py
tests/test_external_interlock_ingress_binding.py
```

The adapter validates the canonical ingress manifest first, computes its canonical SHA-256, then places that exact validated ingress object inside the existing external interaction manifest payload. The external Interlock request binds both the interaction-manifest identity/hash and the canonical ingress profile/hash.

This means:

```text
external interaction manifest = transport/control artifact
canonical ingress manifest     = manifested-data artifact
state-transition evidence      = canonical ingress extension
```

The adapter explicitly records:

```text
authority_transfer: false
sdk_mints_intr_receipt: false
sdk_claims_delivery: false
canonical_ingress_grants_transport_authority: false
```

Validation rejects altered transport-control semantics, interaction-manifest hash mismatch, nested canonical-ingress tampering, canonical-ingress binding mismatch, operation mismatch, and authority-field mutation before any runtime/transport claim can be accepted.

A `PROBE_REQUIRED` state is preserved unchanged through the transport binding; wrapping a manifest cannot promote readiness.

## Focused test predicates

`tests/test_external_interlock_ingress_binding.py` verifies:

1. canonical `stegverse.ingress-manifest.v1` remains nested as the actual manifested-data payload;
2. `stegverse.external_organization.interaction_manifest.v1` remains transport/control metadata;
3. state-transition `READY` remains exact when legitimately derived;
4. `PROBE_REQUIRED` survives transport binding without promotion;
5. nested canonical-ingress tampering fails;
6. canonical-ingress hash-binding tampering fails;
7. transport control cannot be mutated to claim SDK delivery authority.

The existing Manifest Builder Source Validation workflow is updated to run and compile the new adapter/test anonymously from the exact PR source.

README maintenance was reviewed. This adapter adds no new public processing capability identifier, route, universal manifest field, user-facing WorkSpace surface, or runtime claim; the existing README generic-manifest and Interlock separation already describes the controlling semantics. No redundant README edit is required at this source-adapter stage. README must be updated when a new public capability/route/surface or externally observable WorkSpace runtime behavior is actually introduced.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence profile: IMPLEMENTED / VALIDATED / MERGED
Fail-closed READY vs PROBE_REQUIRED derivation: IMPLEMENTED / VALIDATED / MERGED
Canonical ingress -> external Interlock binding: SOURCE IMPLEMENTED / VALIDATION PENDING
External Interlock bootstrap request construction: EXISTS / NON-TRANSPORT
Organization-local InTr consumer pattern: LOCATED / AUTHENTIC SOURCE
Generic WorkSpace organization-local consumer: NOT YET IMPLEMENTED
Shared Docs bespoke API requirement: NONE ESTABLISHED
Shared Docs live synchronization runtime: NOT PROVEN
StegOS/StegNode ephemeral projection runtime: NOT PROVEN
active probe execution: NOT PROVEN
MIR transition reporting: NOT PROVEN
MIR external witness/OTS: TO-BUILD
Master Records authentic custody/reconstruction for this experiment: NOT PROVEN
expiry/revocation runtime enforcement: NOT PROVEN
one-device authentic end-to-end execution: NOT PROVEN
```

Do not promote source validation, request construction, provider observation, or design convergence into runtime completion.

## Ephemeral WorkSpace model

```text
source content: durable under authoritative external system
WorkSpace/StegOS projection: ephemeral and bounded
updates: live/synchronized only while current admission remains valid
MIR: historical state-transition record keeper
Master Records: independent StegVerse custody/replay/reconstruction evidence
```

Anything that changes is a state transition. Expiry, renewal, revocation, edit observation, synchronization, probe result, authorization change, projection creation, and projection destruction are transitions.

Ephemeral content does not imply ephemeral transition history. Required behavior must remain operable from one current mobile device; a second user-operated device is not an admissible dependency.

## Next actions

1. Run hosted exact-head source/package/evaluator validation for the generic ingress-to-InTr adapter and merge if green.
2. Trace the federation gateway ingress dispatch that selects the organization-local consumer; identify the narrow generic service-registration surface rather than cloning the self-characterization consumer.
3. Implement a provider-neutral external-resource projection consumer with explicit operations such as observe/materialize/refresh/revoke only if the existing service-dispatch layer lacks equivalent generic capability.
4. Bind actual probe execution so `PROBE_REQUIRED` can transition to later READY only after durable evidence resolves the relevant predicate/ambiguity/discovery.
5. Bind MIR and Master Records through authentic executable interfaces without conflating custody/authority.
6. Construct the authentic live-edit + probe + expiry/revocation + teardown + one-device experiment.

## Human action

None is required for current source implementation, validation, and receiver/dispatch tracing. Richard Whitney's participation becomes necessary only when an authentic test requires authorized access to his independently controlled Shared Docs runtime or consent to attach an Interlock/InTr participant/adapter to it.
