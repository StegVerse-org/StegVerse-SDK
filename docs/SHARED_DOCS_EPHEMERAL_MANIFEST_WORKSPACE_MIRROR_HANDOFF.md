# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Implementation PR: `#174`
Implementation branch: `shared-docs-ephemeral-workspace`
Status: `ACTIVE / SOURCE_IMPLEMENTATION_IN_VALIDATION`

## Controlling architecture

The Shared Docs experiment reuses the existing generic-manifest + Interlock/InTr architecture. It does not create a bespoke Shared Docs API or a new caller-specific manifest class.

```text
entity
  -> source-native data
  -> stegverse.ingress-manifest.v1
  -> correctly shaped transition evidence
  -> Interlock/InTr / installed processing route
  -> admitted projection/output
```

Identity, relationship, credentials, current state, and requested capability may change admissibility. They do not change the universal manifest class merely because the communicating entity differs.

The inter-Entity rule is universal: ambiguity and discovered unknowns that affect readiness must be representable as state. A genuinely unknown unknown cannot be enforced before discovery; once discovered, it becomes known state and must be incorporated before a later READY classification.

## Universal state-transition rule

```text
Anything that changes is a state transition.
```

This includes document edits, synchronization updates, login/session creation, renewal, expiry, revocation, permission/scope changes, identity/device/node changes, projection creation/refresh/destruction, and incorporation of newly discovered unknowns into known state.

A timer is a transition trigger, not a side channel. Expiry, renewal, and revocation are transitions.

## Ephemeral WorkSpace model

```text
source content: durable under authoritative external system
WorkSpace/StegOS projection: ephemeral and bounded
updates: live/synchronized only while current admission remains valid
MIR: historical state-transition record keeper
Master Records: independent StegVerse custody/replay/reconstruction evidence
```

Ephemeral content does not imply ephemeral transition history. The projection must not silently become a second authoritative document store.

MIR witness/OTS capability remains `TO-BUILD` unless authentic executable evidence proves otherwise. Master Records must not be represented as a substitute for MIR authority.

## Mobile-first invariant

Required behavior must remain operable from one current mobile device. Additional devices/displays may enhance the experience but may not become a prerequisite for the governed workflow.

## Source implementation added in PR #174

PR #174 introduces `stegverse.state-transition-evidence.v1` as a provider-neutral manifest extension helper under the existing `extensions` boundary. The outer manifest remains `stegverse.ingress-manifest.v1`; no new processing route, credential authority, Shared Docs-specific API, or runtime authority is introduced.

Implemented files:

```text
stegverse/state_transition_evidence.py
tests/test_state_transition_evidence.py
.github/workflows/manifest-builder-source-validation.yml
```

The profile records:

- stable `transition_id`;
- `state_domain`;
- `prior_state_ref` and `new_state_ref`;
- `change_type`;
- known `applicable_predicates` with applicability and evidence state;
- `ambiguities`;
- `discovered_unknowns`;
- derived readiness and deterministic probe reasons.

Readiness is fail-closed:

```text
known applicable predicate + SATISFIED evidence -> may contribute to READY
known applicable predicate + unresolved evidence -> PROBE_REQUIRED
predicate applicability UNKNOWN -> PROBE_REQUIRED
open ambiguity -> PROBE_REQUIRED
open discovered unknown -> PROBE_REQUIRED
all represented applicable predicates satisfied + all ambiguity/discoveries resolved -> READY
caller READY contradicting derived state -> reject
```

The helper also records:

```text
evidence_grants_authority: false
unknown_unknown_policy: ENFORCE_AFTER_DISCOVERY_AS_KNOWN_STATE
```

This implements the state representation/readiness discipline only. It does not itself execute probes, govern a transition, materialize a WorkSpace, synchronize a document, or write MIR/Master Records.

## Test coverage added

`tests/test_state_transition_evidence.py` covers:

