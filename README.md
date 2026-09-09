# StegVerse SDK

The StegVerse SDK is a public governance experiment and validation environment for StegGate-style admissibility, AdmittedCode receipt verification, LLM/agent outputs, governed submissions, replay, reconstruction, and inspectable request/receipt boundaries.

A request, manifest, model output, validation result, receipt, or receipt locator does **not** become execution authority merely because it validates.

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

The governed-test runtime dependencies now resolve through public distribution identities for StegCore (`stegverse-stegcore==0.3.0`) and Master Records (`stegverse-master-records==0.2.0`), while Core-Lite remains pinned to its public repository commit. GitHub source access is not required for the two formerly private runtime dependencies; runtime authority remains NONE.

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