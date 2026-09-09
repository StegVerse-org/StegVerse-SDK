# SDK Generic Manifest Downstream Propagation Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
source_goal: SDK-PROCESSOR-GENERIC-MANIFEST-002
source_cosv: 71000000100110
continuation_goal: SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This handoff is the current source of truth for processor-generic downstream propagation and the SDK completion gate opened as issue #137 / PR #138.

## Canonical propagated semantics

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance-specific fields are not universal manifest requirements
unsupported or uninstalled processor/route execution fails closed
```

Current executable processor:

```text
processing.capability: governance
processing.route_id: stegverse.route.canonical-governed.v1
processor-specific request: extensions.stegverse_governance_request
```

Future processors must not inherit governance-only input requirements merely because governance is currently installed.

## SDK completion gate

```text
completion issue: StegVerse-org/StegVerse-SDK#137
completion PR: StegVerse-org/StegVerse-SDK#138
completion branch: sdk-completion-gate-137
one-command surface: stegverse external-run
public preparation mode: --prepare-only
public submission schema: stegverse.sdk.external-framework-submission.v1
executed run schema: stegverse.sdk.external-framework-run.v1
```

PR #138 adds a package-level external-framework path that preserves source-native data, retains evaluator preregistration outside the governance decision request, binds the declared installed governance route, preserves caller-selected return projection, requires a canonical `manifest_receipt_id` after execution, and supports replay plus reconstruction from that receipt.

The public `--prepare-only` path deliberately requires no private governed-runtime dependencies. It emits the exact validated portable submission bundle and does not claim execution or fabricate a receipt. Canonical governed execution remains a separate runtime step using the same manifest and the pinned governed-test dependencies.

## Reproducible ELAN Test 1 assets

```text
inspection/examples/elan-relational-state-test1.json
inspection/examples/elan-governance-request.example.json
inspection/examples/elan-evaluation-declaration-test1.json
docs/ELAN_TEST1_RUNBOOK.md
stegverse/external_framework_runner.py
tests/test_external_framework_runner.py
.github/workflows/external-framework-e2e-validation.yml
```

The source fixture contains only ELAN-observable/source-native data. The governance request is a separate processor-specific example. The evaluator declaration is separately retained evidence metadata.

## Exact validation state

Earlier PR #138 source/package heads demonstrated PASS in:

```text
Manifest Builder Source Validation
SDK Package Artifact Validation
Evaluator Contract Console Validation
```

A first governed end-to-end workflow attempt failed before SDK execution because anonymous pip could not clone the private `StegVerse-Labs/StegCore` governed-test dependency. Repository visibility inspection confirms `StegVerse-Labs/StegCore` and `master-records/orchestration` are private while `Data-Continuation/core-lite` is public. This is a dependency-access boundary, not evidence of an SDK manifest/runner failure.

The completion branch therefore separates two claims:

```text
PUBLIC_EXTERNAL_SUBMISSION_PREPARATION: machine-validated with public SDK dependencies only
CANONICAL_GOVERNED_EXECUTION: requires environment with canonical pinned governed-test dependencies
```

No private repository is to be made public, copied into the SDK, or exposed solely to make anonymous CI pass without an explicit repository-visibility/release decision.

## Durable continuation evidence

```text
source correction: StegVerse-org/StegVerse-SDK PR #126 COMPLETE_VALIDATED_MERGED
assessment: StegVerse-org/StegVerse-SDK PR #127 MERGED
continuation task registration: StegVerse-org/StegVerse-SDK PR #128 MERGED
ownership reconciliation: StegVerse-org/StegVerse-SDK PR #130 MERGED
COSV registration: StegVerse-Labs/.github PR #1184 MERGED
COSV ownership reconciliation: StegVerse-Labs/.github PR #1185 MERGED
SDK completion issue: StegVerse-org/StegVerse-SDK issue #137 OPEN
SDK completion PR: StegVerse-org/StegVerse-SDK PR #138 OPEN
post-completion propagation audit: StegVerse-org/StegVerse-SDK issue #139 OPEN
Site dependency tracker: StegVerse-org/StegVerse-SDK issue #129 OPEN_TRACKING_ONLY
admissibility coordinator: StegVerse-Labs/admissibility-wiki issue #66
admissibility implementation owner: StegVerse-Labs/admissibility-wiki issue #65 / Worker D
```

## Downstream disposition

### StegVerse-Labs/Site

```text
pertinent: YES
required propagation: align the Site SDK preview/backend-facing manifest description with processing.capability, processing.route_id, processor-specific extensions, return_projection, manifest_receipt_id, and the portable submission boundary
implementation boundary: Site remains preview/submission UI; no processor, evaluator, receipt, custody, or route authority
current owner: Site machine orchestration
tracking: StegVerse-org/StegVerse-SDK issue #129
```

Site/public UI completion is downstream product work and is not part of the binary SDK package completion gate.

### GCAT-BCAT-Engine/Publisher

```text
pertinent: NO_DIRECT_CONTRACT_CHANGE
reason: Publisher consumes bounded Site activation/publication projections, not stegverse.ingress-manifest.v1 processor selection
action: preserve projection-only boundaries; do not duplicate SDK processor logic
```

### StegVerse-Labs/admissibility-wiki

```text
pertinent: YES
required propagation: bounded processor-generic SDK interoperability doctrine
coordinator: issue #66
implementation owner: Worker D / issue #65
worker state: MACHINE_OWNED_DO_NOT_COMPETE
required semantics: source-native payload class; independent processing capability; installed route binding; conditional processor evidence; artifact projection; non-authority boundary
```

### StegVerse-002/stegguardian-wiki

```text
pertinent: NO_DIRECT_CONTRACT_CHANGE
reason: Guardian consumes bounded downstream interpretation after upstream evidence; it does not consume SDK ingress manifests directly
action: preserve non-enforcement boundaries; do not duplicate processor semantics
```

## Publicly displayed surfaces

Canonical public domain:

```text
https://stegverse.org/
```

Current public Ecosystem Chat observation target:

```text
https://stegverse.org/ecosystem-chat.html
```

No dedicated processor-generic hosted submission route is claimed until Site creates, deploys, and validates an actual `https://stegverse.org/...` route. The SDK package/CLI does not depend on that hosted UI.

