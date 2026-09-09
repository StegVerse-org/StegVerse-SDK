# ELAN Test 1 Runbook

This runbook defines the first external-framework interoperability test for the SDK completion gate.

## Fixed human-event sequence

1. Emotional ambiguity statement.
2. Follow-up: `I don't know.`
3. Silence for the preregistered interval.

## Source-framework boundary

ELAN remains source-native. Only observable output/state that ELAN legitimately exposes may be placed in the source payload. Missing internal state must not be inferred or invented.

## Required evidence fields

1. human event/state
2. ELAN interpretation
3. ELAN proposed or withheld behavior
4. represented state submitted for processing
5. StegVerse governance disposition and resulting transition/non-transition
6. retrospective reconstruction

## Submission intent

Use the package Manifest Builder with:

- `source_framework=ELAN`
- `data_class=elan.relational-state.v1`
- `process=governance`
- installed route `stegverse.route.canonical-governed.v1`
- `return_depth=full-trace`

The evaluator declaration is preregistered before execution and retained as evidence metadata. It must not alter the governance disposition.

## Completion proof

The SDK completion gate requires exact-head evidence that the built manifest validates, resolves to the installed route, produces a governance result and `manifest_receipt_id`, records canonical custody, and supports replay plus reconstruction.
