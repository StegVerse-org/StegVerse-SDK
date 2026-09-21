# StegVerse SDK

> **SDK 1.3.0 release candidate.** The candidate adds generic manifested concurrent purpose-bound worker groups and has passed the four-stage manifest-only experiment. Muhammad/HGAI references in this repository are hypothetical ecosystem examples of the generic Governance Reference Graph; they are not claims of an implemented HGAI integration.


The StegVerse SDK is a public governance experiment and validation environment for StegGate-style admissibility, AdmittedCode receipt verification, LLM/agent outputs, governed submissions, replay, reconstruction, and inspectable request/receipt boundaries.

A request, manifest, model output, validation result, receipt, or receipt locator does **not** become execution authority merely because it validates.

## Canonical complete-manifest SOUTH lifecycle

For machine-to-machine and evaluator-facing communication, a processing result is not automatically the terminal communication state. A **complete communication manifest** binds the original initiating request/entity, any required Publisher presentation/evidence stage, the final StegVerse-side egress transition surface, the Interlock/InTr egress, and the required far-side transition. The complete governed communication direction toward ecosystem egress is referred to as **SOUTH**.

```text
manifest-selected processing
-> canonical custody / replay / reconstruction as declared
-> Publisher presentation/evidence stage when required
-> SDK binds Publisher/result output to the original initiating request/entity
-> final StegVerse-side egress transition surface
-> Interlock/InTr egress
-> far-side Interlock/InTr transition
-> terminal communication state
```

For an external-framework path whose protocol translation is owned by `StegVerse-org/LLM-adapter`, the LLM Adapter is the **final StegVerse-side state transition** before Interlock/InTr egress. It may translate the SDK result into the framework-native protocol, but it may not change evidence semantics, become evidence authority, select processing retroactively, or claim the terminal far-side transition. The complete communication is terminal only after the corresponding far-side Interlock/InTr transition is observed.

New builder-generated manifests include a machine-readable `completion` block for this lifecycle. Legacy v1 manifests that omit `completion` remain structurally valid for backward compatibility, but they are explicitly **not** classified as complete communication manifests merely because processing returned a result.

Publisher is therefore part of the complete manifest when the request requires presentation/evaluator evidence, just as the final egress transition is part of the complete manifest. Publisher renders authentic retained evidence; it does not become governance, transition, credential, processor-selection, or evidence authority. Interlock/InTr remains the governed ingress/egress transition seam, and TV/TVC remains credential authority where credentials are required.

## Open testing and governed interoperability

StegVerse is meant to be inspected, challenged, and used by people and independent systems. Anyone may use the SDK, exercise the published governance lanes, inspect the governing principles and evidence, and reach their own conclusions.

If StegVerse or the StegVerse SDK materially helps validate, augment, or improve another system, attribution is welcome but is not a condition of access. That does not change the purpose of StegVerse: to remain as transparent, inspectable, and open to independent use as possible.

Independent systems may also connect through governed interlocks that preserve each system's authority while allowing explicitly admitted evidence and state transitions to cross the boundary. Such a connection may help the external system, StegVerse, or both. Openness and interoperability do not grant execution authority; every consequential transition remains governed.

### Generic manifested-data processing contract

The SDK is also a machine-to-machine processing boundary for external frameworks. An external framework may submit its **own manifested data, whatever the source-native class**, declare the StegVerse processing capability it wants, bind that capability request to an installed runtime route, and choose how much of the resulting user-disclosable processing/state-transition evidence is returned.

```text
external framework
-> source-native manifested data
-> stegverse.ingress-manifest.v1
-> caller-facing processing capability
-> declared installed runtime route
-> processor-specific evaluation
-> canonical Master Records custody
-> caller-selected artifact projection
-> returned artifact + manifest_receipt_id
```

The submitted data class, processing capability, runtime route, authority, returned artifact depth, and custody are separate dimensions. A relational-state object, scientific observation, financial event, agent output, device event, legal artifact, image-derived observation, or another manifested class remains the source framework's object.

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
graph representation != authority
hierarchy != authority
graph composition != authority
unknown graph relation != authority
caller projection != canonical custody
```

New manifests declare caller-facing intent with `processing.capability` and bind it to `processing.route_id`. Runtime mechanics remain under `extensions.stegverse_route`. Existing v1 governance manifests that omit `processing` remain backward-compatible only for `stegverse.route.canonical-governed.v1`; future/non-governance processors must declare their processing capability explicitly.

Selecting governance does **not** redefine the payload as a StegVerse-native action. For governance, `candidate` is the separate governance proposition being evaluated in relation to the manifested data, while the complete governance state is carried under `extensions.stegverse_governance_request`. Governance fields are conditional on governance processing rather than globally required by the universal envelope. Missing processor evidence is not invented.

An inline payload is bound with `payload_sha256`. A commitment-only payload must declare `payload_commitment_profile`; the currently published independent-verification profile is `sha256` with a 64-character lowercase hexadecimal commitment.

Caller-facing artifact depth is controlled with `return_projection` while canonical custody remains unchanged:

| Requested artifact depth | Projection |
|---|---|
| Governance artifact only | `SELECTED` governance/result transition classes |
| Governance + selected transition result | `SELECTED` governance plus requested transition/result classes |
| Full user-disclosable state-transition artifact | `ALL` |

`NONE` is a minimal/locator return, not the governance-artifact-only mode. It does not suppress Master Records custody or erase transitions.

Machine-readable ingress schema, processor-generic validator, full semantics, and an external-framework example:

```text
schemas/stegverse.ingress-manifest.v1.schema.json
stegverse/manifest_contract.py
docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md
inspection/examples/external-framework-generic-manifest.json
```

Structural manifest validity does not imply that a processor or route is installed. Executable routing separately resolves the declared route and processor binding and fails closed for unsupported, incomplete, conflicting, or unavailable routes. The currently installed 0B processing capability is `governance` on `stegverse.route.canonical-governed.v1`.

### Generic state-transition evidence

Inter-Entity state changes can be represented without creating a new ingress-manifest class. `stegverse.state-transition-evidence.v1` attaches under `extensions.stegverse_state_transition` and records transition identity, prior/new state references, known applicable predicates, ambiguity, and discovered unknowns. The evidence profile is provider-neutral and non-authorizing; it does not itself execute a probe, admit a transition, materialize a WorkSpace, or grant runtime authority.

Readiness is derived fail-closed. An unresolved applicable predicate, unknown predicate applicability, open ambiguity, or open discovered unknown forces `PROBE_REQUIRED`. `READY` is only derivable when every represented applicable predicate is satisfied and every recorded ambiguity/discovered unknown is resolved. A caller claim that contradicts the derived readiness is rejected. Genuinely unknown unknowns cannot be enforced before discovery; after discovery they become known state and must be resolved before later READY classification.

```python
from stegverse.state_transition_evidence import attach_state_transition_evidence

