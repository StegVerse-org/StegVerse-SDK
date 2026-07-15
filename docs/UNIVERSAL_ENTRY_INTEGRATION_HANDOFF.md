# Universal Entry Integration Handoff

## Purpose

This document is the current continuation source for universal-entry routing, governed conversation, canonical ecosystem retrieval, provider transport, continuation events, Master-Records custody verification, allowlisted repository source reading, and activation-evidence binding in `StegVerse-org/StegVerse-SDK`.

## Installed files

```text
stegverse/universal_entry.py
stegverse/universal_entry_dispatch.py
stegverse/universal_entry_handlers.py
stegverse/universal_entry_runtime.py
stegverse/ecosystem_records.py
stegverse/ecosystem_projection.py
stegverse/ecosystem_catalog.py
stegverse/canonical_source_collector.py
stegverse/repository_source_reader.py
stegverse/governed_conversation.py
stegverse/http_transport.py
stegverse/llm_adapter_bridge.py
stegverse/universal_entry_events.py
stegverse/master_records_custody.py
stegverse/activation_evidence.py
tests/test_universal_entry.py
tests/test_universal_entry_dispatch.py
tests/test_universal_entry_handlers.py
tests/test_universal_entry_integrations.py
tests/test_universal_entry_catalog_events.py
tests/test_universal_entry_transport_projection.py
tests/test_universal_entry_runtime_wrapper.py
tests/test_master_records_custody.py
tests/test_canonical_source_conversation.py
tests/test_repository_source_activation.py
.github/workflows/sdk-demo-test.yml
```

## Universal path

```text
entry adapter
-> universal manifest-bound envelope
-> capability and authority-neutral routing
-> operational lane dispatch
-> bounded or provider-backed conversation synthesis
-> governed return
-> linked continuation events
-> optional authenticated custody submission
-> identity-matched custody receipt
-> independent reconstruction verification
-> activation evidence aggregation
```

Every entry adapter must use this same path. Entry adapters do not own provider credentials, repository credentials, custody credentials, execution authority, admissibility, or release authority.

## Canonical ecosystem path

```text
explicit source inventory
-> CanonicalSourceSpec validation
-> AllowlistedRepositorySourceReader
-> repository / path / ref / blob / content-digest checks
-> CanonicalSourceCollector
-> canonical collection evidence
-> project_records
-> packaged read-only catalog
-> AuthoritativeEcosystemRetriever
-> EcosystemQueryHandler
-> conversation synthesis
```

`AllowlistedRepositorySourceReader` binds each source identifier to one explicit repository, path, and ref. Optional expected blob and content digests are enforced. Unbound sources, repository mismatch, path mismatch, ref mismatch, blob mismatch, empty content, and digest mismatch fail closed.

The fetcher remains dependency-injected and server-side. Connector credentials are not stored by the SDK and must never enter Site JavaScript or portable-node browser storage.

## Governed conversation and provider path

```text
conversation request
-> bounded local handler
-> local response for supported greetings / thanks / capability explanation
-> unresolved general conversation only
-> external_information_allowed check
-> GovernedConversationHandler
-> LLMAdapterHTTPTransport
-> LLM-adapter /api/ecosystem-chat
-> provider identity / usage / receipt preservation
-> non-authority guards
-> governed response
```

Provider fallback occurs only for `GENERAL_CONVERSATION_MODEL_NOT_ATTACHED`. Provider output remains non-authorizing. Provider attempts to grant authority, execution, custody, mutation, publication, or admissibility fail closed.

## Continuation and custody path

```text
routing event
-> retrieval / provider_usage / solver event as applicable
-> synthesis event as applicable
-> event-chain validation
-> build_custody_submission
-> authenticated custody transport
-> identity-matched receipt validation
-> reconstruction retrieval
-> independent event-chain validation
-> reconstructability_status: PASS
```

Without an injected custody client, the governed return records:

```text
custody_submitted: false
custody_verified: false
master_records_installed: false
reconstructability_status: NOT_SUBMITTED
```

Only an external identity-matched custody receipt plus independently verified reconstruction may set custody and installation fields true.

## Activation evidence path

