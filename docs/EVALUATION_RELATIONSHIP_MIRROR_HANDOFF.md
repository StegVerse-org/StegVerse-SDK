# Evaluation Relationship Mirror Handoff

## Authority

This scoped handoff is subordinate to `SDK_MIRROR_HANDOFF.md` and governs the identity-neutral evaluator-interest intake path.

```text
goal_id: SDK-GENERAL-EVALUATION-RELATIONSHIP-001
repository: StegVerse-org/StegVerse-SDK
owner: StegVerse-org/StegVerse-SDK
role: CLAIMED_FOR_IMPLEMENTATION
```

## Goal

Allow any evaluator or developer to state through the SDK exactly what they care to evaluate without requiring recipient-specific packages, directories, repository knowledge, or privileged source access.

The SDK must preserve the participant's stated objectives, require formal acceptance of the current Demo Terms of Service and Demo Terms of Use, intersect the request with a portable package capability catalog and StegVerse boundary policy, and emit a non-authorizing relationship result.

## Mandatory Demo terms gate

No SDK-connected Demo relationship may exist without a valid affirmative acceptance receipt for the exact current terms documents.

Canonical terms surfaces:

```text
legal/demo/DEMO_TERMS_OF_SERVICE.md
legal/demo/DEMO_TERMS_OF_USE.md
stegverse/demo_terms.py
schemas/demo_terms_acceptance_receipt.schema.json
tests/test_demo_terms.py
```

Required acceptance evidence:

```text
participant identity
signer name
signer capacity
affirmative acceptance = true
electronic signature value
acceptance timestamp
exact TOS version + SHA-256
exact TOU version + SHA-256
deterministic acceptance receipt hash
```

Missing, stale, altered, or non-affirmative acceptance fails closed before evaluation relationship resolution.

The Demo terms govern the service/evaluation relationship. They do not replace rights independently granted by an applicable software license for a lawfully obtained software copy.

## Core rule

```text
current TOS + TOU
-> affirmative SDK terms acceptance receipt
-> evaluator stated objectives
-> SDK normalized evaluation request
-> package capability catalog + per-component license provenance
-> StegVerse boundary policy
-> deterministic interest matching
-> admitted capabilities + denied/unavailable capabilities + unresolved objectives
-> bounded relationship receipt bound to terms acceptance receipt
-> package/demo/sandbox/SDK-mediated adapter route
```

The participant may narrow the relationship at any time. A request to broaden scope is only a request; it never grants authority by itself and may require renewed terms acceptance when the current terms version changes.

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

The public evaluator package may expose documentation, deterministic demos, schemas, examples, receipts, applicable license information, and explicitly catalogued sandbox or adapter routes.

`StegGhost/entity-sandbox-runner` may be offered as an optional bounded sandbox capability when admitted by package policy.

`StegVerse-org/LLM-adapter` must never be exposed as the adapter's full sovereign/provider surface. If model interaction is admitted, it must enter through an SDK-mediated evaluator adapter capability bound to the exact SDK relationship receipt and Demo terms acceptance receipt.

## Canonical implementation surfaces

```text
stegverse/demo_terms.py
stegverse/evaluation_relationship.py
schemas/demo_terms_acceptance_receipt.schema.json
schemas/evaluation-interest-request.schema.json
schemas/evaluation-relationship-result.schema.json
legal/demo/DEMO_TERMS_OF_SERVICE.md
legal/demo/DEMO_TERMS_OF_USE.md
tests/test_demo_terms.py
tests/test_evaluation_relationship.py
docs/EVALUATION_RELATIONSHIP.md
```

## Validation

The implementation must prove:

```text
no terms acceptance -> relationship denied
non-affirmative acceptance -> denied
stale or altered terms hash -> denied
valid current acceptance -> relationship resolution permitted
relationship receipt remains bound to acceptance receipt hash
free-form evaluator objectives are preserved
catalog-tag matches are deterministic
explicit capability requests are intersected rather than trusted
package-denied capabilities cannot be admitted
unknown objectives remain unresolved rather than broadening scope
explicit evaluator restrictions always reduce effective scope
full LLM-adapter sovereign surface cannot be admitted as a direct evaluator route
effective scope grants no execution or repository authority
same inputs produce the same receipt hash
```

## Legal posture

The repository implements explicit electronic assent and durable version/hash binding. Electronic contracts and signatures are generally not denied legal effect solely because they are electronic under the U.S. E-SIGN framework, but jurisdiction-specific enforceability and any governing-law/forum provisions should be reviewed by qualified counsel before StegVerse represents these terms as legally final for a production public service.

## Release condition

Release when the Demo terms, acceptance implementation/schema/tests, SDK evaluation implementation/schemas/tests, demo-suite consumer contract, license manifest, and evaluator-scoped adapter entry contract are installed and validated without requiring GitHub Actions or an external runtime.
