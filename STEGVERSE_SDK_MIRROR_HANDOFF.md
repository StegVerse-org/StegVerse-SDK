# StegVerse SDK Mirror Handoff

Updated: 2026-08-22

## Current source of truth

This file is the authoritative continuation record for `StegVerse-org/StegVerse-SDK`. Live default-branch state, Git history, issues, pull requests, workflow runs, artifacts, releases, and committed evidence are authoritative over historical conversation claims.

## Repository role

```text
repository: StegVerse-org/StegVerse-SDK
default branch: main
role: user-facing, non-authorizing intake and compatibility boundary
```

SDK validation, compatibility, submission, aggregation, ingestion, device discovery, capability declaration, or communication demonstration are not execution, authority, admissibility, standing, commit-time validation, publication, deployment, bearer delivery, or Master-Records custody.

## Completed goals retained

```text
Goal 4 governed micro-node return-path validation: COMPLETE
Goal 5 governed-vs-recursive comparison orchestration: COMPLETE
Goal 6 entry-point role and transition-usage contracts: COMPLETE
Goal 6 coordinate-navigation consumption: COMPLETE
Goal 6 aggregate session-usage receipt: COMPLETE
Goal 7 governed edge-cell source consumer: COMPLETE
Communication edge SDK demonstrator: VALIDATED
Installed communication demo command: VALIDATED
```

Existing invariants remain binding:

```text
sdk_validation_is_execution == false
sdk_intake_is_authority == false
sdk_navigation_consumption_is_authority == false
sdk_navigation_consumption_transfers_authority == false
sdk_navigation_consumption_is_commit_time_validation == false
usage_event_is_authority == false
usage_event_is_admissibility == false
session_receipt_is_master_record_custody == false
aggregation_is_universal_cost_claim == false
sdk_communication_demo_is_execution == false
sdk_communication_demo_grants_authority == false
returned_to_origin == true
```

## Communication edge SDK demonstrator — VALIDATED

Task-specific source of truth: `COMMUNICATION_EDGE_SDK_DEMO_MIRROR_HANDOFF.md`.
Human-facing instructions: `docs/COMMUNICATION_EDGE_SDK_DEMO.md`.

Installed evaluator command:

```bash
stegverse-comm-demo
stegverse-comm-demo --compact
stegverse-comm-demo /path/to/custom-packet.json
```

Implemented surfaces:

```text
stegverse/communication_edge_demo.py
stegverse/communication_edge_cli.py
stegverse/demo_data/communication_edge_demo.json
examples/communication_edge_demo.json
tests/test_communication_edge_demo.py
scripts/run_communication_edge_demo.py
scripts/run_pinned_communication_source_integration.py
docs/COMMUNICATION_EDGE_SDK_DEMO.md
.github/workflows/communication-edge-demo-validation.yml
COMMUNICATION_EDGE_SDK_DEMO_MIRROR_HANDOFF.md
```

The SDK package now carries its deterministic demonstration packet as package data, so the installed command does not depend on a repository-relative `examples/` path.

Observed validation evidence:

```text
PR #54 / run 32602726148:
  SDK-only conformance demo
  Python 3.9 / 3.11 / 3.12 -> SUCCESS

PR #55 / run 32602863793:
  pinned real StegTalk + KnowledgeVault source integration
  Python 3.9 / 3.11 / 3.12 -> SUCCESS

StegWhisper PR #15 / run 32602979304:
  real StegWhisper v0.2 -> pinned real StegTalk ST-031 -> pinned real KnowledgeVault
  SUCCESS

PR #57 / runs 32605995150 and 32606024322:
  public evaluator guide present while full communication lane executes
  Python 3.9 / 3.11 / 3.12 -> SUCCESS

PR #58 / runs 32606159922 and 32606199291:
  installed stegverse-comm-demo command
  packaged deterministic fixture
  installed/source JSON parity
  full pinned-source integration revalidation
  Python 3.9 / 3.11 / 3.12 -> SUCCESS
```

Pinned real source exercised by the SDK source-integration proof:

```text
StegVerse-Labs/StegTalk
2361d13ea09818f17aef5239ebf4771a161a0dc7

StegVerse-Labs/continuity-vault-kit
35e6d7ad881e0dea60ba191c49dfd4fba86e3fd7
```

