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

This handoff is the current source of truth for processor-generic downstream propagation and public governed-runtime distribution remediation.

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
merge commit: 4e1942b487972874ce310f4a9ec031f529fa1f09
one-command surface: stegverse external-run
public preparation mode: --prepare-only
public submission schema: stegverse.sdk.external-framework-submission.v1
executed run schema: stegverse.sdk.external-framework-run.v1
```

The merged SDK package preserves source-native data, evaluator preregistration outside the governance decision request, declared processor/route binding, caller-selected return projection, fail-closed unsupported routing, canonical `manifest_receipt_id`, replay, and reconstruction.

## Public runtime distribution remediation

The earlier repository-source installation boundary has been materially remediated without making private source repositories public.

```text
StegCore source/import namespace: stegcore
StegCore public distribution: stegverse-stegcore
StegCore distribution version targeted by SDK: 0.3.0
StegCore distribution rename PR: StegVerse-Labs/StegCore#197 MERGED
StegCore merge: 9a35f39b3425a2c3e9592a03b0362a417094b809
StegCore README public-install documentation: COMPLETE

Master Records public distribution: stegverse-master-records
Master Records version targeted by SDK: 0.2.0
Master Records exact frozen release candidate: c524b1a0c1a43e49c70faeac7b67f78c5908e4e4
Master Records source parent: 03312236c115bc814024d700810391340648601f
Master Records Trusted Publishing PR: master-records/orchestration#85 MERGED
Master Records README public-install documentation: COMPLETE

SDK governed-test dependency branch: public-runtime-package-dependencies
SDK PR: StegVerse-org/StegVerse-SDK#163 DRAFT
SDK exact current branch head after README correction: b229a7a93a59bdd93e134ed1e219e482a81aefb1
SDK dependency identities:
  stegverse-stegcore==0.3.0
  stegverse-master-records==0.2.0
  stegverse-core-lite @ public source commit 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
SDK README stale public-repository wording: CORRECTED
```

StegCore PR #197 exact-head package identity validation and publish-build validation passed before merge. Master Records has the release-bound Trusted Publishing workflow and registered publisher path, but the exact immutable 0.2.0 release is not yet observed as published.

## Anonymous governed-runtime installation gate

SDK PR #163 contains `.github/workflows/anonymous-governed-test-install.yml`. It strips GitHub credentials, anonymously materializes the SDK PR source, installs `.[governed-test]`, verifies distribution identities, executes ELAN Test 1 through `stegverse external-run`, and then requires Master Records custody, replay, and reconstruction evidence.

Latest exact-head observation:

```text
head: b229a7a93a59bdd93e134ed1e219e482a81aefb1
Anonymous Governed Runtime Install: run 34329494516 FAILURE
failure step: Install complete governed test with no private-repository credential
package identity verification: SKIPPED after install failure
ELAN Test 1 execution: SKIPPED after install failure
complete governed result verification: SKIPPED after install failure
```

This is the expected current failure mode while the exact PyPI distributions are not yet authentically published. The branch's package/artifact, evaluator-console, manifest-builder, MCP, output-boundary, portable-package, production-manifold, and related SDK validations passed on the same head. Do not weaken the anonymous-install gate or convert publication absence into a false PASS.

## Release boundary

The separately frozen SDK `v1.2.0` identity remains immutable and must not be retargeted to moving `main`, PR #138, or PR #163.

A post-1.2.0 successor release identity must be coherent across:

```text
pyproject.toml
VERSION.json
release notes
TVC successor release policy
exact immutable tag/release coordinate
Trusted Publisher/PyPI provenance
```

Changing only `pyproject.toml` is not an acceptable release decision. Actual package publication remains subject to the canonical TV/TVC release gate; source validation, GitHub merge, Trusted Publisher registration, or this chat session do not fabricate a GRANTED release authorization.

## Reproducible ELAN Test 1 assets

```text
inspection/examples/elan-relational-state-test1.json
inspection/examples/elan-governance-request.example.json
inspection/examples/elan-evaluation-declaration-test1.json
docs/ELAN_TEST1_RUNBOOK.md
stegverse/external_framework_runner.py
tests/test_external_framework_runner.py
.github/workflows/external-framework-e2e-validation.yml
.github/workflows/anonymous-governed-test-install.yml
```

## Downstream disposition

### StegVerse-Labs/Site

```text
pertinent: YES
required propagation: align the Site SDK preview/backend-facing manifest description with processing.capability, processing.route_id, processor-specific extensions, return_projection, manifest_receipt_id, and the portable submission boundary
implementation boundary: Site remains preview/submission UI; no processor, evaluator, receipt, custody, or route authority
tracking: StegVerse-org/StegVerse-SDK issue #129
current Site state: OBSERVED_BLOCKED
external_tasks_allowed: false
external_session_ownership_allowed: false
admitted task count for this propagation: 0
Conectrr contamination sub-blocker: RESOLVED_VALIDATED_DEPLOYED
completion predicate: FALSE
```

Site/public UI completion remains Site-owned. Do not collide with its machine-owned task lane.

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
transfer comment: #65 issuecomment-5592480056
public-route constraint transfer: #65 issuecomment-5593234328
worker-owned completion transition observed: false
completion predicate: FALSE
```

Do not duplicate Worker D's owned implementation lane.

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
dedicated processor-generic public route: NOT YET OBSERVED
```

## Remaining work by destination

### StegVerse-org/StegVerse-SDK

```text
PR #163: keep draft until exact public runtime distributions exist and anonymous install + ELAN E2E passes
release/version: define coherent post-v1.2.0 successor identity without retargeting v1.2.0
README stale dependency wording: COMPLETE
```

### StegVerse-Labs/StegCore

```text
public distribution rename: COMPLETE_MERGED
README maintenance: COMPLETE
exact immutable publication: pending canonical release gate
```

### master-records/orchestration

```text
Trusted Publishing workflow: COMPLETE_MERGED
README maintenance: COMPLETE
0.2.0 frozen release candidate: c524b1a0c1a43e49c70faeac7b67f78c5908e4e4
exact immutable publication: pending canonical release gate
```

### StegVerse-Labs/Site

```text
docs/ECOSYSTEM_CHAT_SDK_BACKEND_HANDOFF.md
fixtures/ecosystem-chat/sdk-form-payload.example.json only if stale
fixtures/ecosystem-chat/sdk-backend-response.example.json only if stale
associated Site SDK checker/schema only if required by admitted Site-owned mutation
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

## Current status

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE / DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
SDK package generic-manifest completion: COMPLETE_VALIDATED_MERGED_PR_138
StegCore public distribution rename: COMPLETE_MERGED
Master Records Trusted Publishing support: COMPLETE_MERGED
SDK governed-test public distribution dependency rewrite: IMPLEMENTED_IN_DRAFT_PR_163
SDK README stale dependency claim: CORRECTED
anonymous governed-runtime install: BLOCKED_PENDING_EXACT_PYPI_RELEASES
Site completion predicate: FALSE / MACHINE_OWNED
admissibility completion predicate: FALSE / WORKER_OWNED
manual user work: NONE
```
