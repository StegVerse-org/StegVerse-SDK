# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Implementation PR: `#174 MERGED`
Merge SHA: `ee8f7023d74d70fa762e3982776c27c1e372a1f7`
Status: `ACTIVE / STATE-EVIDENCE SOURCE IMPLEMENTATION MERGED / RUNTIME WORKSPACE PROOF PENDING`

## Controlling architecture

The Shared Docs experiment reuses the existing generic-manifest + Interlock/InTr architecture. It does not create a bespoke Shared Docs API or caller-specific manifest class.

```text
entity
  -> source-native data
  -> stegverse.ingress-manifest.v1
  -> provider-neutral state-transition evidence
  -> Interlock/InTr / installed processing route
  -> admitted projection/output
```

Identity, relationship, credentials, current state, and requested capability may affect admissibility. They do not change the universal manifest class merely because the communicating entity differs.

## Universal transition/readiness rule

```text
Anything that changes is a state transition.
```

PR #174 merged `stegverse.state-transition-evidence.v1` under the existing ingress-manifest `extensions` boundary. It records transition identity, state domain, prior/new state references, change type, applicable predicates, ambiguities, discovered unknowns, derived readiness, and deterministic probe reasons.

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

The helper records `evidence_grants_authority: false` and `unknown_unknown_policy: ENFORCE_AFTER_DISCOVERY_AS_KNOWN_STATE`. A genuinely unknown unknown cannot be enforced before discovery; after discovery it becomes known state and must be resolved before later READY classification.

This is state representation/readiness discipline only. It does not itself execute probes, govern transitions, perform transport, materialize a WorkSpace, synchronize documents, mint InTr receipts, or write MIR/Master Records.

## Files merged by PR #174

```text
stegverse/state_transition_evidence.py
tests/test_state_transition_evidence.py
.github/workflows/manifest-builder-source-validation.yml
README.md
docs/SHARED_DOCS_EPHEMERAL_MANIFEST_WORKSPACE_MIRROR_HANDOFF.md
```

README maintenance is complete. The README change was verified before merge as additive (`+34 / -0`) with no existing README content removed.

## Final exact-head validation before merge

Final PR head: `58e3b9a4f8e718dec9495a6c6b3c6cb824c823fa`

```text
Manifest Builder Source Validation 34531713582: SUCCESS
Evaluator Contract Console Validation 34531713574: SUCCESS
SDK Package Artifact Validation 34531713581: SUCCESS
Evaluator Manifest Source Validation 34531713580: SUCCESS
PR mergeable: true
PR draft state before merge: false
merge: SUCCESS
merge SHA: ee8f7023d74d70fa762e3982776c27c1e372a1f7
```

Package validation included wheel/sdist construction and exact-wheel isolated install/smoke testing.

The assistant's local container could not clone GitHub because local DNS resolution for `github.com` was unavailable. This was not treated as SDK failure; GitHub-hosted exact-head validation supplied the execution evidence above.

## Current executable-surface inspection

Inspection after the source implementation identified `stegverse/external_interlock_bootstrap.py` as the nearest existing SDK bridge toward the runtime-facing experiment. It can build manifest/receipt-bound external-organization Interlock requests using InTr semantics, but its contract explicitly states:

```text
sdk_mints_intr_receipt: false
sdk_claims_delivery: false
authority_transfer: false
```

The module is therefore a request/bootstrap construction surface, not proof of transport. Search found no separate SDK consumer for `build_external_interlock_request` outside that module on the inspected default-branch index. The next step is not to pretend the builder is runtime; it is to locate/bind the canonical executable Interlock/InTr consumer that can accept such a request, then determine whether the state-transition evidence should be projected into that boundary or whether an existing canonical ingress adapter already performs the mapping.

This is also a useful architecture check: `stegverse.external_organization.interaction_manifest.v1` must not become a competing universal payload envelope. Any use in the WorkSpace path must remain a transport/bootstrap control artifact around or translated into the canonical `stegverse.ingress-manifest.v1` semantics, not a caller-specific replacement.

## Ephemeral WorkSpace model

```text
source content: durable under authoritative external system
WorkSpace/StegOS projection: ephemeral and bounded
updates: live/synchronized only while current admission remains valid
MIR: historical state-transition record keeper
Master Records: independent StegVerse custody/replay/reconstruction evidence
```

Ephemeral content does not imply ephemeral transition history. MIR witness/OTS capability remains `TO-BUILD` unless authentic executable evidence proves otherwise. Master Records must not be represented as a substitute for MIR authority.

Required behavior must remain operable from one current mobile device; a second user-operated device is not an admissible dependency.

## Authentic Shared Docs capability predicates still open

1. A correctly shaped generic manifest is consumed by the actual executable Interlock/InTr path.
2. A bounded external-document projection is materialized without transferring authoritative custody.
3. A deterministic current document marker/hash is observed.
4. The authoritative document is edited live.
5. The changed observation is represented as a linked state transition using the same generic manifest class.
6. Ambiguity/unknown applicability produces durable `PROBE_REQUIRED` evidence and an actual probe path can resolve it before READY.
7. The projection synchronizes while authorization remains admissible.
8. Expiry or revocation changes state and further access fails closed.
9. Ephemeral projection material is destroyed when no longer admitted.
10. MIR receives historical transition evidence through an authentic executable interface.
11. Master Records independently retains reconstructable evidence through an authentic executable interface.
12. The user-driven end-to-end flow remains possible from one current mobile device.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence profile: IMPLEMENTED / VALIDATED / MERGED
Fail-closed READY vs PROBE_REQUIRED derivation: IMPLEMENTED / VALIDATED / MERGED
README maintenance: COMPLETE
Shared Docs bespoke API requirement: NONE ESTABLISHED
external_interlock_bootstrap request construction: EXISTS / NON-TRANSPORT
canonical executable Interlock/InTr consumer for this WorkSpace path: NOT YET BOUND
Shared Docs live synchronization runtime: NOT PROVEN
StegOS/StegNode ephemeral projection runtime: NOT PROVEN
active probe execution: NOT PROVEN
MIR transition reporting: NOT PROVEN
MIR external witness/OTS: TO-BUILD
Master Records authentic custody/reconstruction for this experiment: NOT PROVEN
expiry/revocation runtime enforcement: NOT PROVEN
one-device authentic end-to-end execution: NOT PROVEN
```

Do not promote source/CI validation, request construction, provider observation, or design convergence into runtime completion.

## Next actions

1. Trace the canonical executable consumer for manifest-bound external Interlock/InTr requests across the relevant StegVerse repositories.
2. Reconcile `external_organization.interaction_manifest.v1` with the canonical generic ingress boundary so it cannot become a parallel universal envelope.
3. Bind `stegverse.state-transition-evidence.v1` into the existing executable transition path at the narrowest non-authorizing adapter boundary.
4. Add an executable provider-neutral external-document observation/projection harness only if the existing canonical path lacks the required adapter.
5. Bind MIR and Master Records only through authentic executable interfaces; retain `TO-BUILD` / `NOT PROVEN` where no such interface exists.
6. Construct the authentic live-edit + probe + expiry/revocation + one-device experiment and retain exact evidence.

## Human action

None is required for current repository inspection and executable-path tracing. Richard Whitney's participation is required only when an authentic test needs authorized access to his independently controlled Shared Docs runtime or consent to attach an Interlock/InTr participant/adapter to it.
