# Universal Entry Integration Handoff

## Purpose

This document is the current continuation source for the authoritative ecosystem-retrieval, governed LLM-adapter, packaged catalog, canonical projection and collection, governed conversation, authenticated transport, continuation-event, governed runtime-return, and Master-Records custody-verification layers in `StegVerse-org/StegVerse-SDK`.

## Installed files

```text
stegverse/ecosystem_records.py
stegverse/ecosystem_catalog.py
stegverse/ecosystem_projection.py
stegverse/canonical_source_collector.py
stegverse/governed_conversation.py
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
tests/test_canonical_source_conversation.py
examples/universal_entry/llm_adapter_round_trip.json
.github/workflows/sdk-demo-test.yml
```

## Canonical ecosystem path

```text
explicitly authorized source inventory
-> CanonicalSourceSpec validation
-> dependency-injected authenticated/read-only source reader
-> repository/path/content-digest identity checks
-> canonical source collection evidence
-> project_record / project_records
-> explicit canonical=true and authoritative=true validation
-> packaged read-only catalog build
-> deterministic catalog identity
-> lifecycle / freshness / supersession filtering
-> AuthoritativeEcosystemRetriever
-> EcosystemQueryHandler
-> conversation synthesis
```

`CanonicalSourceCollector` accepts only explicitly allowlisted source specifications. Every enabled source must declare stable source identity, repository, path, record type, title, observation time, `canonical=true`, and `authoritative=true`. Duplicate source identities and duplicate repository/path locations fail closed.

The dependency-injected reader may return text plus repository, path, digest, and receipt metadata. Repository identity mismatch, path mismatch, empty content, unsupported reader output, and supplied content-digest mismatch fail closed. The collection emits deterministic evidence and projections and remains non-authorizing and non-custodial.

The SDK does not infer authority from repository file presence. Credentials and connector access remain in the server-side reader implementation, not in the SDK collector or browser entry adapters.

## Governed conversation path

```text
conversation request
-> bounded local conversation handler
-> local response when supported
-> otherwise verify external_information_allowed=true
-> governed provider supplied through LLM-adapter bridge
-> provider identity / usage / receipt preservation
-> authority and custody escalation guards
-> governed conversational response
```

`GovernedConversationHandler` invokes the provider only for the existing `GENERAL_CONVERSATION_MODEL_NOT_ATTACHED` degradation. Greetings, thanks, capability explanations, and synthesis remain local and do not invoke a provider. Provider fallback is refused when the manifest prohibits external information or when no provider is configured.

Provider output remains non-authorizing. Provider receipt, model, usage, lifecycle, Master-Records status, and reconstruction status are preserved when supplied. Any provider attempt to grant authority, execution, custody, or admissibility fails closed.

## Governed provider path

```text
universal entry envelope
-> build_adapter_request
-> AuthenticatedJSONTransport / LLMAdapterHTTPTransport
-> HTTPS server-side request to LLM-adapter /api/ecosystem-chat
-> provider result and local provider-usage submission
-> normalize_adapter_response
-> ExternalLLMHandler or GovernedConversationHandler
-> conversation synthesis when applicable
```

Remote cleartext HTTP is rejected. HTTP is accepted only for localhost development. Bearer credentials and same-origin session identity are server-side transport configuration, not browser state. The SDK bridge preserves transition, run, session, message, manifest, parent-transition, and prior-receipt identity and rejects identity, authority, custody, mutation, publication, or admissibility escalation.

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

`run_universal_entry` is the canonical wrapper. Without a custody client it records `custody_submitted=false`, `custody_verified=false`, `master_records_installed=false`, and `reconstructability_status=NOT_SUBMITTED`.

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

The custody receipt must preserve submission, session, message, transition, run, first-event, last-event, count, and event-digest identity. Reconstruction must return the complete validated chain and explicitly report `PASS`. Receipt tamper, identity mismatch, chain drift, digest mismatch, or authority escalation fails closed.

## Current operational state

```text
universal router: installed
engine dispatcher: installed
bounded conversation and synthesis: installed
governed general-conversation fallback: installed_dependency_injected
authoritative record model: installed
canonical projection producer: installed
canonical source collector: installed_dependency_injected
canonical collection integrity validation: installed
packaged read-only catalog builder: installed
catalog integrity validation: installed
authoritative catalog retriever: installed_dependency_injected
live authorized source reader: not_connected
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

The SDK workflow imports the canonical source collector and governed conversation handler, runs `tests/test_canonical_source_conversation.py` with the full universal-entry route-validation set, and verifies both modules remain in the built wheel.

A successful current-main run containing commit `0d7fdf200542b87a7b69e6b611261b74e49a4c71` or later has not yet been independently observed.

## Site boundary

`StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md` remains the Site source of truth. It requires successor Site validation before further Site mutation and keeps live transport disabled. Therefore no Site browser transport, deployment, release, or live-activation change was made in this SDK work block.

## Release boundary

A portable node may declare `ecosystem_read` operational only when a validated packaged catalog or authenticated authoritative source reader is installed. It may declare provider-backed general conversation or `external_llm` operational only when authenticated server-side transport is configured and a live provider result plus provider-usage event is verified. It may claim `RECORDED` only after an identity-matched external custody receipt and independently reconstructed event chain both pass.

Collector code, provider fallback code, transport implementation, fixture receipts, and local reconstruction tests are not live deployment, external custody, or activation evidence.

## Next task

1. Observe current-main SDK validation containing commit `0d7fdf200542b87a7b69e6b611261b74e49a4c71` or later and repair only the first exact repository-local failure.
2. Observe the successor Site Task Runner after Site commit `0c076216f980f6b3c91677571d0692153d7ce94f`; do not mutate Site until the next exact failure or successful evidence set is known.
3. Implement an authorized server-side source reader using the approved repository/connector topology and feed its results to `CanonicalSourceCollector`.
4. Connect an authorized deployed LLM-adapter endpoint to `LLMAdapterHTTPTransport` and `GovernedConversationHandler`; never place credentials in Site or portable-node browser storage.
5. Connect an authorized Master-Records endpoint to `MasterRecordsCustodyClient` and preserve external receipt and reconstruction evidence.
6. Add Site universal-envelope construction and same-origin shared-router submission only after Site handoff gates permit mutation.
7. Add activation evidence binding only after Site validation, live canonical retrieval, live provider use, custody receipt, and reconstructability PASS are observed together.

## Authority boundary

Retrieval is not authority. A source inventory is not authority. A catalog is not authority. A canonical declaration is not execution authority. Provider output is not authority. Authenticated transport is not authority. Local usage persistence is not custody. Continuation events are not proof receipts. Custody-client code is not custody. Only an identity-matched external custody receipt plus independently verified reconstruction can support a bounded `RECORDED` claim, and neither grants execution authority or admissibility.
