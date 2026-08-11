# SDK Mirror Handoff

## Source of truth

Organization: `StegVerse-org`  
Repository: `StegVerse-SDK`  
Canonical branch: `main`  
This file is the canonical repository handoff. Live repository state, Git history, workflow evidence, immutable receipts, and this handoff supersede prior chat claims.

## Active goal

```text
goal_id: SDK-PUBLIC-CONSOLE-001
originating_goal: any developer/tester/evaluator can enter the SDK through one generic console, discover supported surfaces, run allowed local tasks, and obtain accurate help without person-specific instructions
claim_state: COMPLETE
canonical_merge: 0509c4cf3783cb76d9355a866b41ed2999a3d3f6
merged_pr: #14
collision_boundary: no person-specific routes; no duplicate local-model/runtime authority; no credential authority inside SDK
```

## Required user experience

```text
repository checkout
-> python -m pip install -e ".[dev]"
-> stegverse
-> stegverse surfaces
-> stegverse help-surface <surface>
-> stegverse run <surface> [options]
-> JSON result / receipt / bounded routing output
```

The equivalent entry command is `python -m stegverse`.

The public SDK console is generic. No customer, reviewer, evaluator, or named person receives a bespoke route.

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

`stegverse capabilities` reports this callable user-facing registry. Repository-level `sdk.capabilities.json` remains the broader implementation/integration posture and must not be confused with what a user can execute locally.

## Public documentation

```text
README.md
docs/SDK_CONSOLE.md
```

The README is written for arbitrary external developers. Repository checkout is the canonical current demo path. It does not claim that an older published PyPI package already contains unreleased console behavior.

The docs explain discovery, runnable surfaces, AdmittedCode verification, dynamic admissibility, universal-entry routing, checkout validation, and authority boundaries.

## AdmittedCode surface

AdmittedCode is a normal generic SDK surface.

```text
stegverse help-surface admittedcode
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json
```

Canonical consumer: `stegverse/admittedcode_receipt.py`.

SDK `ACCEPTED` means the portable receipt boundary validated. It never changes the receipt's underlying `ALLOW`, `DENY`, or `FAIL_CLOSED` decision and never grants execution authority.

## Credential and GitHub-token boundary

```text
github_tokens_supported_by_public_sdk: false
public_repository_read_credential_requirement: NONE
credential_authority: TV/TVC
private_source_access_is_public_console_capability: false
```

The public SDK does not acquire or resolve GitHub tokens. `stegverse/github_repository_fetcher.py` is credential-free and limited to unauthenticated public GitHub contents reads with non-authorizing provenance receipts.

`stegverse/integration_config.py` rejects credential references on public repository source bindings. Protected/live route credential semantics remain outside the SDK and are governed by TV/TVC. Service bindings may carry non-secret authority references, but embedded credential values remain prohibited.

GitHub Actions may use GitHub's own ephemeral workflow token to check out repository code inside CI. That CI transport detail is not a production SDK/runtime credential dependency and grants no SDK route authority.

## Local model/runtime convergence

The session requirement to replace descriptive local-model selection with executable discovery/launch/proof and to formally develop a local model is not owned by the SDK and must not be duplicated here.

Canonical owner and evidence:

```text
StegVerse-002/micro-node-runtime#22
MICRO_NODE_RUNTIME_MIRROR_HANDOFF.md
docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
validated_code_commit: 395d4013d1354c07bc3cf66c44f4f26f856c75fc
canonical_validation_run: 31339534741 SUCCESS
implementation_state: COMPLETE_RELEASED
```

The canonical local implementation is `stegverse-reference-lm-v1`, a real repository-local order-2 token-transition reference language model. Runtime discovery prefers a qualifying local llama.cpp/GGUF or Ollama model when present and otherwise uses the reference model. The reference model is not to be represented as a production-scale foundation LLM.

LLM-adapter continuation is machine-owned runtime observation, not another implementation claim:

```text
StegVerse-org/LLM-adapter/LLM_ADAPTER_MIRROR_HANDOFF.md
StegVerse-Labs/.github#60 / SHWP-ECOSYSTEM-CHAT-INFERENCE-001
StegVerse-Labs/TVC/tasks/TVC-SOVEREIGN-LOCAL-MODEL-ROUTE-002.json
master-records/orchestration
```

No GitHub token is a production local-model/runtime prerequisite.

## Validation evidence

Final PR head:

```text
272b2fa4b6c9c3dfd754f603547fd7493beddf20
```

All associated hosted workflows completed successfully, including:

```text
StegVerse SDK Validation run 31523742856: SUCCESS
validate run 31523742739: SUCCESS
Architecture Guard run 31523742724: SUCCESS
Validate Provider Usage Ingestion run 31523742712: SUCCESS
Diagnose Python 3.9 Public Imports run 31523742728: SUCCESS
```

The SDK validation job proved Python 3.9/3.11/3.12 complete tests, route-validation, dynamic-admissibility examples, package build, and wheel installation.

Canonical merge:

```text
PR #14: MERGED
main merge commit: 0509c4cf3783cb76d9355a866b41ed2999a3d3f6
successor-main StegVerse SDK Validation run 31523998702: SUCCESS
```

## Integration and release state

```text
PR #14: MERGED
main integration: COMPLETE
successor-main core validation: SUCCESS
published package containing console: NOT YET PROVEN
release/tag authority: NOT GRANTED BY THIS HANDOFF
```

Repository checkout is the current canonical public demo. Do not claim the existing published package contains the new console until a release containing merge `0509c4cf3783cb76d9355a866b41ed2999a3d3f6` is created and verified.

## Session consolidation

Transferred requirements:

1. generic SDK entry for every developer/tester/evaluator;
2. discoverable AdmittedCode surface from the SDK itself;
3. runnable allowed SDK tasks, not documentation-only discovery;
4. help documentation for each generic console route;
5. no person-specific evaluator route;
6. root/session handoff files are project-control records, not SDK user surfaces;
7. no GitHub tokens in the public SDK path;
8. TV/TVC remains credential/route authority;
9. local-runtime discovery/launch/proof requirement transferred to and completed by `StegVerse-002/micro-node-runtime#22`;
10. formal local reference-model development transferred to and completed by `StegVerse-002/micro-node-runtime#22`;
11. LLM-adapter same-carrier execution implementation is complete/released; remaining work is machine-owned runtime observation/custody/reconstruction.

MERGED INTO canonical continuation for local-model/runtime activation:

```text
StegVerse-002/micro-node-runtime#16/#22
StegVerse-org/LLM-adapter#18
StegVerse-Labs/.github#60 / SHWP-ECOSYSTEM-CHAT-INFERENCE-001
StegVerse-Labs/TVC/tasks/TVC-SOVEREIGN-LOCAL-MODEL-ROUTE-002.json
master-records/orchestration
```

## Completion accounting

```text
SDK-PUBLIC-CONSOLE-001 required developed surfaces: 9
implemented on canonical main: 9
scaffolding/stubs in required console path: 0
missing required files: 0
PR-head hosted validation: COMPLETE
main integration: COMPLETE
successor-main core validation: COMPLETE
published package proof: pending future release only
session requirements transferred: 11/11
```

## Archive conditions

The SDK public-console implementation goal is complete on main. This repository no longer requires this session for implementation or validation. Any future PyPI release is a separate release-authority event and must not be inferred from repository checkout readiness.
