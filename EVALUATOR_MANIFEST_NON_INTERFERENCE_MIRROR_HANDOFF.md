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

`StegVerse-Labs/StegCore` already supplies the canonical evaluator and manifested transaction lifecycle used by this route. The SDK passes only `input.steggate_request` into `AdmissibilityRequest.model_validate`; evaluator declaration/requester identity remain SDK evidence metadata. No StegCore semantic change is required for this goal.

The existing StegCore evaluator-reference handoff explicitly prohibits demo-specific and parallel evaluators and preserves participant-neutral evaluation. This SDK change strengthens that boundary at manifest submission rather than creating another evaluator.

Master Records already retains exact-run evidence-package metadata through the canonical custody path used by the SDK; no new custody authority or separate storage route is introduced here.

## Validation

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

This is source/schema validation, not a newly invented runtime-activation proof. The implementation deliberately uses the already-canonical sovereign SDK -> Core-Lite -> StegCore/StegGate -> Master Records route governed by existing handoffs.

## Completion

```text
scoped source implementation remaining: 0
scoped source validation remaining: 0
public documentation synchronization remaining: 0
new StegCore evaluator required: FALSE
new Master Records custody route required: FALSE
new evaluator-specific testing route required: FALSE
scoped state: COMPLETE_SOURCE_VALIDATED
```

No product tag/release is created by this scoped change because repository-wide release authority and unrelated existing activation gates remain governed by their owning handoffs.

## Cross-repository propagation

This implementation is an SDK source/documentation improvement, not a new authorized product release. It therefore does not itself trigger release propagation to Site/Publisher/admissibility-wiki/stegguardian-wiki. At the next authorized SDK release, verify that those public surfaces describe evaluator-defined manifests as configuration of published routes, not evaluator-specific custom code.

## Durable continuation

For this scoped goal, no executable implementation work remains. Any future request for a capability not listed in the published manifest contract must be handled as a separate versioned capability-development goal available generally, not as a private augmentation for one evaluator.
