# Universal Entry Integration Handoff

## Purpose

This document is the current continuation source for the authoritative ecosystem-retrieval, governed LLM-adapter, packaged catalog, canonical projection, authenticated transport, continuation-event, governed runtime-return, and Master-Records custody-verification layers in `StegVerse-org/StegVerse-SDK`.

## Installed files

```text
stegverse/ecosystem_records.py
stegverse/ecosystem_catalog.py
stegverse/ecosystem_projection.py
stegverse/http_transport.py
stegverse/llm_adapter_bridge.py
stegverse/universal_entry_events.py
stegverse/master_records_custody.py
stegverse/universal_entry_runtime.py
tests/test_universal_entry_integrations.py
tests/test_universal_entry_catalog_events.py
tests/test_universal_entry_transport_projection.py
tests/test_universal_entry_runtime_wrapper.py
tests/test_master_records_custody.py
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

`run_universal_entry` is the canonical wrapper. Without a custody client it attaches `continuation_events` and records `custody_submitted=false`, `custody_verified=false`, `master_records_installed=false`, and `reconstructability_status=NOT_SUBMITTED`.

## Master-Records custody path

```text
validated continuation event chain
-> build_custody_submission
-> authenticated dependency-injected custody transport
-> identity-matched Master-Records custody receipt
-> authenticated reconstruction retrieval
-> independent event-chain reconstruction validation
-> reconstructability_status: PASS
-> custody_verified=true
-> master_records_installed=true
```

`MasterRecordsCustodyClient` is transport-neutral. Browser entry adapters must never own custody credentials. The custody receipt must preserve submission, session, message, transition, run, first-event, last-event, count, and event-digest identity. It must record custody, expose reconstruction availability, remain non-authorizing, and pass deterministic receipt validation.

Reconstruction must return the complete validated event chain, match the submission digest and event boundaries, and explicitly report `PASS`. Identity mismatch, receipt tamper, chain drift, event-count mismatch, digest mismatch, missing reconstruction availability, authority escalation, execution escalation, or admissibility escalation fail closed.

When an optional custody client is supplied to `run_universal_entry`, custody and installation fields are set only after both the receipt and reconstructed chain pass validation.

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
Master-Records custody submission builder: installed
Master-Records custody receipt validation: installed
Master-Records reconstruction verification: installed
Master-Records custody client: installed_dependency_injected
live Master-Records endpoint: not_connected
Site universal-envelope transport: not_connected
```

## CI binding

The SDK workflow imports the transport, projection, runtime wrapper, catalog, bridge, continuation, and custody modules. Route validation explicitly runs all universal-entry runtime, integration, catalog/event, transport/projection, runtime-wrapper, custody, and reconstruction tests. The wheel job verifies the modules remain packaged.

A successful current-main run containing commit `3bce42a32bdc7acb4c255e995391eb8178265154` or later has not yet been independently observed.

## Site boundary

`StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md` remains the Site source of truth. It requires successor Site validation before further Site mutation and keeps live transport disabled. Therefore no Site browser transport, deployment, release, or live-activation change was made in this SDK work block.

## Release boundary

A portable node may declare `ecosystem_read` operational only when a validated packaged catalog or authenticated authoritative feed is installed. It may declare `external_llm` operational only when authenticated server-side transport is configured and a live provider result plus provider-usage event is verified. It may claim `RECORDED` only after an identity-matched custody receipt and independently reconstructed event chain both pass.

Transport implementation, custody-client implementation, fixture receipts, or local test reconstruction are not live deployment or external custody evidence.

Projection, catalog generation, retrieval, provider completion, continuation-event emission, local persistence, custody submission construction, and reconstruction code do not grant execution authority, admissibility, standing, publication authority, or Master-Records installation by themselves.

## Next task

1. Observe current-main SDK validation containing commit `3bce42a32bdc7acb4c255e995391eb8178265154` or later and repair only the first exact repository-local failure.
2. Observe the successor Site Task Runner after Site commit `0c076216f980f6b3c91677571d0692153d7ce94f`; do not mutate Site until the next exact failure or successful evidence set is known.
3. Add the live canonical source collector that reads explicitly authorized handoffs, manifests, status records, and receipt projections into `project_records`.
4. Connect an authorized deployed LLM-adapter endpoint to `LLMAdapterHTTPTransport` in a server-side runtime; never place credentials in Site or portable-node browser storage.
5. Connect an authorized Master-Records endpoint to `MasterRecordsCustodyClient` and preserve the external receipt and reconstruction evidence.
6. Add Site universal-envelope construction and same-origin shared-router submission only after Site handoff gates permit mutation.
7. Route general conversation through the governed provider lane when the local bounded handler cannot answer.
8. Add activation evidence binding only after Site validation, live provider use, custody receipt, and reconstructability PASS are observed together.

## Authority boundary

Retrieval is not authority. A catalog is not authority. A canonical projection declaration is not execution authority. Provider output is not authority. Authenticated transport is not authority. Local usage persistence is not custody. Continuation events are not proof receipts. Custody-client code is not custody. A local reconstruction fixture is not external reconstructability evidence. Only an identity-matched external custody receipt plus independently verified reconstruction can support a bounded `RECORDED` claim, and neither grants execution authority or admissibility.
