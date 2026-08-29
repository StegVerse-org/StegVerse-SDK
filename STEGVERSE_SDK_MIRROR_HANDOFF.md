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


## Cross-framework evaluator freeze lane — PR #94

Updated: 2026-08-28

State:

```text
PR: #94
branch: test/cross-framework-current-basis-manifest-draft-20260828
artifact: inspection/examples/cross-framework-current-basis-request.draft.json
status: DRAFT_PRE_FREEZE / EXTERNAL REVIEW IN PROGRESS
final comparison execution permitted: false
```

External evaluator feedback received 2026-08-28:

- a materially changed policy basis and a policy basis already established as invalid must not be treated as equivalent by construction;
- the primary shared vector must describe the changed condition without encoding invalidation as an input conclusion when continuing standing is intended to be independently determined;
- if known material invalidation is tested, the evidence establishing invalidation must be frozen as part of S1;
- preserve controls that distinguish valid continuity, known-invalidated continuity, and unresolved/current-basis continuity;
- after amendment, the evaluator must review the exact revised manifest before freeze/hash.

Required machine correction on PR #94:

1. replace `CURRENT_POLICY_BASIS_INVALIDATED_OR_CHANGED` in the primary vector with a neutral changed-basis condition;
2. stop marking the changed policy basis non-current solely because it changed;
3. explicitly declare that primary-vector invalidation is not asserted as input;
4. retain separate control descriptions for valid continuity and known-material invalidation;
5. validate the revised branch and wait for exact-revision approval before freezing or executing.

Freeze gate remains fail-closed. No approval, hash, execution, or comparison result may be claimed from this draft revision.


## Cross-framework current-basis evaluator freeze lane — live reconciliation 2026-08-28

Authoritative working surface:

```text
repository: StegVerse-org/StegVerse-SDK
PR: #94
branch: test/cross-framework-current-basis-manifest-draft-20260828
artifact: inspection/examples/cross-framework-current-basis-request.draft.json
exact reviewed revision pending external approval: c9b8935309e69d3a6f70e4ad4ef5dd55fb8a9aac
manifest state: DRAFT_PRE_FREEZE
```

Live verified state:

```text
semantic correction: IMPLEMENTED
source validation: VALIDATED
Evaluator Manifest Source Validation run: 33196691745 SUCCESS
PR merged: false
manifest frozen: false
final artifact SHA-256 recorded: false
independent comparison execution: NOT EXECUTED
custody/replay/reconstruction evidence for this comparison: NOT PRESENT
release/deployment/activation implied: false
```

External evaluator evidence received off-GitHub and preserved here:

- evaluator confirmed that separating material change from established invalidation addresses the semantic distinction raised in review;
- evaluator agreed that keeping the unresolved changed-basis case open to independent determination preserves comparison neutrality;
- evaluator agreed with separate controls for continuity, established invalidation, and unresolved continuity;
- evaluator stated intent to review exact revision `c9b8935309e69d3a6f70e4ad4ef5dd55fb8a9aac` before freeze;
- if that exact revision preserves the stated boundary, the next step is hash/freeze;
- evaluator explicitly acknowledged that the artifact should remain `DRAFT_PRE_FREEZE` until exact-revision review completes.

The earlier semantic issue is therefore RESOLVED_IN_SOURCE but external exact-revision approval remains PENDING. Do not infer approval from agreement with the conceptual correction.

Remaining gates, in order:

1. external evaluator reviews the exact revision `c9b8935309e69d3a6f70e4ad4ef5dd55fb8a9aac`;
2. if approved with no material changes, compute and retain the exact manifest SHA-256 and bind both-party freeze attestations to that exact content;
3. transition the artifact from `DRAFT_PRE_FREEZE` to `FROZEN` only under that joint gate;
4. execute each architecture independently against the same frozen definition;
5. retain each side's observable results/evidence and compare semantics/results rather than internal implementation details;
6. preserve exact-run custody, replay, reconstruction, and any negative/tamper evidence required by the declared manifest.

Any content change after external approval invalidates that approval for freeze purposes and requires review of the new exact revision.

No credential, WebAuthn, owner-secret entry, provider activation, or physical device action is required for the current pre-freeze review gate. The only current manual/external dependency is the evaluator's exact-revision review/approval. Future execution may inherit its ordinary SDK/TVC/Master-Records runtime authority requirements, but none may be pre-claimed from this draft.

Downstream propagation obligation after this lane becomes release-worthy: re-check StegVerse-Labs/Site, GCAT-BCAT-Engine/Publisher, admissibility-wiki, and stegguardian-wiki for only the pertinent contract-level changes. No downstream release/propagation is warranted while the manifest is still DRAFT_PRE_FREEZE.
