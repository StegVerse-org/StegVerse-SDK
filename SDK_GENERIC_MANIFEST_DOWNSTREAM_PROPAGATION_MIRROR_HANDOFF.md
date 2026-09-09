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

This handoff is the current source of truth for processor-generic downstream propagation and records the completed SDK package gate from issue #137 / PR #138.

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

## SDK package completion evidence

```text
completion issue: StegVerse-org/StegVerse-SDK#137
completion PR: StegVerse-org/StegVerse-SDK#138 MERGED
validated PR head: 163703afcb246ac697fea860bd1f23f20ed6662d
merge commit: 4e1942b487972874ce310f4a9ec031f529fa1f09
one-command surface: stegverse external-run
public preparation mode: --prepare-only
public submission schema: stegverse.sdk.external-framework-submission.v1
executed run schema: stegverse.sdk.external-framework-run.v1
```

Exact PR-head PASS evidence:

```text
Manifest Builder Source Validation: run 34308291805 PASS
Evaluator Contract Console Validation: run 34308291869 PASS
Generic Manifest Downstream Contract Validation: run 34308291808 PASS
External Framework Public Submission Validation: run 34308291802 PASS
SDK Package Artifact Validation: run 34308291902 PASS
```

The SDK package now provides one external-framework path that preserves source-native data, retains evaluator preregistration outside the governance decision request, binds the declared installed governance route, preserves caller-selected return projection, fails closed on invalid processor/route evidence, requires a canonical `manifest_receipt_id` after governed execution, and supports replay plus reconstruction from that receipt.

The credential-free `--prepare-only` path emits the exact validated portable submission bundle using public SDK dependencies only. It does not claim execution or fabricate a receipt.

## Canonical runtime dependency boundary

An attempted anonymous governed-runtime CI installation established a real distribution boundary: pinned StegCore and Master Records dependencies are currently private repositories, while Core-Lite is public. The SDK therefore does not claim that arbitrary anonymous callers can locally install the complete canonical governed runtime today.

```text
PUBLIC_EXTERNAL_SUBMISSION_PREPARATION: COMPLETE_VALIDATED_MERGED
CANONICAL_GOVERNED_EXECUTION_ORCHESTRATION: COMPLETE_VALIDATED_MERGED
ANONYMOUS_INSTALL_OF_PRIVATE_CANONICAL_RUNTIME_DEPS: NOT_AVAILABLE_BY_CURRENT_REPOSITORY_VISIBILITY
```

No private repository is to be made public, copied into the SDK, or exposed merely to make anonymous CI pass without a separate explicit repository-visibility/release decision.

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

## Durable continuation evidence

```text
source correction: StegVerse-org/StegVerse-SDK PR #126 COMPLETE_VALIDATED_MERGED
assessment: StegVerse-org/StegVerse-SDK PR #127 MERGED
continuation task registration: StegVerse-org/StegVerse-SDK PR #128 MERGED
ownership reconciliation: StegVerse-org/StegVerse-SDK PR #130 MERGED
COSV registration: StegVerse-Labs/.github PR #1184 MERGED
COSV ownership reconciliation: StegVerse-Labs/.github PR #1185 MERGED
SDK completion issue: StegVerse-org/StegVerse-SDK issue #137 COMPLETION_READY_TO_CLOSE
SDK completion PR: StegVerse-org/StegVerse-SDK PR #138 MERGED @ 4e1942b487972874ce310f4a9ec031f529fa1f09
post-completion propagation audit: StegVerse-org/StegVerse-SDK issue #139 OPEN
Site dependency tracker: StegVerse-org/StegVerse-SDK issue #129 OPEN_TRACKING_ONLY
Site Conectrr remediation issue: StegVerse-Labs/Site issue #1143 RESOLVED
Site Conectrr remediation PR: StegVerse-Labs/Site PR #1150 MERGED @ 1260262ba6ab7198b20bf5a04a93264089e203da
Site Conectrr exact validated head: 45f4085cd0cd7ad99ed20bb6d0b9cea2d8184db0
Site Conectrr controller completion: e6991ed197cdde8fc78b62b879ba35165241253b
Site Conectrr clean public observation: StegVerse-Labs/Site#1143#issuecomment-5598275109
SDK Site evidence mirror: StegVerse-org/StegVerse-SDK#129#issuecomment-5598277562
admissibility coordinator: StegVerse-Labs/admissibility-wiki issue #66
admissibility implementation owner: StegVerse-Labs/admissibility-wiki issue #65 / Worker D
```