The proof executes the real ST-031 resolver and KnowledgeVault execution store, selects the higher-capability `stegtalk-ip` path over SMS under AUTO, retains SMS as ordered fallback, persists selection/lease state, reconstructs that state from a fresh KV store instance after restart, blocks automatic fallback after ambiguous post-dispatch state, and allows the exact ordered fallback only after confirmed absence of side effects.

Authority boundary remains:

```text
SDK = non-authorizing compatibility/conformance demonstration
StegWhisper = messenger posture + consent/presentation constraints
StegTalk ST-031 = real bearer admissibility/scoring/selection/fallback authority
KnowledgeVault = durable attempt/receipt/recovery continuity authority
Edge device = ephemeral execution capability
```

The communication demo does not prove a physical/network bearer was executed, a real recipient received a message, or ST-029 modem/SIM activation. Those runtime/physical goals remain open in the StegTalk/StegWhisper/KnowledgeVault handoffs and task registries.

## New machine-owned continuation — `BIOINTERFACE-SDK-001`

Origin: StegHealth/StegNeuro hardware convergence discussion.
Canonical issue: `StegVerse-org/StegVerse-SDK#13`.
Task state: `MACHINE_OWNED`.
Active implementation claim: none.
Session-specific implementation authority: none.
Architecture source: `docs/BIOINTERFACE_DEVICE_SDK_CONVERGENCE.md`.

The requirement is to extract the reusable physical-device substrate shared by physiological and neural nodes without moving domain semantics or execution authority into the SDK.

Required implementation:

1. common device/capability schema;
2. transport-neutral packet/envelope contract compatible with StegHealth native/raw preservation;
3. reference Python host client;
4. device adapter interface;
5. READ/WRITE capability separation and authority-neutrality tests;
6. StegHealth profile fixture;
7. StegNeuro profile fixture spanning CNS/PNS/ANS/ENS/neuromuscular/sensory pathways without implying semantic decoding;
8. conformance tests and existing SDK workflow integration.

Release condition: all eight surfaces are implemented, merged, validated through the existing SDK workflow/package path, and this handoff contains the exact evidence. An implementation lane must claim exact files before mutation to prevent duplicate work.

Collision boundaries:

```text
StegHealth -> physiological signal/hardware semantics
StegNeuro -> neural READ/WRITE interface semantics
StegCore -> admissibility/consequence authority
Master Records -> reconstruction/evidence qualification
StegVerse-SDK -> shared device compatibility/intake substrate only
```

Capability declaration never grants execution authority. READ and WRITE may share hardware/transport but must remain separately declared and governed.

## Goal 7 completion record

```text
goal id: EGC-PROP-SDK
parent goal: EGC-PROP-001
state: COMPLETE
source repository: StegVerse-002/micro-node-runtime
source commit: c9660dd0dffd97d9ececc9b7428ef165ae212419
source propagation registry: StegVerse-002/micro-node-runtime#15
SDK issue: #9
SDK pull request: #10
SDK merge commit: 24c22b617daa4a2f2ea10a14487c047352591e9b
claim state: COMPLETE / RELEASED
claim released: 2026-08-04T11:55:00-05:00
```

Canonical source binding:

```text
profile: stegverse.edge-cell.governed.v1@1.0.0
profile hash: 0a31dabd5ba8e8f5e526a087b4194eccca1456c693546c7428ef165ae212419
activation-input hash: a90a33fb74205e947146f2098e020a299c9e29a50ddf2c8a9cafad759646ea2c
activation-receipt hash: c546a4addf80eebead9cc17324fad7580d6d5050c5347e86969c91d8d9cf7299
```

Installed Goal-7 surfaces remain:

```text
stegverse/edge_cell_consumer.py
examples/edge_cell_source_binding.json
tests/test_edge_cell_consumer.py
scripts/verify_edge_cell_consumer.py
docs/GOVERNED_EDGE_CELL_SDK_CONSUMER.md
STEGVERSE_SDK_MIRROR_HANDOFF.md
```

## Goal 7 validation evidence

Pull-request validation retained:

```text
PR head: 3280f024a57464ddb7d9bd1bf61fbd04db6f4ba2
StegVerse SDK Validation runs: 30930727040 and 30930887252 — success
Architecture Guard: 30930887348 — success
validate: 30930887259 — success
Validate Provider Usage Ingestion: 30930887818 — success
Diagnose Python 3.9 Public Imports: 30930887299 — success
Python matrix: 3.9, 3.11, 3.12 — success
package build and wheel verification — success
```

Inspected Python 3.11 log historically recorded 406 tests collected, 10 edge-cell consumer tests passed, standalone verifier passed, 406 passed.

