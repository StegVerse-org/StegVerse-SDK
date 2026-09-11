# Shared Docs Multiparty Freeze Mirror Handoff

Updated: 2026-09-11
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SHARED-DOCS-MULTIPARTY-FREEZE-001`
COSV: `71000000100110`
Parent / adjacent task: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent WorkSpace handoff: `docs/SHARED_DOCS_EPHEMERAL_MANIFEST_WORKSPACE_MIRROR_HANDOFF.md`
Status: `SOURCE COMPLETE / MERGED / PROVIDER SYNCHRONIZATION SEPARATE`

## Goal

Add a provider-neutral Shared Docs state machine in which each eligible reviewer can independently freeze the exact document revision they reviewed, collective freeze occurs only when the configured revision-bound policy is satisfied, and any content/reviewer-policy change creates a new review revision without erasing prior frozen provenance.

## Core invariant

A **document revision**, not a mutable logical document name, is the unit of freeze.

```text
frozen revision N
+ content edit
-> revision N remains frozen provenance
-> revision N+1 is created
-> reviewer freezes do not carry forward
-> current logical document becomes REVIEW_OPEN / UNFROZEN
```

Initial policy remains `ALL_ELIGIBLE`. A valid reviewer freeze binds the exact `document_id + revision_id + content_digest + review_epoch + reviewer_id + reviewer_role + frozen_at + freeze_receipt_id`.

Lifecycle status is metadata/projection where possible. Changing visible lifecycle metadata should not require mutating reviewed content bytes. If a provider embeds a status line inside reviewed body content, changing that line is a new revision.

## Authority separation

```text
reviewer freeze receipt != document edit authority
reviewer freeze receipt != governance verdict
collective freeze != provider write authority
collective freeze != MIR historical custody
content mutation != automatic acceptance
provider storage != collective freeze proof
```

Provider/TVC retains provider credential and mutation authority. Interlock/InTr retains governed transition authority where applicable. Master Records may retain/reconstruct freeze provenance but does not become editor or reviewer.

## Merged source evidence

SDK PR `#202` exact head:

```text
38bc22dd8341c6cea97586229bbd4a9c48d6c56d
```

Exact-head validation PASS:

```text
Shared Docs Multiparty Freeze Validation 34568759924 PASS
Manifest Builder Source Validation 34568759892 PASS
External Collaboration Authentic Runtime Proof Contract Validation 34568759896 PASS
Evaluator Manifest Source Validation 34568759884 PASS
WorkSpace Active Probe Validation 34568759906 PASS
Evaluator Contract Console Validation 34568759890 PASS
SDK Package Artifact Validation 34568759899 PASS
```

PR `#202` was squash-merged to `main` as:

```text
d505e937dd9f5e531c56427d7477e026789e4769
```

Merged source includes:

```text
stegverse/shared_docs_freeze.py
tests/test_shared_docs_freeze.py
.github/workflows/shared-docs-multiparty-freeze-validation.yml
README.md
docs/SHARED_DOCS_MULTIPARTY_FREEZE_MIRROR_HANDOFF.md
```

Implemented and validated source behavior includes SHA-256 revision binding, deterministic reviewer freeze receipts, `ALL_ELIGIBLE` collective evaluation, stale revision/digest rejection, edit-to-successor semantics, reviewer-set review-epoch reset, and preservation of prior frozen provenance.

## Canonical coordination evidence

Canonical task registration merged through `.github` PR `#1430` at `8c46421bab695d99f2cc6c419fdda11512fa99e8`.

COSV projection `71000000100110` merged through `.github` PR `#1431` at `b8a8899a9ba6171b4279578afb3f38d85dbf5c4b`.

## Scope completion

The source task's completion predicate is satisfied: deterministic source exists, the dedicated exact-head freeze validation and applicable SDK validations passed, and the implementation is merged on SDK `main`.

This does **not** prove any external provider has synchronized freeze metadata, enforced edit-to-successor semantics, or persisted reviewer receipts. Provider/runtime synchronization is a separate proof class and should continue under a successor task rather than keeping the source task artificially open.

## Successor trajectory

Successor task:

```text
SHARED-DOCS-PROVIDER-FREEZE-INTEGRATION-001
```

Purpose: bind the merged provider-neutral freeze state machine to Shared Docs provider observations/mutations while preserving TV/TVC provider authority, Interlock/InTr transition authority, immutable prior revision provenance, and one-device operation. Source merge alone must not be promoted into provider/runtime proof.

## MIR relationship

The MIR × StegVerse v0.3 contract was the motivating example for this generic capability. MIR experiment-specific frozen screenshot evidence remains a separate task and is not subsumed here.
