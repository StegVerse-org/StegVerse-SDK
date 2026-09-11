# Shared Docs Multiparty Freeze Mirror Handoff

Updated: 2026-09-11
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Parent / adjacent task: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent WorkSpace handoff: `docs/SHARED_DOCS_EPHEMERAL_MANIFEST_WORKSPACE_MIRROR_HANDOFF.md`
Status: `ACTIVE / SOURCE IMPLEMENTED / EXACT-HEAD VALIDATION IN PROGRESS`

## Goal

Add a provider-neutral Shared Docs state machine in which each eligible reviewer can independently freeze the exact document revision they reviewed, the current revision becomes collectively frozen only when the configured freeze policy is satisfied, and any content change creates a new review revision whose eligible reviewers must freeze again.

This feature is coordination/provenance state. It does not itself grant document-edit authority, provider credentials, governance authority, historical-custody authority, or execution authority.

## Core invariant

A **document revision**, not a mutable logical document name, is the unit of freeze.

Once a revision becomes collectively frozen, that frozen revision remains immutable provenance. A later content edit does not mutate or erase that historical freeze. Instead it creates a successor revision and moves the logical document's current pointer to that new revision.

Therefore:

```text
frozen revision N
+ content edit
-> revision N remains frozen provenance
-> revision N+1 is created
-> all reviewer freezes for N+1 start unsatisfied
-> current logical document state becomes REVIEW_OPEN / UNFROZEN until policy is satisfied again
```

This resolves the apparent tension between "permanently frozen" and "any change unfreezes the document": prior frozen versions remain permanently frozen, while the newly current version is unfrozen.

## State model

Minimum revision states:

- `REVIEW_OPEN` — no collective freeze yet for the current revision.
- `PARTIALLY_FROZEN` — one or more eligible reviewers froze the exact revision, but policy is not yet satisfied.
- `FROZEN` — freeze policy is satisfied for the exact revision digest and reviewer set.
- `SUPERSEDED` — a later revision became current; this revision retains its historical freeze/provenance state.

A logical document may therefore point to a current `REVIEW_OPEN` revision while one or more prior revisions remain historically `FROZEN`.

## Reviewer freeze contract

Each reviewer freeze binds at minimum:

```text
document_id
revision_id
content_digest
review_epoch
reviewer_id
reviewer_role
frozen_at
freeze_receipt_id
```

A reviewer freeze is valid only for the exact `content_digest`, exact `revision_id`, exact eligible-reviewer set / `review_epoch`, and exact freeze policy in force when the review began.

A reviewer freeze MUST NOT float forward to later revisions.

## Eligible reviewers and freeze policy

Initial policy is intentionally strict:

```text
policy = ALL_ELIGIBLE
```

The current revision is collectively `FROZEN` only when every reviewer in the revision-bound eligible-reviewer set has an accepted freeze receipt for that same revision and digest.

Future M-of-N or role-class policies may be added only as explicit versioned policy extensions. They must not silently weaken an existing review epoch.

Changing the eligible-reviewer set or freeze policy creates a new review epoch and invalidates collective-freeze eligibility for the current review epoch unless the document is re-issued under the new epoch.

## Mutation semantics

Any normative content mutation MUST:

1. derive a new content digest;
2. create a new revision ID;
3. preserve the prior revision and all prior freeze receipts as immutable provenance;
4. reset the new revision's per-reviewer freeze state to unfrozen;
5. return the current logical document to `REVIEW_OPEN`;
6. require every eligible reviewer under the new review epoch to freeze the successor revision again.

No implementation may silently carry reviewer acceptance across a content change.

## Status metadata versus reviewed content

To avoid a self-invalidating freeze cycle, lifecycle state such as `REVIEW_OPEN`, `PARTIALLY_FROZEN`, or `FROZEN` SHOULD be maintained as document metadata / projection rather than embedded inside the content digest itself.

If a provider stores a visible status line inside the document body, modifying that body line is a content mutation and therefore creates a new revision under this contract. A provider UI may instead render the freeze status from lifecycle metadata without changing reviewed bytes.

## Edit after freeze

Editing a frozen revision is never an in-place mutation. The edit operation is modeled as:

```text
frozen revision -> successor draft/review revision
```

The prior frozen revision remains reconstructable and verifiable. The current logical document pointer moves to the successor revision only after the edit is admitted through the applicable document/provider authority.

## Required provenance

