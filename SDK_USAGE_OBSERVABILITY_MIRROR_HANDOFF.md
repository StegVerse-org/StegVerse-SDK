# SDK Usage Observability Mirror Handoff

## Authority

```text
goal_id: SDK-USAGE-OBSERVABILITY-001
active_subtask: SDK-USAGE-GOVERNED-OPERATION-WIRING-002
repository: StegVerse-org/StegVerse-SDK
branch: feat/sdk-governed-operation-wiring
parent_handoff: SDK_MIRROR_HANDOFF.md
baseline_pull_request: #27 MERGED
baseline_merge_commit: 4daea2b6122576e6096609c8f0c65211d7539dc5
active_task: tasks/SDK-USAGE-GOVERNED-OPERATION-WIRING-002.json
implementation_state: BASELINE_MERGED_OPERATION_ADAPTER_IMPLEMENTED_PENDING_VALIDATION
validation_state: BASELINE_HOSTED_TESTS_PASS_OPERATION_ADAPTER_TEST_PENDING
release_state: NOT_RELEASED
credential_authority: NONE_IN_SDK; TV/TVC_FOR_NOTIFICATION_RELAY
```

## Goal

Record disclosure-safe usage of every canonical governance navigation choice so observed use, rather than intuition, can determine whether optional choices remain useful, while distinguishing navigation from actual governed execution.

Canonical choices:

```text
000 = Demo test sequence without user-supplied manifest
00  = User-defined run parameters
0   = Submit data for governance
1   = Replay previously run set
2   = Reconstruct previously run set
```

## Counting correction

A menu selection and an actual governed operation are not the same event.

```text
activity_kind: MENU_SELECTION | GOVERNED_OPERATION
```

`000` and `00` are navigation/configuration surfaces. For `0`, `1`, and `2`, menu selection is observed separately from actual governed execution. Selecting replay/reconstruct guidance therefore never counts as replay/reconstruction of a governed run.

## Baseline merged implementation

PR #27 is merged at `4daea2b6122576e6096609c8f0c65211d7539dc5`.

Installed baseline surfaces:

```text
stegverse/sdk_usage_observability.py
stegverse/cli.py
tests/test_sdk_usage_observability.py
tests/test_cli_sdk_usage_observability.py
.github/workflows/sdk-usage-observability.yml
SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
```

The canonical `stegverse governance --select 000|00|0|1|2` path records one non-authoritative `MENU_SELECTION` after the canonical navigation choice is accepted.

## Actual governed-operation execution adapter

Current branch installs:

```text
stegverse/governed_operations.py
tests/test_governed_operations.py
tasks/SDK-USAGE-GOVERNED-OPERATION-WIRING-002.json
```

`GovernedOperations` is the SDK execution adapter for actual option `0`, `1`, and `2` calls. It accepts injected canonical operation handlers because governance/custody transport authority belongs to StegCore/Master Records, not the SDK.

Semantics:

```text
option 0 submit
  -> handler must return manifest_receipt_id + transaction_id + receipt_chain_head
  -> only then record GOVERNED_OPERATION COMPLETED
  -> malformed/failed operation records FAILED, never COMPLETED

option 1 replay
  -> caller supplies manifest_receipt_id
  -> returned original_manifest_receipt_id must match exactly
  -> consequence_reexecuted must be false
  -> only then record GOVERNED_OPERATION COMPLETED

option 2 reconstruct
  -> caller supplies manifest_receipt_id
  -> returned original_manifest_receipt_id must match exactly
  -> consequence_reexecuted must be false
  -> only then record GOVERNED_OPERATION COMPLETED
```

The adapter supplies no credential, creates no receipt-ID algorithm, creates no custody store, and cannot grant governance authority. It binds observations only after the canonical handler provides required evidence.

## Canonical provider dependency / convergence

The execution authority and locator semantics already exist in:

```text
StegVerse-Labs/StegCore/docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore#85
src/stegcore/manifest_receipts.py
src/stegcore/manifest_receipt_provider.py
master-records/orchestration canonical manifest-receipt custody surface
```

That handoff explicitly requires exposing the same provider contract to SDK callers. This SDK lane must not duplicate the receipt-ID algorithm, evaluator, custody service, or consequence boundary.

Current integration release condition:

