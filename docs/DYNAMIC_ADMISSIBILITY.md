# Dynamic Admissibility Packets

Generated: `2026-06-14`

## Purpose

This document records SDK awareness of the dynamic admissibility packet shape now used by the StegVerse Site demo.

The Site demo accepts live tester packets. The SDK should be able to recognize the same packet family so Site, SDK, LLM adapter, and future runtime services share a common vocabulary.

## Core question

```text
What is this output, artifact, instruction, transition, or claim allowed to become?
```

## Dynamic path

```text
tester packet
→ discipline route
→ authority / evidence / replay / consequence checks
→ admissibility decision
→ result packet
→ receipt posture
```

## Schemas

```text
schemas/admissibility/tester-output.schema.json
schemas/admissibility/dynamic-demo-result.schema.json
```

## Tester packet role

A tester packet is a structured admissibility classification. It records:

```text
discipline
test object
recommended route
tests run
declared intent
authority source
evidence posture
replay posture
consequence level
claim limit
decision
allowed next state
required follow-up
boundary flags
```

## Boundary

The packet does not certify domain correctness.

The packet does not replace discipline review.

The packet does not create proof authority.

The packet only records posture and allowed-next-state classification.

## SDK relationship

The existing SDK flow remains valid:

```text
intent → admissibility evaluation → decision → receipt
```

Dynamic admissibility adds a richer input shape:

```text
discipline-aware tester packet
→ admissibility evaluation
→ allowed next state
→ receipt posture
```

## Site relationship

The Site demo is a browser-local public mirror for dynamic packet evaluation.

The SDK is the appropriate layer to add typed models, validation helpers, adapters, and receipt integration.

## Next integration steps

1. Add SDK model classes for tester-output and dynamic result packets.
2. Add validation helpers for `schemas/admissibility/*.schema.json`.
3. Add adapter method:

```python
sdk.evaluate_admissibility_packet(packet)
```

4. Keep browser-demo local hashes separate from SDK receipts.
