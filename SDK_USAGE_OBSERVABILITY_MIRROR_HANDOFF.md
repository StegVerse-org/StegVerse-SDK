# SDK Usage Observability Mirror Handoff

## Authority

```text
goal_id: SDK-USAGE-OBSERVABILITY-001
active_subtask: SDK-USAGE-GOVERNED-OPERATION-WIRING-002
repository: StegVerse-org/StegVerse-SDK
branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
baseline_pull_request: #27 MERGED
baseline_merge_commit: 4daea2b6122576e6096609c8f0c65211d7539dc5
operation_wiring_pull_request: #28 MERGED
operation_wiring_merge_commit: 94342b56c022ee2710b17981c95a311a978d333f
active_task: tasks/SDK-USAGE-GOVERNED-OPERATION-WIRING-002.json
implementation_state: COMPLETE_VALIDATED_MERGED
validation_state: HOSTED_PASS_16_OF_16
integration_state: BLOCKED_ON_CANONICAL_PROVIDER_TRANSPORT_AND_TV_TVC_NOTIFICATION_ACTIVATION
release_state: SOURCE_RELEASED_INTEGRATION_INCOMPLETE
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

## Merged implementation

PR #27 merged the five-choice ledger/outbox/navigation instrumentation. PR #28 merged actual option `0`, `1`, and `2` execution observation wiring.

Installed canonical surfaces:

```text
stegverse/sdk_usage_observability.py
stegverse/governed_operations.py
stegverse/cli.py
tests/test_sdk_usage_observability.py
tests/test_cli_sdk_usage_observability.py
tests/test_governed_operations.py
.github/workflows/sdk-usage-observability.yml
tasks/SDK-USAGE-GOVERNED-OPERATION-WIRING-002.json
SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
```

The canonical `stegverse governance --select 000|00|0|1|2` path records one non-authoritative `MENU_SELECTION` only after canonical navigation accepts the choice.

`GovernedOperations` supplies the SDK execution adapter for actual option `0`, `1`, and `2` operations. It accepts injected canonical operation handlers because governance/custody transport authority belongs to StegCore/Master Records, not the SDK.

```text
option 0 submit
  -> require manifest_receipt_id + transaction_id + receipt_chain_head
  -> only then record GOVERNED_OPERATION COMPLETED
  -> malformed/failed operation records FAILED, never COMPLETED

option 1 replay
  -> require caller manifest_receipt_id
  -> require returned original_manifest_receipt_id exact match
  -> require consequence_reexecuted=false
  -> only then record GOVERNED_OPERATION COMPLETED

option 2 reconstruct
  -> require caller manifest_receipt_id
  -> require returned original_manifest_receipt_id exact match
  -> require consequence_reexecuted=false
  -> only then record GOVERNED_OPERATION COMPLETED
```

The adapter supplies no credential, creates no receipt-ID algorithm, creates no custody store, and grants no governance authority.

## Validation evidence

```text
PR: #28
validated head: d4b98a543142275431e770f19addf2aa437d57a8
workflow: SDK Usage Observability Validation
run: 31838717711
result: SUCCESS
dedicated test result: 16 passed
merge commit: 94342b56c022ee2710b17981c95a311a978d333f
```

The workflow uses `permissions: {}`, anonymously materializes public source, and explicitly requires process `GITHUB_TOKEN` and `GH_TOKEN` to be absent before executing the observability tests. This validates source behavior only; it does not grant runtime authority.

## Canonical provider dependency / convergence

Execution authority and locator semantics already belong to:

```text
StegVerse-Labs/StegCore/docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore#85
src/stegcore/manifest_receipts.py
src/stegcore/manifest_receipt_provider.py
master-records/orchestration canonical manifest-receipt custody surface
```

That handoff explicitly requires exposing the same provider contract to SDK callers. This SDK lane must not duplicate the receipt-ID algorithm, evaluator, custody service, or consequence boundary.

Integration release condition:

```text
StegCore admitted Master Records transport becomes available
-> bind submit/replay/reconstruct handlers into GovernedOperations
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

The implementation reports `observed_since` and must not call totals `since inception` unless older events are deterministically backfilled from inspectable provenance.

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
[done] hosted validation PASS for operation adapter
[done] PR #28 merged
[done] implementation claim released to integration blocker
[blocked] bind actual canonical StegCore/Master Records provider transport
[pending] TV/TVC relay PR #24 validation/merge
[pending] first real TV/TVC-owned GitHub dispatch observed by StegCore issue #117
[pending] evaluate deterministic pre-install historical backfill
```

## Machine-observable blockers

```text
SDK provider integration blocker:
  owner: StegVerse-Labs/StegCore + master-records/orchestration
  release: admitted manifest-receipt transport proves immutable resolve/replay/reconstruct contract and is exposed to SDK callers
  evidence: docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md + issue #85
  session role: observation/integration after release; no duplicate transport implementation

notification activation blocker:
  owner: StegVerse-Labs/TVC
  release: TV/TVC runtime executes accepted repository_dispatch and StegCore #117 records validated comment
  evidence: TVC-SDK-USAGE-NOTIFICATION-RELAY-001
```

## Session convergence / adjacent goals

The sovereign local-model/runtime goal is complete at source and must not be reopened:

```text
MERGED INTO: StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
source/formal model/discovery/private launch/inference/usage/proof: COMPLETE_RELEASED
live activation: MACHINE_OWNED via StegVerse-Labs/.github#60 -> TVC -> LLM-adapter -> master-records/orchestration
```

The trade-ready goal is also a separate canonical machine-owned workstream:

```text
MERGED INTO: StegVerse-Labs/stegfin-governance/docs/STEGFIN_MIRROR_HANDOFF.md
machine continuation: StegVerse-Labs/TVC/tasks/TVC-CAPABILITY-RUNTIME-002.json -> StegVerse-Labs/.github/handoffs/STEGFIN-CONTINUITY-CARRIER-007.json
terminal release: WALLET_HANDOFF_READY
wallet signing/broadcast: USER_ONLY
```

Canonical continuation for SDK usage observability:

```text
StegVerse-org/StegVerse-SDK/tasks/SDK-USAGE-GOVERNED-OPERATION-WIRING-002.json
-> StegVerse-Labs/StegCore/docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md
-> StegVerse-Labs/TVC/tasks/TVC-SDK-USAGE-NOTIFICATION-RELAY-001.json
-> StegVerse-Labs/StegCore#117
```

No Site, Publisher, admissibility-wiki, or stegguardian-wiki propagation is authorized yet because this feature has not reached end-to-end governed activation/release.

## Completion accounting

```text
required canonical source/control files for observability + adapter: 9
developed: 9/9
scaffolding/stubs: 0
missing required files: 0
validation deliverables: 3/3
integration deliverables: 3/6 (menu wiring + operation adapter + TVC durable relay ownership; provider binding + TVC live dispatch + StegCore receipt pending)
source implementation: COMPLETE_VALIDATED_MERGED
goal activation: 50% of six explicit integration deliverables
session consolidation: unique source requirements transferred; TVC relay implementation/validation remains an active separate lane
```