## Automation contract

Existing SDK pull-request/main workflows remain the validation owner. `BIOINTERFACE-SDK-001` must integrate into those workflows rather than create an isolated parallel validation authority unless technically required and explicitly recorded.

The communication-edge demo remains owned by `Communication Edge SDK Demo Validation`; its successful conformance runs do not grant runtime communication authority.

Missing implementation remains fail-closed as incomplete; issue presence or architecture documentation does not equal SDK implementation.

## Cross-repository continuation

```text
shared biointerface SDK: StegVerse-org/StegVerse-SDK#13
physiological device profiles: StegVerse-Labs/StegHealth
neural device profiles: StegVerse-Labs/StegNeuro
admissibility/consequence: StegVerse-Labs/StegCore
reconstruction resolution: master-records/core-lite#31

communication posture surface: StegVerse-Labs/StegWhisper
communication bearer/admissibility selection: StegVerse-Labs/StegTalk
communication continuity/recovery host: StegVerse-Labs/continuity-vault-kit
communication public conformance surface: StegVerse-org/StegVerse-SDK
```

Existing Goal-7 source/destination relationships remain preserved and are not reopened.

## Completion accounting

Completed Goal-7 slice remains 6/6 developed, 4/4 validation, 3/3 integration.

Communication-edge SDK slice:

```text
human-facing guide: complete + validated
SDK simulator: complete + validated
installed command: complete + validated
packaged deterministic fixture: complete + validated
pinned StegTalk/KV source proof: complete + validated
full StegWhisper->StegTalk->KV source proof: complete + validated
physical bearer execution: outside SDK / not claimed
```

New `BIOINTERFACE-SDK-001` denominator remains independent:

```text
architecture transfer: 1/1 complete
implementation deliverables: 0/8
scaffolding/stubs presented as implementation: 0
validation: 0/3 new-goal gates
integration: 0/3 new-goal domain bindings
claim: MACHINE_OWNED / no active implementation claimant
```

## Session consolidation

The communication-edge SDK work is durable in its source, package command, public guide, workflow, task-specific handoff, and observed validation runs. Future communication runtime activation must continue from StegTalk/StegWhisper/KnowledgeVault rather than treating SDK conformance as physical execution.

The shared Health/Neuro device-substrate requirement and whole-nervous-system profile scope remain durable in `docs/BIOINTERFACE_DEVICE_SDK_CONVERGENCE.md` and issue #13. Future implementation must proceed from the issue and this handoff.


## Active cross-framework current-basis evaluator review lane — 2026-08-28

```text
PR: #94
branch: test/cross-framework-current-basis-manifest-draft-20260828
current PR head: 18ff1808ef19d25faf7386236f0478f5c4f32c70
manifest: inspection/examples/cross-framework-current-basis-request.draft.json
manifest blob: 2dd0468779975d18ad53dfe400e1d2fcf83650c3
vector schema: stegverse.cross-framework-current-basis-vector.v0.2
state: DRAFT_PRE_FREEZE
current-head source validation: 33222653960 SUCCESS
external approval: NONE
StegVerse freeze attestation: NONE
frozen: NO
executed: NO
results: NONE
```

External evaluator feedback corrected the original draft so material policy-basis change is not treated as already-established invalidation. The current primary vector declares `CURRENT_POLICY_BASIS_CHANGED`, `invalidation_asserted_as_input=false`, independent S1 current-basis determination, and explicit `VALID_CONTINUITY_CONTROL` / `KNOWN_INVALIDATION_CONTROL`; known invalidation requires its establishing evidence to be frozen with S1.

Human review is provided through the non-authorizing Site evaluator-review front end. Site PR #576 implemented/validated/merged the generic UI; Site PR #590 validated/merged the exact v0.2 public projection as `dd7e6d5685abea6c87429e90e36b1069bd9c9b9d`. Public-route observation remains pending. Site never becomes test, approval, freeze, execution, credential, custody, replay, or reconstruction authority.

Next boundary: observe the public Site v0.2 projection; external evaluator reviews the exact v0.2 manifest blob/hash above (current PR head may contain non-manifest handoff changes); any content change invalidates approval for freeze purposes; only matching exact-revision/hash approvals may proceed to canonical freeze, followed by independent execution and ordinary TV/TVC + Master Records evidence/custody boundaries.


### Manifest-content continuity note — PR #94 head advance

