# Ecosystem Chat Local Issuer

## Purpose

This issuer creates deterministic local receipt identifiers for Ecosystem Chat testing.

It is not used by the default pipeline.

## Import

```python
from stegverse.ecosystem_chat_local_issuer import LocalGovernedEcosystemChatIssuer
```

## Use

```python
result = run_ecosystem_chat_pipeline(
    payload,
    issuer=LocalGovernedEcosystemChatIssuer(),
)
```

## Receipt identifier shape

```text
ecr-local-<24 hex chars>
```

## Boundary

Default pipeline behavior remains fail-closed.

External record persistence remains disabled.

This issuer only accepts eligible pending receipt decisions with a valid request hash.
