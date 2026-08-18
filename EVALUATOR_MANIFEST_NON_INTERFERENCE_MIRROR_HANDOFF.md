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

Core implementation merged to `main` by PR `#44`, squash commit `976d1953385ac4ef903fc2cd969f5b20ef311d39`:

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
  immutable commit-archive source binding
  source branch + dirty-tree/archive-state capture
  SHA-256 and byte size for applicable artifacts
  self-binds the builder, validator, tests, workflow, handoff, and plan

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
  exact-commit SHA-256 artifact manifest emitted in logs
  permissions remain empty
  no runtime, signing, release, custody, or evaluator authority

tests/test_public_inspection_governed_binding.py
  stale fixture corrected to include required execution provenance
```

Artifact-manifest follow-ons:

```text
PR #45 -> 5420a4153567cf264b5d7cd384f25a68b33a674e
  immutable commit-archive binding added
  workflow emits exact-commit artifact manifest
  validation run 32166774317: SUCCESS

PR #46 -> 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
  artifact manifest self-binds methodology + workflow + governed-binding tests
  validation run 32166903844: SUCCESS
  validation job 95808521073: SUCCESS
  24 source/boundary tests: PASS
  17 expected artifacts hashed
  missing artifacts: []
```

The validated PR head `d4d615bb63d02894b2e26497285d259892112739` and squash-merged candidate `16c99037a42e4d667b9df4a7a5efbaae9dd7184c` have the identical Git tree:

```text
d238131690fdc3833cc861b69b0760e570e2b55a
```

Durable source receipt:

```text
evidence/oda3/evaluation-boundary-source-receipt-2026-08-18.json
```

The receipt records the 17 SHA-256 artifact hashes, exact validation run/job, test counts, source-binding method, validated/merged tree equivalence, and the explicit boundary that governed runtime activation is not claimed.

The SDK governed-test dependency set remains pinned by `pyproject.toml`:

```text
StegVerse-Labs/StegCore @ 083557adec1bdbace09ebd10fb0765eb8e9a9d08
Data-Continuation/core-lite @ 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
master-records/orchestration @ 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

At the pinned StegCore revision, the applicable runtime identity contract identifies portable product `0.2.0`, contract `stegverse.steggate.runtime-identity.v1`, and runtime identity `stegverse:steggate:canonical:three-layer:v1`.

### Frozen first governed-run candidate

The first ODA3 governed evaluation-boundary run is frozen to:

```text
SDK candidate commit: 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
SDK candidate tree: d238131690fdc3833cc861b69b0760e570e2b55a
source receipt: evidence/oda3/evaluation-boundary-source-receipt-2026-08-18.json
execution task: StegVerse-org/StegVerse-SDK#47
```

Later documentation/evidence commits do not silently move this candidate. A different candidate requires an explicit new source receipt and task-state update.

### Mandatory evaluator ingress and exposure boundary

The first ODA3 experiment must begin at the evaluator-facing SDK submission surface:

```text
external evaluator
-> StegVerse SDK manifested submission / normalization / binding
-> Core-Lite manifested route carrier
-> StegCore / canonical StegGate
-> Master Records custody
-> governed result returned through the manifested route
```

For this primary experiment, direct evaluator submission/injection to Core-Lite, StegCore, or StegGate is not authorized and does not satisfy the proposition under test. Those remain downstream governed/internal surfaces. An evaluator-accessible alternate route around SDK ingress is itself a boundary violation and must be unavailable or rejected.

### Aggregate production release-set gate

The exact run is additionally bound to aggregate release set:

```text
release_set_id: ODA3-EVALUATOR-PATH-2026-08-18-R1
manifest: evidence/oda3/aggregate-release-set-candidate-2026-08-18.json
SDK:            v1.0.13 -> 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
Core-Lite:      v0.9.0  -> 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
StegCore:       v0.2.0  -> 083557adec1bdbace09ebd10fb0765eb8e9a9d08
Master Records: v0.1.0  -> 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

Prepared release notes and release-control handoffs now exist in all four repositories. The tags themselves must be published by TV/TVC-governed release authority and must resolve exactly to the candidate commits above. GitHub Actions must not be promoted into runtime/control-plane authority to manufacture this state.

### ODA3 activation/evidence boundary

Completed source/release-preparation milestones:

```text
1. focused PR opened against main: COMPLETE (#44)
2. credential-free source-validation passes on exact PR head: COMPLETE (run 32166517959)
3. implementation merged to main: COMPLETE (976d1953385ac4ef903fc2cd969f5b20ef311d39)
4. exact-commit artifact manifest generated and durably retained: COMPLETE
5. aggregate release set frozen with release notes/target tags across all four repos: COMPLETE_SOURCE_PREP
```

Remaining activation/evidence milestones:

```text
6. TV/TVC-governed release tags published for all four exact candidates
7. tag resolutions verified and SDK release catalog reports all_components_release_tag_bound=true
8. exact governed boundary run executed from evaluator -> SDK through canonical manifested route
9. representative route receipts + manifest receipt + Master Records custody retained
10. replay/reconstruction evidence retained where requested
11. independent unmodified verification PASS retained
12. manifest/governance-result tamper verification FAIL evidence retained
13. ODA3 independently reproduces or receives a complete evidence packet
```

GitHub CI proves source/schema/binding behavior and exact source-file identity only. It does not prove exact governed activation and must not become production/runtime/control-plane authority.

### Files/modules still required for this follow-on

Destination `StegVerse-org/StegVerse-SDK` / issue `#47`:

```text
PENDING: TV/TVC-published/verified aggregate release tags
PENDING: exact normalized ODA3 valid manifest used for governed run
PENDING: exact sovereign result JSON
PENDING: exact route receipt chain / manifest receipt evidence
PENDING: reconstruction artifact
PENDING: replay artifact if ODA3 requests replay in the first packet
PENDING: independent PASS verification report
PENDING: independent tamper FAIL reports
PENDING: complete ODA3 evidence packet / independent reproduction record
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

Release-set preparation is now explicit. Actual tag/release publication remains TV/TVC-governed. After all four fixed tags exist and are verified against their exact candidate commits, validate tag-based installation and propagate release/changelog identities to:

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
ODA3 deliberate boundary-test source implementation: MERGED_SOURCE_VALIDATED
ODA3 exact source artifact manifest: COMPLETE
ODA3 source receipt: COMPLETE
ODA3 frozen governed-run candidate: 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
ODA3 aggregate release-set preparation: COMPLETE_SOURCE_PREP
ODA3 aggregate tag publication: PENDING_TV_TVC_RELEASE_AUTHORITY
ODA3 exact governed run: PENDING (#47)
ODA3 exact-run evidence packet: PENDING (#47)
ODA3 independent reproduction: PENDING (#47)
new StegCore evaluator required: FALSE
new Master Records custody route required: FALSE
new evaluator-specific route required: FALSE
scoped state: ACTIVE_DISTINCT_SUPPORT
```

## Durable continuation

Continue from this handoff, `PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md`, `docs/ODA3_EVALUATION_BOUNDARY_TEST_PLAN.md`, aggregate release manifest `evidence/oda3/aggregate-release-set-candidate-2026-08-18.json`, source receipt `evidence/oda3/evaluation-boundary-source-receipt-2026-08-18.json`, and issue `#47`. Do not create a second evaluator-specific mirror handoff for the same workstream. Any requested capability outside the published registry remains a separate generally versioned capability-development goal rather than a private ODA3 augmentation.
