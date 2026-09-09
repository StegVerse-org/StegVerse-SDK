# SDK Public Distribution Privacy Mirror Handoff

Updated: 2026-09-09T03:36:29-05:00

## Canonical authority

```text
goal_id: SDK-PUBLIC-DISTRIBUTION-PRIVACY-001
repository: StegVerse-org/StegVerse-SDK
branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
originating_goal: preserve the SDK as the public aperture while allowing implementation repositories to remain private
credential_authority: TV/TVC
NON-TV/TVC secret/token authority: PROHIBITED
GitHub token runtime authority: NONE
publication_authority: StegVerse-Labs/TVC
state: BLOCKED_PENDING_EXACT_PUBLICATION_PROOF
```

## Current dependency boundary

The original defect was a public SDK governed-test path that directly depended on protected repository source. That source-level defect has now been remediated in the active SDK distribution branch without making private repositories public.

Current SDK PR #163 governed-test identities:

```text
stegverse-stegcore==0.3.0
stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
stegverse-master-records==0.2.0
```

StegCore retains Python import/module namespace `stegcore`; its public distribution identity is `stegverse-stegcore`.

## Completed source remediation

```text
StegCore distribution rename PR: StegVerse-Labs/StegCore#197 MERGED
StegCore merge: 9a35f39b3425a2c3e9592a03b0362a417094b809
StegCore README public install documentation: COMPLETE
StegCore targeted distribution: stegverse-stegcore==0.3.0

Master Records Trusted Publishing PR: master-records/orchestration#85 MERGED
Master Records targeted distribution: stegverse-master-records==0.2.0
Master Records exact frozen candidate: c524b1a0c1a43e49c70faeac7b67f78c5908e4e4
Master Records source parent: 03312236c115bc814024d700810391340648601f
Master Records README public install documentation: COMPLETE

SDK public dependency rewrite: StegVerse-org/StegVerse-SDK#163 DRAFT
SDK README stale repository-visibility statement: CORRECTED
SDK branch evidence head after README correction: b229a7a93a59bdd93e134ed1e219e482a81aefb1
```

Repository visibility is no longer the intended acquisition mechanism for StegCore or Master Records on the governed-test branch.

## Remaining publication proof blocker

Source remediation is not equivalent to public artifact availability. Exact immutable publication has not yet been observed through the canonical release path.

SDK PR #163 contains an anonymous installation/E2E gate that:

```text
materializes exact public SDK source with no GitHub credential
-> pip install -e .[governed-test]
-> verify stegverse-stegcore==0.3.0
-> verify stegverse-master-records==0.2.0
-> execute ELAN Test 1 through stegverse external-run
-> require manifest_receipt_id
-> require Master Records custody RECORDED
-> require replay
-> require reconstruction
```

Latest observation:

```text
Anonymous Governed Runtime Install: run 34329494516 FAILURE
exact SDK head: b229a7a93a59bdd93e134ed1e219e482a81aefb1
source materialization: PASS
package installation: FAIL
package identity verification: SKIPPED
ELAN governed execution: SKIPPED
replay/reconstruction verification: SKIPPED
```

The current fail-closed interpretation is `BLOCKED_PENDING_EXACT_PUBLICATION_PROOF`. Do not weaken the gate or infer runtime failure from an installation-stage failure.

## Required architecture

```text
public StegVerse SDK
-> immutable TVC-admitted public distribution artifacts
-> exact version/provenance verification
-> install locally
-> no protected repository credential required
-> runtime/governance authority remains local StegVerse + TV/TVC
```

Repository visibility must remain irrelevant to StegCore/Master Records public package acquisition.

## Release boundary

Trusted Publisher registration and a merged release workflow are transport prerequisites, not release authorization.

The canonical TVC successor-release handoff currently preserves a fail-closed release gate. No GitHub source mutation, workflow PASS, connector credential, or chat session may fabricate a TV/TVC GRANTED authorization, SKAP custody proof, interlock receipt, immutable tag/release, or aggregate release receipt.

The separately prepared SDK `v1.2.0` identity must not be moved or retargeted. Current generic-manifest/public-distribution work requires a coherent post-v1.2.0 successor identity before an SDK release containing it can be tagged.

## Collision boundary

Do not:

