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
physical_host_topology: ONE_SOVEREIGN_PHYSICAL_HOST
additional_physical_machine_required: FALSE
third_party_runtime_infrastructure_required: FALSE
```

This handoff owns the SDK-facing distribution/install surface for portable StegVerse S and NS Micro-Ecosystems. It does not own canonical StegGate evaluation, Node Sovereign membership authority, permanent artifact publication authority, or StegFin economic authority.

## Completed source goal

`SDK-PORTABLE-PACKAGE-CONSOLE-001`

```text
source_implementation: COMPLETE
credential_free_source_validation: PASS
merged: TRUE
merge_commit: 92c11583ee6e78fb2bcc1816776af58fcbc4282b
source_PR: #34
single_host_sovereignty_enforcement: COMPLETE_VALIDATED
portable_receipt_v2_v3_compatibility: COMPLETE_VALIDATED
remote_download_active: FALSE
exact_release_artifacts_bound: FALSE
```

## Single-host sovereignty consumer contract

The SDK now refuses any portable archive that turns a StegVerse deployment into infrastructure dependent on another physical machine or required third-party runtime service.

Accepted package receipts are currently:

```text
stegverse.sdk.portable-package-receipt.v2
stegverse.sdk.portable-package-receipt.v3
```

Both versions are accepted only when `PACKAGE_RECEIPT.json` and the embedded `micro_ecosystem/manifest.json` independently agree on the exact contract:

```text
physical_host_topology: ONE_SOVEREIGN_PHYSICAL_HOST
additional_physical_machine_required: false
third_party_machine_required: false
third_party_process_host_required: false
third_party_scheduler_required: false
third_party_state_host_required: false
third_party_control_plane_executor_required: false
third_party_platform_availability_may_block_local_operation: false
independent_validation_mechanism: SAME_HOST_ISOLATED_LOGICAL_BOUNDARIES
local_governance_replay_reconstruction_survive_third_party_absence: true
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
```

The embedded StegCore authority boundary must also say:

```text
requires_external_host: false
requires_additional_physical_machine: false
requires_third_party_runtime_infrastructure: false
```

Missing, mismatched, or weakened declarations fail closed before installation.

External providers, blockchains, sites, and other nodes may remain optional participants/inputs. They cannot become required infrastructure for the portable deployment's local governance, verification, replay, reconstruction, or control-plane operation.

## Installed console capability

Public commands:

```text
stegverse-portable list
stegverse-portable inspect --deployment-class S|NS
stegverse-portable verify --archive <package.zip|package.tar.gz>
stegverse-portable install --archive <package.zip|package.tar.gz> --destination <directory>
stegverse-portable download --deployment-class S|NS --format zip|tar.gz --output <path>
```

Current behavior:

```text
list: ACTIVE
inspect: ACTIVE
verify: ACTIVE_SINGLE_HOST_FAIL_CLOSED
install: ACTIVE_NON_EXECUTING
download: FAIL_CLOSED_NO_GOVERNED_RELEASE_ARTIFACT
```

`download` remains intentionally inactive until an exact immutable artifact locator and expected archive SHA-256 are bound. No mutable `latest` URL or guessed release location is accepted.

## Required deployment choice

```text
S  = StegVerse S Ecosystem / Sovereign
NS = StegVerse NS Ecosystem / Node Sovereign profile
```

There is no default. Both classes retain the one-physical-host sovereignty requirement. Installing NS does not create Node Sovereign membership.

## Verification / install contract

Before installation the console verifies:

1. `PACKAGE_RECEIPT.json` exists and uses supported v2/v3 schema;
2. package ID matches S/NS class;
3. every declared file hash and size matches;
4. no undeclared archive members exist;
5. no path traversal or duplicate archive members exist;
6. no provider-account requirement exists;
7. no non-TV/TVC-secret requirement exists;
8. no package claims installation confers Node Sovereign membership;
9. NS retains separate membership activation requirement;
10. receipt single-host sovereignty contract is complete;
11. embedded StegCore manifest single-host contract is complete;
12. receipt and embedded manifest sovereignty contracts match exactly;
13. no additional physical machine is required;
14. no third-party machine/process/scheduler/state/control-plane executor is required;
15. third-party platform availability cannot block declared local operation.

Installation remains:

```text
verification first
-> safe extraction to a new target
-> INSTALLATION_RECEIPT.json
-> state INSTALLED_NOT_ACTIVATED
-> executed_after_install=false
-> node_membership_granted=false
-> physical_additional_machine_required=false
-> third_party_runtime_infrastructure_required=false
```

## Validation evidence

Single-host enforcement commits on `main`:

```text
5274f721669a69e4074f134d85627ddffef53b43  enforce receipt + embedded manifest sovereignty
ab822cff7a22ef7df1873036c8ca809512eccaa9  fail-closed single-host test coverage
7272c8cc87e3b32d86f9f16004bb1fa5edbcd554  dual archive v2 fixture propagation
3e2c1818a3b7b260357df05d1b3f779248d31cf8  push-enabled credential-free validation gate
edb5fd85224f5df4aa3f31cb88fdc9fc185f7ca3  accept producer v3 under same contract
67dfa4f80d9e5d9e0105dfb75bbfe0217827bb8e  prove v2/v3 compatibility
```

Canonical validation:

```text
workflow: Portable Package Source Validation - No Credential Authority
run: 31926083091
head: 67dfa4f80d9e5d9e0105dfb75bbfe0217827bb8e
conclusion: SUCCESS
```

That run uses anonymous public source materialization, no runtime credential authority, focused v2/v3/ZIP/TAR.GZ tests, and explicit non-authorizing console assertions. GitHub Actions remains validation-only.

## Authority boundary

```text
SDK package download != governance authority
SDK package install != activation
SDK package install != Node Sovereign membership
NS profile selection != Node Sovereign membership
package verification != StegGate ALLOW
package source identity != execution authority
GitHub/release hosting != runtime authority
GitHub Actions validation != sovereign deployment
one-host logical isolation proof != Node Sovereign membership
wallet signing authority: USER_ONLY
broadcast authority: USER_ONLY
protected credential authority: TV/TVC
```

## Canonical producer relationship

Package production belongs to:

```text
StegVerse-Labs/StegCore
docs/STEGVERSE_MICRO_ECOSYSTEM_MIRROR_HANDOFF.md
sdk/portable_package_catalog.v1.json
tools/build_portable_ecosystem_package.py
```

The producer's active immutable-artifact work is `STEGVERSE-PORTABLE-ARTIFACT-002`.

### Active producer collision boundary

StegCore PR `#137` (`feat/portable-candidate-artifact-transport-v0`) is the canonical version-driven artifact-transport claimant. It advances package receipts to v3 while preserving the single-host contract. The SDK has proactively validated v3 consumption.

