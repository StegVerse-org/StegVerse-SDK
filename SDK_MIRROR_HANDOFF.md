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
SDK-AUTHORITY-BOUNDARY-PRESERVATION-001: ACTIVE_RUNNER_SOURCE_VALIDATED_PENDING_SOVEREIGN_EXECUTION
SDK-AUTHORITY-BOUNDARY-SOVEREIGN-RUN-002: COMPLETE_RELEASED_TO_MACHINE_EXECUTION
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
credential authority: TV/TVC
non-TV/TVC secret or runtime token required: FALSE
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

The default public-inspection runtime is sovereign/local. Hosted HTTP is optional transport, never a prerequisite.

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

The complete canonical custody snapshot is retained in `master-records/orchestration` at `validation/evaluator-frozen-sovereign-custody-2026-08-13.zlib.b64`. These identifiers supersede earlier local-ephemeral evaluator test IDs.

## Replay and reconstruction

Replay is non-mutating with respect to the original exact run, but its requested operation is new ecosystem history:

```text
REQUESTED -> SOURCE_RESOLVED -> EVALUATED -> RETURNED
```

Reconstruction does not re-execute the original consequence, but its operation trajectory is new ecosystem history:

```text
REQUESTED -> SOURCE_RESOLVED -> ARTIFACT_DERIVED -> RETURNED
```

Each state receives an `MRO-*` receipt before the operation artifact can be returned.

## Third-party hosting and credential boundary

Render, Vercel, GitHub Actions, or another hosted provider may be used as optional non-authorizing validation/transport. Their quota, availability, authentication, or deployment state cannot gate the sovereign route. Protected runtime credentials remain under TV/TVC authority. GitHub credentials are not StegVerse runtime authority.

## Authority-boundary preservation extension

Tracking issue: `#25`.
Initial fixture implementation: PR `#26`, merge commit `d2b2bee3d61f414d0908105b1afdef7533234649`.

The active integration goal is a participant-neutral extension of `Manifest_and_Receipt_Governance_Boundary.md` that tests whether an explicit T0 authority boundary remains reconstructably intact across downstream acknowledgement, attempted endorsement inference, attempted attribution/public association, replay, and reconstruction.

Installed participant-neutral surfaces on `main`:

```text
experiments/authority_boundary_preservation/README.md
experiments/authority_boundary_preservation/fixture.json
experiments/authority_boundary_preservation/validate_fixture.py
experiments/authority_boundary_preservation/run_sovereign_experiment.py
tests/test_authority_boundary_preservation_experiment.py
tests/test_authority_boundary_sovereign_runner.py
.github/workflows/authority-boundary-source-validation.yml
claims/SDK-AUTHORITY-BOUNDARY-SOVEREIGN-RUN-002.json
```

Invariant:

```text
UNDERSTANDING=true does not imply agreement, validation, endorsement, acceptance,
claim authority, publication authority, attribution authority,
public-association authority, or delegation authority.
```

The sovereign runner now prepares the exact fixture as canonical `PRODUCTION_VALIDATION` requests, requires ALLOW for acknowledgement and DENY for attempted authority widening, requires a ten-transition route and exact-run custody shape, then invokes replay and reconstruction and requires four operation receipts for each. It does not encode an external reviewer identity and requires no non-TV/TVC secret or token.

### Source validation — COMPLETE

```text
workflow: Authority Boundary Source Validation (Non-Authorizing)
run: 31838347112
job: 94889598424
head: e629fa05f14a7b09a393417b179895e18095dcaf
result: SUCCESS
fixture validator: AUTHORITY_BOUNDARY_PRESERVED
tests: 3 passed
process GITHUB_TOKEN present: false
process GH_TOKEN present: false
credential_authority: TV/TVC
production_activation_role: NONE
```

The GitHub runner platform reports its normal metadata-read token context, but the validation process explicitly proves `GITHUB_TOKEN` and `GH_TOKEN` are absent and anonymously materializes public source. This hosted run validates source only. It does not prove `SOVEREIGN_LOCAL` execution, TVC `ROUTE_ADMITTED`, production Master Records custody, or governed activation.

### Completion boundary

```text
fixture/specification installed on main: COMPLETE
fixture deterministic validation: COMPLETE
sovereign runner source installed: COMPLETE
runner contract tests: COMPLETE
no-token/non-authorizing hosted source validation: COMPLETE
implementation claim: RELEASED_TO_MACHINE_EXECUTION
sovereign SDK manifested execution of this exact fixture: PENDING
Master Records exact-run + route custody: PENDING
replay operation custody: PENDING
reconstruction operation custody: PENDING
independent reviewer interpretation: PENDING_EXTERNAL
```

A source-validation PASS must not be represented as a sovereign execution result. Goal completion requires execution by the canonical sovereign SDK lane and retained immutable run/replay/reconstruction evidence.

## Local model/runtime convergence for this session

The session requirements to replace descriptive local-runtime selection and formally develop the local model have already converged on a completed canonical owner and must not be duplicated here.

```text
MERGED INTO: StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
source state: COMPLETE_RELEASED
formal model: stegverse-reference-lm-v1 COMPLETE_RELEASED
local discovery/private launch/real inference/usage/proof: COMPLETE_RELEASED
canonical validation: 31339534741 SUCCESS
persistent endpoint validation: 31384116055 SUCCESS
github_token_required: false
third_party_inference_required: false
credential authority: TV/TVC
```

Live same-carrier activation is separately machine-owned and must not be duplicated by this SDK/session:

```text
StegVerse-Labs/.github#60
resident sovereign heartbeat -> TVC -> LLM-adapter -> master-records/orchestration
last directly observed heartbeat: HB29
release condition: fresh authorized fence >20 + real private model observation + TVC ROUTE_ADMITTED credential_requirement NONE + exact LLM-adapter execution + measured usage + same-execution Master Records reconstruction PASS
```

## Trade-readiness convergence

The user-directed trade-ready goal is owned by `StegVerse-Labs/stegfin-governance`, not this SDK. Canonical continuation is `docs/STEGFIN_MIRROR_HANDOFF.md` and `task-state/STEGFIN-LIVE-ENTRY-003.json`. Source readiness is complete; wallet signing and broadcast are USER_ONLY; TV/TVC owns credentials/provider operation. The live terminal `WALLET_HANDOFF_READY` receipt has not been observed. No SDK or chat-session trade execution authority is inferred.

## Remaining work

```text
authority-boundary sovereign execution/custody (#25): canonical sovereign SDK execution lane
local-model live activation: MACHINE_OWNED StegVerse-Labs/.github#60 chain
trade-ready wallet handoff: MACHINE_OWNED StegFin/TVC/.github continuation until WALLET_HANDOFF_READY; signing/broadcast USER_ONLY
operation retry/idempotency: general SDK hardening
explicit failed-operation terminal state custody: general SDK hardening
portable custody import/export CI execution: general SDK hardening
backup/replication automation: general SDK hardening
LLM-adapter convergence on manifested/custody-before-return invariant: canonical adapter integration owner
hosted transport activation: optional only
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
three genuine frozen evaluator manifest_receipt_id values: READY_TO_SEND
authority-boundary source runner: COMPLETE_VALIDATED
authority-boundary exact sovereign run: PENDING_MACHINE_EXECUTION
```

Interpretation of the frozen cases and the future authority-boundary execution remains open to independent reviewers.
