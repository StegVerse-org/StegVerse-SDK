# Governed LLM Session Packets

## Purpose

This document defines the SDK-side intake contract for complete governed LLM adapter session packets emitted by `StegVerse-org/LLM-adapter`.

The SDK validator does not execute actions and does not grant authority. It verifies that the adapter packet is structurally coherent before downstream routing.

## Done State

SDK intake is aligned when it can validate a packet containing:

```text
provider_request
provider_request_hash
provider_response
continuity
adapter_result
action_route
commitment_request
authority_decision
execution_handoff
```

## Validation Function

```python
from stegverse import validate_governed_llm_session_packet

decision = validate_governed_llm_session_packet(session_packet)
print(decision.to_dict())
```

## Validation Rules

| Rule | Result |
| --- | --- |
| Missing required top-level key | raise `GovernedLLMSessionValidationError` |
| Provider response request hash mismatch | raise `GovernedLLMSessionValidationError` |
| Unknown execution handoff status | `FAIL_CLOSED` |
| `ready_for_external_executor` without authority `ALLOW` | `FAIL_CLOSED` |
| Adapter `DENY` | `DENY` |
| Adapter `QUARANTINE` | `QUARANTINE` |
| Adapter `ALLOW` with authority `NOT_REQUIRED` or `ALLOW` | `ALLOW` |
| Unresolved adapter/authority combination | `FAIL_CLOSED` |

## Boundary

```text
Adapter packet validation is not execution.
Adapter packet validation is not authority.
Adapter packet validation is structural intake standing only.
```

## Relationship to LLM-adapter

`LLM-adapter` emits the governed session packet.

`StegVerse-SDK` validates the packet before the ecosystem decides whether to retain, route, quarantine, or reject it.

## Local Verification

Run:

```bash
pytest tests/test_governed_llm_session.py
```