```text
StegCore admitted Master Records transport becomes available
-> bind its submit/replay/reconstruct calls into GovernedOperations
-> prove one option 0, 1, and 2 operation through canonical transport
-> verify each emits one GOVERNED_OPERATION observation
-> verify replay/reconstruct never re-execute consequence
```

## Local observation stores

```text
~/.stegverse/sdk-usage-events.jsonl
~/.stegverse/sdk-usage-notification-outbox.jsonl
```

Overrides:

```text
STEGVERSE_SDK_USAGE_LEDGER
STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX
```

The ledger and outbox contain no SDK payload, policy body, credential, token, or authority-bearing material.

## Historical boundary

```text
historical_coverage: OBSERVED_ONLY
```

The implementation reports `observed_since` and must not call the total `since inception` unless older events are deterministically backfilled from inspectable provenance.

## Notification continuation

The safe outbox schema is:

```text
stegcore.sdk_usage_notification.v1.1
```

The TV/TVC consumer is durably owned by:

```text
StegVerse-Labs/TVC/docs/SDK_USAGE_NOTIFICATION_RELAY_MIRROR_HANDOFF.md
StegVerse-Labs/TVC/tasks/TVC-SDK-USAGE-NOTIFICATION-RELAY-001.json
StegVerse-Labs/TVC#24
```

The SDK holds no GitHub credential. TV/TVC is the only credential authority for the GitHub notification relay. GitHub remains a notification projection only.

## Hosted validation evidence

Baseline PR #27 hosted validation passed before merge. The new operation-adapter tests are installed but have not yet produced a hosted execution receipt; do not claim the adapter VALIDATED or RELEASED until that run succeeds.

## Completion requirements

```text
[done] canonical five-choice labels resolved from SDK source
[done] append-only disclosure-safe local ledger installed
[done] lifetime and trailing-30-day counts installed
[done] percent / last-used / runtime / status counts installed
[done] MENU_SELECTION vs GOVERNED_OPERATION distinction installed
[done] canonical governance CLI navigation wired for all five menu selections
[done] local safe-notification outbox installed
[done] payload/authority non-disclosure invariants installed
[done] baseline tests installed and hosted validation PASS
[done] baseline PR #27 merged
[done] actual option 0/1/2 execution adapter installed
[done] option 0/1/2 adapter tests installed
[done] durable operation-wiring task/claim installed
[pending] hosted validation PASS for operation adapter
[pending] merge operation-adapter branch
[blocked] bind actual canonical StegCore/Master Records provider transport
[pending] TV/TVC relay PR #24 validation/merge
[pending] first real TV/TVC-owned GitHub dispatch observed by StegCore issue #117
[pending] evaluate deterministic pre-install historical backfill
[pending] reconcile parent SDK_MIRROR_HANDOFF.md after operation adapter merge
```

## Machine-observable blockers

```text
SDK provider integration blocker:
  owner: StegVerse-Labs/StegCore + master-records/orchestration
  release: admitted manifest-receipt transport proves immutable resolve/replay/reconstruct contract
  evidence: docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md + issue #85

notification activation blocker:
  owner: StegVerse-Labs/TVC
  release: TV/TVC runtime executes accepted repository_dispatch and StegCore #117 records validated comment
  evidence: TVC-SDK-USAGE-NOTIFICATION-RELAY-001
```

## Session consolidation

The local sovereign model/runtime goal is not unique to this SDK lane and must not be reopened. It is already source-complete in `StegVerse-002/micro-node-runtime#22` and transferred to the machine-owned route recorded by `StegVerse-Labs/TVC/docs/SOVEREIGN_LOCAL_MODEL_ROUTE_MIRROR_HANDOFF.md`.

Canonical continuation for this goal:

```text
StegVerse-org/StegVerse-SDK/tasks/SDK-USAGE-GOVERNED-OPERATION-WIRING-002.json
-> StegVerse-Labs/StegCore/docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md
-> StegVerse-Labs/TVC/tasks/TVC-SDK-USAGE-NOTIFICATION-RELAY-001.json
-> StegVerse-Labs/StegCore#117
```

## Completion accounting

```text
required canonical source/control files for observability + adapter: 9
developed: 9/9
scaffolding/stubs: 0
validation deliverables: 2/3 (baseline source tests + baseline hosted validation; adapter hosted validation pending)
integration deliverables: 3/6 (menu wiring + operation adapter + TVC durable relay ownership; provider binding + TVC live dispatch + StegCore receipt pending)
goal activation: NOT COMPLETE
```
