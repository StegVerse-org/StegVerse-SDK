# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
```

Live repository state, immutable commits, retained validation evidence, scoped mirror handoffs, and this file supersede prior chat claims.

## Goal inventory

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED
SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002: COMPLETE_STATIC_VALIDATED_MERGED
SDK-PUBLIC-INSPECTION-GOVERNED-TEST-004: SUPERSEDED_BY_CUSTODY_BACKED_RUNTIME
SDK-PUBLIC-INSPECTION-CUSTODY-REPLAY-005: COMPLETE_SOVEREIGN_VALIDATION
SDK-SOVEREIGN-PRODUCTION-VALIDATION-008: COMPLETE_VALIDATION_EVIDENCE_RETAINED
```

No person-specific evaluator route is canonical.

## Governing invariants

```text
every ecosystem state transition is recorded in Master Records
manifest establishes intended route
recorded checkpoint receipt clears next manifest leg
heartbeat is transaction/routing carrier state
successful governed SDK run without Master Records custody: PROHIBITED
successful replay/reconstruction return without operation-transition custody: PROHIBITED
caller projection may suppress Master Records custody: FALSE
third-party host required for execution or validation: FALSE
manifest_receipt_id grants authority: FALSE
GitHub grants runtime authority: FALSE
```

## Canonical governance navigation

```text
000 -> optional worked transparency/demo
00  -> optional return/explanation configuration
0   -> ordinary governed submission
1   -> replay by manifest_receipt_id
2   -> reconstruction by manifest_receipt_id
```

`000` and `00` are optional human inspection surfaces and are not prerequisites for machine-to-machine evaluation.

## Production-validation provenance

The evaluator validation lane is explicitly manifested as:

```text
lane_class: PRODUCTION_VALIDATION
routing_surface: CANONICAL_PRODUCTION
containment: PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE
external_consequence_enabled: false
```

A sovereign execution additionally records:

```text
execution_host_class: SOVEREIGN_LOCAL
third_party_host_required: false
```

This is intentionally distinct from `ENCLOSED_DEMO_TEST`, which remains on demo/test repository surfaces. Lane provenance is transaction data and is retained with the manifest and receipt history.

## Canonical sovereign route

The default public-inspection runtime is now sovereign/local. Hosted HTTP is optional transport, never a prerequisite.

```text
SDK entry
-> Core-Lite manifested route carrier
-> Master Records MRR-* checkpoint custody
-> canonical StegCore manifested transaction
-> canonical StegGate + commit-coherence evaluation
-> Master Records MR-* exact-run custody
-> return ingestion/CGE
-> Master Records MRR-* return custody
-> SDK return
```

Every successful frozen case produced this 10-transition route:

```text
MANIFEST_ESTABLISHED
SDK_ENTERED
INGESTION_ENTERED
CGE_ADMITTED
CGE_ROUTED
MODULE_ENTERED
MODULE_RESULT
CGE_RETURN_INGESTED
ROUTE_CLEARED
RETURNED
```

A transition that is not `RECORDED` cannot clear advancement.

Canonical component bindings:

```text
StegCore manifested validation / transaction identity: 083557adec1bdbace09ebd10fb0765eb8e9a9d08
Core-Lite manifest route carrier: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
Master Records sovereign/portable custody: 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

SDK optional `governed-test` dependencies pin those canonical implementations. The SDK does not embed a parallel evaluator or Master Records algorithm.

## Frozen evaluator validation

Retained validation evidence:

```text
validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md
```

Frozen cases:

```text
T0   original 420 USD state                                  -> ALLOW
T1-A same 420 USD, materially changed current policy state   -> DENY
T1-B 4200 USD candidate retaining earlier 420 approval bind  -> DENY
```

Genuine sovereign production-validation exact-run locators:

```text
T0   MR-2F21EC98FB60A78DD0135E580DD80B1FE6CEC9C62B905A4F758E5567F1C666E2
T1-A MR-620DDEE41541E2F787BC2702FE56977F4BB298BC1CE34C4284203A429F5453C8
T1-B MR-804AF43FC68949F0BBC4B89E4729CA1880AB5BFA4655185C171CE5D2332487B4
```

Assertions retained as PASS:

```text
all StegCore receipt chains verified
all exact-run Master Records custody recorded
all three routes contain 10 ordered MRR-* transitions
one transaction identity preserved across each manifested route
production-validation provenance retained
third-party host required = false
replay operation custody recorded, four MRO-* transitions per case
reconstruction operation custody recorded, four MRO-* transitions per case
replay/reconstruction consequence reexecution = false
```

The complete canonical custody snapshot is retained in `master-records/orchestration`:

```text
validation/evaluator-frozen-sovereign-custody-2026-08-13.zlib.b64
```

It contains 3 exact-run records, 30 route events, and 24 replay/reconstruction operation events. It is portable transport only and grants no authority.

These identifiers supersede earlier local-ephemeral evaluator test IDs.

## Replay

Replay is non-mutating with respect to the original exact run, but its requested operation is new ecosystem history:

```text
REQUESTED -> SOURCE_RESOLVED -> EVALUATED -> RETURNED
```

Each state receives an `MRO-*` Master Records operation receipt before the replay artifact can be returned.

## Reconstruction

Reconstruction does not re-execute the original consequence, but its operation trajectory is new ecosystem history:

```text
REQUESTED -> SOURCE_RESOLVED -> ARTIFACT_DERIVED -> RETURNED
```

Each state receives an `MRO-*` receipt before the reconstruction artifact can be returned.

## Third-party hosting boundary

Render, Vercel, GitHub Actions, or another hosted provider may be used as optional transport/compute. Their quota, availability, authentication, or deployment state cannot gate the sovereign route.

The previous hosted-deployment gate is superseded. Hosted StegCore remains useful for public/live transport but is not required to establish the frozen evaluator production-validation records.

## Credential boundary

Protected runtime credentials remain under TV/TVC authority. The sovereign evaluator run does not require a public caller to manage Master Records bearer credentials and does not use GitHub credentials as StegVerse authority.

## Remaining work after evaluator handoff

Evaluator handoff is no longer blocked. Remaining tasks are general hardening rather than prerequisites for the frozen evaluation:

```text
operation retry/idempotency
explicit failed-operation terminal state custody
portable custody import/export CI execution
backup/replication automation
LLM-adapter convergence on the same manifested/custody-before-return invariant
hosted transport activation where useful
```

## Evaluator handoff state

```text
ordinary SDK route: READY
frozen production-validation run: COMPLETE
Master Records exact-run custody: COMPLETE
manifested route custody: COMPLETE
replay custody: COMPLETE
reconstruction custody: COMPLETE
third-party dependency: NONE
three genuine manifest_receipt_id values: READY_TO_SEND
```

Interpretation of the frozen cases is intentionally left open to the external evaluator.