PR #94 now points to head `18ff1808ef19d25faf7386236f0478f5c4f32c70`, and Evaluator Manifest Source Validation run `33222653960` is SUCCESS. The manifest file content is unchanged from the externally discussed v0.2 revision: blob `2dd0468779975d18ad53dfe400e1d2fcf83650c3`. Therefore no approval is inferred or invalidated—none existed. Future approval/freeze must bind the exact manifest content hash/version, not rely on a stale PR-head label.


## Cross-framework current-basis v0.4 reconciliation — 2026-08-29

This section supersedes the earlier v0.2/v0.3 status for the active cross-framework current-basis lane.

```text
test_id: cross-framework-current-basis-001
vector_schema: stegverse.cross-framework-current-basis-vector.v0.4
frozen manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
frozen manifest Git blob SHA-1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
external exact-v0.4 approval: APPROVED_FOR_HASH_FREEZE
StegVerse owner freeze attestation: FROZEN
common execution window: OPEN
StegCore native derivation PR: StegVerse-Labs/StegCore#162
StegCore validation: 33290922006 SUCCESS
StegCore manifold regression: 33290922002 SUCCESS
StegCore merge: e80e927616750a88ad7fc88f4017fc496474f1e4
SDK role: THIN_CLIENT_OF_CANONICAL_STEGCORE
SDK parallel evaluator: false
authentic independent StegVerse execution: NOT YET OBSERVED
```

Testing-state rule: absent explicitly supplied prior-state data, S0 is the declared initial state from which evaluation begins; no historical S0 receipt is required. Material change does not itself establish invalidation/non-currentness. StegCore independently derives native currentness fields from the frozen neutral S1 observed facts, leaving unestablished currentness unknown. The S0->S1 transition receipt remains post-observation evidence.

Current integration is reconciled from the historical PR #94 branch onto current SDK main rather than overwriting later SDK/Interlock work. The exact frozen manifest bytes are preserved unchanged. The SDK thin client is `stegverse/current_basis.py`; `stegverse/sovereign_validation_runtime.py` accepts an independently derived canonical StegCore request without requiring architecture-native fields inside the frozen common manifest.

Result publication remains verification/distribution only through `.github/workflows/cross-framework-result-artifact-publication.yml`; GitHub Actions does not become runtime, receipt, custody, or governance authority.


## SDK-only dependency boundary source candidate — 2026-09-23

Registry owner: `StegVerse-Labs/.github:data/canonical-task-records/SDK-UNTRUSTED-DEPENDENCY-EXECUTION-BOUNDARY-001.json`; canonical handoff: `StegVerse-Labs/.github:docs/SDK_UNTRUSTED_DEPENDENCY_EXECUTION_BOUNDARY_MIRROR_HANDOFF.md`; COSV `71000000111111`, ACTIVE/HANDOFF_READY, canonical generation 207. Existing canonical collision evaluator source was reviewed for the exact proposed SDK-only file/test component: its canonical registry identity scan gives COORDINATE_CONVERGENCE on declared adjacency (Richard, micro-node, MR, org custody) and existing SDK repository co-ownership, without an identified hard component collision for this narrow component. This was a read-only source-level reconstruction, **not an actual append-only resident check-in event**; the canonical event-history check remains required before mutation-capable integration. Explicit issue #1620 coordination comment 5804402084 records the component-011 separation. This source candidate changes only SDK-local non-executing descriptor review, inert tests and documentation; component-011 defensive-envelope/TVC/dispatcher, existing SDK runtime routes, worker lifecycle, InTr and Master Records remain untouched.

No declared descriptor is executable authority or containment evidence, no declared observed receipt is independently authenticated, and no fixture can satisfy runtime closure. Validate the exact candidate head before review/merge; require canonical check-in and owner convergence for any shared execution-path wiring. No external device or new runtime.


### Scoped Task Registry collision evaluator closure — 2026-09-23

