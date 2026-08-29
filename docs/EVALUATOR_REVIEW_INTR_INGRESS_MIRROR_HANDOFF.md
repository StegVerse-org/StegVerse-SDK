# Evaluator Review Interlock + InTr SDK Ingress Mirror Handoff

Updated: 2026-08-29

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
issue: #96
implementation_pr: #97
merge: 00e8acc274be0328fc009807feaf1afd35f3f0de
claim: SDK-EVALUATOR-REVIEW-INTR-INGRESS-96-20260829
linked_site_issue: StegVerse-Labs/Site#634
linked_site_pr: StegVerse-Labs/Site#635
parent_handoff: SDK_MIRROR_HANDOFF.md
production_governance_owner: StegVerse-Labs/StegCore
production_runtime: stegcore.manifold_governance.govern_manifold_action
credential_authority: TV/TVC
transport_owner: StegVerse runtime Interlock Connector + InTr
sdk_role: ADMITTED_DEMO_TEST_CLIENT
parallel_evaluator_permitted: false
authority_effect: NONE
activation_effect: false
```

## Goal

Provide the receiving SDK boundary for browser-originated evaluator/demo/test requests that have already been admitted and transported through canonical StegVerse Interlock + InTr. The SDK validates the bounded request contract and delegates execution to existing SDK test-client surfaces without implementing transport, credentials, receipts, or a parallel evaluator.

## Installed source

```text
stegverse/evaluator_review_intr.py
  - validates stegverse.evaluator_review.interlock_request.v1
  - requires request_class=EVALUATOR_REVIEW
  - requires transport=InTr
  - requires opaque authority_ref
  - requires authority_transfer=false
  - preserves exact test/revision/manifest-hash bindings
  - rejects payload/binding disagreement
  - exposes execute_admitted_demo_test(...)
  - routes surface=manifold-governance to existing SDK client
  - delegates to evaluate_manifold_governance(...)
  - does not mint Interlock/InTr receipts
  - does not grant authority

tests/test_evaluator_review_intr.py
  - valid admitted request
  - non-InTr rejection
  - authority-transfer rejection
  - revision-binding mismatch rejection
  - invalid manifest hash rejection
```

## Runtime sequence

```text
Site browser UI
  -> Site bounded evaluator Interlock request
  -> provisioned Interlock Connector
  -> InTr transport / receiving admission
  -> SDK admit_evaluator_review_request(...)
  -> existing SDK test-client surface
  -> canonical StegCore evaluator where applicable
  -> SDK result
  -> runtime Interlock response + InTr return receipt
  -> Site receipt/binding validation
  -> UI projection
```

The SDK starts after receiving Interlock admission. It does not assert that a request reached it merely because `transport=InTr` is declared; the runtime must verify real transport before invoking SDK ingress.

## Authority boundaries

```text
SDK credential authority: false
SDK transport authority: false
SDK InTr receipt minting: false
SDK governance authority: false
SDK parallel evaluator: false
SDK external consequence authority: false
StegCore production governance authority: unchanged
TV/TVC credential authority: unchanged
Master Records custody/replay/reconstruction: unchanged where applicable
```

## Validation + merge evidence

```text
SDK PR: #97
final head: f97d38d2c71981f4268992eb09ebeb56deb92157
SDK Package Artifact Validation (Non-Authorizing): run 33274191061 / SUCCESS
merge: 00e8acc274be0328fc009807feaf1afd35f3f0de
source_state: IMPLEMENTED_VALIDATED_MERGED
```

## Current completion gates

```text
pre-work collision check: COMPLETE
SDK issue/claim: COMPLETE
admitted request validator: IMPLEMENTED
bounded manifold-governance execution adapter: IMPLEMENTED
focused deterministic/package validation: SUCCESS
SDK merge: COMPLETE
Site source counterpart: IMPLEMENTED ON PR #635 / VALIDATION IN PROGRESS
runtime Interlock Connector provisioning: NOT CLAIMED
live browser->InTr->SDK receipt: NOT OBSERVED
live execution/result return: NOT OBSERVED
activation: NOT CLAIMED
```

## Non-claims

Source, CI, merge, release, or documentation cannot establish real Interlock admission, InTr transport, runtime execution, result return, custody, replay, reconstruction, or activation. Those require directly inspectable runtime evidence.