## Resolved Site Conectrr contamination sub-blocker

`SITE-CONECTRR-GOVERNANCE-CONTAMINATION-001` is resolved. Site PR #1150 removed default Conectrr fixture execution from ordinary Ecosystem Chat sessions while retaining explicit `?conectrr-fixture=1` test/demo execution. The rebased exact head `45f4085cd0cd7ad99ed20bb6d0b9cea2d8184db0` passed Site Handoff run `34317414408`, Bootstrap/application run `34317414402`, Heartbeat run `34317414414`, Canonical Gateway observation run `34317414404`, and gateway-binding run `34317414395`. The Site repository controller then advanced the task COMPLETE at `e6991ed197cdde8fc78b62b879ba35165241253b` with default loader and default fixture execution disabled.

Authentic post-deploy evidence was supplied as a Safari `.webarchive` of `https://stegverse.org/ecosystem-chat.html` captured at approximately `2026-09-09T07:52:51Z`–`2026-09-09T07:52:59Z`. The governed stream contained an ordinary `What time Is it?` interaction and contained neither `event:conectrr:handoff:001` nor `event:stegverse:evaluation:001`; no `Conectrr`/`conectrr` text appeared. This closes the contamination sub-blocker only; it does not satisfy the separate Site generic-SDK-surface completion predicate.

## Downstream disposition

### StegVerse-Labs/Site

```text
pertinent: YES
required propagation: align the Site SDK preview/backend-facing manifest description with processing.capability, processing.route_id, processor-specific extensions, return_projection, manifest_receipt_id, and the portable submission boundary
implementation boundary: Site remains preview/submission UI; no processor, evaluator, receipt, custody, or route authority
tracking: StegVerse-org/StegVerse-SDK issue #129
Conectrr contamination sub-blocker: RESOLVED_VALIDATED_DEPLOYED
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
```

### StegVerse-002/stegguardian-wiki

```text
pertinent: NO_DIRECT_CONTRACT_CHANGE
reason: Guardian consumes bounded downstream interpretation after upstream evidence; it does not consume SDK ingress manifests directly
action: preserve non-enforcement boundaries; do not duplicate processor semantics
```

## Publicly displayed surfaces

```text
canonical public domain: https://stegverse.org/
current Ecosystem Chat observation: https://stegverse.org/ecosystem-chat.html
```

No dedicated processor-generic hosted submission route is claimed until Site creates, deploys, and validates an actual `https://stegverse.org/...` route. The SDK package/CLI does not depend on that hosted UI.

## Remaining files/modules by destination

### StegVerse-org/StegVerse-SDK

```text
README wording still contains a stale statement that governed-test dependencies are public and should be corrected in a successor documentation/release change.
release/version decision must not reuse or retarget the separately prepared v1.2.0 identity.
```

### StegVerse-Labs/Site

```text
docs/ECOSYSTEM_CHAT_SDK_BACKEND_HANDOFF.md
fixtures/ecosystem-chat/sdk-form-payload.example.json only if stale
fixtures/ecosystem-chat/sdk-backend-response.example.json only if stale
associated Site SDK checker/schema only if required by admitted Site-owned mutation
```

The Conectrr fixture-contamination remediation is no longer remaining work.

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

`pyproject.toml` declares `1.2.0`, but `v1.2.0` is a separately prepared exact successor release identity recorded in `docs/SDK_1_2_0_SUCCESSOR_RELEASE_MIRROR_HANDOFF.md` and must not be moved to current `main` or PR #138. PR #138 adds a new public CLI capability, so any release carrying it requires a successor version/release candidate rather than retargeting `v1.2.0`.

Post-completion verification issue #139 exists to audit pertinent propagation to Site, Publisher, admissibility-wiki, and stegGuardian after the successor release decision.

## Status

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
SDK package completion: COMPLETE_VALIDATED_MERGED_PR_138
Site Conectrr contamination sub-blocker: RESOLVED_VALIDATED_DEPLOYED
public external-framework preparation: COMPLETE_VALIDATED_MERGED
canonical governed execution orchestration: COMPLETE_VALIDATED_MERGED
anonymous canonical runtime dependency installation: NOT_AVAILABLE_BY_CURRENT_PRIVATE_REPOSITORY_VISIBILITY
hosted Site submission UI: DOWNSTREAM_NOT_SDK_PACKAGE_BLOCKER
manual user work: NONE
```
