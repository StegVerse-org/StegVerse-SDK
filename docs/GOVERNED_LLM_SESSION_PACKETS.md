# Governed LLM Session Packets

## Purpose

This document defines the SDK-side intake contract for complete governed LLM adapter session packets emitted by `StegVerse-org/LLM-adapter`.

The SDK validator does not execute actions and does not grant authority. It verifies that the adapter packet is structurally coherent before downstream routing.

The SDK intake wrapper turns the validation decision into route-ready guidance: route, quarantine, reject, or fail closed.

The SDK manifest binder turns the packet and intake result into a receipt-ready manifest object.

## Done State

SDK intake is aligned when it can validate, route, and bind a packet containing:

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

## Manifest Binding Function

```python
from stegverse import build_governed_llm_manifest

manifest = build_governed_llm_manifest(session_packet)
print(manifest["manifest_hash"])
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

## Manifest Fields

```text
schema_version
created_at
manifest_type
source_repo
session_hash
intake_decision
route
retain_record
manifest_hash
intake
```

The manifest is receipt-ready. It is not execution, authority, or downstream installation.

## Boundary

```text
Adapter packet validation is not execution.
Adapter packet validation is not authority.
Adapter packet intake is not execution.
Adapter packet intake is not authority.
Adapter packet intake is route guidance only.
Manifest binding is not execution.
Manifest binding is receipt preparation only.
```

## Relationship to LLM-adapter

`LLM-adapter` emits the governed session packet.

`StegVerse-SDK` validates, routes, and binds the packet before the ecosystem decides whether to retain, route, quarantine, reject, or hand off the manifest.

## Local Verification

Run:

```bash
pytest tests/test_governed_llm_session.py
pytest tests/test_governed_llm_session_intake.py
pytest tests/test_governed_llm_manifest.py
```
