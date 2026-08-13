# Public credential boundary

The public StegVerse SDK does not ask evaluators, contributors, LLMs, or ordinary SDK callers to provide GitHub tokens, provider keys, Master Records bearer tokens, private keys, passwords, or other protected credential material.

Credential and route authority belong to TV/TVC. Public SDK inputs and inspection requests are non-secret and non-authorizing.

For custody-backed governed runs, authenticated Master Records access is an internal TV/TVC runtime concern. A public caller may provide non-secret endpoint or request data only where the canonical runtime contract permits it. Protected custody credentials must be resolved inside TV/TVC and must not be copied into SDK commands, manifests, pull requests, fixtures, receipts, logs, or public environment instructions.

Current reconciliation task:

```text
StegVerse-Labs/TVC/tasks/TVC-MASTER-RECORDS-CUSTODY-BROKER-004.json
StegVerse-Labs/TVC/docs/MASTER_RECORDS_CUSTODY_BROKER_MIRROR_HANDOFF.md
```

Until that credential-neutral custody transport is integrated and validated, public SDK users should treat custody-backed production-validation execution as unavailable from an ordinary local checkout. Local governance navigation, demos, request preparation, AdmittedCode verification, and other credential-free SDK surfaces remain available.

Authority invariants:

```text
credential presence != authority
SDK caller credential handling: prohibited
GitHub token runtime authority: none
provider output != authority
manifest_receipt_id != authority
TVC transport != custody authority
Master Records remains custody authority
```
