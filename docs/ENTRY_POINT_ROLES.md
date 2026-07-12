# StegVerse Entry-Point Roles

StegVerse entry points share session, transition, usage, receipt, and authority-boundary obligations, but they do not serve identical audiences or interaction types.

## Shared rule

```text
entry-point acceptance != authority
translation != admissibility
display != execution
session identity survives entry-point changes
usage lineage survives entry-point changes
```

The canonical machine-readable contract is `schemas/entry_point_role.schema.json`. The SDK registry is `stegverse/entry_point_roles.py`.

## StegVerse SDK

**Primary role:** developer-native programmatic intake, testing, integration, and observation boundary.

The SDK supports raw-data governance testing, module compatibility testing, schema validation, manifest generation, receipt validation, sandbox routing, runtime comparison, demos, and application integration. It should preserve developer-provided structures rather than forcing them into conversational formats.

Related roles include testing harness, integration contract, transport boundary, schema surface, and evidence-inspection tool.

## StegVerse LLM Adapter

**Primary role:** machine-readable translation and interoperability boundary.

The LLM Adapter accepts prompts, provider responses, tool traces, agent traces, recursive outputs, and external framework packages. It converts them into canonical intent, transition packages, telemetry envelopes, provider-neutral result structures, and receipt-ready machine-readable records.

It may perform the same broad interaction classes exposed through the SDK, but its distinguishing responsibility is translation between external model or framework activity and StegVerse contracts.

## StegVerse Ecosystem Chat

**Primary role:** universal browser interface for governed conversation, ecosystem discovery, development, testing, and orchestration.

Ecosystem Chat supports governed LLM-like conversation, capability discovery, guided testing, governed coding, governed research, governed social posting, module creation guidance, receipt and usage review, and cross-entry session continuation.

It is the broadest human-facing entry point. It may guide a user into SDK packages, LLM Adapter routes, governed runtimes, or ecosystem modules while preserving one session and transition lineage.

## Cross-entry continuity

A session may begin in Ecosystem Chat, export a developer package to the SDK, invoke the LLM Adapter, execute through a runtime, and return to the browser. Every hop must preserve:

```text
session_id
transition_id
parent_transition_id
origin_entry_point
current_processor
interaction_type
usage measurement identity
receipt references
```

## Usage responsibility

Each entry point emits usage events only for measurements it owns. Every measurement requires a stable `measurement_id` and `metric_owner` so the shared usage ledger can prevent double counting.

Examples:

```text
LLM Adapter owns provider-call and token measurements.
SDK owns SDK validation and orchestration measurements.
Runtime owns node, execution, closure, and runtime-cost measurements.
Ecosystem Chat owns browser interaction and presentation measurements.
Master-Records owns custody and persistence measurements.
```

## Extension rule

New entry points must publish a role declaration before they can claim cross-entry synchronization. Their declaration must describe audiences, accepted inputs, produced outputs, interaction types, usage behavior, continuity behavior, and authority boundaries.