Canonical .github PR [#2599](https://github.com/StegVerse-Labs/.github/pull/2599) merged as `c3e4ae98ad308accb68cb340db211c56b9b81b63` after repairing a concrete false-positive: unrelated top-level tasks shared `parent_task_id=None`, previously causing spurious hard lineage collisions. The scoped source check-in test exercised the **actual** canonical collision evaluator on Task Registry generation 207, with an ephemeral append-only event, and verified `COORDINATE_CONVERGENCE`, no hard collision for the distinct SDK-only inert checker component, retained adjacency and authority_effect NONE. Exact-head Cross-Task Coordination, DeepSeek and KV AI Memory workflows passed on PR head `3f83a12d5e69392a97338685d322dae6a0173d2e`. Existing component-011 owner coordination notice: StegVerse-Labs/.github issue #1620 comment 5804402084. This source coordination does not issue WorkerCoordinator claim/fence or authorize shared defensive-envelope mutation; future production wiring still requires owner convergence and authentic runtime receipts. SDK PR #310 modifies only metadata review, inert tests, the existing source-validation workflow and documentation.


### Existing component-011 receipt compatibility — 2026-09-23

Task Registry `SDK-UNTRUSTED-DEPENDENCY-EXECUTION-BOUNDARY-001` is ACTIVE/HANDOFF_READY at generation 207, COSV 71000000111111. The source-validated SDK-only inert dependency review from PR #310 is the initial manifest/descriptor classifier. The shortest *candidate* existing execution path, without manufacturing another runtime, is `.github/control/resident-execution-request.d/ungoverned-ai-defensive-envelope-001.json` -> existing resident dispatcher and `scripts/consume_ungoverned_ai_defensive_envelope_request.py` -> targeted `refresh_and_execute_resident_task.py` -> existing WorkerCoordinator fenced component-011 worker -> TVC `tasks/ungoverned_ai_defensive_envelope.py` SES stdio bounded Python probe. This currently targets the independently owned `ECOSYSTEM-INGRESS-AI-BOUNDARIES-001` task, **not** the SDK security task, and its `ALLOW` concerns one bounded demonstration, not arbitrary dependency installation. Source-owner coordination: .github issue #1620 comment 5805318241. That checked-out owner must handle any shared consumer/worker changes.

The new SDK-only `stegverse/component011_receipt_compatibility.py` performs offline non-authorizing comparison of copies of the existing consumption/boundary/canonical-state/org-ledger/MR schemas. It tests claim/fence, bounded denied probes, boundary-to-canonical exact digest and canonical-to-org exact digest, and MR claimed reconstruction equality. No runtime calls, execution, credential issuance, independently authenticated receipt readbacks or new custody storage occur; even perfect caller-provided snapshots remain unverified and cannot promote authority. A source audit identified the checked-out consumer's first concrete receipt gap: terminal status derives from a completed worker return rather than directly requiring and binding the exact boundary receipt, and there is no organization-ledger or MR custody evidence in that completion predicate. The authoritative owner was notified; exact runtime validation remains pending. The org ledger already accepts `stegverse.canonical-state-transition-receipt/v1` and records `stegverse.organization-transition-receipt/v1`; do not relabel a standalone SES probe or consumption receipt as a canonical governed transition. Exact MR receipt closure requires verified authorized transition and immediate predecessor, RECORDED, reconstruction PASS, required evidence PASS and digest equality. The source compatibility checker cannot independently prove any of these.


## 2026-09-25 actionable transition-boundary diagnostics (draft source)

Existing SDK application-spine owner issue #61; parent ecosystem contract central `.github` #1766 / #1615. New `stegverse/transition_disposition.py` exposes opt-in `attempt_manifest_transition(manifest)` and preserves unchanged `execute_manifest()` behavior. It calls existing `derive_execution_request`, existing Universal InTr transport and existing runtime-result validator. On failed SDK admission, missing installed InTr URL, absent scoped TV/TVC relay authorization, transport failure or response-validation failure, it returns a precise local non-ALLOW diagnostic with exact failure code, predicate, repair, retry edge and immutable diagnostic digest. It explicitly marks `is_intr_receipt=false`, `is_master_records_receipt=false`, `consequence_committed=false`. Authentic validated success passes through without alteration. This avoids invented downstream DENY when resident was never invoked. Six isolated local mock tests cover the seams; they are NOT execution receipts. Existing manifest-driven route selection and TV/TVC, InTr, Master Records dependency boundaries remain unchanged. External-framework actual findings require independently retained runtime receipt and reconstruction before claiming an ALLOW or executed DENY. Source staged only: merge, exact-head CI, caller adoption and live InTr receipt/reconstruction are separate.


First focused PR CI run 36168671748 failed during module import because its new workflow did not install the SDK's declared runtime dependency `requests`; no test assertions were reached. The workflow was corrected to run `pip install -e .` before the six targeted unit tests and now supports exact-branch validation. Recheck the current head's workflow outcomes; no source-test PASS or runtime result is inferred from the earlier failed run.
