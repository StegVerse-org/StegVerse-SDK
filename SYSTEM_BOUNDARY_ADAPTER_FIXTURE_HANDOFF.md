# Adapter-Origin System-Boundary Fixture Handoff

## Authority

This is the bounded continuation record for the adapter-origin system-boundary fixture path in `StegVerse-org/StegVerse-SDK`.

Repository-wide authority remains `SDK_MIRROR_HANDOFF.md`. This file supersedes only the item that required an adapter-produced fixture to enter SDK manifest serialization without test-local reconstruction.

## Source and consumer

```text
source repository: StegVerse-org/LLM-adapter
source fixture: tests/fixtures/system-boundary-sdk-session-packet.v1.json
source commit: dbd6ca0bde250bdf9865532049f58d523269d305

consumer repository: StegVerse-org/StegVerse-SDK
consumer fixture: tests/fixtures/adapter-system-boundary-session-packet.v1.json
```

## Installed consumer path

```text
stegverse/system_boundary_round_trip.py
-> reconstruct adapter declaration identity, receipt, and enriched reference
-> stegverse/governed_llm_manifest.py
-> preserve adapter reference unchanged
-> stegverse/governed_llm_receipt.py
-> preserve reference in receipt handoff
```

## Installed commits

```text
641d2c89270ce63fd98fa1dd20017b46d3171156  mirror adapter-origin fixture
c225fdd664a2e953fceb13d20c64ab8665704d1a  repair manifest contract for full adapter tuple
1089bbf6df3cb14f8643ea96e6805de653d57cfa  adapter-origin fixture tests
ab32578396a289ccd50f33c01ba4a802898139f3  explicit workflow binding
edb3b6997f74adea54c0dc49ebac174d517fd37a  installation receipt
```

## Contract repair

The prior optional manifest binder used a full-declaration hash and exact minimal-reference equality. The adapter contract instead derives identity from the canonical operational content view and includes receipt-bound fields:

```text
receipt_hash
production_binding_enabled: false
```

The SDK binder now:

```text
- validates the declaration shape and non-claims;
- reconstructs the full adapter declaration/receipt/reference tuple;
- rejects declaration, receipt, digest, or identity drift;
- rejects authority, custody, admissibility, or production escalation;
- preserves the validated enriched adapter reference unchanged;
- retains the earlier minimal-reference path only for legacy receipt-less packets.
```

## Test coverage

```text
adapter tuple accepted without test-local reconstruction
manifest preserves source declaration and enriched reference
receipt handoff preserves enriched reference
identical fixture replay preserves declaration identity and reference
tampered receipt fails closed
production_binding_enabled=true fails closed
```

## Current state

```text
adapter_origin_fixture: installed
cross_repository_source_chain: installed
manifest_contract_reconciliation: installed
receipt_reference_preservation: installed
explicit_workflow_binding: installed
workflow_observation: pending
production_binding: disabled
execution_authority: none
custody_transfer: none
admissibility_effect: none
```

## Remaining work

```text
- observe sdk-demo-test containing ab32578396a289ccd50f33c01ba4a802898139f3 or later;
- repair only the first repository-local failure, if any;
- preserve a workflow-bound fixture result receipt after a successful run;
- keep automatic adapter production binding disabled until separately authorized.
```

## Archive readiness

All adapter-origin fixture decisions, source/consumer identities, contract repair, tests, commits, boundaries, and remaining observations are durable here. Earlier conversation context is not required.
