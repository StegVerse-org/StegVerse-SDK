# Manifest Receipt Navigation Mirror Handoff

## Canonical authority

```text
goal_id: SDK-MANIFEST-RECEIPT-NAVIGATION-001
repository: StegVerse-org/StegVerse-SDK
branch: main
issue: #16
parent_handoff: SDK_MIRROR_HANDOFF.md
credential_authority: TV/TVC
github_token_runtime_authority: NONE
non-TV/TVC secret_or_token_required: false
current_session_claim: claims/SDK-INGRESS-RUNTIME-BINDING-006.json
release_task: tasks/SDK-SOVEREIGN-RELEASE-ACTIVATION-004.json
```

Live repository state and issue #16 supersede older descriptive-only navigation notes.

## Goal

Provide one public SDK governance vocabulary:

```text
000 -> SDK-owned governed demo
00  -> caller run/return preferences
0A  -> raw/user public-inspection request -> canonical sovereign StegGate runtime
0B  -> stegverse.ingress-manifest.v1 -> validated canonical sovereign StegGate runtime
1   -> exact-run replay by manifest_receipt_id
2   -> exact-run reconstruction by manifest_receipt_id
```

Every executable path remains non-authorizing at the SDK boundary. Canonical governance is StegCore/StegGate and canonical exact-run custody is Master Records.

## Installed execution surfaces

```text
stegverse/governance_navigation.py
stegverse/governance_fallback.py
stegverse/governed_operations.py
stegverse/governance_ingress_runtime.py
stegverse/governance_ingress_cli.py
stegverse/cli.py
stegverse/demo_data/manifest_000_governance_outcomes.json
```

Focused tests:

```text
tests/test_governance_navigation.py
tests/test_governance_fallback.py
tests/test_governance_fallback_cli.py
tests/test_governed_operations.py
tests/test_governance_public_execution.py
tests/test_governance_ingress_runtime.py
```

## 0A / 1 / 2

`stegverse governance` is source-wired to the canonical sovereign runtime for:

```bash
stegverse governance --select 0 --input <public-inspection-request.json>
stegverse governance --select 1 --manifest-receipt-id <MR-...>
stegverse governance --select 2 --manifest-receipt-id <MR-...>
```

The permanent degraded-mode fallback remains separate and may be selected only for pre-governance runtime/transport failure. A genuine `ALLOW`, `DENY`, `REVIEW`, or `FAIL_CLOSED` result is never reinterpreted by fallback selection.

## Option 0B — executable ingress binding

Structural `stegverse.ingress-manifest.v1` validation alone cannot authorize or supply missing StegGate evidence. The public profile already provides `extensions`; executable 0B now requires:

```text
extensions.stegverse_governance_request
```

That value must contain the complete canonical StegGate request, including its candidate and required judgment/signal/execution evidence. The SDK does not synthesize missing evidence.

Before execution:

1. `validate_external_manifest()` validates/canonicalizes the ingress manifest.
2. The governance-request candidate hash must exactly equal the ingress-manifest candidate hash.
3. Source framework, source instance/output ID, ingress profile/version, and canonical manifest hash are copied into non-authorizing `declared_context.sdk_ingress_manifest_identity` and the public input metadata.
4. `authority_claim=false`; external consequence remains disabled.
5. The resulting public request is delegated to `stegverse.sovereign_validation_runtime`.

Executable entry:

```bash
python -m stegverse.governance_ingress_cli 0B <manifest.json> \
  --custody-db ./stegverse-master-records-validation.db
```

0B fails closed when the complete governance request is absent, its declared context conflicts with canonical ingress identity, or its candidate differs from the ingress candidate.

## Option 000 — executable safe canonical demo

The SDK-owned dataset remains:

```text
stegverse.000-demo-dataset.v1
```

It contains exactly one teaching example each of `ALLOW`, `DENY`, `REVIEW`, and `FAIL_CLOSED`. Those examples remain data, not four actual decisions.

`build_000_public_request()` now constructs an explicit complete bounded StegGate request for the demo-only candidate. It declares:

```text
demo_only=true
external_side_effect=false
authority_effect=NONE
continuity.required=false
approval.required=false
```

The actual run is delegated to the same canonical sovereign runtime used by the ordinary path. The static `demo_output_manifest_shape()` intentionally remains `PENDING_RUNTIME_BINDING`; only `run_000_demo()` replaces that state after it receives a canonical runtime result with receipt/custody fields.

Executable entry:

