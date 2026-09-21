# Governed Wiki Publication Transition Mirror Handoff

Status: ACTIVE — SDK CANDIDATE-TO-MANIFEST SEAM IMPLEMENTATION
Goal Task ID: `GOVERNED-WIKI-PUBLICATION-TRANSITION-001`
COSV ID: NOT ESTABLISHED IN CANONICAL TASK REGISTRY

## Canonical goal

Bind an already-reviewed `external_framework_wiki_publication_transition` candidate through the existing StegVerse SDK external-manifest ingress, require Interlock/InTr-governed Master Records closure with:

- `state=RECORDED`
- `reconstruction_status=PASS`
- `required_evidence_validation_status=PASS`
- exact `receipt_sha256 == reconstructed_receipt_sha256`

and permit repository mutation only after that exact closure is verified.

## Existing predecessor chain

```text
public External Chat submission
-> compatibility receipt
-> cooperative review package
-> delegated review/correction receipt
-> external_framework_wiki_publication_transition
```

The publication transition remains a candidate only. Its contract requires `publication_executed=false`.

## Required successor chain

```text
publication-transition candidate
-> deterministic SDK manifest conversion
-> existing stegverse.ingress-manifest.v1 validation
-> existing SDK governance runtime
-> Interlock/InTr governed result
-> canonical Master Records closure
-> existing publication mutation adapter
-> repository mutation receipt
```

## Authority invariants

- submitter direct repository mutation authority: false
- publication candidate grants publication authority: false
- SDK manifest validation grants publication authority: false
- Interlock/InTr remains governed transition authority
- Master Records remains custody/reconstruction authority and grants no transition authority
- Publisher/mutation adapter may execute only after exact governed closure
- `DENY_PUBLICATION` and `REVIEW_REQUIRED` must never reach mutation
- no new runtime, scheduler, dispatcher, WorkerCoordinator, custody store, authority plane, credential path, or second user-operated device

## First implementation seam

Implement one deterministic SDK converter that consumes the existing publication-transition object without modifying it and emits the existing generic ingress manifest.

The converter must preserve and hash-bind:

- `package_id`
- `correction_receipt_id`
- `publisher_ref`
- `source_commit_ref`
- `target_path`
- target repository profile
- `decision`
- `evidence_references`
- `publication_executed=false`
- exact canonical publication-transition SHA-256

The converter must not claim execution, publication authorization, repository mutation authorization, certification, or standing.

## Downstream gate to repair

The existing LLM-adapter repository mutation route currently validates stored `ALLOW_PUBLICATION_CANDIDATE`, mutator identity/delegation/policy/freshness, repository head, and target blob. It does not yet require the exact SDK/Interlock/InTr/Master Records closure. That is the next existing seam after SDK conversion.

## Reuse scope

The contract must remain repository/path-profiled so it can serve Admissibility first and later StegGuardian, StegTalk, and SDK public documentation without enabling any target by default.

## Completion truth

Source implementation and tests are not completion. Completion requires authentic end-to-end retained evidence through governed closure and Publisher mutation, plus zero-mutation negative controls for non-ALLOW outcomes.