manifest = attach_state_transition_evidence(
    manifest,
    {
        "profile": "stegverse.state-transition-evidence.v1",
        "transition_id": "workspace-transition-002",
        "state_domain": "external_document_projection",
        "prior_state_ref": "sha256:before",
        "new_state_ref": "sha256:after",
        "change_type": "LIVE_EDIT",
        "applicable_predicates": [
            {
                "predicate_id": "session_admitted",
                "applicability": "APPLICABLE",
                "evidence_status": "SATISFIED",
            }
        ],
        "ambiguities": [],
        "discovered_unknowns": [],
    },
)
```

The outer object remains `stegverse.ingress-manifest.v1`, so caller identity or provider choice does not create a bespoke manifest class. Source/CI validation of this evidence profile must not be promoted into a claim that Interlock/InTr, a provider, MIR, Master Records, or an ephemeral WorkSpace actually executed the represented transition.

### Shared Docs multiparty freeze

Shared Docs now has a provider-neutral revision-freeze state model. Each eligible reviewer freezes the exact revision and SHA-256 content digest they reviewed. The default policy is `ALL_ELIGIBLE`: one reviewer's freeze produces `PARTIALLY_FROZEN`; the revision becomes collectively `FROZEN` only when every eligible reviewer has frozen that same revision, digest, review epoch, and policy.

A frozen revision is immutable provenance. Editing the logical document never rewrites that frozen revision. Instead, the edit creates a successor revision, preserves the prior frozen receipts, and resets the current revision to `REVIEW_OPEN` with no inherited reviewer acceptance. Changing the eligible-reviewer set or freeze policy likewise requires a new review epoch/revision.

```text
reviewer freeze != edit authority
individual freeze != collective freeze
collective freeze != governance authority
content change != inherited acceptance
frozen revision N + edit -> frozen provenance N + REVIEW_OPEN revision N+1
```

Lifecycle status should be projected as metadata rather than embedded in the reviewed content bytes; otherwise changing a visible status line is itself a content mutation and correctly requires a new review revision.

Implementation and tests:

```text
stegverse/shared_docs_freeze.py
tests/test_shared_docs_freeze.py
docs/SHARED_DOCS_MULTIPARTY_FREEZE_MIRROR_HANDOFF.md
```

The state model is coordination/provenance only. Provider mutations still require the applicable provider/TVC authority, governed transitions still require Interlock/InTr where applicable, and Master Records reconstruction does not make Master Records a reviewer or editor.

### Manifest Builder

Most users and external frameworks do not need to hand-author `stegverse.ingress-manifest.v1`. The SDK Manifest Builder constructs the canonical manifest from three user-facing choices: source-native data, the installed processing class, and the desired return depth. Processor-specific evidence is still supplied explicitly; the builder never invents missing governance facts.

Python API:

```python
from stegverse.manifest_builder import build_manifest

manifest = build_manifest(
    data=source_native_object,
    data_class="elan.relational-state.v1",
    source_framework="ELAN",
    source_output_id="elan-boundary-001",
    process="governance",
    processor_request=complete_governance_request,
    return_depth="result+evidence",
)
```

Primary CLI:

```bash
stegverse manifest build \
  --input source.json \
  --governance-request governance-request.json \
  --source-framework ELAN \
  --source-output-id elan-boundary-001 \
  --data-class elan.relational-state.v1 \
  --return-depth result+evidence \
  --output elan-boundary-manifest.json
```

Return-depth aliases map deterministically to the canonical projection contract:

| Builder return depth | Canonical projection |
|---|---|
| `result-only` | `SELECTED` governance evidence |
| `result+evidence` | `SELECTED` governance plus relevant transition/custody evidence |
| `full-trace` | `ALL` user-disclosable transition evidence |
| `locator-only` | `NONE` transition-detail projection |

The resulting file is submission-ready for the existing 0B route:

```bash
stegverse governance --select 0B --manifest elan-boundary-manifest.json
```

Builder construction and validation are not governance decisions and grant no authority. Source semantic custody remains external, while canonical Master Records custody remains independent of the caller-facing return depth.

## 90-second start

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse governance
```

