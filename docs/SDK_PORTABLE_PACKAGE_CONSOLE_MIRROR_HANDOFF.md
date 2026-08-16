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

This is the canonical continuation record for the SDK-facing distribution, release-index, verification, and installation surface for portable StegVerse S and NS ecosystems. Live repository state, release records, TVC publication receipts, and current claims supersede historical chat or stale PR references.

## Active goal

```text
goal_id: SDK-PORTABLE-ARTIFACT-BINDING-002
originating_goal: expose automatically versioned portable StegVerse releases at the SDK entry point and bind exact immutable S/NS ZIP/TAR.GZ artifacts without transferring runtime, governance, node-membership, wallet, or credential authority to GitHub or the SDK
canonical_owner: StegVerse-org/StegVerse-SDK
upstream_producer: StegVerse-Labs/StegCore
publication_authority: StegVerse-Labs/TVC
current_claim_state: DISTINCT_CONSUMER_WAITING_ON_CANONICAL_TVC_PUBLICATION
active_implementation_claim: NONE
active_validation_claim: NONE
```

## Completed producer/source chain

Canonical StegCore producer state:

```text
source_merge: cbbe8a0046bc23844d2d8a4baeea9eeb4e11996a
source_workflow: Portable Release Candidate - Build Only / TV-TVC Publication Authority
source_workflow_run: 31926374208 / SUCCESS
source_artifact_id: 9257951032
source_artifact_name: stegverse-portable-release-candidate-v0.2.0-cbbe8a0046bc23844d2d8a4baeea9eeb4e11996a
source_artifact_digest: sha256:ffac18929f2f9dca7fabc124fc9d3245e2641cef45f4a2f3a3a937a5f647f709
release_version: 0.2.0
publication_state: CANDIDATE_NOT_PUBLISHED
publication_authority: TV/TVC
```

The producer creates deterministic S and NS packages in both ZIP and TAR.GZ, emits independent hashes plus `SHA256SUMS`, records component versions and a component-version fingerprint, and requires a new overall release when a declared versioned component changes. Stable package families are versioned in filenames rather than embedding a prototype generation into the family identity.

A later duplicate-compatible StegCore merge `716667e80b1b99ebbcec84ac6dabc5e3d24e4c33` introduced no file delta relative to `cbbe8a...`; canonical source evidence remains the earlier `cbbe8a...` candidate and TVC handoff. Superseded/duplicate branches must not create competing publication candidates.

## Completed SDK implementation

Initial console and sovereignty implementation is complete. The current version-contract reconciliation is also complete:

```text
initial_console_PR: #34
initial_console_merge: 92c11583ee6e78fb2bcc1816776af58fcbc4282b
single_host_validation_head: 67dfa4f80d9e5d9e0105dfb75bbfe0217827bb8e
single_host_validation_run: 31926083091 / SUCCESS
superseded_version_PR: #38 CLOSED
canonical_version_PR: #39 MERGED
canonical_version_head: 993bb172d8369e44448a2420419a0f54b89af108
canonical_version_merge: bee2b903bfa31ef0a3af3edda5d5bc5f5fa34099
portable_package_source_run: 31927711993 / SUCCESS
portable_release_index_run: 31927711997 / SUCCESS
```

Current public commands:

```text
stegverse-portable list
stegverse-portable inspect --deployment-class S|NS
stegverse-portable verify --archive <versioned-package.zip|versioned-package.tar.gz>
stegverse-portable install --archive <versioned-package.zip|versioned-package.tar.gz> --destination <directory>
stegverse-portable download --deployment-class S|NS --format zip|tar.gz --output <path>
stegverse-versions [--complete-only]
```

Current package contract:

```text
receipt_schema: stegverse.sdk.portable-package-receipt.v3
stable S family:  stegverse-sdk-s-micro-ecosystem
stable NS family: stegverse-sdk-ns-micro-ecosystem
package_version: explicit semantic version
release_version: explicit semantic version
versioned_package_id: <stable-family>-v<package_version>
archive_name: <versioned_package_id>.zip | <versioned_package_id>.tar.gz
installation_target: versioned_package_id
```

`stegverse-versions` consumes the canonical public `StegVerse-Labs/StegCore` GitHub Releases API and exposes release version plus S/NS component package versions. A release is complete only when both S and NS have version-consistent ZIP and TAR.GZ asset pairs. Public release discovery has authority effect `NONE` and returns `UNAVAILABLE_NON_AUTHORIZING` on public-index unavailability rather than inventing release state.

## Required deployment choice and sovereignty contract

```text
S  = StegVerse S Ecosystem / Sovereign
NS = StegVerse NS Ecosystem / Node Sovereign profile
```

There is no default. Installation does not activate either class and NS installation does not create Node Sovereign membership.