- make `master-records/orchestration` public merely to repair SDK installation;
- use `GITHUB_TOKEN`, `GH_TOKEN`, or another non-TV/TVC credential to fetch protected source as a substitute for public distribution;
- duplicate StegCore, Core-Lite, Master Records, TV, TVC, publication, evaluator, or custody logic inside the SDK;
- claim an exact public distribution exists merely because its Trusted Publisher is configured;
- claim the governed-test extra is anonymously installable until the exact anonymous install/E2E gate passes;
- retarget the frozen SDK `v1.2.0` release identity.

## Execution ownership

```yaml
- task_id: SDK-PUBLIC-DISTRIBUTION-PRIVACY-001
  role: CLAIMED_FOR_INTEGRATION
  owner: StegVerse-org/StegVerse-SDK consumer lane
  collision_scope: SDK governed-test dependency acquisition, public distribution binding, anonymous clean-install verification
  release_condition: exact public distributions are verified and anonymous install + governed ELAN E2E + replay/reconstruction pass
  next_action: preserve PR #163 draft until exact publication; rerun its anonymous gate after canonical release publication

- release/publication lane
  role: TV/TVC-GATED
  owner: StegVerse-Labs/TVC release chain
  release_condition: canonical TV/TVC release predicates are satisfied and immutable artifacts are authentically published
  next_action: no credential workaround from the SDK lane
```

## Privatization eligibility gates

```text
StegVerse-Labs/StegCore -> NOT YET VERIFIED ELIGIBLE
  source dependency blocker: REMEDIATED_IN_SDK_PR_163
  remaining gates:
    - exact stegverse-stegcore 0.3.0 public publication observed
    - anonymous governed-test installation PASS
    - any other public GitHub release-index coupling separately reconciled if still applicable

Data-Continuation/core-lite -> NOT YET ELIGIBLE
  blocker:
    - SDK governed-test still intentionally pins its public repository source
  eligibility:
    - public immutable package/artifact acquisition independent of source repo visibility PASS

master-records/orchestration -> SOURCE MAY REMAIN PRIVATE
  source dependency blocker: REMEDIATED_IN_SDK_PR_163
  remaining gates:
    - exact stegverse-master-records 0.2.0 public publication observed
    - anonymous governed-test installation PASS
```

## Validation ladder

```text
1 static dependency inspection: PASS for StegCore/Master Records rewrite in PR #163
2 artifact/package manifest validation: SOURCE VALIDATIONS PASS / PUBLICATION NOT YET PROVEN
3 exact public version/provenance verification: PENDING
4 anonymous clean-environment SDK install: FAIL_CLOSED_PENDING_PUBLICATION
5 governed-test local deterministic execution: NOT REACHED BY ANONYMOUS GATE
6 replay/reconstruction: NOT REACHED BY ANONYMOUS GATE
7 no credential-like environment input required: ENFORCED BY WORKFLOW
8 post-privatization install regression: PENDING
```

No higher level is implied by a lower one.

## Current completion

```text
original distribution/privacy defect identified: COMPLETE
StegCore source-dependency remediation: COMPLETE_IN_DRAFT_SDK_PR
Master Records source-dependency remediation: COMPLETE_IN_DRAFT_SDK_PR
StegCore distribution rename: COMPLETE_MERGED
Master Records Trusted Publishing workflow: COMPLETE_MERGED
repository README maintenance: COMPLETE for StegCore and Master Records
SDK README visibility correction: COMPLETE_IN_DRAFT_PR
exact immutable PyPI publication: PENDING_TV_TVC_GATE
anonymous clean install proof: FAIL_CLOSED_PENDING_PUBLICATION
ELAN governed E2E through anonymous install: PENDING_AFTER_INSTALL
replay/reconstruction proof: PENDING_AFTER_INSTALL
```

## Canonical continuation

```text
StegVerse-Labs/TVC/docs/POST_RETURN_SUCCESSOR_RELEASE_PREPARATION_MIRROR_HANDOFF.md
-> SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md
-> StegVerse-org/StegVerse-SDK#163
-> this handoff for repository-privacy eligibility
-> StegVerse-Labs/.github/docs/REPOSITORY_VISIBILITY_BOUNDARY_MIRROR_HANDOFF.md
```

## Archive condition

This lane remains active until exact public distribution provenance and the anonymous clean-install/governed-E2E/replay/reconstruction chain are verified. Source remediation alone is not archive completion.
