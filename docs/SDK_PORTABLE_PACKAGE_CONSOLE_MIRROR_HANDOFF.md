# SDK Portable Package Console Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
credential_authority: TV/TVC
GitHub_token_runtime_authority: NONE
non-TV/TVC_secret_required: FALSE
```

This handoff owns the SDK-facing distribution/install surface for portable StegVerse S and NS Micro-Ecosystems. It does not own canonical StegGate evaluation, Node Sovereign membership authority, or StegFin economic authority.

## Completed source goal

`SDK-PORTABLE-PACKAGE-CONSOLE-001`

```text
source_implementation: COMPLETE
focused_tests: PASS 9/9
credential_free_source_validation: PASS
merged: TRUE
merge_commit: 92c11583ee6e78fb2bcc1816776af58fcbc4282b
source_PR: #34
remote_download_active: FALSE
exact_release_artifacts_bound: FALSE
```

The focused validation first exposed one compatibility defect: the repository's lightweight pytest runner did not support `capsys`. The test was repaired to use standard-library stdout capture; the replacement exact-head portable-package source validation then passed.

## Installed console capability

Public commands:

```text
stegverse-portable list
stegverse-portable inspect --deployment-class S|NS
stegverse-portable verify --archive <package.zip>
stegverse-portable install --archive <package.zip> --destination <directory>
stegverse-portable download --deployment-class S|NS --output <path>
```

Current behavior:

```text
list: ACTIVE
inspect: ACTIVE
verify: ACTIVE
install: ACTIVE_NON_EXECUTING
download: FAIL_CLOSED_NO_GOVERNED_RELEASE_ARTIFACT
```

`download` is intentionally present but inactive until an exact immutable artifact locator and expected archive SHA-256 are bound. No mutable `latest` URL or guessed release location is accepted.

## Required deployment choice

```text
S  = StegVerse S Ecosystem / Sovereign
NS = StegVerse NS Ecosystem / Node Sovereign profile
```

There is no default.

Installing NS does not create Node Sovereign membership.

## Verification / install contract

Before installation the console verifies:

1. `PACKAGE_RECEIPT.json` exists and has the supported schema;
2. package ID matches the selected S/NS class;
3. every declared file hash and size matches;
4. no undeclared archive members exist;
5. no path traversal or duplicate archive members exist;
6. no provider-account requirement is present;
7. no non-TV/TVC-secret requirement is present;
8. no package claims installation confers Node Sovereign membership;
9. NS retains separate membership activation requirement.

Installation:

```text
verification first
-> safe extraction to a new target
-> INSTALLATION_RECEIPT.json
-> state INSTALLED_NOT_ACTIVATED
-> executed_after_install=false
-> node_membership_granted=false
```

## Authority boundary

```text
SDK package download != governance authority
SDK package install != activation
SDK package install != Node Sovereign membership
NS profile selection != Node Sovereign membership
package verification != StegGate ALLOW
package source identity != execution authority
GitHub/release hosting != runtime authority
wallet signing authority: USER_ONLY
broadcast authority: USER_ONLY
protected credential authority: TV/TVC
```

## Canonical producer relationship

Package production belongs to:

```text
StegVerse-Labs/StegCore
merge: 1cdd479a8c50a61cda9a236fc05b126592362fff
sdk/portable_package_catalog.v1.json
tools/build_portable_ecosystem_package.py
docs/STEGVERSE_SDK_PORTABLE_DISTRIBUTION.md
```

StegCore's successor package goal is `STEGVERSE-PORTABLE-ARTIFACT-002`.

## Early-adopter/community role

The SDK is intentionally the first distribution channel so ordinary users, developers, beta testers, researchers, and future Node Sovereign operators can use the portable units before later app/product promotion.

Lifecycle:

```text
SDK_EARLY_ACCESS
-> SDK_COMMUNITY
-> APP_PRODUCT_CANDIDATE
-> PAID_PRODUCT_CANDIDATE
```

Promotion timing is evidence-driven, not hardcoded.

Verified useful community contribution may later flow into StegFin provisional contribution accounting. Installation, enrollment, passive holding, traffic generation, or self-created identities are not rewardable work by themselves.

## Completion states

```text
HANDOFF_INSTALLED: COMPLETE
PORTABLE_CATALOG_INSTALLED: COMPLETE
LOCAL_VERIFY_IMPLEMENTED: COMPLETE
LOCAL_INSTALL_IMPLEMENTED: COMPLETE
DOWNLOAD_FAIL_CLOSED_WITHOUT_RELEASE: COMPLETE
CONSOLE_ENTRYPOINT_WIRED: COMPLETE
FOCUSED_TESTED: COMPLETE
HOSTED_SOURCE_VALIDATED: COMPLETE
MERGED: COMPLETE
RELEASE_ARTIFACT_BOUND: PENDING
DOWNLOAD_ACTIVE: PENDING
SDK_EARLY_ACCESS_RELEASED: PENDING
```

Do not collapse these states.

## Successor goal

`SDK-PORTABLE-ARTIFACT-BINDING-002`

Acceptance:

```text
exact immutable S artifact locator exists
exact immutable NS artifact locator exists
expected archive SHA-256 values are retained
catalog binds exact artifact + hash
console download verifies archive hash
console package verifier passes downloaded artifact
console install emits INSTALLED_NOT_ACTIVATED
NS downloaded/installed package still grants no membership
no provider account required
no non-TV/TVC secret required
```

## Remaining work

1. Consume exact immutable S/NS artifacts produced by StegCore Goal `STEGVERSE-PORTABLE-ARTIFACT-002`.
2. Bind artifact locators and hashes into the SDK package catalog.
3. Validate public download -> verify -> install for both S and NS.
4. Keep NS membership activation separate.
5. Preserve early-access/community usage evidence for product lifecycle decisions.
6. Coordinate verified contribution receipts with StegFin without rewarding installation alone.
7. At actual release readiness, reconcile Site, Publisher, admissibility-wiki, and stegguardian-wiki under their own handoffs.

## Current claim

```yaml
completed_task: SDK-PORTABLE-PACKAGE-CONSOLE-001
completed_commit: 92c11583ee6e78fb2bcc1816776af58fcbc4282b
active_successor_goal: SDK-PORTABLE-ARTIFACT-BINDING-002
claim_state: SUCCESSOR_WORK_ACTIVE
parallel_safety: WAITING_ON_EXACT_STEGCORE_ARTIFACTS_FOR_REMOTE_BINDING
credential_authority: TV/TVC
```