Every accepted package must independently prove in both `PACKAGE_RECEIPT.json` and embedded `micro_ecosystem/manifest.json`:

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

Missing, mismatched, weakened, unversioned, or filename-inconsistent declarations fail closed before installation.

## Authority boundary

```text
SDK package download != governance authority
SDK package install != activation
SDK package install != Node Sovereign membership
NS profile selection != Node Sovereign membership
package verification != StegGate ALLOW
package source identity != execution authority
GitHub release hosting != runtime authority
GitHub Actions != sovereign deployment or publication authority
one-host logical isolation proof != Node Sovereign membership
wallet signing authority: USER_ONLY
broadcast authority: USER_ONLY
protected credential authority: TV/TVC
non-TV/TVC secret/token: PROHIBITED
Render production dependency: PROHIBITED
```

## Canonical TVC publication continuation

Permanent publication is not an SDK implementation task. It is owned by:

```text
StegVerse-Labs/TVC/docs/PORTABLE_ARTIFACT_PUBLICATION_MIRROR_HANDOFF.md
task: TVC-PORTABLE-ARTIFACT-PUBLICATION-001
source artifact: StegCore 9257951032
canonical machine owner: TVC repository heartbeat / sole-host StegVerse control plane
```

Current TVC blocker is machine-owned and explicit:

```text
state: BLOCKED_DEPENDENCY
reason: TVC_MANAGED_EPHEMERAL_PUBLICATION_CAPABILITY_NOT_PRESENT
non-TV/TVC credential workaround: PROHIBITED
```

Release condition: the TVC-managed sole-host lane materializes exact private TVC source and exact StegCore candidate, validates it, emits `CANDIDATE_ADMITTED`, performs authorized immutable publication, and verifies exact public locators/hashes.

## SDK successor execution after publication

When TVC emits a verified immutable publication receipt, the SDK task is:

```text
exact S ZIP/TAR.GZ public locators + hashes
-> release-index observation
-> download exact artifact
-> hash verification
-> package receipt + embedded sovereignty verification
-> install
-> INSTALLED_NOT_ACTIVATED
-> NS membership remains false unless separately admitted
```

No mutable `latest` URL is authoritative. No provider account or non-TV/TVC secret is required.

## Cross-repository continuation

```text
StegVerse-Labs/StegCore cbbe8a0046bc23844d2d8a4baeea9eeb4e11996a
-> StegVerse-Labs/TVC TVC-PORTABLE-ARTIFACT-PUBLICATION-001
-> StegVerse-org/StegVerse-SDK SDK-PORTABLE-ARTIFACT-BINDING-002
```

At actual release readiness, re-read current handoffs before propagation to `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-002/stegguardian-wiki`. No propagation is currently claimed.

## Validation commands

```text
python -m pytest tests/test_portable_packages.py tests/test_portable_dual_archive.py -q
python -m pytest tests/test_release_index.py -q
```

## Session consolidation

Transferred requirements from the originating session:

1. portable ZIP and TAR.GZ generation is generalized beyond StegOS;
2. declared component-version change requires a new release version rather than replacing same-version assets;
3. S and NS remain explicit deployment choices;
4. package family identity is stable and package/release versions are explicit;
5. GitHub may build/distribute but does not gain runtime or publication authority;
6. TV/TVC owns protected credential and publication authority;
7. no non-TV/TVC secret/token may enter the canonical path;
8. SDK version inventory derives automatically from immutable GitHub Releases rather than requiring a cross-repository catalog commit;
9. installation is separate from activation and NS installation is separate from node admission.

All nine are installed or durably transferred. Remaining publication and immutable binding are machine/dependency owned and require no duplicate SDK implementation while the TVC claim remains active.

MERGED INTO: `StegVerse-Labs/TVC/docs/PORTABLE_ARTIFACT_PUBLICATION_MIRROR_HANDOFF.md` -> `StegVerse-org/StegVerse-SDK/docs/SDK_PORTABLE_PACKAGE_CONSOLE_MIRROR_HANDOFF.md`.

## Completion accounting

```text
required SDK developed files for current consumer contract: 5
current developed files: 5/5
scaffolding/stubs: 0
missing required files: 0
source validation: 2/2 exact-head workflows PASS
source integration: COMPLETE / merge bee2b903...
release publication integration: PENDING_TVC_MACHINE_OWNER
public immutable download binding: PENDING_TVC_PUBLICATION
session requirements transferred-or-complete: 9/9
SDK source goal activation: COMPLETE
SDK artifact-binding goal activation: PENDING_UPSTREAM_PUBLICATION
```

## Archive condition

This SDK workstream no longer has an implementation claim. It remains a distinct consumer waiting on canonical TVC publication. A new SDK mutation is permitted only after an immutable TVC publication receipt exists or a directly observed producer/consumer incompatibility creates a bounded corrective task.
