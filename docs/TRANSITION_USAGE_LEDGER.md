# Cross-Entry Transition Usage Ledger

The transition usage ledger is a shared ecosystem surface. It is not owned by Ecosystem Chat, the SDK, or the LLM Adapter alone.

## Purpose

Every synchronized entry point emits usage records using the same contract so one session may be observed across browser, SDK, adapter, runtime, and custody boundaries.

```text
Ecosystem Chat
SDK
LLM Adapter
External Chat
CLI / API
future entry points
    -> TRANSITION_USAGE_RECORDED
    -> shared session lineage
    -> deduplicated usage ledger
    -> transition prepend and session timeline
```

## Required identity

Each event preserves:

```text
measurement_id
session_id
transition_id
parent_transition_id
origin_entry_point
entry_point
entry_point_role
interaction_type
metric_owner
measurement_source
receipt_refs
```

The combination of `measurement_id` and `metric_owner` is the initial deduplication key.

## Ownership rule

Each component reports only measurements it owns.

```text
SDK              validation and orchestration measurements
LLM Adapter      provider calls, tokens, provider latency, recursive traces
Runtime          node activation, execution, closure, runtime cost
Ecosystem Chat   browser interaction and presentation measurements
Master-Records   custody and persistence measurements
```

Rendering a measurement does not make the renderer its owner.

## Evidence classes

Every metric remains classified as one of:

```text
MEASURED
CONFIGURED
DERIVED
UNAVAILABLE
```

Configured or modeled values cannot silently become measured values during aggregation.

## Transition prepend

A browser or other presentation surface may prepend a transition with a usage summary, but the prepend is rendered metadata rather than part of the provider or governed output hash.

Example:

```text
Session: session-001
Transition: transition-009
Entry point: Ecosystem Chat
Current processor: LLM Adapter
Interaction: governed coding
Evidence: MEASURED
Model calls: 2
Input tokens: 1842
Output tokens: 614
Governance checks: 5
Receipts: 3
Transition cost: 0.0124 USD
Transition latency: 2460 ms
```

## Session aggregation

`aggregate_session_usage()`:

- rejects mixed session identities;
- deduplicates repeated measurements;
- preserves entry-point and transition membership;
- sums only matching metric names, units, and evidence classes;
- excludes unavailable values from totals without hiding them;
- emits a deterministic aggregation hash.

## Authority boundary

```text
usage event != authority
usage event != admissibility
display != execution
session aggregation != standing
usage total != proof of universal superiority
```

The ledger describes what a transition consumed and where the measurement came from. It does not authorize the transition or establish that one route is universally better than another.

## Implementation files

```text
schemas/transition_usage_event.schema.json
stegverse/transition_usage.py
tests/test_transition_usage.py
stegverse/entry_point_roles.py
docs/ENTRY_POINT_ROLES.md
```

## Remaining ecosystem integrations

```text
StegVerse-org/LLM-adapter
  -> emit provider and recursive-route usage events

StegVerse-org/core-node-runtime-demo
  -> emit runtime/node/closure usage events

StegVerse-Labs/Site
  -> transition prepend component
  -> cross-entry session ledger page
  -> entry-point and processor timeline

master-records
  -> canonical custody
  -> deduplication index
  -> session and transition lineage reconstruction
```
