# SDK Mirror Handoff

## Source of truth

Organization: `StegVerse-org`  
Repository: `StegVerse-SDK`  
Canonical branch: `main`

This is the canonical repository handoff. Live repository state, immutable commits, local validation receipts, and this handoff supersede prior chat claims.

## Goal inventory

### SDK-PUBLIC-CONSOLE-001 — COMPLETE_RELEASED

Generic public SDK console and AdmittedCode surface are merged and released. No recipient-specific evaluator route is canonical.

Historical release evidence:

```text
PR #14 merge: 0509c4cf3783cb76d9355a866b41ed2999a3d3f6
PR #15 merge: 17e2d163734ab1d76702884f6407ef859dd54f8b
```

### SDK-GENERAL-EVALUATION-RELATIONSHIP-001 — COMPLETE_RELEASED

Canonical scoped handoff:

```text
docs/EVALUATION_RELATIONSHIP_MIRROR_HANDOFF.md
```

Released implementation includes exact Demo TOS/TOU acceptance binding, deterministic evaluator-interest resolution, bounded relationship receipts, and SDK-mediated evaluator LLM request envelopes. Direct LLM-adapter access is not granted by the SDK relationship.

Release commit:

```text
985cdb57ec953fc95b5020ea781a9c3e4aaf097b
```

### SDK-NO-GITHUB-AUTHORITY-003 — COMPLETE_RELEASED

Originating requirement:

```text
GitHub tokens are not StegVerse credential authority.
TV/TVC owns credential and capability authority.
StegVerse continuity is primary; third-party accessibility is fallback.
GitHub account pause, billing exhaustion, workflow outage, or provider outage must not prevent canonical SDK validation, release preparation, evidence handling, or continuation.
```

Canonical claim state:

```text
implementation_claim: COMPLETE_RELEASED
validation_claim: COMPLETE_RELEASED
session_claim: NONE
```

## Credential and continuity boundary

```text
github_token_runtime_authority: NONE
github_token_release_authority: NONE
github_token_evidence_authority: NONE
github_token_tvc_authority: NONE
github_actions_continuity_authority: NONE
github_actions_release_authority: NONE
github_actions_repository_mutation_authority: NONE
github_actions_package_publication_authority: NONE
github_actions_oidc_authority: NONE
credential_authority: TV/TVC
canonical_validation_path: SOVEREIGN_LOCAL
canonical_release_path: SOVEREIGN_LOCAL_TV_TVC
third_party_accessibility_role: OPTIONAL_FALLBACK_ONLY
```

The SDK does not acquire, resolve, transport, inherit, mint, publish, or persist GitHub tokens, provider keys, TV/TVC identity material, package-registry credentials, private keys, bearer tokens, passwords, or wallet secrets through GitHub Actions.

## Hosted workflow boundary

All 12 workflow files under `.github/workflows/` were directly inspected after the no-token reconciliation:

```text
architecture-guard.yml
caller-example.yml
diagnose-python39-public-imports.yml
goal7-review-authority-validation.yml
headless-release.yml
public-sdk-surface.yml
reusable-release.yml
sdk-demo-test.yml
system-boundary-evidence-sync.yml
tvc-ephemeral.yml
validate-provider-usage-ingest.yml
validate.yml
```

Canonical rule:

```text
hosted workflows: OPTIONAL_MANUAL_OR_REUSABLE_FALLBACK_ONLY
permissions: EMPTY
repository writes: PROHIBITED
push/tag/release creation: PROHIBITED
package publication: PROHIBITED
OIDC credential minting: PROHIBITED
TV/TVC secret transport: PROHIBITED
workflow secret inheritance: PROHIBITED
automatic push/PR/schedule continuity triggers: PROHIBITED
artifact upload/download as authority path: PROHIBITED
external GitHub Actions dependencies: PROHIBITED
```

The optional hosted wrappers may validate public source when deliberately invoked, but success or availability is not a release, activation, continuity, or archive prerequisite.

## Removed authority paths

The following prior hosted paths were explicitly retired:

```text
02f55dbe0e0de03f3c08a489303ddeaf2d416f75  headless release -> validation-only
b07fa019b0c653a8b48f5b0920225e01d3fb7589  reusable release -> validation-only
ef1bbeb6bba5486acc2db327575d180bba89db27  TVC hosted secret transport disabled
216cfffbb77eb2f656abf14215ecb746bc9d515e  hosted evidence mutation disabled
5617895603c4e2f586519b44014f26472f818366  Architecture Guard -> optional anonymous validation
c05d8ad735d7904c197af2413af7e49ce57f3181  public SDK gate -> optional anonymous validation
380856c422dffe2b0dba53b9e050e9162bb24a85  SDK validation -> optional anonymous validation
376ab8f79c3d6a9397f89f165d5407cc1ae98ea1  public-import diagnostic -> optional anonymous validation
5ff3b21e4e6911fc949b2516185316dae8fac47c  Goal 7 validation -> optional anonymous validation
60c904fe5e1303028222af941c5e7622c0cb6033  SDK diagnostic repository-write authority removed
737a54037560547fbee43749bc4d4de1bc25a135  provider usage validation -> optional anonymous validation
2ddaf0567a17ab6b1f6aaaca9a7df1745cdb5882  inherited workflow secrets removed
1cad6ccacc3c94b3034729d10c4a96c354e32884  automatic hosted evidence trigger removed
```