Canonical human-facing navigation:

| Option | Meaning |
|---|---|
| `000` | Optional worked transparency/demo sequence |
| `00` | Optional return/explanation preferences |
| `0` | Ordinary governed submission |
| `1` | Replay by `manifest_receipt_id` |
| `2` | Reconstruction by `manifest_receipt_id` |

Direct help is also available:

```bash
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 0A
stegverse governance --select 0B
stegverse governance --select 1
stegverse governance --select 2
stegverse manifest build --help
```

### Pull up the evaluator contract from the console

An evaluator does not need to browse the repository or ask a StegVerse developer for the accepted testing contract. The installed SDK exposes it directly:

```bash
stegverse contract             # summary, supported capabilities, evidence classes, submission commands
stegverse contract --schema    # machine-readable public-inspection JSON Schema
stegverse contract --example   # ready-to-edit evaluator request JSON
stegverse contract --all       # summary + schema + example
```

The same commands are available through `python -m stegverse contract ...`.

An evaluator may author the resulting JSON anywhere, by hand or programmatically, and submit it with:

```bash
stegverse governance --select 0A --input my-test.json
```

or directly through the canonical runtime:

```bash
python -m stegverse.public_inspection_runtime run my-test.json
```

A caller that already has a preformatted `stegverse.ingress-manifest.v1` can submit that manifest through the same primary governance console:

```bash
stegverse governance --select 0B --manifest my-manifest.json
```

The equivalent credential-free module entry remains available:

```bash
python -m stegverse.governance_ingress_cli 0B my-manifest.json
```

`000` and `00` are optional human/LLM transparency surfaces. Option `0A` manifests raw/user request data through the SDK. Option `0B` first validates the processor-generic ingress envelope, then resolves the declared installed route and processor binding. The currently installed 0B binding is governance, which additionally requires and verifies the governance request and candidate identity before delegating to the canonical sovereign runtime. Invalid, incomplete, conflicting, unsupported, or unavailable processor/route requests fail closed rather than being converted by invented semantics.

## Run the canonical governed TEST locally

The public inspection runtime is sovereign/local by default. It uses the canonical pinned Core-Lite, StegCore/StegGate, and Master Records implementations and does **not** require Render, Vercel, GitHub Actions, or another hosted runtime.

Install the pinned governed-test dependencies:

```bash
python -m pip install -e ".[dev,governed-test]"
```

Then run a governed test request:

```bash
python -m stegverse.public_inspection_runtime run \
  inspection/examples/governed-test-request.json
```

The default local custody file is:

```text
./stegverse-master-records-validation.db
```

You may choose another local path explicitly:

```bash
python -m stegverse.public_inspection_runtime run \
  inspection/examples/governed-test-request.json \
  --custody-db ./my-validation-custody.db
```

A successful run returns a canonical governance state, one continuous transaction identity, manifested-route receipts, a `manifest_receipt_id`, verified StegCore receipt-chain status, and `master_records_custody_status: RECORDED`.

The governed TEST uses a deliberately simulated consequence executor:

```text
external_side_effect: false
third_party_host_required: false
```

The governance and custody transitions are real TEST evidence; the test does not perform the proposed external consequence.

## Structured authority and delegation evidence

For evaluator tests that need to distinguish **role labels** from **current scoped authority**, the SDK provides an authority-basis composition path in addition to the ordinary evaluator manifest builder.

The boundary is intentionally narrow:

```text
external framework role/context
+ frozen structured authority/delegation assertions
+ exact candidate action/target/scope
-> canonical StegCore authority-basis resolver
-> actor_authority_current / delegation_current
-> normal StegGate governance request
```

The SDK does not decide that a role name such as `board_member` or `junior_operator` carries authority. The same role label can be paired with different evidence, and the same valid scoped authority evidence can be paired with different role labels without changing the derived currentness facts. What matters at this boundary is whether the structured authority/delegation basis actually covers the exact candidate and is current at the declared evaluation instant.

The authority-basis request and non-authorizing resolution binding remain distinct from the StegGate request. The request also declares whether the submitted authority and delegation assertion sets are complete for the candidate under test. The SDK rejects pre-authored `actor_authority_current` or `delegation_current` values on this path so the evaluator cannot silently smuggle the conclusion into the test input.

```text
role label != authority
structured assertion != issued authority
authority-basis resolution != credential verification
StegGate ALLOW != proof of execution
TV/TVC remains protected credential/scoped-authority issuance authority
Interlock/InTr remains governed transition authority
```

An incomplete basis with no candidate-covering match remains unknown and fails closed in the canonical resolver. Only when the relevant basis is explicitly declared complete may absence of a current candidate-covering authority/delegation establish a DENY. A matching current scoped assertion may establish the positive currentness fact. This prevents partial evidence from being converted into a false negative and keeps independent role/authority comparisons fail-closed without adding a second SDK authority engine.

Python composition is exposed through `build_authority_bound_evaluator_governance_manifest(...)`; the canonical resolver is injected rather than reimplemented by the SDK.

## Governance Reference Graph

The manifest can optionally carry a generic, hash-bound **Governance Reference Graph (GRG)** under `extensions.governance_reference_graph`. HITL hierarchy is one projection of this contract, not the contract itself. The same representation can carry humans, AI systems, services, devices, organizations, roles, datasets, sensors, constraints, credentials, provenance relationships, supervision, escalation, quorum references, delegation context, and other governance-relevant structure.

The SDK validates and preserves the graph; it does not turn graph position, hierarchy, composition, or an unknown relationship into authority:

