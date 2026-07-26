# Provider-Owned Usage Event Ingestion

The SDK accepts the provider-owned event emitted by `StegVerse-org/LLM-adapter` only as descriptive evidence.

```text
provider-owned usage event
-> SDK structural and hash validation
-> transition usage projection
-> session aggregation
-> receipt-required return path
```

The adapter remains the event owner. SDK validation does not transfer execution authority, publication authority, admissibility, custody, actor identity, attribution, or value authority.

## Required invariants

```text
sdk_validation_is_execution == false
aggregation_is_authority == false
session_receipt_is_custody == false
provider_event_ownership_preserved == true
full_chain_of_thought_ingested == false
```

The SDK verifies the provider/model/version identity, request and response hashes, token arithmetic, latency measurement, bounded reasoning-provenance reference, return-to-origin receipt requirement, event self-hash, and all adapter non-authority assertions.

`PROVIDER_RESPONSE`, `PROVIDER_REFUSAL`, and `PROVIDER_ERROR` are accepted event classes. None is automatically admissible or executable.

## Verification

```bash
pytest tests/test_provider_usage_ingest.py -v
```

Canonical upstream implementation:

```text
StegVerse-org/LLM-adapter
PR 48
merge 623dbefca7c18d4838d423434aeeb4ede04eceb1
```