## Regression prevention

Repository-native validator:

```text
scripts/verify_github_fallback_boundary.py
```

Regression tests:

```text
tests/test_github_fallback_boundary.py
```

Installation commits:

```text
39fae32d70daed9e83654f28223ba05b098a0074  validator
39c501522a843c820c72249bd617af2441dc5608  tests
```

The validator fails if a workflow reintroduces automatic push/PR/schedule/workflow-run triggers, secret contexts, GitHub token contexts, write/OIDC permissions, external Actions dependencies, artifact authority paths, GitHub releases, package publication, repository pushes, or inherited secrets.

Canonical local validation command:

```bash
python scripts/verify_github_fallback_boundary.py
python -m unittest tests.test_github_fallback_boundary
```

## Local model/runtime convergence

No SDK implementation claim exists for the sovereign local-model lane because it is already complete in the canonical owner:

```text
StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
StegVerse-002/micro-node-runtime/work_claims/SOVEREIGN-LOCAL-MODEL-001.json
validated_code_commit: 395d4013d1354c07bc3cf66c44f4f26f856c75fc
implementation_state: COMPLETE_RELEASED
credential_authority: TV/TVC
github_token_required: false
```

The repository-local fallback `stegverse-reference-lm-v1` is formally developed and provides actual discovery, launch, inference, and proof. It is a bounded local reference language model, not a claim of production-scale foundation-model equivalence.

## Cross-repository ownership

```text
Demo evaluator package: StegVerse-org/stegverse-demo-suite/docs/DEMO_EVALUATOR_MIRROR_HANDOFF.md
Evaluator relationship: StegVerse-org/StegVerse-SDK/docs/EVALUATION_RELATIONSHIP_MIRROR_HANDOFF.md
Restricted evaluator model facade: StegVerse-org/LLM-adapter/docs/EVALUATOR_ENTRY_MIRROR_HANDOFF.md
Local model/runtime: StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
Trading continuation: StegVerse-Labs/stegfin-governance/docs/STEGFIN_MIRROR_HANDOFF.md
Sovereign heartbeat: StegVerse-Labs/.github/control/heartbeat-state.json
```

No SDK duplication of those owners is authorized.

## Machine-owned continuation

The SDK has no unresolved implementation claim from this session. Runtime/live-trading continuation belongs to the canonical heartbeat and StegFin task registry. GitHub-hosted workflows are not observers or release conditions for those tasks.

## Propagation obligations

The no-GitHub-authority correction is an SDK/control-plane boundary correction, not a product-content publication requiring duplicate implementation in Site, Publisher, admissibility-wiki, or stegguardian-wiki. Downstream repositories must consume TV/TVC and sovereign/local authority semantics through their canonical contracts; they must not recreate GitHub as credential authority.

## Completion accounting

For `SDK-NO-GITHUB-AUTHORITY-003`:

```text
required workflow surfaces audited: 12/12
workflow authority leaks removed: 6/6 classes
canonical regression validator: 1/1
regression test module: 1/1
automatic hosted continuity/release gates: 0
scaffolding_or_stubs: 0
missing_required_files: 0
implementation: COMPLETE
static repository validation: COMPLETE
integration: COMPLETE
claim_state: COMPLETE_RELEASED
```

Six eliminated authority classes:

1. GitHub-token/repository write authority;
2. package-registry credential/publication authority;
3. GitHub release/tag/push authority;
4. GitHub OIDC authority;
5. TV/TVC secret/identity transport through hosted workflows;
6. automatic hosted workflow dependency for canonical validation/evidence continuity.

## Session consolidation

Durably transferred/completed session requirements include:

1. generic SDK evaluator/developer surface;
2. Demo TOS/TOU relationship gate;
3. bounded LLM-adapter evaluator entry;
4. no person-specific evaluator implementation;
5. no GitHub-token credential authority;
6. TV/TVC credential authority preserved;
7. third-party accessibility reduced to fallback;
8. sovereign/local validation and release continuity primary;
9. actual local-runtime discovery/launch/inference/proof transferred to canonical micro-node-runtime owner;
10. formal local reference-model development transferred to canonical micro-node-runtime owner;
11. StegFin live activation transferred to its machine-owned heartbeat/task-registry path.

## Archive conditions

This SDK repository requires no further work from this chat session. Public SDK, evaluator relationship, no-GitHub-authority, local-model ownership, and continuation boundaries are durably installed. Any remaining live runtime/trading work is separately owned by canonical machine/human authority records and does not require preservation of this conversation.