```text
graph representation != authority
hierarchy != authority
composition != authority
unknown relation != authority
SDK graph validation != governance resolution
```

Each graph has a stable ID/version, its own canonical SHA-256 commitment, typed nodes and directed relationships, applicability fields, source/evidence/basis references, optional canonical constraint references, scoped coverage/completeness declarations, and an explicit non-authorizing authority boundary. The graph is also included in the canonical manifest hash, so changing graph content changes the manifested input binding.

Completeness remains scoped and explicit. A missing relationship in an incomplete graph is not evidence that the relationship is false. This preserves the existing structured-authority rule that incomplete no-match remains UNKNOWN/fail-closed while only an applicable complete basis can support a negative finding.

Python:

```python
from stegverse import build_governance_reference_graph
from stegverse.manifest_builder import build_manifest

graph = build_governance_reference_graph(
    graph_id="external-governance-001",
    nodes=[...],
    relations=[...],
    coverage=[...],
    source_refs=[...],
)

manifest = build_manifest(
    data=source_native_object,
    source_framework="EXTERNAL_FRAMEWORK",
    source_output_id="output-001",
    processor_request=complete_governance_request,
    process="governance",
    governance_reference_graph=graph,
)
```

CLI:

```bash
stegverse manifest build \
  --input source.json \
  --processor-request governance-request.json \
  --source-framework EXTERNAL_FRAMEWORK \
  --source-output-id output-001 \
  --governance-reference-graph governance-reference-graph.json \
  --output manifest.json
```

The evaluator-safe manifest builders accept the same optional graph. Existing structured authority/delegation resolution remains separate: the SDK graph does not independently infer `actor_authority_current`, `delegation_current`, credential validity, or transition permission. Recognized graph semantics belong to canonical StegCore/StegGate projection; TV/TVC remains credential/scoped-authority issuance and verification authority, and Interlock/InTr remains governed transition authority.

Console discovery:

```bash
stegverse governance-graph
stegverse governance-graph --schema
stegverse governance-graph --example
stegverse governance-graph --all
```

The console example is intentionally HITL-shaped for readability, but HITL is only one projection of the generic contract. The console summary and example explicitly report that graph representation, hierarchy, composition, unknown relations, and SDK validation do not grant authority.

Full contract and examples: `docs/GOVERNANCE_REFERENCE_GRAPH.md`.

## Evaluator-defined manifests, fixed testing route

A tester or evaluator does not need to disclose a proposed test to a StegVerse developer so the developer can construct a special route. If the published SDK already exposes the required capability, the evaluator can declare the experiment in the request manifest and submit it through the published governed routing contract.

The optional `evaluation_declaration` records the evaluator's **WHAT / HOW / WHY** before execution:

```json
{
  "evaluation_declaration": {
    "what": "Evaluate commit-time admissibility after a declared state change.",
    "how": "Use the published canonical route and retained exact-run evidence.",
    "why": "Determine what the resulting evidence can establish.",
    "expected_observation": "A stale authorization does not establish current admissibility.",
    "requested_capabilities": [
      "commit_time_admissibility",
      "master_records_custody",
      "replay",
      "reconstruction"
    ],
    "requested_evidence": [
      "governance_decision",
      "manifest_receipt",
      "route_receipts",
      "exact_run_custody"
    ]
  }
}
```

The actual governed candidate and state are supplied under `input.steggate_request`. The declaration is retained as evidence metadata; `requester_label`, `why`, and `expected_observation` are **not** passed into the StegGate decision model. They cannot alter the disposition.

The public testing contract is:

```text
configuration != augmentation
same manifest + same governing inputs + same published runtime semantics -> same evaluation semantics
evaluator identity is not a decision input
expected outcome is not a decision input
manifest submission cannot hot-patch or add a route
unsupported requested capability -> reject before execution
```

Currently published evaluator-facing capability identifiers are:

```text
commit_time_admissibility
bounded_consequence
master_records_custody
replay
reconstruction
```

`requested_capabilities` declares which already-published capabilities the evaluator intends to exercise; it does not dynamically install them or rewrite their semantics. `replay` and `reconstruction` remain separately invoked operations using option `1` or `2` after an exact-run `manifest_receipt_id` exists.

The sovereign run binds the normalized submitted manifest and the exact StegGate request with SHA-256 values in retained transaction metadata and returns `submitted_manifest_hash`, `governance_request_hash`, and a `result_binding_hash`. This makes the submitted experiment inspectable without converting its declared purpose or expectation into authority.

Schema and worked examples are retained in the repository:

```text
inspection/request.schema.json
inspection/examples/governed-test-request.json
schemas/stegverse.ingress-manifest.v1.schema.json
inspection/examples/external-framework-generic-manifest.json
```

## No caller-managed protected runtime credentials

The sovereign evaluator path requires no GitHub token and no caller-managed protected Master Records credential.

```text
GitHub token runtime authority: NONE
public caller credential authority: NONE
protected runtime credential semantics: TV/TVC
```

The optional governed-test dependencies are pinned to public repository commits. GitHub is a source-distribution surface here, not StegVerse runtime authority.

## Frozen evaluator validation — T0 / T1-A / T1-B

The canonical sovereign path has already been exercised against the frozen evaluator cases. Retained validation evidence is in:

```text
validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md
```

Results:

```text
T0   original $420 state                                 -> ALLOW
T1-A same $420, materially changed current policy state  -> DENY
T1-B $4,200 candidate retaining earlier $420 binding     -> DENY
```

Exact-run `manifest_receipt_id` values:

