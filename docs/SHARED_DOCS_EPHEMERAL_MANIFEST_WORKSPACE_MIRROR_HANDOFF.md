# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / DESIGN_AND_CAPABILITY_TEST_PREPARATION`

## Purpose

This handoff captures the 2026-09-10 convergence around using the already-solved generic-manifest + Interlock/InTr architecture to test live, synchronized, ephemeral access to an independently controlled collaborative document system (Richard Whitney's Shared Docs) without requiring a bespoke Shared Docs API.

This is a bounded continuation record. It does not claim that Shared Docs is integrated, that a StegOS/StegNode instance has been materialized on Richard's device, or that an authentic cross-system runtime test has completed.

## Core conclusion

The Shared Docs experiment is not a new manifest problem and should not create a parallel access protocol.

The existing generic-manifest semantics remain controlling:

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance-specific fields are not universal manifest requirements
```

Any requester that can present the correctly shaped manifested request through the applicable Interlock/InTr path should be evaluated by the same contract. The caller may be StegVerse, Richard's LLM, another AI/entity, another external framework, or a future StegOS/StegNode participant. Caller identity matters only insofar as identity and current state affect admissibility, authorization, scope, or return projection.

No caller-specific Shared Docs API is required merely because the caller differs.

## WorkSpace candidate observation

Richard Whitney's Shared Docs platform was observed during a real collaborative drafting session to provide a useful WorkSpace substrate/candidate interaction model, including:

- owner/editor sharing;
- direct document sharing;
- live editing;
- autosave;
- collision-safe concurrent editing behavior as reported by Richard;
- mobile/iPhone usability;
- shared persistent artifact state.

Richard stated that he developed the document platform himself.

This observation establishes only candidate/reference value. It does not establish reuse rights, StegVerse ownership, integration rights, or a completed StegVerse WorkSpace implementation.

## Mobile-first invariant

The session reinforced the StegVerse constraint that required functionality must not depend on a second user-operated device.

Candidate WorkSpace invariant:

```text
Capability may scale with additional displays/devices;
required functionality must remain complete on one user device.
```

Desktop, split-screen, multi-display, or keyboard support may enhance the experience but must not become a prerequisite for the core governed workflow.

## Universal state-transition invariant

The controlling state rule established in this session is:

```text
Anything that changes is a state transition.
```

There is no separate class of hidden or ordinary mutation outside the transition model. Relevant state domains remain distinct, including:

- document state;
- authorization/login/session state;
- ephemeral projection state;
- StegOS/StegNode state;
- discovered/known-state classification;
- governance/admissibility state where applicable.

Examples of transitions include document edits, synchronization updates, login creation, renewal, expiry, revocation, permission/scope changes, node-continuity changes, projection creation, projection refresh, projection destruction, and incorporation of newly discovered unknowns into known state.

A timer is a transition trigger, not a side channel. Renewal is a state transition. Revocation is a state transition. Expiry is a state transition. A session refresh that changes authority, scope, evidence, or expiry is a state transition.

## Ephemeral live-projection model

The desired WorkSpace/StegOS behavior is:

```text
source content: durable under the authoritative external system
access/materialization: ephemeral in StegOS/StegNode
updates: live/synchronized during the admitted lifetime
transition history: durable as required by the record/evidence architecture
```

The ephemeral instance must not silently become a second durable document store.

A bounded projection may contain only the content/resource scope admitted for that requester and task/session. It remains synchronized while access is admissible. When access leaves an admissible state, synchronization stops and ephemeral content, indexes, handles, caches, and temporary session material are destroyed according to policy.

The effective projection lifetime is state-dependent. A time limit remains valid, but time is only one condition capable of causing the authorization state to transition. Owner revocation, changed scope, changed identity/device/node evidence, task completion, or other governing conditions may transition access earlier.

## Manifest semantics for external file/workspace access

The Shared Docs resource should be treated as source-native external data/resources represented through the generic manifest, not as a special StegVerse-native object merely because StegVerse accesses it.

The manifest must be of the correct shape for the requested operation regardless of requester. The specific exact schema fields must be derived from the existing generic manifest contract rather than introducing caller-specific fields.

At minimum, the manifested request must be able to bind the applicable concepts already required by the generic architecture, including:

- requester/entity identity or reference when identity is materially applicable;
- source/resource reference or source-native object binding;
- requested processing/capability;
- route binding where required;
- relevant state/evidence inputs;
- requested return projection;
- processor-specific extension only when that processor requires it.

The generic-manifest rule remains that unsupported/uninstalled processing or route execution fails closed rather than inventing missing semantics.

## Interlock/InTr role

No bespoke Shared Docs REST API is required if the independently controlled system can participate through the existing manifested Interlock/InTr boundary.

Conceptually:

```text
requesting entity
  -> correctly shaped manifest
  -> Interlock/InTr
  -> admitted processing / authorization
  -> bounded external resource access or projection
  -> caller-selected returned projection
```

For live collaboration, source changes can cause new state observations/transitions and update the ephemeral projection while the authorization state remains admissible.

This does not mean every external system must internally implement StegVerse semantics. An adjacent participant/adapter may bridge the system to the Interlock/InTr boundary while preserving the external system's internal implementation and authoritative custody.

## MIR and Master Records separation

MIR is the historical record-keeping system for state transitions in this architecture.

StegOS and StegNode should report every state transition to MIR in the same sense that StegVerse runtime transitions are also retained through the applicable Master Records path.

The records must remain separate in authority:

```text
transition source
  -> direct transition report to MIR
  -> independent applicable StegVerse Master Records retention/custody
```

Master Records must not become a substitute for MIR's authoritative historical custody, and StegVerse must not ingest MIR's historical stream as an alternate MIR history store. The same transition may be independently evidenced/custodied by both systems for their respective purposes.

Controlling principle:

```text
ephemeral content does not imply ephemeral transition history
```

The document itself may disappear from the StegOS ephemeral projection after teardown while the fact that the relevant state transitions occurred remains durably evidenced according to the MIR/Master Records separation-of-powers model.

## Candidate lifecycle

A first bounded capability lifecycle can be modeled conceptually as:

```text
REQUESTED
  -> AUTHORIZED
  -> MATERIALIZED
  -> SYNCHRONIZED
  -> UPDATED*          # zero or more live source changes
  -> EXPIRED | REVOKED
  -> DESTROYED
```

Every actual change in the applicable state domain is a transition. The labels above are illustrative state names, not a new canonical schema claim.

## Authentic capability test

The first useful experiment should prove behavior, not merely source readiness.

Target experiment:

1. A Shared Docs document is made available to a requester through a correctly shaped manifested request and admitted Interlock/InTr path.
2. A bounded ephemeral projection is materialized without transferring permanent authoritative document custody to StegVerse.
3. The requester reads a deterministic document marker/current section and computes or returns a content binding/hash suitable for freshness comparison.
4. The authoritative Shared Docs document is edited live.
5. The ephemeral projection observes/synchronizes the changed state while authorization remains admissible.
6. The requester reads the new marker/content binding and distinguishes it from the prior state.
7. Access expires or is revoked as a state transition.
8. Further access fails closed.
9. The ephemeral projection is destroyed.
10. MIR and the applicable Master Records path retain the required transition history/evidence without requiring permanent retention of the projected document contents.

A stronger comparative variant has Richard's LLM and StegVerse independently access the same live document under their own correctly shaped manifested requests and compare current title/section/hash observations before and after a controlled edit.

## What this experiment would establish if authentic runtime evidence succeeds

A successful authentic run could establish, subject to exact evidence:

- generic-manifest applicability to a live external collaborative resource;
- Interlock/InTr-mediated access without a bespoke per-caller API;
- externally authoritative content with ephemeral StegOS/StegNode projection;
- live synchronized update observation;
- state-dependent login/access expiry and revocation;
- caller-independent manifest shape with state-dependent results;
- durable transition record/evidence while projected content remains ephemeral;
- a credible first WorkSpace interoperability pattern for independently developed systems.

It would not, by itself, establish that Shared Docs is the final StegVerse WorkSpace product, that every external system can interoperate without an adapter, or that all security/privacy/governance predicates for production deployment are complete.

## MIR x StegVerse contract implications

The separation-of-powers contract should eventually make explicit, without changing the already-agreed role split, that:

- StegOS/StegNode transition producers report state transitions to MIR for historical custody;
- StegVerse may independently retain required evidence/records in Master Records for StegVerse custody, replay, reconstruction, and governance support;
- independent Master Records custody does not make StegVerse the authoritative historical custodian of MIR history;
- provenance/recording of a transition does not itself grant governance or execution authority;
- ephemeral content/data projection can terminate while durable transition evidence remains.

This session also identified that MIR's external witness/OTS anchoring remains TO-BUILD per Richard's correction: MIR currently has an internal chain and fire-and-forget announcement behavior, but no captured signed witness/OTS proof should be represented as already implemented.

## README review

`README.md` was reviewed at session close. Its existing sections already document:

- independent systems connecting through governed interlocks while preserving authority;
- the generic manifested-data processing boundary;
- separation of payload class, processing capability, runtime route, authority, caller projection, and canonical custody;
- source-native data preservation;
- fail-closed unsupported routing.

No README modification is required merely to record this proposed Shared Docs capability experiment because the experiment applies those existing public semantics rather than changing the SDK's published interface or runtime contract. If implementation later adds a new public capability identifier, route, manifest field, user-facing WorkSpace surface, or externally observable runtime behavior, README maintenance becomes required with that implementation.

## Existing implementation boundary

The parent SDK handoff remains authoritative for actual implementation/release state. At session close:

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
SDK 1.3.0 candidate: source-valid draft/release-gated per parent handoff
Shared Docs WorkSpace authentic runtime test: NOT YET EXECUTED
Shared Docs bespoke API requirement: NONE ESTABLISHED
Interlock/InTr manifested access reuse: DESIGN CONVERGED / AUTHENTIC TEST PENDING
StegOS/StegNode ephemeral projection implementation for this resource: NOT YET PROVEN
MIR transition-reporting integration for this experiment: NOT YET PROVEN
```

Do not convert this design convergence into a runtime-completion claim.

## Next-session continuation

Next session should begin from this handoff and the parent SDK generic-manifest handoff, then:

1. verify the current canonical `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003` task state before any mutation;
2. inspect the current generic ingress-manifest schema/processor semantics and identify the exact existing shape applicable to external resource access without inventing Shared Docs-specific fields;
3. inspect current Interlock/InTr and StegOS/StegNode executable surfaces for the smallest authentic path that can materialize a bounded ephemeral projection;
4. determine whether any existing route/capability can perform the test now or whether a new capability implementation is required;
5. bind state-transition reporting to MIR and independent Master Records evidence surfaces without conflating authority;
6. construct an authentic live-edit/expiry-or-revocation test with explicit completion predicates and evidence requirements;
7. do not require a bespoke Shared Docs API unless actual inspection proves the external system needs an adapter surface to reach Interlock/InTr.

## Human action

None required to continue source inspection/design reconciliation. Richard's participation becomes necessary only when an authentic test requires access to his independently controlled Shared Docs runtime/device or consent to attach an Interlock/InTr participant to it.
