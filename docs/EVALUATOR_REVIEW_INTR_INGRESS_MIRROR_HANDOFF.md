# Evaluator Review Interlock + InTr SDK Ingress Mirror Handoff

Updated: 2026-08-29

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
issue: #96
branch: feat/evaluator-review-intr-ingress-96
claim: SDK-EVALUATOR-REVIEW-INTR-INGRESS-96-20260829
linked_site_issue: StegVerse-Labs/Site#634
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

Provide the receiving SDK boundary for browser-originated evaluator/demo/test requests that have already been admitted and transported through canonical StegVerse Interlock + InTr. The SDK must validate the bounded request contract and delegate execution to existing SDK test-client surfaces without implementing transport, credentials, receipts, or a parallel evaluator.

## Implemented source

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
  - initially routes only surface=manifold-governance
  - delegates to existing evaluate_manifold_governance(...)
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

## Current completion gates

```text
pre-work collision check: COMPLETE / no open conflicting issue found
SDK issue/claim: COMPLETE
SDK branch: COMPLETE
admitted request validator: IMPLEMENTED
bounded manifold-governance execution adapter: IMPLEMENTED
focused deterministic tests: IMPLEMENTED / CI NOT YET OBSERVED
SDK merge: PENDING
Site merge: PENDING
runtime Interlock Connector provisioning: NOT CLAIMED
live browser->InTr->SDK receipt: NOT OBSERVED
live execution/result return: NOT OBSERVED
activation: NOT CLAIMED
```

## Non-claims

Source, CI, merge, release, or documentation cannot establish real Interlock admission, InTr transport, runtime execution, result return, custody, replay, reconstruction, or activation. Those require directly inspectable runtime evidence.
