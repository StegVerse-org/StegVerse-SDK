# SDK Mirror Handoff

## Source of truth

Organization: `StegVerse-org`  
Repository: `StegVerse-SDK`  
Canonical branch: `main`  
Active integration branch: `feat/generic-sdk-console-20260811`  
Active pull request: `#14`  
This file is the canonical repository handoff. Live repository state, Git history, PR state, workflow evidence, immutable receipts, and this handoff supersede prior chat claims.

## Active goal

```text
goal_id: SDK-PUBLIC-CONSOLE-001
originating_goal: any developer/tester/evaluator can enter the SDK through one generic console, discover supported surfaces, run allowed local tasks, and obtain accurate help without person-specific instructions
claim_state: CLAIMED_FOR_IMPLEMENTATION
claimant: PR #14 / feat/generic-sdk-console-20260811
release_condition: merge PR #14 after hosted validation on its final head, then observe successor-main validation
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

## Local model/runtime convergence

The session requirement to replace descriptive local-model selection with executable discovery/launch/proof and to formally develop a local model is **not owned by this SDK branch**.

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

## Validation

Canonical workflow: `.github/workflows/sdk-demo-test.yml`.

PR #14 validation must cover:

```text
Python 3.9 / 3.11 / 3.12 complete test suite
public imports
CLI tests
credential-free GitHub source tests
integration-config TV/TVC boundary tests
route validation
dynamic admissibility examples
package build
wheel installation
architecture guard
```

Do not claim merged/main or public-package readiness from branch implementation alone.

## Integration and release state

```text
PR #14: OPEN
branch implementation: ACTIVE
final-head hosted validation: REQUIRED
main integration: NOT YET COMPLETE
published package containing console: NOT YET PROVEN
release/tag authority: NOT GRANTED BY THIS HANDOFF
```

After PR #14 reaches final-head green validation, merge only if repository policy permits, observe successor-main validation, then update this handoff with exact merge and workflow evidence.

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
implemented on PR branch: 9
scaffolding/stubs in required console path: 0
missing required files: 0
final-head hosted validation: pending after latest branch mutations
main integration: pending
published package proof: pending
session requirements transferred: 11/11
```

## Archive conditions

This session is not archive-ready while PR #14 remains unmerged or its final head is not hosted-green, because the SDK public-console goal remains an active unique integration claim. Local-model/runtime implementation does not require this session and must not be duplicated here.
