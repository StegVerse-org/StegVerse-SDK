# SDK Usage Observability Mirror Handoff

## Authority

```text
goal_id: SDK-USAGE-OBSERVABILITY-001
repository: StegVerse-org/StegVerse-SDK
branch: feat/sdk-usage-observability
parent_handoff: SDK_MIRROR_HANDOFF.md
implementation_state: INSTALLED_UNVALIDATED
release_state: NOT_RELEASED
```

## Goal

Record disclosure-safe usage of every canonical governance navigation choice so observed use, rather than intuition, can determine whether optional choices remain useful.

Canonical choices, resolved from `stegverse/governance_navigation.py`:

```text
000 = Demo test sequence without user-supplied manifest
00  = User-defined run parameters
0   = Submit data for governance
1   = Replay previously run set
2   = Reconstruct previously run set
```

## Counting correction

A menu selection and an actual governed operation are not the same event.

The usage record therefore carries:

```text
activity_kind: MENU_SELECTION | GOVERNED_OPERATION
```

`000` and `00` are currently navigation/configuration surfaces, so their usefulness is measured by actual menu selections. For `0`, `1`, and `2`, menu selection may be observed separately from a later actual governed operation. This prevents a user who merely asks for replay guidance from being reported as having replayed a governed run.

## Installed surfaces

```text
stegverse/sdk_usage_observability.py
stegverse/cli.py
tests/test_sdk_usage_observability.py
tests/test_cli_sdk_usage_observability.py
SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
```

The canonical `stegverse governance --select 000|00|0|1|2` path now validates the choice through the existing governance-navigation implementation and then records one non-authoritative `MENU_SELECTION` observation.

## Local observation stores

Default paths:

```text
~/.stegverse/sdk-usage-events.jsonl
~/.stegverse/sdk-usage-notification-outbox.jsonl
```

Overrides:

```text
STEGVERSE_SDK_USAGE_LEDGER
STEGVERSE_SDK_USAGE_NOTIFICATION_OUTBOX
```

The ledger and outbox contain no SDK payload, policy body, credential, token, or authority-bearing material. They are outside Master Records and exist only for operational observability.

## Metrics

For each of `000`, `00`, `0`, `1`, `2`:

```text
lifetime observed invocations
trailing 30-day invocations
percent of all observed choices
last-used timestamp
unique runtime identities
completed / failed / cancelled / active counts
menu-selection count
governed-operation count
```

Aggregates:

```text
core choices 0+1+2
all choices 000+00+0+1+2
```

## Historical boundary

The implementation starts with:

```text
historical_coverage: OBSERVED_ONLY
```

It MUST report `observed_since` using the earliest retained event and MUST NOT describe that total as `since inception` unless older historical SDK activity is deterministically backfilled from inspectable provenance.

## Notification boundary

Each accepted observation is also placed in a disclosure-safe local notification outbox using schema:

```text
stegcore.sdk_usage_notification.v1.1
```

The outbox is intended for a TV/TVC-owned bridge. The SDK itself does not hold or select a GitHub credential. GitHub remains a notification projection, not canonical custody or authority.

## Failure behavior

Usage observation is intentionally non-authoritative. If its local ledger/outbox cannot be written or validated, the CLI emits an explicit warning but the governance-navigation operation is not converted into an authorization failure.

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
[done] tests installed
[pending] hosted/repository tests PASS
[pending] open and merge implementation PR
[pending] wire actual option 0/1/2 governed execution call sites to `record_governed_operation`
[pending] connect TV/TVC outbox consumer to StegCore repository-dispatch notification projection
[pending] first real GitHub notification observed
[pending] evaluate whether deterministic pre-install historical usage can be backfilled
[pending] reconcile parent SDK_MIRROR_HANDOFF.md after merge
```

## Activation boundary

Menu-selection counting is installed on the feature branch. Full SDK usage observability is not ACTIVATED until the branch is merged/released, actual option `0`/`1`/`2` governed operations are instrumented at their canonical execution call sites, and a TV/TVC-owned bridge successfully projects a real event to the StegCore notification issue.
