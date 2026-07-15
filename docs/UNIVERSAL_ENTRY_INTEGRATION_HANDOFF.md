# Universal Entry Integration Handoff

## Purpose

This document is the current continuation source for the authoritative ecosystem-retrieval, governed LLM-adapter, packaged catalog, and continuation-event layers in `StegVerse-org/StegVerse-SDK`.

## Installed files

```text
stegverse/ecosystem_records.py
stegverse/ecosystem_catalog.py
stegverse/llm_adapter_bridge.py
stegverse/universal_entry_events.py
tests/test_universal_entry_integrations.py
tests/test_universal_entry_catalog_events.py
examples/universal_entry/llm_adapter_round_trip.json
.github/workflows/sdk-demo-test.yml
```

## Ecosystem retrieval and packaged catalog path

```text
canonical handoff / manifest / status / receipt projection
-> EcosystemRecord validation
-> packaged read-only catalog build
-> deterministic catalog identity
-> authority / lifecycle / freshness / supersession filtering
-> AuthoritativeEcosystemRetriever
-> EcosystemQueryHandler
-> conversation synthesis
```

`build_catalog` accepts explicit canonical projections and emits a deterministic, read-only, non-authorizing catalog. Unsupported record classes fail closed. Non-authoritative, superseded, deprecated, and quarantined projections are excluded. Duplicate record identities and catalog tamper fail closed.

The SDK does not decide that a repository file is authoritative merely because it exists. A producing gateway or build task must explicitly project canonical records into the catalog input contract.

## Governed provider path

```text
universal entry envelope
-> build_adapter_request
-> dependency-injected authenticated server-side transport
-> LLM-adapter /api/ecosystem-chat
-> provider result and local provider-usage submission
-> normalize_adapter_response
-> ExternalLLMHandler
-> conversation synthesis
```

The SDK bridge preserves transition, run, session, message, manifest, parent-transition, and prior-receipt identity. It rejects identity mismatch and authority, custody, mutation, publication, or admissibility escalation.

## Continuation event path

```text
routing decision
-> routing event
-> retrieval event when ecosystem records are used
-> provider-usage event when an external provider lane runs
-> solver event when the checked solver runs
-> synthesis event when conversation combines lane results
-> deterministic linked event chain
```

Installed event classes:

```text
routing
retrieval
provider_usage
solver
synthesis
```

Every event preserves session, message, transition, run, entry-point, and prior-event identity. Event chains reject discontinuity, digest drift, authority escalation, execution escalation, custody escalation, and admissibility escalation.

These continuation events are not Master-Records custody. They are transport-neutral records prepared for later authenticated custody submission.

## Current operational state

```text
universal router: installed
engine dispatcher: installed
bounded conversation and synthesis: installed
authoritative record model: installed
packaged read-only catalog builder: installed
catalog integrity validation: installed
authoritative catalog retriever: installed_dependency_injected
canonical projection producer: not_connected
LLM-adapter request builder: installed
LLM-adapter return validator: installed
LLM-adapter transport: installed_dependency_injected
live deployed provider endpoint: not_connected
provider usage preservation: installed
routing/retrieval/provider/solver/synthesis continuation events: installed
continuation chain validation: installed
Master-Records custody transport: not_connected
Site universal-envelope transport: not_connected
```

## CI binding

The SDK workflow imports the catalog and continuation-event modules, runs `tests/test_universal_entry_catalog_events.py` in route validation, and verifies both modules are present in the built wheel.

A successful current-main run containing commit `38ccc4ffc195c64edf0d0e32d5aac123b160653b` or later has not yet been independently observed.

## Release boundary

A portable node may declare `ecosystem_read` operational only when a validated packaged catalog or authenticated authoritative catalog feed is installed. It may declare `external_llm` operational only when authenticated server-side transport is configured and a live provider result plus provider-usage event is verified.

Catalog generation, retrieval, provider completion, continuation-event emission, and local persistence do not grant execution authority, admissibility, custody, standing, publication authority, or Master-Records installation.

## Next task

1. Add an authenticated server-side HTTP transport implementation for the LLM-adapter bridge.
2. Add the canonical projection producer that packages current handoffs, manifests, status records, and receipt projections.
3. Add Site universal-envelope construction and same-origin shared-router submission.
4. Route general conversation through the governed provider lane when the local bounded handler cannot answer.
5. Attach continuation-event output to the governed return envelope and downstream custody submission interface.
6. Connect authenticated Master-Records custody and reconstructability verification.
7. Observe current-main SDK validation and repair only the first exact repository-local failure.

## Authority boundary

Retrieval is not authority. A catalog is not authority. A current handoff is not execution authority. Provider output is not authority. Local usage persistence is not custody. Continuation events are not proof receipts or Master-Records installation.
