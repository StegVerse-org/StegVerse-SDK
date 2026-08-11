# SDK Mirror Handoff

## Source of truth

Organization: `StegVerse-org`  
Repository: `StegVerse-SDK`  
Canonical branch: `main`  
Active integration branch: `polish/public-sdk-surface-20260811`  
Active pull request: `#15`  

This file is the canonical repository handoff. Live repository state, Git history, PR state, workflow evidence, immutable receipts, and this handoff supersede prior chat claims.

## Goal inventory

### SDK-PUBLIC-CONSOLE-001 — COMPLETE

Originating goal: any developer/tester/evaluator can enter the SDK through one generic console, discover supported surfaces, run allowed local tasks, and obtain accurate help without person-specific instructions.

```text
canonical_merge: 0509c4cf3783cb76d9355a866b41ed2999a3d3f6
merged_pr: #14
successor_main_validation: 31523998702 SUCCESS
claim_state: COMPLETE_RELEASED
```

### SDK-PUBLIC-POLISH-002 — CLAIMED_FOR_IMPLEMENTATION/VALIDATION

Originating goal: make the SDK surface 100% polished and ready for public display, including AdmittedCode as a normal self-discoverable surface usable by any external developer from checkout and, when released, from the built wheel.

```text
branch: polish/public-sdk-surface-20260811
pull_request: #15
claimant: this PR
claim_created: 2026-08-11
release_condition: final-head hosted validation PASS + merge + successor-main Public SDK Surface Readiness PASS
collision_boundary: no person-specific routes; no duplicate local-model authority; no credential authority inside SDK
```

## Public user experience

Canonical checkout path:

```text
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse surfaces
stegverse help-surface <surface>
stegverse run <surface> [options]
```

Bundled proof path:

```text
stegverse demo admittedcode
stegverse demo admittedcode --case allow
stegverse demo admittedcode --case deny
```

Equivalent module entry: `python -m stegverse`.

The public console is generic. No customer, reviewer, evaluator, or named person receives a bespoke route.

## Callable console surfaces

Canonical registry: `stegverse/sdk_surfaces.py`.

```text
admissibility
llm-admissibility
math-admissibility
admittedcode
universal-entry
bridges
entry-points
```

Every callable surface must publish summary, command, backing module, documentation pointer, and `authority_effect: NONE`.

## AdmittedCode public surface

AdmittedCode is a first-class generic SDK surface.

Canonical consumer:

```text
stegverse/admittedcode_receipt.py
```

Bundled wheel-safe fixtures:

```text
stegverse/demo_data/admittedcode_allow.json
stegverse/demo_data/admittedcode_deny.json
```

Required proof semantics:

```text
ALLOW fixture -> SDK ACCEPTED; decision ALLOW
DENY fixture  -> SDK ACCEPTED; decision DENY
SDK ACCEPTED does not rewrite the underlying decision
authority_effect: NONE
```

The consumer validates required fields, supported schema, decision vocabulary, refusal/key-request boundary, authority escalation, and canonical receipt hash. Invalid or corrupt receipts fail closed.

## Public documentation

Canonical public docs:

```text
README.md
docs/SDK_CONSOLE.md
```

Public polish requirements:

1. first-time developer can reach a working demo in under two minutes from repository checkout;
2. AdmittedCode is visible in the root README and console discovery;
3. help explains result semantics, not only command syntax;
4. no private or person-specific directions are required;
5. README does not claim an unreleased PyPI version already contains current behavior;
6. package metadata describes the SDK as testing/verification/bounded routing, not as execution authority;
7. built wheel includes the bundled demo fixtures and can execute `stegverse demo admittedcode` outside the repository checkout.

## Credential and GitHub-token boundary

```text
github_tokens_supported_by_public_sdk: false
public_repository_read_credential_requirement: NONE
credential_authority: TV/TVC
private_source_access_is_public_console_capability: false
```

The public SDK does not acquire or resolve GitHub tokens, provider keys, private keys, bearer tokens, or passwords. Protected/live route credential semantics remain outside the SDK and are governed by TV/TVC.

