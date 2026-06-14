# Dynamic Admissibility Packets

Generated: `2026-06-14`

## Purpose

This document records SDK awareness of the dynamic admissibility packet shape now used by the StegVerse Site demo.

The Site demo accepts live tester packets. The SDK now includes a dependency-free helper module that recognizes the same packet family so Site, SDK, LLM adapter, and future runtime services share a common vocabulary.

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

## SDK helper module

```text
stegverse/admissibility.py
```

Current helper functions:

```python
validate_tester_packet(packet)
evaluate_admissibility_packet(packet, strict=False)
result_to_decision(result)
stable_hash(payload)
```

Example:

```python
from stegverse.admissibility import evaluate_admissibility_packet

result = evaluate_admissibility_packet(packet)
print(result["classification"]["decision"])
print(result["classification"]["allowed_next_state"])
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

The current helper is local and side-effect free. It can be used before receipt-backed execution or integrated into future adapters.

## Site relationship

The Site demo is a browser-local public mirror for dynamic packet evaluation.

The SDK is the appropriate layer to add typed models, validation helpers, adapters, and receipt integration.

## Run example

```bash
python examples/dynamic_admissibility_packet.py
```

## Run tests

```bash
pytest tests/test_dynamic_admissibility.py
```

The test file covers valid research-note posture, missing-authority review, high-consequence fail-closed behavior, receipt-backed allow-with-posture behavior, strict validation failure, and deterministic local hashing.

## Next integration steps

1. Expose `evaluate_admissibility_packet` through the top-level package init once package layout is confirmed.
2. Attach real SDK receipts when a dynamic packet is admitted into an executable action.
3. Keep browser-demo local hashes separate from SDK receipts.
