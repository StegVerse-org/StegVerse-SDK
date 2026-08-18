# Evaluator Manifest Non-Interference Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
branch: main
credential authority: TV/TVC
GitHub token runtime authority: NONE
```

This scoped handoff records the evaluator-defined testing-manifest implementation. It is subordinate to `SDK_MIRROR_HANDOFF.md` for repository-wide authority and does not reopen completed evaluator/reference-freeze lanes.

## Goal

Allow a tester/evaluator to declare the WHAT, HOW, and WHY of an experiment at submission time when the required capabilities are already published, while preventing evaluator-specific augmentation or tuning of the canonical testing route.

## Invariant

```text
configuration != augmentation
manifest declaration != execution authority
evaluator identity != StegGate decision input
expected observation != StegGate decision input
unsupported requested capability -> reject before execution
published route semantics cannot be hot-patched by a test manifest
```

The evaluator controls the experiment declaration. The published runtime controls the semantics of already-available capabilities. Neither declaration nor developer foreknowledge controls the disposition.

## Installed implementation

```text
inspection/request.schema.json
  optional evaluation_declaration
  WHAT/HOW/WHY declaration
  expected_observation
  supported requested_capabilities
  supported requested_evidence

stegverse/public_inspection.py
  canonical declaration validation
  unsupported capability rejection
  public non-interference testing contract

stegverse/sovereign_validation_runtime.py
  declaration retained as evidence metadata
  declaration excluded from StegGate request model
  requester identity excluded from StegGate request model
  normalized submitted-manifest SHA-256 binding
  exact governance-request SHA-256 binding
  returned-result SHA-256 binding

scripts/validate_public_inspection_request.py
  delegates to runtime's canonical manifest validator
  remains directly executable from repository checkout

inspection/examples/governed-test-request.json
  public evaluator-defined WHAT/HOW/WHY example

tests/test_public_inspection_request.py
  declaration preservation tests
  unsupported-capability rejection test
  non-interference contract assertions

README.md
docs/SDK_CONSOLE.md
  public documentation synchronized with executable behavior

.github/workflows/evaluator-manifest-source-validation.yml
  credential-free, non-authorizing source/schema validation
```

## Published evaluator capability identifiers

```text
commit_time_admissibility
bounded_consequence
master_records_custody
replay
reconstruction
```

These identifiers declare which existing capability surfaces an evaluator intends to exercise. They do not dynamically install a capability or alter route semantics. Replay and reconstruction remain separately invoked operations after an exact-run `manifest_receipt_id` exists.

## Evidence boundary

The canonical runtime computes and returns:

```text
submitted_manifest_hash
governance_request_hash
result_binding_hash
```

The first two are also included in exact-run transaction metadata before Master Records custody. The evaluator declaration is retained in metadata for later comparison between the pre-execution proposition and post-execution claims, but it is not provided to the StegGate decision model.

## Related repository assessment

`StegVerse-Labs/StegCore` already supplies the canonical evaluator and manifested transaction lifecycle used by this route. The SDK passes only `input.steggate_request` into `AdmissibilityRequest.model_validate`; evaluator declaration/requester identity remain SDK evidence metadata. No StegCore semantic change is required for the original goal.

The existing StegCore evaluator-reference handoff explicitly prohibits demo-specific and parallel evaluators and preserves participant-neutral evaluation. This SDK change strengthens that boundary at manifest submission rather than creating another evaluator.

Master Records already retains exact-run evidence-package metadata through the canonical custody path used by the SDK; no new custody authority or separate storage route is introduced here.

## Prior validation

The initial source-validation run exposed a real public-command defect: invoking `python scripts/validate_public_inspection_request.py ...` from a clean repository materialization did not place the repository root on `sys.path`. That defect was corrected rather than waived.

```text
initial run: 31931876666
initial job: 95127854449
initial head: 9250cac8c0223a5e0990ddc5e6496358239e7711
initial result: FAILURE
failure: ModuleNotFoundError for stegverse from standalone documented validator command

corrective commit: a15a122895c5368558bfe7d6434de5db47ab0f82
validation run: 31931907941
validation job: 95127927823
validation result: SUCCESS
manifest validation step: SUCCESS
runtime-module compile step: SUCCESS
source-only boundary step: SUCCESS
runtime authority granted by workflow: FALSE
protected credentials required: FALSE
```

This is source/schema validation, not runtime-activation proof. The implementation deliberately uses the already-canonical sovereign SDK -> Core-Lite -> StegCore/StegGate -> Master Records route governed by existing handoffs.

## ODA3 bounded evaluation-boundary follow-on — 2026-08-18

ODA3 requested that the first bounded exercise test the evaluation boundary itself before advancing to an authority-state-change scenario. The requested matrix adds deliberate attempts to violate or tamper with the boundary, plus independent verification of the resulting evidence.

Canonical task document:

```text
docs/ODA3_EVALUATION_BOUNDARY_TEST_PLAN.md
```

New implementation installed on branch `chatgpt/oda3-evaluation-boundary-handoff-20260818`:

```text
stegverse/evaluation_boundary_verifier.py
  independent recomputation of submitted-manifest binding
  independent recomputation of exact governance-request binding
  independent recomputation of returned-result binding
  explicit PASS / FAIL / NOT_PROVIDED results
  grants no execution or governance authority
  canonicalization profile: stegverse.sdk-canonical-json.v1