The Shared Docs module should preserve enough state to answer deterministically:

- which exact revision each reviewer froze;
- which digest they reviewed;
- which reviewer set and policy applied;
- whether collective freeze was ever achieved;
- what change caused a successor revision;
- which prior frozen revision was superseded;
- whether any reviewer freeze was invalidated by content or reviewer-set change.

## Authority boundary

```text
reviewer freeze receipt != document edit authority
reviewer freeze receipt != governance verdict
collective freeze != provider write authority
collective freeze != MIR historical custody
content mutation != automatic acceptance
provider storage != collective freeze proof
```

Provider/TVC authority remains responsible for provider mutations. Interlock/InTr remains responsible for governed transitions where applicable. Master Records may retain/reconstruct freeze provenance but does not become the document editor or reviewer.

## Implemented source

SDK PR `#202` installs:

```text
stegverse/shared_docs_freeze.py
tests/test_shared_docs_freeze.py
.github/workflows/shared-docs-multiparty-freeze-validation.yml
README.md
docs/SHARED_DOCS_MULTIPARTY_FREEZE_MIRROR_HANDOFF.md
```

Implemented behavior includes exact SHA-256 content binding, deterministic per-reviewer freeze receipts, `ALL_ELIGIBLE` evaluation, stale revision/digest rejection, edit-to-successor revision semantics, reviewer-set review-epoch reset, and preservation of prior frozen provenance.

The README now documents the externally meaningful Shared Docs collaboration semantics and includes the focused unit-test command.

## Canonical coordination registration

Canonical task registration merged through `StegVerse-Labs/.github` PR `#1430` at merge commit:

```text
8c46421bab695d99f2cc6c419fdda11512fa99e8
```

The task is `ACTIVE` in the canonical Task Registry shard.

COSV task projection `71000000100110` merged through `.github` PR `#1431` at merge commit:

```text
b8a8899a9ba6171b4279578afb3f38d85dbf5c4b
```

Task/COSV registration is coordination only and grants no execution authority.

## Validation history

The first dedicated Shared Docs validation run `34568617386` failed before executing any freeze-state assertion because a bare Python runner imported the SDK package without installing its declared runtime dependency `requests`.

```text
failure_class: VALIDATION_ENVIRONMENT_DEPENDENCY_MISSING
implementation assertion failure: NO
reported error: ModuleNotFoundError: No module named 'requests'
```

`pyproject.toml` already declares `requests>=2.28.0`. The workflow was repaired to install the SDK (`python -m pip install -e .`) before executing `python -m unittest tests.test_shared_docs_freeze`.

That repair is committed on SDK PR `#202`; exact-head revalidation is now the required next predicate. No source-validation PASS is claimed until the dedicated exact-head workflow passes.

Existing SDK validation surfaces on the preceding implementation head passed, including WorkSpace Active Probe, Manifest Builder, External Collaboration runtime-proof-contract validation, Evaluator Manifest, Evaluator Contract Console, and SDK Package Artifact validation. These passes do not substitute for the dedicated freeze-state test on the final head.

## MIR v0.3 motivating case

The bilaterally frozen MIR × StegVerse Separation-of-Powers Evidence Contract v0.3 exposed the need for this module capability:

- StegVerse independently accepted/froze v0.3;
- MIR independently accepted/froze the same normative version;
- mutual acceptance established bilateral freeze;
- a later status-display change should not silently mutate the previously reviewed normative text.

This is a motivating example only; the module remains generic and provider-neutral.

## Completion boundary

Source completion requires an exact-head PASS of the deterministic Shared Docs freeze tests and the applicable repository validation surfaces, followed by merge of SDK PR `#202`. Runtime/provider synchronization is a separate proof class and must not be inferred from source/CI validation.

## Current state / next action

```text
canonical task registration: MERGED
COSV projection: MERGED
source implementation: PRESENT ON PR #202
README integration: PRESENT ON PR #202
dedicated validation first run: FAILED — runner dependency setup only
dependency remediation: COMMITTED
exact-head post-remediation validation: IN PROGRESS / PENDING OBSERVATION
SDK PR #202 merge: NOT YET CLAIMED
provider/runtime synchronization: NOT CLAIMED
```

Next: observe the exact-head dedicated Shared Docs Multiparty Freeze Validation and the applicable SDK workflows. Merge PR #202 only after the final head is green, then reconcile this handoff with the merge evidence without promoting source validation into provider/runtime proof.