```text
T0   MR-2F21EC98FB60A78DD0135E580DD80B1FE6CEC9C62B905A4F758E5567F1C666E2
T1-A MR-620DDEE41541E2F787BC2702FE56977F4BB298BC1CE34C4284203A429F5453C8
T1-B MR-804AF43FC68949F0BBC4B89E4729CA1880AB5BFA4655185C171CE5D2332487B4
```

For all three cases, retained evidence records:

```text
StegCore receipt chain verified: PASS
Master Records exact-run custody: PASS
manifested route transitions: 10/10
one transaction identity across each route: PASS
replay operation custody: PASS
reconstruction operation custody: PASS
replay/reconstruction consequence reexecution: FALSE
third_party_host_required: FALSE
```

The corresponding portable custody snapshot is retained by `master-records/orchestration` at `validation/evaluator-frozen-sovereign-custody-2026-08-13.zlib.b64`.

## Replay — option 1

Replay uses the exact-run locator and does not overwrite the original run or re-execute its original consequence.

```bash
python -m stegverse.public_inspection_runtime replay \
  MR-<SHA256>
```

Replay itself is new ecosystem history and records this operation trajectory before returning its artifact:

```text
REQUESTED -> SOURCE_RESOLVED -> EVALUATED -> RETURNED
```

## Reconstruction — option 2

```bash
python -m stegverse.public_inspection_runtime reconstruct \
  MR-<SHA256>
```

Reconstruction does not re-execute the original consequence. Its own operation trajectory is recorded before the artifact is returned:

```text
REQUESTED -> SOURCE_RESOLVED -> ARTIFACT_DERIVED -> RETURNED
```

## Public inspection requests

A contributor may create a visible declarative inspection request through an ordinary pull request using:

```text
.github/PULL_REQUEST_TEMPLATE/public-inspection-request.md
inspection/request.schema.json
```

A pull request is a collaboration/request record only. It is not evaluator code, runtime authority, release authority, or custody authority.

Validate or prepare a request without executing governance:

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

## Focused subsystem experiments

The five-option governance navigator is the broad experiment workflow. Focused lower-level surfaces remain available:

```bash
stegverse surfaces
stegverse capabilities
stegverse help-surface admittedcode
stegverse demo admittedcode
```

Current focused surfaces include:

```text
admittedcode
admissibility
llm-admissibility
math-admissibility
universal-entry
bridges
entry-points
```

AdmittedCode is a portable receipt-verification experiment. It is not the whole governance workflow. A valid DENY receipt can be SDK `ACCEPTED` because receipt validation preserves the underlying DENY rather than converting it into permission.

A local LLM-output posture experiment can be run without calling a hosted model:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

## Self-characterization trajectory lane

The SDK now exposes a reusable bounded S0 experiment contract for self-characterization trajectory analysis.

```bash
stegverse run self-characterization \
  --input inspection/examples/self-characterization-s0.example.json

stegverse-self-characterization prepare \
  --input inspection/examples/self-characterization-s0.example.json
```

The primary scored object is the evidence-backed trajectory by which a subject self-model is established, challenged, expanded, corrected, preserved, or reconciled. The normalized experimental score is pre-registered as 50% trajectory, 30% governance, and 20% accountability/reconstruction. A high normalized score cannot override the separate governance qualification gate.

Every experiment state change is receipt-linked. Each transition record binds the prior state, resulting state, observable change, declared evidence/rationale for the transition, and the declared basis for the next planned transition. The caller may choose `transition_explanation_projection: ALL|NONE` for final results; this choice never suppresses canonical custody, replay, or reconstruction.

The lane accepts one to three frozen organizational communication counterparts. SDK-mediated experiments may reveal additional structure, but discovery does not confer standing and direct or proxy-equivalent communication outside the frozen set is prohibited.

The maximum lane end state is:

```text
SELF_CHARACTERIZED_EVIDENCE_REVISED_RECONCILED_SDK_RELATIONALLY_EXPANDED
```

This maximum does not grant new execution, credential, governance, persistence, organizational communication, or legal authority.

Every public viewer may bind replay/reconstruction to a stable node identity:

```bash
stegverse-self-characterization viewer-replay \
  --manifest-receipt-id MR-<HEX> \
  --viewer-node-id node:<stable-viewer-id>

stegverse-self-characterization viewer-reconstruct \
  --manifest-receipt-id MR-<HEX> \
  --viewer-node-id node:<stable-viewer-id>
```

Canonical replay/reconstruction remain unchanged. The SDK appends a non-authorizing `VIEWER_BOUND` operation event to the same Master Records custody, producing deterministic `VR-<SHA256>` and `VC-<SHA256>` correlation identities tied to the canonical run locator, viewer node ID, operation, and lane version. The source run is not mutated and viewer identity is not a governance decision input.

Full contract: `docs/SELF_CHARACTERIZATION_TRAJECTORY_LANE.md`.

## Local model/runtime ownership

The former descriptive “select a local model/runtime” step is obsolete. Executable local-model discovery, launch, private serving, inference, measurement, and proof plus the formally developed `stegverse-reference-lm-v1` are complete and released in `StegVerse-002/micro-node-runtime`.

The SDK does not duplicate that model/runtime authority. LLM provider/runtime translation belongs to `StegVerse-org/LLM-adapter`; route and protected credential semantics remain with TV/TVC.

## Core invariants

