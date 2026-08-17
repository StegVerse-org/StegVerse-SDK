# Admissibility Composition Mirror Handoff

Updated: 2026-08-17

## Scope and authority

```text
goal_id: SDK-ADMISSIBILITY-COMPOSITION-002
originating_session_goal: test n>1 non-separability after n=1 matrix-maturity proof; individually admissible transitions must not imply their composition is admissible
repository: StegVerse-org/StegVerse-SDK
canonical_branch: main
implementation_branch: feat/admissibility-composition-002
parent_handoff: SDK_MIRROR_HANDOFF.md
predecessor_handoff: ADMISSIBILITY_MATRIX_MATURITY_MIRROR_HANDOFF.md
credential_authority: TV/TVC
non_TV_TVC_secret_or_token_allowed: false
GitHub_runtime_authority: NONE
Render_required: false
```

This scoped handoff is subordinate to `SDK_MIRROR_HANDOFF.md`. Existing `evaluation_relationship.py` concerns evaluator-to-capability selection and does not implement joint transition admissibility. Existing `admissibility_bundle.py` packages one tester/result/receipt tuple and does not infer composition admissibility. No matching open SDK issue or active scoped composition claim was found before implementation began.

## Active claim

```text
task_id: SDK-ADMISSIBILITY-COMPOSITION-002
claimant: current-session-admissibility-composition
role: CLAIMED_FOR_IMPLEMENTATION_AND_VALIDATION
claim_created_at: 2026-08-17T17:00:00-05:00
claim_release_condition: validated implementation merged to main or explicitly transferred to a canonical nonconflicting owner
collision_boundary:
  - stegverse/admissibility_composition.py
  - tests/test_admissibility_composition.py
  - .github/workflows/admissibility-composition-validation.yml
  - tasks/SDK-ADMISSIBILITY-COMPOSITION-002.json
  - ADMISSIBILITY_COMPOSITION_MIRROR_HANDOFF.md
```

## Formal invariant

The SDK must not infer joint admissibility from component admissibility:

```text
Adm(A) = true
Adm(B) = true
DOES NOT IMPLY Adm(A composed_with B) = true
```

Composition is a distinct candidate relation with its own state, consequence, evidence, and relation coverage. If every component is individually admissible but no explicit joint relation is established, consequential composition is `RELATION_UNRESOLVED` and must fail closed.

## Minimum n>1 falsification case

```text
A: individually ALLOW_WITH_POSTURE
B: individually ALLOW_WITH_POSTURE
A+B joint consequence: critical
explicit_joint_relation: absent
expected composition: FAIL_CLOSED
expected maturity: under_development
expected basis: no_explicit_composition_admissibility_relation
```

A second positive-control case must prove that an explicitly declared, non-high-consequence joint relation can be represented as known/conditionally admissible without granting execution authority.

## Required implementation

Explicit denominator: five deliverables.

1. Deterministic composition evaluator over two or more component admissibility results.
2. Verify each component's local receipt hash before composition reasoning; tampered or incomplete components fail closed.
3. Never lift component `ALLOW_*` dispositions into joint admissibility automatically.
4. Represent absent consequential joint relation as unresolved/under-development and `FAIL_CLOSED`.
5. Validate the n=2 non-separability falsification case and a positive explicit-joint-relation control in a credential-clean hosted run.

## Authority boundary

The composition evaluator is an SDK-side falsification and relation-coverage surface only. It does not execute component actions, certify domain correctness, create production authority, or substitute for canonical StegCore/StegGate/Master Records execution-boundary evaluation and custody.

## Validation target

```text
python -m pip install -e '.[dev]'
pytest -q tests/test_admissibility_composition.py tests/test_dynamic_admissibility.py tests/test_admissibility_bundle.py tests/test_admissibility_exchange.py
```

Hosted validation must assert absent `GITHUB_TOKEN`, `GH_TOKEN`, `TV_IDENTITY_KEY`, and `TVC_SECRET` before anonymously materializing the exact public source SHA.

## Cross-repository obligation

After merge, assess the same canonical consumers identified by the predecessor handoff. Do not propagate merely because the SDK implementation exists; read each consumer's applicable handoff and transfer only contract/vocabulary changes actually consumed there.

## Current completion

```text
task_completion: 0/5
developed_files: 1/5 required scoped surfaces (handoff only)
scaffolding_or_stubs: 0
missing_required_files: 4
validation: 0/2
integration: 0/1
goal_activation: 0%
```

## Archive condition

Do not archive this session while the n>1 composition requirement remains unique, claimed, and unvalidated. Release this claim after validated merge or durable transfer, then complete the downstream propagation assessment and session consolidation record.