This SDK workstream must not duplicate PR #137's build/artifact transport or TV/TVC permanent publication role. If PR #137 is temporarily non-mergeable because its builder branch predates current StegCore main, its owner must reconcile/rebase current main while preserving the contract; that is producer integration work, not SDK publication authority.

## Early-adopter/community role

The SDK remains the first distribution channel so ordinary users, developers, beta testers, researchers, and future Node Sovereign operators can exercise portable production artifacts before later app/product promotion.

Lifecycle remains:

```text
SDK_EARLY_ACCESS
-> SDK_COMMUNITY
-> APP_PRODUCT_CANDIDATE
-> PAID_PRODUCT_CANDIDATE
```

Verified useful community contribution may later flow into StegFin provisional accounting. Installation, enrollment, passive holding, traffic generation, or self-created identities are not rewardable work by themselves.

## Completion states

```text
HANDOFF_INSTALLED: COMPLETE
PORTABLE_CATALOG_INSTALLED: COMPLETE
LOCAL_VERIFY_IMPLEMENTED: COMPLETE
LOCAL_INSTALL_IMPLEMENTED: COMPLETE
SINGLE_HOST_SOVEREIGNTY_ENFORCED: COMPLETE_VALIDATED
V2_V3_RECEIPT_COMPATIBILITY: COMPLETE_VALIDATED
DOWNLOAD_FAIL_CLOSED_WITHOUT_RELEASE: COMPLETE
CONSOLE_ENTRYPOINT_WIRED: COMPLETE
HOSTED_SOURCE_VALIDATED: COMPLETE
RELEASE_ARTIFACT_BOUND: PENDING_PRODUCER_TVC
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
single-host sovereignty receipt/manifest match passes
console install emits INSTALLED_NOT_ACTIVATED
NS package still grants no membership
no provider account required
no non-TV/TVC secret required
```

## Remaining work

1. Wait on the distinct StegCore PR #137/TVC artifact-production and permanent-publication owners; do not duplicate them.
2. Consume the admitted exact S/NS immutable artifact locators and hashes when produced.
3. Validate public download -> verify -> install for both S and NS.
4. Keep NS membership activation separate.
5. Preserve early-access/community evidence for product lifecycle decisions.
6. At actual release readiness, re-read Site, Publisher, admissibility-wiki, and stegguardian-wiki handoffs before propagation.

## Current claim

```yaml
completed_task: SDK-PORTABLE-PACKAGE-CONSOLE-001 + SINGLE-HOST-SOVEREIGNTY-CONSUMER
single_host_validation_head: 67dfa4f80d9e5d9e0105dfb75bbfe0217827bb8e
active_successor_goal: SDK-PORTABLE-ARTIFACT-BINDING-002
claim_state: DISTINCT_CONSUMER_WAITING_ON_CANONICAL_PRODUCER
parallel_safety: DO_NOT_COMPETE_WITH_STEGCORE_PR_137_OR_TV_TVC_PUBLICATION
credential_authority: TV/TVC
```