tests/test_evaluation_boundary_contract.py
  condition 1: valid published-capability manifest
  condition 2: changed evaluator identity/rationale/expected observation
  condition 3: undeclared capability rejection
  condition 4: canonical-route / semantic override rejection
  condition 5: alternate execution path rejection
  condition 6: post-normalization manifest tamper detection
  condition 7: governance-request / returned-result tamper detection
  condition 8: complete independent verification PASS
  hash-profile parity with sovereign runtime

scripts/build_evaluation_boundary_artifact_manifest.py
  exact local Git source-commit capture
  source branch + dirty-tree capture
  SHA-256 and byte size for applicable artifacts
  non-zero exit on dirty/unbound/incomplete source state

docs/ODA3_EVALUATION_BOUNDARY_TEST_PLAN.md
  exact artifact/request mapping
  pinned governed-test dependency commits
  StegGate product/runtime identity contract mapping
  manifest-field influence boundary
  binding/canonicalization specification
  independent-vs-canonical execution arrangement
  external evidence packet requirements
  later autonomous-actor identification gate

.github/workflows/evaluator-manifest-source-validation.yml
  pull-request validation added
  new boundary tests and verifier compile included
  anonymous source materialization retained
  permissions remain empty
  no runtime, signing, release, custody, or evaluator authority
```

The SDK governed-test dependency set remains pinned by `pyproject.toml`:

```text
StegVerse-Labs/StegCore @ 083557adec1bdbace09ebd10fb0765eb8e9a9d08
Data-Continuation/core-lite @ 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
master-records/orchestration @ 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

At the pinned StegCore revision, the applicable runtime identity contract identifies portable product `0.2.0`, contract `stegverse.steggate.runtime-identity.v1`, and runtime identity `stegverse:steggate:canonical:three-layer:v1`.

### ODA3 activation/evidence boundary

The follow-on is **not complete merely because the source files exist**. Completion requires the strongest available evidence chain:

```text
1. focused PR opened against main
2. credential-free source-validation workflow passes on the exact PR head
3. changes merged to main through normal repository authority
4. clean exact-commit artifact manifest generated
5. exact governed boundary run executed through canonical route
6. representative route receipts + manifest receipt + Master Records custody retained
7. replay/reconstruction evidence retained where requested
8. independent unmodified verification PASS retained
9. manifest/governance-result tamper verification FAIL evidence retained
10. ODA3 independently reproduces or receives a complete evidence packet
```

GitHub CI can prove only source behavior in this lane. It cannot prove exact governed activation.

### Files/modules still required for this follow-on

Destination `StegVerse-org/StegVerse-SDK`:

```text
PENDING: PR creation and source-validation result for current branch
PENDING: merge commit on main
PENDING: exact clean-checkout evaluation-boundary-artifacts.json
PENDING: exact normalized ODA3 valid manifest used for governed run
PENDING: exact sovereign result JSON
PENDING: exact route receipt chain / manifest receipt evidence
PENDING: reconstruction artifact
PENDING: replay artifact if ODA3 requests replay in the first packet
PENDING: independent PASS verification report
PENDING: independent tamper FAIL reports
```

Destination `StegVerse-Labs/StegCore`:

```text
NO NEW SEMANTIC IMPLEMENTATION CURRENTLY REQUIRED for the boundary claim.
VERIFY during exact run that canonical runtime identity remains the pinned contract tuple.
```

Destination `master-records/orchestration`:

```text
NO NEW CUSTODY ROUTE CURRENTLY REQUIRED.
VERIFY exact-run custody and reconstruction evidence for the ODA3 packet.
```

The later authority-state experiment additionally requires a separately identified autonomous actor/model version, consequential action, and exact enforcement point where StegVerse may permit, refuse, or defer that action. That actor must not be inferred from the governance SDK.

## Release and propagation

The original implementation and this ODA3 follow-on are SDK source/evidence work and do not independently authorize a product tag. Repository-wide release authority and unrelated activation gates remain governed by their owning handoffs.

When the SDK next reaches an authorized tag/release state, verify propagation to:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
admissibility-wiki
stegguardian-wiki
```

Those surfaces should describe evaluator-defined manifests as configuration of published routes, not evaluator-specific custom code, and should not imply that source validation equals live governed activation.

## Current scoped state

```text
original evaluator-manifest source implementation: COMPLETE_SOURCE_VALIDATED
ODA3 deliberate boundary-test source implementation: INSTALLED_ON_BRANCH
ODA3 PR validation: PENDING
ODA3 merge to main: PENDING
ODA3 exact governed run: PENDING
ODA3 exact-run evidence packet: PENDING
ODA3 independent reproduction: PENDING
new StegCore evaluator required: FALSE
new Master Records custody route required: FALSE
new evaluator-specific route required: FALSE
scoped state: ACTIVE_DISTINCT_SUPPORT
```

## Durable continuation

Continue from this handoff and `docs/ODA3_EVALUATION_BOUNDARY_TEST_PLAN.md`. Do not create a second evaluator-specific mirror handoff for the same workstream. Any requested capability outside the published registry remains a separate generally versioned capability-development goal rather than a private ODA3 augmentation.
