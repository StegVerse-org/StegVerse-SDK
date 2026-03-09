# StegVerse SDK

SDK for interacting with the **StegVerse Trust Kernel**.

StegVerse provides runtime governance for autonomous systems by enforcing decision verification at the **execution boundary**.

```text
system proposes action
        ↓
   Trust Kernel
        ↓
allow / deny / defer
        ↓
execution
```

The SDK allows external systems to interact with this runtime.

## Core Concepts

### Intent

An **intent** is a structured description of an action a system wants to perform.

```python
intent = {
    "action": "deploy.compute",
    "target": "render.cluster",
    "parameters": {
        "gpu": "A100",
        "count": 4
    }
}
```

### Decision

The Trust Kernel returns a decision:

```text
allow
deny
defer
```

### Execution Receipt

Every executed action produces a **receipt** that proves:
- the decision was verified
- the action was authorized
- execution occurred within admissible constraints

## Minimal SDK Interface

```python
submit_intent(intent)
get_decision(intent_id)
verify_receipt(receipt)
```