1. all represented applicable predicates satisfied -> `READY`;
2. unknown predicate applicability -> `PROBE_REQUIRED`;
3. open ambiguity -> `PROBE_REQUIRED`;
4. discovered unknown -> `PROBE_REQUIRED` until resolved;
5. contradictory caller claim of `READY` -> rejected;
6. invalid NOT_APPLICABLE/evidence combination -> rejected;
7. Shared Docs-shaped external document observation attaches without changing manifest class or source-native payload;
8. initial materialization may have `prior_state_ref: null`.

The Manifest Builder Source Validation workflow was extended to execute and compile the new module/test.

## Validation evidence

Exact PR #174 head after the initial three source/CI commits was `05a0f4b2014aeaa9dca39e2a1c47e9f17c83873a`.

Observed GitHub Actions evidence on that head:

```text
Manifest Builder Source Validation run 34531438582: SUCCESS
SDK Package Artifact Validation run 34531438495: in progress at last observation
```

The local assistant container could not clone GitHub because DNS resolution for `github.com` was unavailable. This is a local tool-network condition, not an SDK test failure; hosted exact-head validation is the usable evidence path.

## Authentic Shared Docs capability predicates

The first authentic capability test still requires evidence that:

1. a correctly shaped generic manifest admits an external document/resource request through the ordinary path;
2. a bounded ephemeral projection is materialized without transferring authoritative custody;
3. a deterministic current document marker/hash is observed;
4. the authoritative document is edited live;
5. the new observation is represented as a linked state transition using the same generic manifest class;
6. ambiguity/unknown applicability cannot be silently inferred READY and produces durable probe/evidence state;
7. the changed projection synchronizes while authorization remains admissible;
8. expiry or revocation changes state and further access fails closed;
9. the ephemeral projection is destroyed;
10. MIR receives required historical transition evidence when an executable MIR interface exists;
11. Master Records independently retains reconstructable evidence when an executable custody path exists;
12. the user-driven flow remains possible from one current mobile device.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / previously merged
State-transition evidence profile: IMPLEMENTED IN PR #174
Fail-closed READY vs PROBE_REQUIRED derivation: SOURCE IMPLEMENTED / HOSTED TEST PASS
Shared Docs bespoke API requirement: NONE ESTABLISHED
Shared Docs live synchronization runtime: NOT PROVEN
StegOS/StegNode ephemeral projection runtime: NOT PROVEN
Interlock/InTr execution of this Shared Docs transition profile: NOT PROVEN
active probe execution: NOT PROVEN
MIR transition reporting: NOT PROVEN
MIR external witness/OTS: TO-BUILD
Master Records authentic custody/reconstruction for this experiment: NOT PROVEN
expiry/revocation runtime enforcement: NOT PROVEN
one-device authentic end-to-end execution: NOT PROVEN
```

Do not promote source/CI validation, provider observation, or design convergence into runtime completion.

## README maintenance

The prior design-only session correctly found no README change necessary. PR #174 now adds a public generic state-transition evidence helper/profile, so README maintenance is required before this implementation PR is merge-ready. The README must document the extension as evidence-only/non-authorizing and distinguish derived `READY`/`PROBE_REQUIRED` from actual transition execution or admission.

## Next actions

1. Complete README maintenance for the new public state-transition evidence helper/profile.
2. Observe all exact-head PR #174 validations after documentation commits settle.
3. Repair any failing validation rather than weakening the fail-closed model.
4. Inspect current executable Interlock/InTr and StegOS/StegNode surfaces for the smallest actual ephemeral projection consumer.
5. Add an executable provider-neutral Shared Docs observation adapter/harness only where the external system needs a bridge to the existing manifested boundary.
6. Bind MIR and Master Records only through authentic executable interfaces; retain `TO-BUILD` / `NOT PROVEN` where no interface exists.
7. Construct the authentic live-edit + expiry/revocation + single-device test and retain exact evidence.

## Human action

None is required for current source implementation and validation. Richard Whitney's participation becomes necessary only when an authentic test requires authorized access to his independently controlled Shared Docs runtime or attachment of an Interlock/InTr participant/adapter to it.
