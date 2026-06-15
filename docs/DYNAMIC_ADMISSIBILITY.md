# Dynamic Admissibility Packets

Generated: `2026-06-14`

## Purpose

This document records SDK awareness of the dynamic admissibility packet shape now used by the StegVerse Site demo.

The Site demo accepts live tester packets. The SDK now includes a dependency-free helper module that recognizes the same packet family so Site, SDK, LLM adapter, math-solver adapter, and future runtime services share a common vocabulary.

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
schemas/admissibility/llm-bridge-result.schema.json
schemas/admissibility/math-bridge-result.schema.json
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

Top-level package import:

```python
from stegverse import evaluate_admissibility_packet
```

Example:

```python
from stegverse.admissibility import evaluate_admissibility_packet

result = evaluate_admissibility_packet(packet)
print(result["classification"]["decision"])
print(result["classification"]["allowed_next_state"])
```

## Bridge registry

```text
stegverse/bridge_registry.py
```

Current registry functions:

```python
bridge_ids()
list_dynamic_bridges()
get_dynamic_bridge("llm_output")
require_dynamic_bridge("math_artifact")
bridge_registry_snapshot()
```

Registered bridge ids:

```text
generic_tester_packet
llm_output
math_artifact
```

## LLM bridge module

```text
stegverse/llm_admissibility.py
```

Current bridge functions:

```python
build_llm_tester_packet(...)
evaluate_llm_output_admissibility(...)
summarize_llm_admissibility(result)
```

Example:

```python
from stegverse.llm_admissibility import evaluate_llm_output_admissibility

bridge = evaluate_llm_output_admissibility(
    provider="openai",
    model="gpt-test",
    prompt="Draft a governance note.",
    output="This is a draft governance note.",
    declared_intent="research_note",
)

print(bridge["decision"])
print(bridge["allowed_next_state"])
```

Run the LLM bridge example:

```bash
python examples/llm_dynamic_admissibility.py
```

## Math bridge module

```text
stegverse/math_admissibility.py
```

Current bridge functions:

```python
build_math_tester_packet(...)
evaluate_math_artifact_admissibility(...)
summarize_math_admissibility(result)
```

Example:

```python
from stegverse.math_admissibility import evaluate_math_artifact_admissibility

bridge = evaluate_math_artifact_admissibility(
    formalism_id="RTG-STCM",
    artifact_type="solver_artifact",
    artifact_summary="Placeholder derivation attempt for RTG/STCM observer-window relationship.",
    declared_intent="formalism_support_claim",
)

print(bridge["decision"])
print(bridge["allowed_next_state"])
```

Run the math bridge example:

```bash
python examples/math_dynamic_admissibility.py
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

## Run examples

```bash
python examples/dynamic_admissibility_packet.py
python examples/llm_dynamic_admissibility.py
python examples/math_dynamic_admissibility.py
```

## Run tests

```bash
pytest tests/test_dynamic_admissibility.py tests/test_dynamic_admissibility_public_api.py tests/test_llm_admissibility.py tests/test_math_admissibility.py tests/test_bridge_registry.py
```

The tests cover valid research-note posture, missing-authority review, high-consequence fail-closed behavior, receipt-backed allow-with-posture behavior, strict validation failure, deterministic local hashing, top-level package import stability, the LLM bridge packet path, the math bridge packet path, and dynamic bridge discovery.

## Next integration steps

1. Expose the LLM and math bridges through the top-level package API after the existing package surface can be updated cleanly.
2. Attach real SDK receipts when a dynamic packet is admitted into an executable action.
3. Keep browser-demo local hashes separate from SDK receipts.
4. Connect bridge packets to downstream adapter execution paths.
