# STEGVERSE SDK

![PyPI](https://img.shields.io/pypi/v/stegverse-sdk)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Build](https://github.com/StegVerse-org/StegVerse-SDK/actions/workflows/sdk_demo_test.yml/badge.svg)
![License](https://img.shields.io/github/license/StegVerse-org/StegVerse-SDK)

> Execution is not assumed. Execution is admitted.

StegVerse verifies every action **before** it happens and produces cryptographic proof of that decision.

---

## WHAT IT DOES

You propose an action  
→ StegVerse evaluates it  
→ Decision: **ALLOW | DENY | DEFER**  
→ If allowed: execution + receipt  

Every executed action produces a verifiable receipt.

---

## WHY THIS MATTERS

**Traditional flow**  
AI decides → executes → humans audit later

**StegVerse flow**  
AI proposes → evaluated at commit → executes only if admitted

This eliminates ungoverned execution at the point of irreversibility.

---

## QUICK START

### Install

```bash
pip install stegverse-sdk
```

### Example

```python
from stegverse import StegVerseSDK

sdk = StegVerseSDK()

result = sdk.submit_intent(
    action="deploy.compute",
    target="render.cluster",
    parameters={"gpu": "A100", "count": 4}
)

print(result["decision"])   # allow | deny | defer
print(result["receipt_id"])  # verifiable receipt
```

---

## SAFETY STACK

1. **Mathematical Gate (GCAT/BCAT)**
   - Evaluates admissibility at commit-time
   - Denies unsafe transitions by default

2. **Human Review**
   - Handles ambiguous edge cases

3. **Circuit Breakers**
   - Stops execution on system instability

4. **Consensus Controls**
   - Multi-party emergency halt

5. **Fail-Safe**
   - Defaults to denial if control is lost

---

## DYNAMIC ADMISSIBILITY PACKETS

The SDK is schema-aware of the dynamic admissibility packet family used by the StegVerse Site demo and includes local evaluator, bridge, receipt-reference, and verifier helpers.

Dynamic admissibility asks:

```text
What is this output, artifact, instruction, transition, or claim allowed to become?
```

Packet path:

```text
tester packet
→ discipline route
→ authority / evidence / replay / consequence checks
→ admissibility decision
→ result packet
→ local admissibility reference
→ optional execution receipt attachment
```

SDK-visible schemas:

```text
schemas/admissibility/tester-output.schema.json
schemas/admissibility/dynamic-demo-result.schema.json
schemas/admissibility/llm-bridge-result.schema.json
schemas/admissibility/math-bridge-result.schema.json
schemas/admissibility/bridge-registry.schema.json
```

SDK helper:

```python
from stegverse.admissibility import evaluate_admissibility_packet

result = evaluate_admissibility_packet(packet)
print(result["classification"]["decision"])
print(result["classification"]["allowed_next_state"])
```

Bridge examples:

```bash
python examples/dynamic_admissibility_packet.py
python examples/list_dynamic_bridges.py
python examples/llm_dynamic_admissibility.py
python examples/math_dynamic_admissibility.py
```

Receipt-reference examples:

```bash
python examples/admissibility_receipt_reference.py
python examples/verify_receipt_with_admissibility_reference.py
```

Execution receipts remain backward-compatible with `receipt_id`, `decision`, and `timestamp`. They may also carry `admissibility_receipt_reference`; when present, `verify_receipt(...)` validates that reference before accepting the receipt.

Reference docs:

```text
docs/DYNAMIC_ADMISSIBILITY.md
```

These packets align the SDK with the Site demo, applicability map, discipline test matrix, tester-output template, LLM bridge, and math-solver bridge.

---

## LLM ADAPTER

Govern any LLM output before execution:

```python
from stegverse import StegVerseLLMAdapter, LLMProvider

adapter = StegVerseLLMAdapter()

result = adapter.govern_llm_output(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    prompt="Write a risk scoring function",
    output=llm_output
)
```

Returns:
- decision (allow | deny | defer)
- receipt
- reasoning

### Ecosystem Optimization

```python
result = adapter.optimize_ecosystem(
    ecosystem_metrics={"cpu": 0.85, "memory": 0.90},
    proposed_changes={"type": "scale", "cost": 5000}
)
```

---

## THE MODEL

Legitimacy constraint:

```
Φ(x) = K · g^α · c^β · t^γ − a
```

Where:
- g = governance capacity
- c = constraints
- a = action pressure
- t = trust

Decision rule:
- Φ(x) ≥ 0 → ALLOW
- Φ(x) < 0 → DENY

---

## INTEGRATION

| Downstream | Consumes |
|------------|----------|
| TV/TVC | Ephemeral secrets via TrustVault |
| GCAT-BCAT-Engine | Deployment verification |
| demo_ingest_engine | Orchestrated ingestion |
| AaCT-E | Audit trail |
| StegDB | State monitoring |
| Site demo | Dynamic admissibility tester packets |
| Applicability map | Discipline routes and tester-output templates |
| LLM bridge | LLM output to dynamic admissibility packet |
| Math bridge | Formalism artifact to dynamic admissibility packet |
| Receipts | Optional admissibility receipt references |

---

## LINKS

- Docs: https://stegverse.org/docs
- API: https://api.stegverse.org
- Issues: https://github.com/StegVerse-org/StegVerse-SDK/issues
- Ingestion: https://github.com/StegVerse-org/demo_ingest_engine
- Email: sdk@stegverse.org

---

## ONE LINE

StegVerse enforces commit-time governance with verifiable execution receipts.
