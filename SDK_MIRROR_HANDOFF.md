# SDK Mirror Handoff

## Source of truth

This file is the current handoff and task source of truth for `StegVerse-org/StegVerse-SDK`.

## Active goal

```text
Goal: SDK-origin governed transition candidate emission
Phase: emitter-fixture-validator-tests-and-workflow-installed
Result: LOCAL_IMPLEMENTATION_INSTALLED_VALIDATION_PENDING
```

## Architecture

```text
SDK-origin request
-> emit schema-compatible DECLARED transition candidate
-> hybrid-collab-bridge normalization
-> Ecosystem-Delegation decision
-> master-records/orchestration lifecycle
-> final receipt / custody / reconstruction
-> Site projection
```

The SDK is a sibling input nest. It does not grant execution, delegation, publication, orchestration, final-receipt, or Master-Records authority.

## Installed files

```text
stegverse/transition_candidate.py
examples/sdk_transition_candidate.json
scripts/verify_sdk_transition_candidate.py
tests/test_transition_candidate.py
.github/workflows/sdk-demo-test.yml
```

The emitter uses the canonical relationship shape owned by `master-records/orchestration` and emits:

```text
origin_class: SDK_INPUT
lifecycle_state: DECLARED
admissibility_result: PENDING
commit_time_validity: PENDING
final_receipt_id: null
master_record_status: NOT_YET_SUBMITTED
```

## Preserved HPS role

```text
StegVerse-org/HPS-runtime -> runtime standing state
StegVerse-Labs/hybrid-collab-bridge -> sibling input normalization
StegVerse-Labs/Ecosystem-Delegation -> governed delegation evaluation
master-records/orchestration -> lifecycle, receipts, custody references, reconstruction
```

## Next task

```text
1. Verify sdk-demo-test workflow.
2. Connect SDK candidate output to hybrid-collab-bridge normalization.
3. Record observed workflow evidence in master-records/orchestration.
4. Preserve transition_id and run_id through delegation and final receipt.
```

## Boundary

A candidate manifest is not execution authority. SDK route ALLOW permits only progression to the next governed boundary.

## Archive readiness

This handoff contains the complete current SDK transition-candidate state. Earlier thread context is not required.
