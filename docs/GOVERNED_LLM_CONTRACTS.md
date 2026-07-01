# Governed LLM SDK Contracts

## Purpose

This document defines the shared SDK contract for StegVerse-governed LLM responses.

The SDK does not authorize execution by itself. It provides deterministic packet and receipt helpers so an LLM adapter can prove what evidence was used, what policy and delegation standing were referenced, and what output was emitted.

## Done State

This contract is complete when a runtime adapter can:

1. classify a user query;
2. identify allowed retrieval sources;
3. bind retrieved evidence by pointer and hash;
4. create a query packet before model response generation;
5. create a response receipt after output validation;
6. reconstruct the response path later from hashes, pointers, policy state, delegation state, and output hash.

## Boundary

```text
LLM output is not execution.
Execution is not authority.
Authority is not admissibility.
A response becomes reusable only through reconstructable standing.
```

## Contract Components

| Component | File | Role |
| --- | --- | --- |
| Evidence pointer | `stegverse/governed_llm.py` | Minimal source reference with content hash and freshness state. |
| Query packet | `stegverse/governed_llm.py` | Pre-response packet binding query, source scope, evidence, policy, delegation, and risk tier. |
| Response receipt | `stegverse/governed_llm.py` | Post-response receipt binding model/provider, decision, output hash, and reconstruction status. |
| Reconstruction summary | `stegverse/governed_llm.py` | Minimal map for downstream continuity-search and master-record paths. |

## Retrieval Model

```text
user query
  -> query classification
  -> allowed source map
  -> evidence pointers + hashes
  -> GovernedQueryPacket
  -> model candidate output
  -> admissibility decision
  -> GovernedResponseReceipt
  -> reconstruction summary
```

## Storage-Minimizing Rule

The packet stores pointers and hashes instead of duplicating full source payloads. Full payload retention belongs only where custody, quarantine, explicit distribution, or master-record storage policy requires it.

## Freshness Rule

A prior response may be reconstructable without being currently reusable.

The adapter must distinguish:

```text
historically reconstructable
currently admissible
currently superseded
currently stale
currently revoked
currently denied
```

## SDK Usage

```python
from stegverse.governed_llm import (
    EvidencePointer,
    build_query_packet,
    build_response_receipt,
    reconstruction_summary,
)

pointer = EvidencePointer(
    source_type="receipt",
    pointer="master-records://example/receipt/1",
    content_hash="abc123",
    retrieved_at="2026-07-01T00:00:00+00:00",
)

packet = build_query_packet(
    "What changed since the last answer?",
    allowed_sources=("receipt_index", "model_knowledge"),
    evidence=(pointer,),
    policy={"policy": "read-only"},
    delegation={"adapter": "read"},
)

receipt = build_response_receipt(
    packet,
    "The earlier answer remains reconstructable but needs fresh retrieval before execution.",
    model_provider="example-provider",
    model_name="example-model",
    decision="ALLOW",
    admissibility_status="allowed_read_only",
)

summary = reconstruction_summary(packet, receipt)
```

## Related Runtime Repo

The runtime implementation belongs in:

```text
StegVerse-org/LLM-adapter
```

## Related Public Doctrine

The public explanation belongs in:

```text
StegVerse-Labs/admissibility-wiki
```
