# Evaluation Relationship Mirror Handoff

## Authority

This scoped handoff is subordinate to `SDK_MIRROR_HANDOFF.md` and governs the identity-neutral evaluator/developer relationship path.

```text
goal_id: SDK-GENERAL-EVALUATION-RELATIONSHIP-001
repository: StegVerse-org/StegVerse-SDK
branch: feat/general-demo-terms-current-20260812
owner: StegVerse-org/StegVerse-SDK
implementation_claim: CLAIMED_FOR_INTEGRATION_AND_VALIDATION
validation_claim: CLAIMED_FOR_VALIDATION
claim_release_condition: exact Demo terms acceptance, relationship resolver, SDK-scoped LLM request envelope, schemas/tests, Demo capability catalog, and LLM-adapter consumer are mutually consistent and deterministically validated, then merged.
```

## Goal

Allow any evaluator or developer to state through the SDK exactly what they care to evaluate without recipient-specific packages, directories, repository knowledge, privileged source access, or direct access to broader StegVerse services.

## Required sequence

```text
current Demo TOS + TOU
-> affirmative hash-bound acceptance receipt
-> evaluator states objectives + optional restrictions
-> SDK resolves against frozen capability catalog + StegVerse Demo policy
-> admitted + denied/unavailable + unresolved sets
-> bounded non-authorizing relationship receipt
-> optional SDK-mediated capability invocation
```

No current acceptance receipt means no SDK-connected Demo relationship.

## General evaluator perimeter

The frozen package may expose documentation, deterministic demos, schemas, examples, receipts, licenses, and explicitly catalogued SDK-mediated interactive capabilities.

Permitted interactive capability classes when individually admitted:

```text
sdk://StegGhost/entity-sandbox-runner
sdk://StegVerse-org/LLM-adapter/evaluator-entry
```

The LLM-adapter evaluator route is not direct adapter access. Evaluator-entry v1 is restricted to `local_reference_only`, maximum output 512 tokens, no provider selection, no credential access, no sovereign route authority, no repository access, and no execution authority.

## Non-authority invariants

```text
recipient_specific_package: false
identity_bound_package: false
execution_authority_granted: false
mutation_authority_granted: false
publication_authority_granted: false
wallet_authority_granted: false
credential_authority_granted: false
repository_access_granted: false
unknown_interest_auto_admitted: false
github_token_required: false
credential_authority: TV/TVC
```

Software license rights remain separate from Demo service access. Demo TOS/TOU do not silently replace rights independently granted by an applicable component license.

## Canonical implementation surfaces

```text
legal/demo/DEMO_TERMS_OF_SERVICE.md
legal/demo/DEMO_TERMS_OF_USE.md
stegverse/demo_terms.py
stegverse/evaluation_relationship.py
stegverse/evaluator_llm_entry.py
schemas/demo_terms_acceptance_receipt.schema.json
schemas/evaluation-interest-request.schema.json
schemas/evaluation-relationship-result.schema.json
schemas/evaluator_llm_entry_request.schema.json
tests/test_demo_terms.py
tests/test_evaluation_relationship.py
tests/test_evaluator_llm_entry.py
docs/EVALUATION_RELATIONSHIP_MIRROR_HANDOFF.md
```

Cross-repository consumers:

```text
StegVerse-org/stegverse-demo-suite/config/evaluator_capability_catalog.json
StegVerse-org/stegverse-demo-suite/config/evaluator_license_manifest.json
StegVerse-org/LLM-adapter/llm_adapter/evaluator_entry.py
StegVerse-org/LLM-adapter/docs/EVALUATOR_ENTRY_MIRROR_HANDOFF.md
```

## Validation

Required deterministic validation:

```text
python -m unittest tests.test_demo_terms tests.test_evaluation_relationship tests.test_evaluator_llm_entry
```

Validation must prove exact terms hash binding, affirmative assent, stale/tampered receipt denial, evaluator-interest preservation, deterministic catalog matching, evaluator self-restriction, hidden/unknown capability denial, SDK-mediated LLM admission only, local-reference-only request scope, provider/credential escalation denial, and deterministic receipt/request hashes.

Cross-repository validation must prove the SDK-produced relationship/request is independently accepted by the LLM-adapter evaluator facade and the same capability/route exists in the Demo catalog.

## Machine-owned continuation

Once released, evaluator relationship creation and narrowing are SDK-owned. Requests to broaden scope are re-evaluated through the same policy path. An unavailable interactive dependency removes only that capability; it does not block frozen-package inspection or broader StegVerse continuity.

## Release and archive conditions

Release when the clean current-main successor implementation is deterministically validated, Demo/SDK/LLM contracts are mutually consistent, no recipient-specific package is canonical, and the final generalized package can be built and verified locally without GitHub Actions, Render, GitHub tokens, or another hosted runtime.

Developed-files percentage: 100%
Validation percentage: 70%
Integration percentage: 80%
Goal-activation percentage: 75%
Session-consolidation state: ACTIVE — UNIQUE WORK REMAINS