GitHub Actions may use GitHub's own ephemeral workflow transport for CI checkout. That is not a production SDK/runtime credential dependency and grants no SDK route authority.

## Local model/runtime convergence

No SDK implementation claim is authorized for the local model/runtime lane.

Canonical owner/evidence:

```text
StegVerse-002/micro-node-runtime#16/#22
MICRO_NODE_RUNTIME_MIRROR_HANDOFF.md
docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
validated_code_commit: 395d4013d1354c07bc3cf66c44f4f26f856c75fc
canonical_validation_run: 31339534741 SUCCESS
implementation_state: COMPLETE_RELEASED
```

The fallback `stegverse-reference-lm-v1` is a formally developed repository-local reference language model and is not a production-scale foundation LLM.

LLM-adapter runtime activation remains machine-owned by its canonical handoff and carrier/TVC/Master Records workstream. This SDK session must not duplicate it.

## Validation

Existing canonical workflow:

```text
.github/workflows/sdk-demo-test.yml
```

Public-readiness gate added by PR #15:

```text
.github/workflows/public-sdk-surface.yml
scripts/verify_public_sdk_surface.py
```

The public-readiness workflow must prove:

```text
editable checkout install
public surface registry completeness
all surfaces non-authorizing
AdmittedCode help discoverability
AdmittedCode bundled ALLOW/DENY demo
package build
clean virtualenv wheel install
wheel execution outside repository checkout
stegverse surfaces from wheel
stegverse help-surface admittedcode from wheel
stegverse demo admittedcode from wheel
```

Do not claim 100% public readiness until final PR-head checks pass, PR #15 merges, and successor-main Public SDK Surface Readiness passes.

## Integration and release state

```text
PR #14 generic console: COMPLETE_MERGED_VALIDATED
PR #15 public polish: ACTIVE
current repository checkout public readiness: branch implementation complete, hosted validation pending
published package containing PR #15: NOT RELEASED
release/tag authority: NOT GRANTED BY THIS HANDOFF
```

A future PyPI release is a separate release-authority event. Repository public-display readiness and package-publication status must remain distinct.

## Session consolidation

Durably transferred requirements:

1. generic SDK entry for every developer/tester/evaluator;
2. discoverable and runnable AdmittedCode surface from the SDK itself;
3. self-contained bundled AdmittedCode ALLOW/DENY demonstration;
4. help documentation that explains result semantics;
5. no person-specific evaluator route;
6. root/session handoff files remain project-control records rather than user surfaces;
7. no GitHub-token dependency in the public SDK path;
8. TV/TVC remains credential/route authority;
9. local-runtime discovery/launch/proof remains canonical in `StegVerse-002/micro-node-runtime#22`;
10. formal local reference-model development remains canonical in `StegVerse-002/micro-node-runtime#22`;
11. wheel must preserve the public console and bundled AdmittedCode demo outside a source checkout;
12. public metadata must not describe the SDK as an execution authority.

## Completion accounting

For `SDK-PUBLIC-POLISH-002`, required deliverables are:

```text
1 root README public landing page
1 console guide
1 enriched public surface registry
1 generic console with bundled demo routing
2 packaged AdmittedCode fixtures
1 package metadata correction
1 deterministic public-readiness verifier
1 hosted public-readiness workflow
1 CLI validation suite
1 canonical handoff update
```

Current branch accounting:

```text
developed_files: 11/11
scaffolding_or_stubs: 0
missing_required_files: 0
implementation: COMPLETE_ON_BRANCH
validation: PENDING_FINAL_HEAD
integration: PENDING_PR_MERGE
propagation: not required for this repository-only public SDK polish goal
session_requirements_transferred: 12/12
```

## Archive conditions

This session remains a distinct SDK integration/validation lane until PR #15 is hosted-green, merged, successor-main public-readiness validation is successful, and this handoff is updated with immutable evidence. No local-model/runtime implementation work remains here.
