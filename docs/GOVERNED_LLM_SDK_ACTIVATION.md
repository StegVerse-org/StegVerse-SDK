# Governed LLM SDK Activation

## Status

`StegVerse-org/StegVerse-SDK` now contains the governed LLM contract layer needed to receive, validate, route, manifest-bind, and receipt-handoff-bind packets emitted by `StegVerse-org/LLM-adapter`.

## Active Chain

```text
adapter session packet
  -> SDK validation
  -> SDK intake routing
  -> SDK manifest binding
  -> SDK receipt handoff
```

## Done Definition

This SDK layer is considered active when:

1. governed LLM evidence/query/response receipt contracts exist;
2. complete adapter session packets can be validated;
3. malformed packets are rejected with retained records;
4. quarantined packets route to quarantine guidance;
5. allowed packets route to read-only or external-executor handoff guidance;
6. unresolved packets fail closed;
7. valid intake results can be bound into manifests;
8. manifests can be bound into receipt handoffs;
9. no SDK path grants authority or executes side effects.

## Capability Manifest

Machine-readable capability status is in:

```text
sdk.capabilities.json
```

## Local Verification

Run unit tests:

```bash
pytest tests/test_governed_llm.py
pytest tests/test_governed_llm_session.py
pytest tests/test_governed_llm_session_intake.py
pytest tests/test_governed_llm_manifest.py
pytest tests/test_governed_llm_receipt.py
```

Run smoke script:

```bash
python scripts/smoke_governed_llm_sdk.py
```

Expected smoke result:

```json
{
  "status": "PASS",
  "actual": {
    "intake_decision": "ROUTE",
    "receipt_status": "route_ready_record_retained",
    "retain_record": true,
    "route": "route_read_only_or_external_executor_handoff"
  }
}
```

## Explicit Non-Claims

```text
SDK validation is not execution.
SDK intake routing is not authority.
Manifest binding is not persistence by itself.
Receipt handoff is not master-record installation by itself.
External executor integration remains outside this SDK contract layer.
```

## Remaining External Integration Work

| Integration | Status | Notes |
| --- | --- | --- |
| Master-record persistence | external | Receipt handoff is ready, but persistence is not performed here. |
| External executor | external | Must be separately governed. |
| Release publishing | external | Package version bump/release remains separate. |

## Activation Conclusion

The SDK can now accept the completed LLM adapter boundary and produce a retained, receipt-ready handoff object without granting authority or causing side effects.