```text
observation != inference
inference != intent
intent != instruction
instruction != authorization
authorization != admissibility
submission != execution
manifest validity != ALLOW
receipt acceptance != action approval
manifest_receipt_id != authority
public PR != runtime authority
replay != historical rewrite
reconstruction != consequence re-execution
provider output != authority
configuration != route augmentation
evaluator identity != decision input
expected observation != decision input
GitHub != runtime authority
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
governance fields globally required by universal ingress: FALSE
unsupported processor/route execution: FALSE
caller projection != canonical custody
```

## Validate the checkout

```bash
pytest tests/ -v
python scripts/verify_github_fallback_boundary.py
python -m unittest tests.test_github_fallback_boundary
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_public_inspection_runtime
python -m unittest tests.test_governance_ingress_runtime
python -m unittest tests.test_cli_preformatted_manifest
python -m unittest tests.test_generic_manifest_processing_contract
python -m unittest tests.test_manifest_builder
python -m unittest tests.test_state_transition_evidence
python -m unittest tests.test_shared_docs_freeze
pytest -q tests/test_evaluator_contract_console.py
```

Full console documentation: `docs/SDK_CONSOLE.md`.

## Repository control files

Files matching `*_MIRROR_HANDOFF.md` preserve implementation continuity, validation state, task ownership, supersession, and archive conditions. They are project-control records, not evaluator commands. The public SDK should remain usable from this README plus installed console/help output without a private instruction channel.


## Active cross-framework current-basis comparison — v0.4

The active comparison is frozen against one exact neutral common input. Each architecture derives its own native current-basis representation independently; neither consumes the other's result before its own run completes.

```text
test_id: cross-framework-current-basis-001
vector schema: stegverse.cross-framework-current-basis-vector.v0.4
manifest Git blob SHA-1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
manifest SHA-256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
source validation: PASS
StegVerse owner freeze attestation: FROZEN
common execution window: OPEN
StegCore native derivation: VALIDATED_MERGED
StegCore merge: e80e927616750a88ad7fc88f4017fc496474f1e4
StegVerse independent execution: NOT YET OBSERVED
cross-framework semantic comparison: NOT YET PERFORMED
```

For this testing lane, absent explicitly supplied prior-state data, S0 is the declared initial state from which evaluation begins. A historical S0 receipt is not required. The S0→S1 transition receipt is post-observation evidence: execution independently derives and observes S1 first, then binds the transition receipt.

The exact approved JSON remains byte-for-byte unchanged; its embedded `DRAFT_PRE_FREEZE` label is snapshot content. Effective freeze state is carried by the separate hash-bound attestation under `evidence/evaluator/`.

The SDK thin client for this lane is `stegverse/current_basis.py`. It verifies the exact frozen identity and delegates native derivation/evaluation to canonical `stegcore.current_basis.evaluate_current_basis_vector`; the SDK does not implement a parallel evaluator.

After authentic completion, the result/custody/replay/reconstruction packet must be durably retained and made evaluator-visible through StegVerse-native surfaces. `scripts/package_cross_framework_current_basis_results.py` produces a host-neutral verified packet. `.github/workflows/cross-framework-result-artifact-publication.yml` is only an optional GitHub mirror of that already-complete packet; GitHub is not required for execution, custody, retention, evaluator availability, activation, or completion.

## HGAI Governance Reference Graph example

A concrete HGAI-facing HITL mapping is retained at `docs/HGAI_GOVERNANCE_REFERENCE_GRAPH_EXAMPLE.md`, with a machine-readable fixture at `inspection/examples/hgai-governance-reference-graph.json`.

The example preserves AI supervision, human escalation, evidence provenance, quorum references, scoped authority evidence, time/scope applicability, and explicit completeness while keeping the GRG non-authorizing. It does **not** claim that hierarchy grants authority or that arbitrary GRG relations have already been projected through live StegCore/Interlock execution.


## GRG canonical semantic projection workstream

Child Goal Task `SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001` has merged the recognized-relation source/console projection into SDK main without adding SDK governance semantics; live StegOS/Interlock/InTr receipt proof remains pending. Its canonical handoff is `SDK_GRG_CANONICAL_PROJECTION_CONSOLE_MIRROR_HANDOFF.md`.

The workstream begins with `HAS_SCOPED_AUTHORITY` -> existing StegCore authority-basis resolution and `REQUIRES_CONSTRAINT` -> existing canonical policy-shape ownership, while unknown relations remain preserved/hash-bound/non-authorizing. Source or console validation must not be reported as live Interlock/InTr runtime proof.


## GRG recognized-relation projection console

The public GRG console now has an authority-neutral projection operation:

```bash
stegverse governance-graph --project graph.json \
  --task-id SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001 \
  --action approve \
  --target case:123 \
  --scope irreversible_commitment \
  --observed-at 2026-09-18T18:00:00Z
```

Recognized `HAS_SCOPED_AUTHORITY` relations are projected only into the existing
`stegcore.authority-basis-request.v1` owner contract. The public SDK does not need
StegCore installed to inspect that projection. When canonical StegCore is installed,
`--evaluate-authority-if-available` delegates the projected request to
`stegcore.authority_basis.resolve_authority_basis`; the SDK validates/binds the
returned facts and still does not issue authority.

Recognized `REQUIRES_CONSTRAINT` relations carrying a canonical
`stegcore:policy-shape:...` reference are routed to the existing StegCore
policy-shape ownership boundary. No public callable relation-projection seam exists
there yet, so the SDK reports that exact unsatisfied seam instead of duplicating
quorum, veto, time-lock, escalation, or other policy semantics.

