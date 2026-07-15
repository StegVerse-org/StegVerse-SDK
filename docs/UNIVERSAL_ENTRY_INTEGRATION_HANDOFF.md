# Universal Entry Integration Handoff

## Purpose

This document is the current continuation source for the authoritative ecosystem-retrieval, governed LLM-adapter, packaged catalog, canonical projection, authenticated transport, continuation-event, and governed runtime-return layers in `StegVerse-org/StegVerse-SDK`.

## Installed files

```text
stegverse/ecosystem_records.py
stegverse/ecosystem_catalog.py
stegverse/ecosystem_projection.py
stegverse/http_transport.py
stegverse/llm_adapter_bridge.py
stegverse/universal_entry_events.py
stegverse/universal_entry_runtime.py
tests/test_universal_entry_integrations.py
tests/test_universal_entry_catalog_events.py
tests/test_universal_entry_transport_projection.py
tests/test_universal_entry_runtime_wrapper.py
examples/universal_entry/llm_adapter_round_trip.json
.github/workflows/sdk-demo-test.yml
```

## Canonical ecosystem path

```text
explicit canonical handoff / manifest / status / receipt source
-> project_record / project_records
-> explicit canonical=true and authoritative=true validation
-> EcosystemRecord validation
-> packaged read-only catalog build
-> deterministic catalog identity
-> lifecycle / freshness / supersession filtering
-> AuthoritativeEcosystemRetriever
-> EcosystemQueryHandler
-> conversation synthesis
```

The SDK does not infer authority from repository file presence. A producer must explicitly declare a source canonical and authoritative before projection. Unsupported record classes, missing source identity, invalid lifecycle state, duplicate projected identities, catalog tamper, and duplicate catalog identities fail closed.

## Governed provider path

```text
universal entry envelope
-> build_adapter_request
-> AuthenticatedJSONTransport / LLMAdapterHTTPTransport
-> HTTPS server-side request to LLM-adapter /api/ecosystem-chat
-> provider result and local provider-usage submission
-> normalize_adapter_response
-> ExternalLLMHandler
-> conversation synthesis
```

Remote cleartext HTTP is rejected. HTTP is accepted only for localhost development. Bearer credentials and same-origin session identity are transport configuration, not browser state. The SDK bridge preserves transition, run, session, message, manifest, parent-transition, and prior-receipt identity and rejects identity, authority, custody, mutation, publication, or admissibility escalation.

## Continuation and governed return path

```text
route_universal_entry
-> operational lane dispatch
-> governed return
-> routing event
-> retrieval / provider_usage / solver events as applicable
-> synthesis event as applicable
-> validate_event_chain
-> continuation metadata attached to governed return
```

`run_universal_entry` is the canonical wrapper. It attaches `continuation_events` and a continuation summary containing the first event, last event, count, `custody_submitted=false`, and `master_records_installed=false`.

Continuation events preserve session, message, transition, run, entry-point, and prior-event identity. They reject chain discontinuity, digest drift, authority escalation, execution escalation, custody escalation, and admissibility escalation. They are transport-neutral records, not proof receipts or Master-Records custody.

## Current operational state

```text
universal router: installed
engine dispatcher: installed
bounded conversation and synthesis: installed
authoritative record model: installed
canonical projection producer: installed
packaged read-only catalog builder: installed
catalog integrity validation: installed
authoritative catalog retriever: installed_dependency_injected
live canonical source collector: not_connected
LLM-adapter request builder: installed
LLM-adapter return validator: installed
authenticated server-side JSON transport: installed
LLM-adapter HTTP transport: installed
live deployed provider endpoint: not_connected
provider usage preservation: installed
routing/retrieval/provider/solver/synthesis continuation events: installed
continuation chain validation: installed
continuation events attached to governed return: installed
Master-Records custody transport: not_connected
Site universal-envelope transport: not_connected
```

## CI binding

The SDK workflow imports the transport, projection, runtime wrapper, catalog, bridge, and continuation modules. Route validation explicitly runs all universal-entry runtime, integration, catalog/event, transport/projection, and runtime-wrapper tests. The wheel job verifies the modules remain packaged.

A successful current-main run containing commit `12993715bbd0f42808026d96230b2d3831887067` or later has not yet been independently observed.

## Site boundary

`StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md` remains the Site source of truth. It currently requires successor Site validation before further Site mutation and keeps live transport disabled. Therefore no Site browser transport, deployment, release, or live-activation change was made in this SDK work block.

## Release boundary

A portable node may declare `ecosystem_read` operational only when a validated packaged catalog or authenticated authoritative feed is installed. It may declare `external_llm` operational only when authenticated server-side transport is configured and a live provider result plus provider-usage event is verified. Transport implementation alone is not live-provider evidence.

Projection, catalog generation, retrieval, provider completion, continuation-event emission, and local persistence do not grant execution authority, admissibility, custody, standing, publication authority, or Master-Records installation.

## Next task

1. Observe current-main SDK validation containing commit `12993715bbd0f42808026d96230b2d3831887067` or later and repair only the first exact repository-local failure.
2. Observe the successor Site Task Runner after Site commit `0c076216f980f6b3c91677571d0692153d7ce94f`; do not mutate Site until the next exact failure or successful evidence set is known.
3. Connect an authorized deployed LLM-adapter endpoint to `LLMAdapterHTTPTransport` in a server-side runtime; never place credentials in Site or portable-node browser storage.
4. Add the live canonical source collector that reads explicitly authorized handoffs, manifests, status records, and receipt projections into `project_records`.
5. Add Site universal-envelope construction and same-origin shared-router submission only after Site handoff gates permit mutation.
6. Route general conversation through the governed provider lane when the local bounded handler cannot answer.
7. Add an authenticated Master-Records custody client for continuation-event chains and require identity-matched custody receipts.
8. Add reconstructability verification against the returned custody record before any RECORDED claim.

## Authority boundary

Retrieval is not authority. A catalog is not authority. A canonical projection declaration is not execution authority. Provider output is not authority. Authenticated transport is not authority. Local usage persistence is not custody. Continuation events are not proof receipts or Master-Records installation.
