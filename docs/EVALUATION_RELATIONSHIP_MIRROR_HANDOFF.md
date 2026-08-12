# Evaluation Relationship Mirror Handoff

## Authority

This scoped handoff is subordinate to `SDK_MIRROR_HANDOFF.md` and governs the identity-neutral Demo evaluator/developer relationship path.

```text
goal_id: SDK-GENERAL-EVALUATION-RELATIONSHIP-001
repository: StegVerse-org/StegVerse-SDK
branch: feat/general-demo-terms-and-relationship-20260812
owner: StegVerse-org/StegVerse-SDK
role: CLAIMED_FOR_IMPLEMENTATION_AND_VALIDATION
```

## Goal

Allow any evaluator/developer to state through the SDK exactly what they care to evaluate without recipient-specific packages, directories, repository knowledge, or privileged source access.

A Demo relationship may not be created until the participant affirmatively accepts the exact current Demo Terms of Service and Terms of Use. The SDK preserves the evaluator's objectives, intersects them with a frozen capability catalog and StegVerse boundary policy, and emits a non-authorizing relationship result bound to the acceptance-receipt hash.

## Canonical sequence

```text
Demo TOS + TOU
-> affirmative hash-bound acceptance receipt
-> evaluator stated objectives + exclusions + interaction ceiling
-> SDK normalized evaluation request
-> frozen package capability catalog
-> StegVerse boundary policy
-> deterministic interest matching
-> admitted + denied/unavailable + unresolved sets
-> bounded relationship receipt
-> local frozen package and/or optional SDK-mediated route
```

The evaluator may narrow the relationship at any time. A request to broaden scope is re-evaluated and is never authority by itself.

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
```

## General evaluator perimeter

The frozen public evaluator package may expose documentation, deterministic demos, schemas, examples, receipts, licensing provenance, and explicitly catalogued SDK-mediated routes.

Optional routes when specifically admitted:

- `StegGhost/entity-sandbox-runner` evaluator sandbox;
- `StegVerse-org/LLM-adapter:evaluator-entry` restricted model-evaluation facade.

The full LLM-adapter is not directly exposed. The adapter entry must validate the exact SDK relationship receipt/capability and must not expose provider credentials, sovereign route authority, heartbeat, custody, wallet, private-repository, or broader adapter evidence surfaces.

## Demo terms and licensing

Canonical terms:

```text
legal/demo/DEMO_TERMS_OF_SERVICE.md
legal/demo/DEMO_TERMS_OF_USE.md
stegverse/demo_terms.py
schemas/demo_terms_acceptance_receipt.schema.json
```

The terms govern the Demo service relationship. Applicable software licenses govern software/artifact copies. The SDK relationship does not silently revoke rights independently granted by an applicable license, and an open-source license does not grant live StegVerse service authority.

## Canonical implementation surfaces

```text
stegverse/demo_terms.py
stegverse/evaluation_relationship.py
schemas/demo_terms_acceptance_receipt.schema.json
schemas/evaluation-interest-request.schema.json
schemas/evaluation-relationship-result.schema.json
tests/test_demo_terms.py
tests/test_evaluation_relationship.py
docs/EVALUATION_RELATIONSHIP.md
docs/EVALUATION_RELATIONSHIP_MIRROR_HANDOFF.md
```

Consumer contracts:

```text
StegVerse-org/stegverse-demo-suite/config/evaluator_capability_catalog.json
StegVerse-org/stegverse-demo-suite/config/evaluator_license_manifest.json
StegVerse-org/LLM-adapter evaluator-entry contract
```

## Validation requirements

The implementation must prove:

```text
no SDK relationship without exact current TOS/TOU acceptance
tampered/stale terms acceptance fails closed
free-form evaluator objectives are preserved
catalog-tag matches are deterministic
explicit requests are intersected rather than trusted
package-denied capabilities cannot be admitted
unknown objectives remain unresolved rather than broadening scope
evaluator restrictions always reduce scope
LLM capability can be admitted only as the SDK-scoped evaluator entry
effective scope grants no execution, credential, wallet, or repository authority
same inputs produce the same receipt hash
```

Validation must be locally executable and must not require GitHub Actions, Render, provider credentials, or a live StegVerse runtime.

## Release condition

Release when Demo terms acceptance, SDK relationship implementation/schemas/tests, generalized Demo-suite consumer contract, and restricted LLM-adapter evaluator entry are installed and deterministically validated. Production sovereign LLM-adapter behavior remains a separate authority surface.
