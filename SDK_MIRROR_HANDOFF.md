# SDK Mirror Handoff

## Source of truth

Organization: `StegVerse-org`  
Repository: `StegVerse-SDK`  
Canonical branch: `main`  

This file is the canonical repository handoff. Live repository state, Git history, workflow evidence, immutable receipts, and this handoff supersede prior chat claims.

## Goal inventory

### SDK-PUBLIC-CONSOLE-001 — COMPLETE_RELEASED

Originating goal: any developer/tester/evaluator can enter the SDK through one generic console, discover supported surfaces, run allowed local tasks, and obtain accurate help without person-specific instructions.

```text
merged_pr: #14
canonical_merge: 0509c4cf3783cb76d9355a866b41ed2999a3d3f6
successor_main_validation: 31523998702 SUCCESS
```

### SDK-PUBLIC-POLISH-002 — COMPLETE_RELEASED

Originating goal: make the SDK surface polished and ready for public display, including AdmittedCode as a normal self-discoverable surface usable by any external developer from checkout and from the built wheel artifact.

```text
merged_pr: #15
canonical_merge: 17e2d163734ab1d76702884f6407ef859dd54f8b
final_pr_head: 060aaca83b8e7691800dd1598c2a971e00e152e6
claim_state: COMPLETE_RELEASED
```

Final PR-head hosted validation:

```text
Public SDK Surface Readiness run 31526157562: SUCCESS
StegVerse SDK Validation run 31526157647: SUCCESS
validate run 31526157572: SUCCESS
Architecture Guard run 31526157588: SUCCESS
Validate Provider Usage Ingestion run 31526157583: SUCCESS
Diagnose Python 3.9 Public Imports run 31526157568: SUCCESS
```

Successor-main public distribution proof:

```text
Public SDK Surface Readiness run 31526281736: SUCCESS
merge commit: 17e2d163734ab1d76702884f6407ef859dd54f8b
```

That successor-main run proved editable checkout installation, deterministic public-surface verification, package build, clean virtualenv wheel installation outside the repository checkout, and successful execution of `stegverse surfaces`, `stegverse help-surface admittedcode`, and `stegverse demo admittedcode` from the installed wheel.

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

Every callable surface publishes a summary, command, backing module, documentation pointer, and `authority_effect: NONE`.

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

Verified proof semantics:

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

The README gives a sub-two-minute checkout-to-demo path, exposes AdmittedCode directly, distinguishes repository checkout from unreleased PyPI state, and describes the SDK as testing/verification/bounded routing rather than as execution authority.

The console guide documents surface discovery, AdmittedCode semantics, direct receipt verification, LLM/math admissibility, universal-entry routing, credential boundaries, exit behavior, troubleshooting, and repository-control-file boundaries.

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

No SDK implementation claim exists for the local model/runtime lane.

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

LLM-adapter runtime activation remains machine-owned by its canonical handoff and carrier/TVC/Master Records workstream. No duplication is authorized here.

## Validation and automation

Canonical SDK workflow:

```text
.github/workflows/sdk-demo-test.yml
```

Permanent public-readiness gate:

```text
.github/workflows/public-sdk-surface.yml
scripts/verify_public_sdk_surface.py
```

The public-readiness workflow automatically proves:

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

This gate runs on pull requests to main and pushes to main, preventing future public-surface regressions from silently passing as release-ready repository state.

## Integration and release state

```text
PR #14 generic console: COMPLETE_MERGED_VALIDATED
PR #15 public polish: COMPLETE_MERGED_VALIDATED
repository checkout public-display readiness: COMPLETE
built wheel artifact public-surface readiness: COMPLETE_VALIDATED
published PyPI package containing PR #15: NOT RELEASED
release/tag authority: NOT GRANTED BY THIS HANDOFF
```

Repository public-display readiness and PyPI publication remain distinct. A future package release is a separate release-authority event.

## Session consolidation

Durably transferred/completed requirements:

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
11. built wheel preserves the public console and bundled AdmittedCode demo outside a source checkout;
12. public metadata does not describe the SDK as an execution authority;
13. permanent automated public-readiness regression gate is installed.

## Completion accounting

For `SDK-PUBLIC-POLISH-002`:

```text
developed_files: 11/11
scaffolding_or_stubs: 0
missing_required_files: 0
implementation: COMPLETE
validation: COMPLETE
integration: COMPLETE
public_display_readiness: COMPLETE
published_package_release: OUTSIDE_THIS_GOAL / NOT_RELEASED
session_requirements_transferred_or_complete: 13/13
```

## Archive conditions

The SDK public-console and public-polish implementation goals are complete, merged, validated, and automation-protected. This repository no longer requires this session for implementation, validation, or integration. Any future PyPI release is a distinct release-authority event and must not be inferred from repository public-display readiness.
