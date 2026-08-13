# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
```

Live repository state, immutable commits, validation evidence, scoped mirror handoffs, and this file supersede prior chat claims. Historical detail remains available in Git history.

## Goal inventory

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002: COMPLETE_STATIC_VALIDATED_MERGED, NOT_RELEASED
```

No person-specific evaluator route is canonical.

## Public inspection governed binding

Source of truth: `docs/PUBLIC_INSPECTION_GOVERNED_BINDING_MIRROR_HANDOFF.md`

```text
merge_commit: e67f78f9a1b9730b8848a268a5abc896396f760d
implementation: stegverse/public_inspection.py
binding_tests: tests/test_public_inspection_governed_binding.py
validation: validation/PUBLIC_INSPECTION_GOVERNED_BINDING_2026-08-13.md
```

A bounded public inspection request now binds to the ordinary SDK option `0A` raw-data submission descriptor. Preparation does not claim a governed runtime run or exact-run custody and does not fabricate a receipt locator.

## Documentation and instructions

The current public/control surfaces for this goal are reconciled:

```text
README.md
SDK_README.md
docs/SDK_CONSOLE.md
docs/PUBLIC_INSPECTION_ENTRY.md
docs/PUBLIC_INSPECTION_ENTRY_MIRROR_HANDOFF.md
docs/PUBLIC_INSPECTION_GOVERNED_BINDING_MIRROR_HANDOFF.md
SDK_MIRROR_HANDOFF.md
```

`SDK_README.md` is a compatibility pointer so historical examples do not compete with the current SDK contract.

## Canonical flow

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

The SDK-local goal ends at preparation of the option `0A` descriptor. Downstream runtime and custody are not claimed by this handoff.

## Collaboration boundary

GitHub is a public collaboration and inspection carrier, not canonical runtime or custody. A pull request does not become evaluator/runtime code merely by being submitted. Untrusted PR code must not replace trusted SDK/StegGate processing.

Repository-native regression protection remains:

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

## Next integration goal

```text
goal: PUBLIC-INSPECTION-END-TO-END-CUSTODY-003
state: NEXT_NOT_CLAIMED
```

Prove one prepared public inspection request traverses admitted ordinary ingress, canonical StegCore governance, exact-run Master Records custody, caller projection, and returns a real `manifest_receipt_id` that can be independently replayed and reconstructed. The locator may then be posted back to the originating public PR as an observation.

## Release and propagation

The public-inspection binding is not yet a product release. Do not cut a product tag until the applicable release gates are satisfied. Site/Publisher/wiki propagation is not triggered merely by this merged but unreleased integration change.

## Archive condition

The SDK-local governed-binding goal is complete and durably transferred. Remaining work belongs to the explicitly named cross-repository end-to-end custody goal and does not require older chat history.