```bash
python -m stegverse.governance_ingress_cli 000 \
  --custody-db ./stegverse-master-records-validation.db
```

This preserves the anti-false-completion invariant: embedding a dataset is not represented as processing it.

## Caller projection / custody separation

```text
return_projection -> user-disclosable transition receipt projection
manifest_labels   -> user-facing explanatory labels
Master Records    -> canonical custody independent of both
```

Neither projection control grants authority or suppresses canonical custody.

## Cross-repository owners

```text
StegVerse-Labs/StegCore
  canonical StegGate evaluation and receipt semantics

master-records/orchestration
  exact-run custody and reconstruction

StegVerse-org/LLM-adapter
  governed machine ingress/transport where applicable

StegVerse-Labs/TV + StegVerse-Labs/TVC
  credential/release/route authority where credentials are required
```

No second evaluator, custody registry, credential authority, or receipt-ID authority is created here.

## Validation evidence

Previously retained local deterministic evidence:

```text
fallback dispatch/error separation: 4/4 PASS
canonical sovereign result-alias adapter checks: 3/3 PASS
fallback module syntax: PASS
```

Current 000/0B source and focused tests are committed. The execution environment available to this session cannot resolve github.com for an anonymous checkout, and GitHub reported zero workflow runs for the latest ingress CLI head. Therefore the new 000/0B tests are **installed but not claimed PASS** in this handoff.

Hosted validation is not manually triggered during the billing incident. Missing execution evidence remains a validation gap, not success.

## Claims / collision control

```text
SDK-GOVERNANCE-SOVEREIGN-FALLBACK-003: RELEASED
SDK-PUBLIC-GOVERNANCE-EXECUTION-005: RELEASED
SDK-INGRESS-RUNTIME-BINDING-006: CLAIMED_FOR_INTEGRATION until validation/handoff transfer is complete
SDK-AUTHORITY-BOUNDARY-SOVEREIGN-RUN-002: MACHINE_OWNED exact execution/custody evidence lane; DO NOT COMPETE
```

## Remaining executable tasks

```text
1. execute tests/test_governance_ingress_runtime.py in a credential-free sovereign/local lane;
2. execute the existing public 0A/1/2 focused tests in that same lane;
3. obtain one actual 000 canonical run receipt and verify dataset SHA-256/custody/result binding;
4. obtain one actual 0B canonical run receipt and verify ingress identity is retained in exact-run evidence;
5. fold 000/0B into the primary `stegverse governance` command only after the executable binding is validated, without duplicating the canonical runtime;
6. TV/TVC-authorized release lane publishes a release/package containing the corrected surfaces and verifies the distributed contents;
7. exact evaluator/user execution evidence confirms the distributed package reaches canonical governance rather than an unavailable hosted ingress.
```

Owners for tasks 1-4: canonical credential-free sovereign SDK validation / machine evidence lane. Owner for task 5: issue #16 integration after validation release. Owner for task 6: `tasks/SDK-SOVEREIGN-RELEASE-ACTIVATION-004.json`. Owner for task 7: evaluator/machine evidence lane consumed by issue #16.

## Completion accounting

Current navigation/execution source denominator:

```text
1 000/00/0/1/2 navigation: COMPLETE
2 0A canonical source execution: COMPLETE_SOURCE
3 1 replay source execution: COMPLETE_SOURCE
4 2 reconstruction source execution: COMPLETE_SOURCE
5 permanent canonical fallback: COMPLETE_SOURCE
6 0B complete-evidence binding: COMPLETE_SOURCE_UNVALIDATED
7 000 complete bounded runtime binding: COMPLETE_SOURCE_UNVALIDATED
8 credential-free focused validation of current complete surface: PENDING
9 distributed TV/TVC-authorized release verification: PENDING_MACHINE_OWNED
10 exact external/evaluator execution evidence: PENDING_MACHINE_OWNED
```

```text
task completion: 7/10 = 70%
developed files required for current source scope: 10/10 = 100%
scaffolding/stubs: 0
validation: 4/7 gates with retained evidence or prior proven source behavior; new 000/0B execution gates pending
integration: 7/9 source integrations complete; primary CLI folding + distributed activation pending
goal activation: 7/10 release predicates complete
session consolidation: all originating goals have durable canonical owners; current claim must still be released before session closure
```

## Archive condition

This handoff is sufficient to continue the SDK work without chat history once `SDK-INGRESS-RUNTIME-BINDING-006` is released and its validation/evidence continuation is transferred to the named machine/repository owners. Product activation is distinct from session archival readiness and must not be inferred from source completion.
