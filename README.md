# STEGVERSE SDK
Execution is not assumed. Execution is admitted.

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

sdk = StegVerseSDK(api_key="your-key")

result = sdk.submit_intent({
    "action": "deploy.compute",
    "target": "render.cluster",
    "parameters": {"gpu": "A100", "count": 4}
})

print(result["decision"])   # allow | deny | defer
print(result["receipt"])    # cryptographic proof
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

## PRICING

| Tier        | Evaluations | Price  |
|-------------|------------|--------|
| Free        | 100/mo     | $0     |
| Pro         | 10,000/mo  | $499   |
| Enterprise  | Unlimited  | $4,999 |

Usage:
- $0.01 per evaluation  
- $0.001 per stored receipt  

---

## LINKS

- Docs: https://stegverse.org/docs  
- API: https://api.stegverse.org  
- Issues: https://github.com/StegVerse-Org/stegverse-sdk/issues  
- Email: sdk@stegverse.org  

---

## ONE LINE

StegVerse enforces commit-time governance with verifiable execution receipts.