Unknown relations remain `UNKNOWN_RELATION_PRESERVED`, hash-bound, and
non-authorizing. Source/console projection is never reported as
`LIVE_RUNTIME_BOUND`; authentic StegOS/Interlock/InTr receipt lineage remains a
separate runtime predicate.

## TT purpose-bound worker local console

The SDK exposes a source/local semantic demonstration of a purpose-bound worker derived from one declared TT transition cell:

```bash
stegverse worker-lifecycle --input inspection/examples/tt-purpose-worker.example.json
```

The initial built-in arbitrary task uses capability `text.integrity_summary` to compute a SHA-256 digest, UTF-8 byte count, and word count for a supplied text payload. The console records ordered `MATERIALIZED -> INVOCATION_STARTED -> TASK_COMPLETED -> RETIRED` lifecycle receipts and then returns a records-only packet with `worker_live_after_close=false`.

This demonstrates construction, invocation ordering, retirement, and records-only decomposition. It does **not** claim live StegOS/InTr worker materialization, protected authority issuance, or resident runtime execution. Those remain separate authentic-runtime predicates.

## Product-scoped SDK result provenance

Governed SDK results expose a generic `product_processing` provenance envelope so an outside evaluator can distinguish which product processed which portion of a composed transaction. `admittedcode_processing` is the typed AdmittedCode projection of that envelope.

The contract does not infer processing from branding or route labels. AdmittedCode admission, StegCore governance implementation, Core-Lite route carriage, Master Records custody, Interlock/InTr transition authority, StegAgents/runtime execution, LLM-adapter upstream processing, and future product boundaries remain separately attributable. Missing authentic Interlock/InTr or worker evidence is returned as `NOT_OBSERVED`, not promoted from route or generic execution evidence.

The existing runtime `result_binding_hash` remains bound to the underlying canonical runtime result. `sdk_return_binding_hash` binds the enriched SDK return including product provenance. See `docs/PRODUCT_PROCESSING_PROVENANCE.md`.

Product-processing provenance source status: **validated and merged** via SDK PR #268. The source contract is non-authorizing; runtime/transition/custody activation remains owned by the corresponding canonical products.


## SDK Test 2: atomic task activation and task-bound worker creation

`SDK-TT-ATOMIC-TASK-WORKER-BINDING-001` is a completed externally replayable semantic test of the task/worker seam. It preserves the earlier purpose-bound lifecycle test unchanged and tests the stronger invariant that, for this executable-task class, task activation and creation/binding of its task-specific worker are one constitutive transition.

```text
HANDOFF_READY task T + manifest-governed capability M
-> ACTIVATE(T)+CREATE_AND_BIND(W,T)
-> INVOCATION_STARTED
-> TASK_COMPLETED
-> CLOSE(T)+RETIRE(W,T)
-> records-only reconstruction
```

Replay:

```bash
python -m unittest tests.test_atomic_task_worker_binding -v
stegverse task-worker-binding --input inspection/examples/tt-atomic-task-worker-binding.example.json
```

The test fails closed for split ACTIVE/worker states, mismatched binding, pre-created worker state, early invocation, manifest-boundary expansion, incomplete retirement, and retained executor/callable state. This is local semantic evidence only and does not claim authentic WorkerCoordinator, TV/TVC, Interlock/InTr, resident runtime, or Master Records execution.

Canonical handoff: `SDK_TT_ATOMIC_TASK_WORKER_BINDING_MIRROR_HANDOFF.md`.


Test 2 source status: **validated and merged** via SDK PR #271 at `79da01e219342e982406d257d1a417a4aeb05814`. Exact-head Test 2 validation run `35425851872` passed, all eight falsification cases fail closed, and the deterministic records packet hash for the canonical fixture is `b5bbb5476350805a55f365cd27fc0fa8145c75d4cb5b27338d5299d328ca5890`. This remains semantic/replay evidence only; authentic governed runtime seam validation is separate.


### Purpose-bound worker cost/lifetime matrix demo

The SDK now includes a four-case local semantic demonstration that makes the cost-to-lifetime relationship explicit:

```text
Task 1: 1 worker, 1 compute unit  -> 15 s derived maximum lifetime
Task 2: 1 worker, 3 compute units -> 30 s derived maximum lifetime
Task 3: 1 worker, 9 compute units -> 60 s derived maximum lifetime
Task 4: 3 simultaneous workers, 9 aggregate compute units / 3 each
        -> 30 s derived maximum per worker and 30 s group wall-clock budget
```

Task 2 is the median single-worker reference. Task 4 demonstrates that a larger aggregate task can be partitioned across three simultaneous purpose-bound workers without multiplying each worker's authority window: each worker receives the same 30-second median cost/lifetime budget, has a distinct worker identity, overlaps the other two live intervals, retires independently, and contributes only a records-only packet to the final aggregate.

Run the demonstration with:

```bash
python -m stegverse.purpose_bound_worker_cost_demo \
  --input inspection/examples/tt-purpose-worker-cost-demo.example.json
```

The stated lifetimes are maximum derived budgets, not minimum residence times. Purpose completion still retires a worker early. This remains local SDK semantic evidence and does not itself claim authentic WorkerCoordinator, TV/TVC, Interlock/InTr, resident-runtime, or Master Records execution.


### Test One through Manifest Builder

Test One now uses the same processor-generic ingress contract as other SDK manifested tests. The evaluator does not call `worker-lifecycle` directly. It builds a canonical manifest, then executes that manifest through its published installed route:

