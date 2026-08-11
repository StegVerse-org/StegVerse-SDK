# Evaluation Relationship Mirror Handoff

## Authority

This scoped handoff is subordinate to `SDK_MIRROR_HANDOFF.md` and governs the identity-neutral evaluator-interest intake path.

```text
goal_id: SDK-GENERAL-EVALUATION-RELATIONSHIP-001
repository: StegVerse-org/StegVerse-SDK
branch: main
owner: StegVerse-org/StegVerse-SDK
role: CLAIMED_FOR_IMPLEMENTATION
```

## Goal

Allow any evaluator to state through the SDK exactly what they care to evaluate without requiring recipient-specific packages, directories, repository knowledge, or privileged source access.

The SDK must preserve the evaluator's stated objectives, intersect them with a portable package capability catalog and StegVerse boundary policy, and emit a non-authorizing relationship result.

## Core rule

```text
evaluator stated objectives
-> SDK normalized evaluation request
-> package capability catalog
-> StegVerse boundary policy
-> deterministic interest matching
-> admitted capabilities + denied/unavailable capabilities + unresolved objectives
-> bounded relationship receipt
-> package/demo/sandbox route
```

The evaluator may narrow the relationship at any time. A request to broaden scope is only a request; it never grants authority by itself.

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

The default public evaluator package may expose documentation, deterministic demos, schemas, examples, receipts, and explicitly catalogued sandbox routes. `StegGhost/entity-sandbox-runner` may be offered as an optional bounded sandbox capability when admitted by package policy. `StegVerse-org/LLM-adapter` is excluded from the default evaluator perimeter.

## Canonical implementation surfaces

```text
stegverse/evaluation_relationship.py
schemas/evaluation-interest-request.schema.json
schemas/evaluation-relationship-result.schema.json
tests/test_evaluation_relationship.py
docs/EVALUATION_RELATIONSHIP.md
```

## Validation

The implementation must prove:

```text
free-form evaluator objectives are preserved
catalog-tag matches are deterministic
explicit capability requests are intersected rather than trusted
package-denied capabilities cannot be admitted
unknown objectives remain unresolved rather than broadening scope
explicit evaluator restrictions always reduce effective scope
LLM-adapter remains excluded when absent/denied by the package catalog
effective scope grants no execution or repository authority
same inputs produce the same receipt hash
```

## Release condition

Release when the SDK implementation, schemas, tests, and demo-suite consumer contract are installed and validated without requiring GitHub Actions or any external runtime.
