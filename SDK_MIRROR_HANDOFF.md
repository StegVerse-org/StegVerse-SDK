# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
```

Live repository state, immutable commits, validation evidence, scoped mirror handoffs, and this file supersede prior chat claims. Detailed historical handoff revisions remain available in Git history.

## Completed canonical goals

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED, NOT_RELEASED
```

The public SDK remains person-independent. No recipient-specific evaluator route is canonical.

## Current active goal

```text
goal_id: SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002
source_of_truth: docs/PUBLIC_INSPECTION_GOVERNED_BINDING_MIRROR_HANDOFF.md
branch: feat/public-inspection-governed-binding
state: INSTALLED_PENDING_VALIDATION
release_state: NOT_RELEASED
```

Purpose: bind a bounded public inspection request to the ordinary SDK option `0A` raw-data submission descriptor without creating a separate evaluator/runtime or falsely claiming that runtime execution or Master Records custody occurred.

Installed implementation for the active goal:

```text
stegverse/public_inspection.py
tests/test_public_inspection_governed_binding.py
```

Documentation/instruction reconciliation for the active goal:

```text
README.md
SDK_README.md
docs/SDK_CONSOLE.md
docs/PUBLIC_INSPECTION_ENTRY.md
docs/PUBLIC_INSPECTION_ENTRY_MIRROR_HANDOFF.md
docs/PUBLIC_INSPECTION_GOVERNED_BINDING_MIRROR_HANDOFF.md
SDK_MIRROR_HANDOFF.md
```

## Canonical public inspection boundary

```text
public PR or local request
-> bounded declarative validation
-> ordinary SDK option 0A descriptor
-> trusted governed ingress
-> canonical governance / consequence boundary
-> canonical Master Records custody
-> caller projection
-> actual manifest_receipt_id may be associated with the public record
```

The SDK goal currently implemented in this repository stops at preparation of the option `0A` descriptor. Until the downstream governed path actually runs, preparation must report no runtime run, no custody claim, and no fabricated receipt locator.

## GitHub / authority boundary

GitHub is an optional public collaboration and inspection carrier. It is not canonical StegVerse runtime, release, custody, or protected capability authority. Public pull requests do not become evaluator code merely by being submitted. Untrusted PR code must not be substituted for trusted SDK/StegGate processing.

The existing repository-native fallback-boundary validator and tests remain authoritative regression protection:

```text
scripts/verify_github_fallback_boundary.py
tests/test_github_fallback_boundary.py
```

## Cross-repository ownership

```text
Evaluator relationship: docs/EVALUATION_RELATIONSHIP_MIRROR_HANDOFF.md
Public inspection entry: docs/PUBLIC_INSPECTION_ENTRY_MIRROR_HANDOFF.md
Public inspection governed binding: docs/PUBLIC_INSPECTION_GOVERNED_BINDING_MIRROR_HANDOFF.md
Provider/runtime translation where applicable: StegVerse-org/LLM-adapter
Canonical governance: StegVerse-Labs/StegCore
Exact-run custody: master-records/orchestration
Local model/runtime: StegVerse-002/micro-node-runtime
```

The SDK must not duplicate those downstream owners.

## Validation required for the active goal

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m stegverse.public_inspection inspection/examples/example-request.json
python scripts/verify_github_fallback_boundary.py
python -m unittest tests.test_github_fallback_boundary
```

## Release and propagation

The active goal is not yet released. Do not cut a product tag until the applicable release authority and release gates are satisfied. Site/Publisher/wiki propagation is not triggered merely by an unmerged or unreleased SDK integration change.

## Continuation

After this SDK binding is validated and merged, the next integration goal is to prove the same prepared request traverses admitted ordinary ingress, canonical StegCore governance, exact-run Master Records custody, caller projection, and returns a real `manifest_receipt_id` that can be independently replayed/reconstructed. That cross-repository goal must be evidenced before it is called active or complete.

This repository is **not archive-ready for the active goal** until the current branch is validated, merged, and the scoped handoff is reconciled on `main`.