```bash
stegverse manifest build \
  --input inspection/examples/sdk-test1-source.json \
  --processor-request inspection/examples/sdk-test1-purpose-worker.processor-request.json \
  --source-framework external_evaluator \
  --source-output-id sdk-test-one-001 \
  --process purpose_bound_worker \
  --return-depth full-trace \
  --output /tmp/sdk-test1.manifest.json

stegverse run-manifest --manifest /tmp/sdk-test1.manifest.json
```

The processor derives the canonical TT worker request from the validated manifest. There is no second worker-specific variable input. Test One uses one compute unit and a 15-second derived maximum lifetime (6 task + 1 known delay + 2 inferred delay reserve + 3 records decomposition + 3 safety reserve), with early retirement on purpose completion.



## run-manifest result lineage binding (2026-09-20)

Canonical coordination goal: `SDK-RUN-MANIFEST-RESULT-LINEAGE-BINDING-001` / COSV `71000000111111`.

Every successful public `stegverse run-manifest` result is now bound by the shared dispatcher to the validated complete canonical ingress manifest and to a deterministic generic run-manifest execution request. The returned result includes `canonical_manifest_sha256`, `request_sha256`, `processor_result_sha256`, and a `manifest_lineage` object carrying the exact request object whose digest is reported. `processor_result_sha256` commits the processor result before dispatcher enrichment, so nested lifecycle receipts/closures are transitively committed without requiring test-specific result logic.

Test 3's canonical future-facing scenario identifier is `TEST_3_INVARIANCE_SHORT_LIVED_ACTOR_SEAM`. The historical `TEST_3_RICHARD_SHORT_LIVED_ACTOR_SEAM` identifier remains accepted only as a compatibility alias for retained/replayable evidence. Historical four-stage artifacts are not rewritten. SDK 1.3.0 remains a release candidate until the canonical tag/release publication occurs.

## Four-stage manifest-only experiment rerun (2026-09-20)

Canonical coordination goal: `SDK-FOUR-STAGE-MANIFEST-EXPERIMENT-RERUN-001`.

The four-stage evaluator experiment now freezes the exact checked-out SDK head, builds all four manifests before execution, and changes only the manifest supplied to `run-manifest` between stages. Task 4 concurrency evidence is derived from overlapping post-ready-barrier worker invocation lifetimes (`execution_started_ns` through `execution_completed_ns`) synchronized by a generic invocation-start barrier. It proves concurrent worker invocation lifetimes, not CPU-parallel instruction execution. Test 3 intentionally exercises the same installed `atomic_task_worker` processor as Test 2 with a distinct manifested identity and preregistered proposition; it is an invariance/person-neutrality test, not a hidden Test-3-specific execution route. The retained workflow artifact includes raw manifests, raw results, source-index evidence, experiment metadata, and SHA-256 inventory for independent replay.


## Public developer wiki

Canonical goal: `SDK-PUBLIC-DEVELOPER-WIKI-001`.

The SDK repository now owns the source for a developer-facing public wiki projection targeting `https://sdk.stegverse.org/`. The wiki is built from current canonical SDK files at publication time and publishes a SHA-256 source manifest so the displayed developer surface can be tied back to the exact repository revision and exact source bytes.

Primary developer flow:

```text
source-native manifested data
-> stegverse.ingress-manifest.v1
-> caller-selected processing capability
-> declared installed runtime route
-> processor-specific evaluation
-> canonical Master Records custody
-> caller-selected return projection
-> returned artifact + manifest_receipt_id
-> replay / reconstruction where applicable
```

Implementation:

```text
scripts/build_sdk_public_wiki.py
tests/test_sdk_public_developer_wiki.py
.github/workflows/sdk-public-developer-wiki-pages.yml
docs/SDK_PUBLIC_DEVELOPER_WIKI_MIRROR_HANDOFF.md
```

The public wiki is documentation/navigation only. It grants no governance, execution, transition, credential, custody, evidence, processor-selection, release, or publication-transition authority.


Current public cutover status: **RETIRED / COMPLETE / PUBLICLY OBSERVED**. GitHub-hosted observation run `35649334318` independently fetched the deployed ingress schema, external-framework example, receipt-navigation document, and Site `wikis.html` link over HTTPS with HTTP 200 and required served-body markers. Site claim/COSV terminalization merged in Site PR #1448.


## Four-stage evidence remediation — 2026-09-21

Goal `SDK-FOUR-STAGE-EVIDENCE-REMEDIATION-001` hardens the manifest-only four-stage experiment without changing the retired historical evidence package. The current development branch makes Task-4 overlap falsifiable with a serialized negative control, partitions the source text into ordered disjoint ranges with exact reconstruction evidence, recomputes the group result commitment, declares local semantic worker routes as `SDK_LOCAL_SEMANTIC_DEMONSTRATION`, enforces rejection if those local bindings are ever presented as governed-runtime completion, and compares Test 2/Test 3 through an explicit invariance projection modulo identity/proposition fields.

This work is evidence/test-contract hardening only. It does not assert authentic WorkerCoordinator standing, retained retirement, Master Records custody, HB authority, deployment, or governed runtime execution. Those retained-standing/retirement predicates belong to a separate successor task after this remediation is merged and validated.


### Public SDK wiki observation

`scripts/observe_sdk_public_wiki.py` performs observation-only HTTPS fetches of the deployed ingress schema, external-framework example, receipt-navigation document, and Site wiki-directory link. The paired `Observe SDK Public Wiki` workflow runs those checks from GitHub-hosted Actions and records a machine-readable report without granting execution, governance, publication, or custody authority.
