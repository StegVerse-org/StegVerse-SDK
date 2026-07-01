# Governed LLM Session Packets

## Purpose

This document defines the SDK-side intake contract for complete governed LLM adapter session packets emitted by `StegVerse-org/LLM-adapter`.

The SDK validator does not execute actions and does not grant authority. It verifies that the adapter packet is structurally coherent before downstream routing.

The SDK intake wrapper turns the validation decision into route-ready guidance: route, quarantine, reject, or fail closed.

## Done State

SDK intake is aligned when it can validate and route a packet containing:

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

## Intake Function

```python
from stegverse import intake_governed_llm_session_packet

intake = intake_governed_llm_session_packet(session_packet)
print(intake.to_dict())
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

## Intake Routing Rules

| Validation Decision | Intake Decision | Route |
| --- | --- | --- |
| `ALLOW` | `ROUTE` | `route_read_only_or_external_executor_handoff` |
| `ALLOW` + execution handoff ready | `ROUTE` | `route_external_executor_handoff` |
| `QUARANTINE` | `QUARANTINE` | `quarantine_before_consequence` |
| `DENY` | `REJECT` | `reject_denied_adapter_output` |
| malformed packet | `REJECT` | `reject_malformed_packet` |
| unresolved / fail closed | `FAIL_CLOSED` | `fail_closed_unresolved_session` |

## Boundary

```text
Adapter packet validation is not execution.
Adapter packet validation is not authority.
Adapter packet intake is not execution.
Adapter packet intake is not authority.
Adapter packet intake is route guidance only.
```

## Relationship to LLM-adapter

`LLM-adapter` emits the governed session packet.

`StegVerse-SDK` validates the packet before the ecosystem decides whether to retain, route, quarantine, or reject it.

## Local Verification

Run:

```bash
pytest tests/test_governed_llm_session.py
pytest tests/test_governed_llm_session_intake.py
```
