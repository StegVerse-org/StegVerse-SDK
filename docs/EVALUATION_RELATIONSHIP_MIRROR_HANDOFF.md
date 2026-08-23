# Evaluation Relationship Mirror Handoff

## Authority

This scoped handoff is subordinate to `SDK_MIRROR_HANDOFF.md` and governs the identity-neutral evaluator/developer relationship path.

```text
goal_id: SDK-GENERAL-EVALUATION-RELATIONSHIP-001
repository: StegVerse-org/StegVerse-SDK
branch: main
owner: StegVerse-org/StegVerse-SDK
implementation_claim: COMPLETE_RELEASED
validation_claim: COMPLETE_RELEASED
```

## Goal

Allow any evaluator or developer to state through the SDK exactly what they care to evaluate without recipient-specific packages, directories, repository knowledge, privileged source access, or direct access to broader StegVerse services.

## Independent evaluator validation surface

The SDK is the canonical independent-evaluator validation surface for StegVerse governance behavior.

An evaluator does not need a privileged examiner role, recipient-specific fixture, StegVerse repository access, production authority, or a paid certification relationship in order to test a governance proposition. The evaluator supplies the proposition, constraints, and inputs they genuinely care to examine; the SDK binds those inputs to the ordinary governed path and returns portable evidence sufficient for verification, replay, and reconstruction where the admitted capability supports them.

The intended relationship is cooperative but non-authorizing:

```text
independent evaluator interest
-> evaluator-defined governance proposition / restrictions
-> identity-neutral SDK admission
-> governed execution or explicit fail-closed/unavailable result
-> portable receipts + evidence
-> replay / reconstruction where applicable
-> evaluator reaches their own conclusion
```

The evaluator's conclusion is external to StegVerse authority. StegVerse does not require an evaluator to purchase an opinion, certification, or proprietary examination in order to validate the system. Likewise, the SDK does not grant special standing merely because an evaluator charges for a report. Any commercial, accreditation, certification, or consulting relationship an evaluator separately offers is outside the SDK trust model and is not a prerequisite for independent validation.

A cooperative agreement may define mutually useful test boundaries, disclosure constraints, or consequence limits, but it must not make the evaluator a governance authority or substitute evaluator reputation for the underlying evidence.

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

No valid current acceptance receipt means no SDK-connected Demo relationship.

## General evaluator perimeter

Permitted interactive capability classes when individually admitted:

```text
sdk://StegGhost/entity-sandbox-runner
sdk://StegVerse-org/LLM-adapter/evaluator-entry
```

The LLM-adapter evaluator route is not direct adapter access. Evaluator-entry v1 is `local_reference_only`, maximum output 512 tokens, no provider selection, no credential access, no sovereign route authority, no repository access, and no execution authority.

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

## Deterministic validation evidence

Performed 2026-08-12 without GitHub Actions, Render, GitHub tokens, or hosted runtime. Exact repository content was materialized into an isolated local test tree through the connected repository interface because anonymous `github.com` DNS was unavailable in the execution container.

```text
python -m unittest tests.test_demo_terms tests.test_evaluation_relationship tests.test_evaluator_llm_entry
result: 11/11 PASS
terms hash binding: PASS
nonaffirmative/stale/tampered acceptance denial: PASS
evaluator-interest matching/self-restriction/hidden capability denial: PASS
SDK-mediated LLM admission only: PASS
provider/credential escalation denial: PASS
request/relationship deterministic hash integrity: PASS
```

Cross-repository contract validation:

```text
Demo terms acceptance
-> SDK relationship receipt
-> SDK evaluator LLM request
-> independent LLM-adapter request verification
-> bounded local-reference execution
-> non-authorizing measured response receipt
PASS
```

The response receipt proves provider credentials are not exposed, evaluator provider-selection authority is false, GitHub-token requirement is false, third-party execution-platform requirement is false, and authority effect is NONE.

## Machine-owned continuation

Evaluator relationship creation and narrowing are SDK-owned. Requests to broaden scope are re-evaluated through the same policy path. An unavailable optional interactive dependency removes only that capability; it does not block frozen-package inspection or broader StegVerse continuity.

## Release state

```text
implementation: COMPLETE
validation: COMPLETE
integration: COMPLETE
claim: COMPLETE_RELEASED
recipient-specific evaluator path: NONE
```

## Completion accounting

```text
developed_files: 13/13
scaffolding_or_stubs: 0
missing_required_files: 0
validation: 13/13
integration: 13/13
goal_activation: 100%
session_consolidation: COMPLETE_FOR_THIS_GOAL
```