```text
SDK current-main validation
+ Site current-main validation and entry-point parity
+ non-empty canonical source collection
+ live provider result, provider receipt, and usage event
+ external custody receipt and reconstructability PASS
-> evaluate_activation_evidence
-> deterministic readiness packet
```

`activation_evidence.py` evaluates evidence only. It cannot deploy or activate anything. Its packet always preserves:

```text
activation_performed: false
deployment_authorized: false
release_authorized: false
authorizing: false
execution_authority_granted: false
admissibility_determined: false
```

A complete packet may report `ready_for_separate_activation_decision=true`; that is not activation authority. Missing validation, source collection, provider use, usage evidence, custody, reconstruction, or entry-point parity remains an explicit blocker.

## Current operational state

```text
universal router: installed
engine dispatcher: installed
bounded conversation and synthesis: installed
governed general-conversation fallback: installed_dependency_injected
authoritative record model: installed
canonical projection producer: installed
canonical source collector: installed_dependency_injected
allowlisted repository source reader: installed_dependency_injected
repository/path/ref/blob/content integrity guards: installed
packaged read-only catalog builder: installed
authoritative catalog retriever: installed_dependency_injected
live authorized repository fetcher: not_connected
LLM-adapter request and return bridge: installed
authenticated server-side JSON transport: installed
LLM-adapter HTTP transport: installed
live deployed provider endpoint: not_connected
provider usage preservation: installed
continuation event chain: installed
Master-Records custody client: installed_dependency_injected
custody receipt validation: installed
reconstruction verification: installed
live Master-Records endpoint: not_connected
activation evidence binder: installed_non_authorizing
Site universal-envelope transport: not_connected
```

## CI binding

The SDK workflow imports all universal-entry, collection, source-reader, provider, event, custody, and activation-evidence modules. Route validation explicitly includes `tests/test_repository_source_activation.py`, and the wheel job verifies the new modules remain packaged.

A successful current-main run containing commit `dc4f6f1cff684a862cd81df1f98aa770c1c52964` or later has not yet been independently observed. The GitHub combined-status endpoint returned no status entries, so there is no concrete failing check to repair yet.

## Site boundary

`StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md` remains the Site source of truth. It requires successor Site validation before further Site mutation and keeps live transport disabled. No Site browser transport, deployment, release, or live activation was changed in this SDK block.

## Release boundary

A portable node may declare:

- `ecosystem_read` operational only when a validated packaged catalog or authenticated allowlisted source reader is configured;
- provider-backed conversation or `external_llm` operational only after a live governed provider response, provider receipt, and usage event are verified;
- `RECORDED` only after external custody and reconstruction both pass;
- activation readiness only after all required evidence is present in one validated packet.

Reader code, transport code, fixtures, local tests, and readiness packets are not deployment, activation, release, custody, admissibility, or execution authority.

## Next task

1. Observe current-main SDK validation containing commit `dc4f6f1cff684a862cd81df1f98aa770c1c52964` or later and repair only the first exact repository-local failure.
2. Observe the successor Site Task Runner after Site commit `0c076216f980f6b3c91677571d0692153d7ce94f`; do not mutate Site until the next exact failure or successful evidence set is known.
3. Configure an authorized server-side repository fetcher for `AllowlistedRepositorySourceReader` and preserve read receipts and immutable refs.
4. Connect an authorized deployed LLM-adapter endpoint to `LLMAdapterHTTPTransport` and preserve provider and usage evidence.
5. Connect an authorized Master-Records endpoint to `MasterRecordsCustodyClient` and preserve the external custody receipt and reconstructed chain.
6. Add Site universal-envelope construction and same-origin shared-router submission only after Site handoff gates permit mutation.
7. Build one activation-evidence packet only after SDK validation, Site validation, canonical retrieval, provider use, entry-point parity, custody, and reconstructability PASS are observed together.
8. Do not deploy, activate, release, merge, or tag from this handoff.

## Authority boundary

Retrieval is not authority. A source inventory is not authority. A catalog is not authority. Provider output is not authority. Authenticated transport is not authority. Continuation events are not proof receipts. Custody-client code is not custody. Activation-evidence readiness is not activation authority. Only separately authorized deployment may activate transport, and neither validation nor custody grants execution authority or admissibility.