## Remaining files/modules by destination

### StegVerse-org/StegVerse-SDK

```text
PR #138 exact-head validation must pass before merge
README external-run/public-prepare wording must be reconciled before release if stale
release/version decision must not reuse or retarget the pending historical v1.2.0 release identity
```

### StegVerse-Labs/Site

```text
docs/ECOSYSTEM_CHAT_SDK_BACKEND_HANDOFF.md
fixtures/ecosystem-chat/sdk-form-payload.example.json only if stale
fixtures/ecosystem-chat/sdk-backend-response.example.json only if stale
associated Site SDK checker/schema only if required by the admitted Site-owned mutation
```

### StegVerse-Labs/admissibility-wiki

```text
Worker D-owned bounded public SDK interoperability doctrine surface
associated subordinate handoff or existing external-framework handoff reconciliation
repository-native validator/public-route binding only if required by the created public surface
```

### GCAT-BCAT-Engine/Publisher

```text
none required now
```

### StegVerse-002/stegguardian-wiki

```text
none required now
```

## Release/tag determination

`pyproject.toml` currently declares `1.2.0`, but `v1.2.0` is a separately prepared, exact historical successor release identity recorded in `docs/SDK_1_2_0_SUCCESSOR_RELEASE_MIRROR_HANDOFF.md` and must not be moved to current `main` or PR #138. PR #138 adds a new public CLI capability; any release carrying it requires a successor version/release candidate rather than retargeting `v1.2.0`.

Post-completion verification issue #139 exists to audit pertinent propagation to Site, Publisher, admissibility-wiki, and stegGuardian after the SDK completion/release decision.

## Next machine continuation

```text
1. Require PR #138 exact-head source/package/public-submission validation PASS.
2. Reconcile README wording if it still implies anonymous access to private governed-test dependencies.
3. Merge PR #138 only after exact-head validation passes.
4. Record merge SHA and exact successful workflow runs here and in issue #137.
5. Close consolidated SDK-local subtasks into issue #137 rather than proliferating parallel completion work.
6. Prepare a successor release identity; never retarget v1.2.0.
7. Run issue #139 downstream propagation audit after the release decision.
```

## Status

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
SDK completion overlay: ACTIVE_SDK_COMPLETION_GATE_PR_138
SDK package completion: PR_138_VALIDATION_PENDING
public external-framework preparation: IMPLEMENTED_PR_138
canonical governed execution path: IMPLEMENTED_REQUIRES_CANONICAL_PRIVATE_DEPENDENCY_ENVIRONMENT
hosted Site submission UI: DOWNSTREAM_NOT_SDK_BLOCKER
manual user work: NONE
```
