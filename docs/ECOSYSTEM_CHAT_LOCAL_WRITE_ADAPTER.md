# Ecosystem Chat Local Write Adapter

## Purpose

This adapter creates deterministic local write identifiers for Ecosystem Chat testing.

It is not used by the default pipeline.

## Import

```python
from stegverse.ecosystem_chat_local_write_adapter import LocalEcosystemChatWriteAdapter
```

## Use

```python
result = run_ecosystem_chat_pipeline(
    payload,
    issuer=LocalGovernedEcosystemChatIssuer(),
    write_adapter=LocalEcosystemChatWriteAdapter(),
)
```

## Write identifier shape

```text
ecw-local-<24 hex chars>
```

## Boundary

Default pipeline behavior remains fail-closed.

The local adapter accepts only pending persistence plans with valid receipt and persistence hashes.
