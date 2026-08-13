# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
```

Live repository state, immutable commits, validation evidence, scoped mirror handoffs, and this file supersede prior chat claims.

## Goal inventory

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002: COMPLETE_STATIC_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-TEST-004: COMPLETE_CONTRACT_VALIDATED_MERGED, NOT_RELEASED
```

No person-specific evaluator route is canonical.

## Governed public inspection TEST runtime

```text
source_of_truth: docs/PUBLIC_INSPECTION_GOVERNED_TEST_RUNTIME_MIRROR_HANDOFF.md
merge_pr: #21
merge_commit: 4d98e6e51f86e15f3262e67fe36eaad61f99778d
validation: validation/PUBLIC_INSPECTION_GOVERNED_TEST_RUNTIME_2026-08-13.md
pinned_stegcore: 8774a024ba6efe7e45d0846db70362f1836e7f36
```

The public SDK now has two distinct request operations:

```text
PREPARE -> validate/bind request without running governance
TEST    -> run canonical StegCore governance and return a test result
```

Python 3.11+ governed TEST command:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```

The TEST result includes `governance_state`, `manifest_receipt_id`, `transaction_id`, chain verification, exact-run evidence, and reconstruction. CLI defaults persist the local run in append-only StegCore test files. In-memory programmatic use does not claim persistence.

Local TEST retention is distinct from production Master Records custody. Production custody still requires the separately admitted Master Records transport and readiness gates.

## Public PR boundary

A public PR is a visible declarative request/discussion record. It can retain the request and a labeled local TEST result. PR-supplied code is not used as the evaluator/runtime.

## Cross-repository ownership

```text
LLM transport/translation: StegVerse-org/LLM-adapter
Canonical governance/exact-run semantics: StegVerse-Labs/StegCore
Production exact-run custody: master-records/orchestration
```

## Remaining stronger goal

```text
goal: PUBLIC-INSPECTION-END-TO-END-CUSTODY-003
state: PRODUCTION_CUSTODY_NOT_YET_CLAIMED
```

The remaining gap is production shared custody and independent shared-backing replay/reconstruction, not the ability to submit public SDK test data and get a governed result.

## Release state

The governed TEST runtime is merged but not yet tagged/released. Release propagation is not yet triggered.
