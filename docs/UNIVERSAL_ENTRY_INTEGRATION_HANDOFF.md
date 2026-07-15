# Universal Entry Integration Handoff

## Purpose

This document records the authoritative ecosystem-retrieval and governed LLM-adapter integration layer installed after the universal router, dispatcher, operational handlers, synthesis, and entry-point parity foundation.

## Installed files

```text
stegverse/ecosystem_records.py
stegverse/llm_adapter_bridge.py
tests/test_universal_entry_integrations.py
examples/universal_entry/llm_adapter_round_trip.json
.github/workflows/sdk-demo-test.yml
```

## Ecosystem retrieval path

```text
repository/manifests/handoffs/status/receipt projection
-> EcosystemRecord validation
-> authority/lifecycle/freshness/supersession filtering
-> deterministic query scoring
-> source and receipt-reference preservation
-> EcosystemQueryHandler
-> conversation synthesis
```

`AuthoritativeEcosystemRetriever` accepts a bounded record catalog supplied by an entry runtime or gateway. It does not own repository credentials and does not infer authority from file presence alone.

Records must include stable identity, repository, source, type, title, text, observed time, lifecycle state, and explicit authority posture. Duplicate identities fail closed. Non-authoritative, superseded, deprecated, quarantined, and optionally stale records are excluded.

## Governed provider path

```text
universal entry envelope
-> build_adapter_request
-> dependency-injected LLM-adapter transport
-> existing /api/ecosystem-chat contract
-> provider result and local provider-usage submission
-> normalize_adapter_response
-> ExternalLLMHandler
-> conversation synthesis
```

The SDK bridge preserves transition, run, session, message, manifest, and prior-receipt identity. It rejects transition/run mismatch and authority, custody, mutation, publication, or admissibility escalation.

The bridge preserves provider identity, model, usage metadata, provider receipt, lifecycle state, Master-Records status, and reconstruction status. Local provider-usage persistence remains explicitly not Master-Records custody.

## Dispatch context

The universal dispatcher now places the original universal entry envelope into the immutable handler context as:

```text
universal_entry_envelope
```

This permits provider and retrieval adapters to derive canonical identity without entry adapters directly invoking engines or holding provider/repository credentials.

## Current operational state

```text
universal router: installed
engine dispatcher: installed
bounded conversation and synthesis: installed
authoritative record model: installed
authoritative catalog retriever: installed_dependency_injected
live repository catalog feed: not_connected
LLM-adapter request builder: installed
LLM-adapter return validator: installed
LLM-adapter transport: installed_dependency_injected
live deployed provider endpoint: not_connected
provider usage preservation: installed
identity/authority/custody guards: installed
adapter round-trip fixture: installed
Master-Records custody: not_connected
```

## Release boundary

This integration makes the node capable of using real ecosystem and provider engines when transports are supplied. It does not establish a live endpoint, provider credentials, authenticated repository feed, Master-Records custody, deployment evidence, or release authority.

A portable node must not declare `ecosystem_read` operational until an authenticated or packaged authoritative record feed is present. It must not declare `external_llm` operational until the governed LLM-adapter transport is configured and a live provider response plus provider-usage event has been verified.

## Next task

1. Add a packaged read-only ecosystem catalog builder from canonical handoffs, manifests, status records, and receipt projections.
2. Add an authenticated server-side HTTP transport for the LLM-adapter bridge; never place provider credentials in Site or portable-node browser storage.
3. Add Site universal-envelope construction and same-origin shared-router submission.
4. Add general conversational-model routing through the governed provider lane.
5. Add routing, retrieval, provider-usage, synthesis, and solver continuation records.
6. Connect authenticated Master-Records custody and reconstructability verification.
7. Observe current-main SDK validation containing this integration block and repair only the first exact repository-local failure.

## Authority boundary

Retrieval is not authority. A current handoff record is not execution authority. Provider output is not authority. Local usage persistence is not custody. A gateway, routing, dispatch, provider, or synthesis receipt is not Master-Records installation or admissibility.
