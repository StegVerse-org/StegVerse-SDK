# SDK Public Distribution Privacy Mirror Handoff

Updated: 2026-08-17T09:45:00-05:00

## Canonical authority

```text
goal_id: SDK-PUBLIC-DISTRIBUTION-PRIVACY-001
repository: StegVerse-org/StegVerse-SDK
branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
originating_goal: preserve the SDK as the public aperture while allowing implementation repositories to become private
credential_authority: TV/TVC
NON-TV/TVC secret/token authority: PROHIBITED
GitHub token runtime authority: NONE
publication_authority: StegVerse-Labs/TVC
state: ACTIVE_BLOCKED_ON_PUBLIC_DISTRIBUTION_RECONCILIATION
```

## Directly observed defect

`pyproject.toml` currently defines:

```text
[project.optional-dependencies].governed-test
  stegcore @ git+https://github.com/StegVerse-Labs/StegCore.git@083557...
  stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@72bdb0...
  stegverse-master-records @ git+https://github.com/master-records/orchestration.git@6626c6...
```

Live repository metadata observed during this goal:

```text
StegVerse-Labs/StegCore: public
Data-Continuation/core-lite: public
master-records/orchestration: private
```

Therefore the current repository-source dependency contract is inconsistent with a fully anonymous public governed-test installation path. The README statement that governed-test dependencies are pinned to public repository commits is not true for the Master Records dependency in current live metadata.

This is a distribution/privacy defect, not authority permission to make Master Records public or to use a GitHub token. It must be resolved by removing public SDK installation dependence on protected repository-source visibility.

## Required architecture

```text
public StegVerse SDK
-> immutable TVC-admitted public distribution artifacts
-> exact package hash / receipt verification
-> install locally
-> no GitHub repository credential required
-> runtime/governance authority remains local StegVerse + TV/TVC
```

Repository visibility must become irrelevant to public package acquisition.

## Existing canonical continuation to reuse

Do not create a parallel publisher.

```text
StegVerse-Labs/TVC/docs/PORTABLE_ARTIFACT_PUBLICATION_MIRROR_HANDOFF.md
  task: TVC-PORTABLE-ARTIFACT-PUBLICATION-001
  current state: BLOCKED_DEPENDENCY
  blocker: TVC_MANAGED_EPHEMERAL_PUBLICATION_CAPABILITY_NOT_PRESENT

StegVerse-org/StegVerse-SDK/docs/SDK_PORTABLE_PACKAGE_CONSOLE_MIRROR_HANDOFF.md
  goal: SDK-PORTABLE-ARTIFACT-BINDING-002
  current state: DISTINCT_CONSUMER_WAITING_ON_CANONICAL_TVC_PUBLICATION
```

## Collision boundary

Do not:

- make `master-records/orchestration` public merely to repair public SDK installation;
- use `GITHUB_TOKEN`, `GH_TOKEN`, or another non-TV/TVC credential to fetch protected source;
- duplicate StegCore, Core-Lite, Master Records, TV, TVC, publication, evaluator, or custody authority inside the SDK;
- claim StegCore/Core-Lite are safe to privatize while the SDK still fetches their repository source directly;
- claim the current governed-test extra is anonymously installable until exact evidence proves it.

## Execution ownership

```yaml
- task_id: SDK-PUBLIC-DISTRIBUTION-PRIVACY-001
  role: CLAIMED_FOR_INTEGRATION
  owner: StegVerse-org/StegVerse-SDK + StegVerse-Labs/TVC publication chain
  collision_scope: public SDK dependency acquisition and immutable artifact binding only
  release_condition: public credential-free acquisition of exact required artifacts is verified and governed-test no longer depends on repository-source visibility
  next_action: consume TVC immutable publication receipt when available; replace direct repository-source dependency assumptions with exact artifact/package binding; validate anonymous install

- task_id: TVC-PORTABLE-ARTIFACT-PUBLICATION-001
  role: MACHINE_OWNED_BLOCKED_DEPENDENCY
  owner: StegVerse-Labs/TVC repository heartbeat / sole-host StegVerse control plane
  release_condition: TVC-managed publication capability materializes exact private source and exact candidate, validates, publishes immutable artifacts, and verifies locators/hashes
  next_action: canonical TVC machine lane continues; no token workaround
```

## Privatization eligibility gates

```text
StegVerse-Labs/StegCore -> NOT YET ELIGIBLE
  blockers:
    - SDK governed-test direct git dependency remains
    - SDK release index currently consumes public StegCore GitHub Releases API
  eligibility:
    - TVC immutable public publication verified
    - SDK artifact/index binding updated to a public locator independent of repo visibility
    - anonymous install/download verification PASS

Data-Continuation/core-lite -> NOT YET ELIGIBLE
  blocker:
    - SDK governed-test direct git dependency remains
  eligibility:
    - public immutable package/artifact acquisition independent of source repo visibility PASS

master-records/orchestration -> ALREADY PRIVATE
  required correction:
    - public SDK path must not imply anonymous direct git acquisition of this repo
    - exact public distributable artifact or another TVC-authorized credential-free package path must carry the required local implementation
```

## Validation ladder

```text
1 static dependency inspection
2 artifact/package manifest validation
3 exact hash/receipt verification
4 anonymous clean-environment SDK install
5 governed-test local deterministic execution
6 replay/reconstruction
7 no credential-like environment input required
8 post-privatization install regression
```

No higher level is implied by a lower one.

## Current completion

```text
source defect identified: COMPLETE
canonical upstream publication owner located: COMPLETE
collision boundary installed: COMPLETE
credential boundary preserved: COMPLETE
public artifact publication: PENDING_MACHINE_OWNED
SDK immutable artifact binding: PENDING_UPSTREAM_PUBLICATION
anonymous clean install proof: PENDING
StegCore privatization eligibility: BLOCKED
Core-Lite privatization eligibility: BLOCKED
Master Records privacy preservation: CURRENTLY_PRIVATE / PUBLIC_ACQUISITION_DEFECT_PENDING
```

## Canonical continuation

```text
MERGED INTO:
StegVerse-Labs/TVC/docs/PORTABLE_ARTIFACT_PUBLICATION_MIRROR_HANDOFF.md
-> StegVerse-org/StegVerse-SDK/docs/SDK_PORTABLE_PACKAGE_CONSOLE_MIRROR_HANDOFF.md
-> this handoff for repository-privacy eligibility
-> StegVerse-Labs/.github/docs/REPOSITORY_VISIBILITY_BOUNDARY_MIRROR_HANDOFF.md
```

## Archive condition

This scoped SDK integration state is durable. The parent repository-visibility session is not archive-ready until remaining estate classifications are transferred and its active claim is released or merged into machine/current-authority continuation.
