# Universal Entry Integration Handoff

## Purpose

This document is the current continuation source for universal-entry routing, governed conversation, canonical ecosystem retrieval, provider transport, continuation events, Master-Records custody verification, allowlisted repository source reading, server-side composition, non-secret external integration configuration, and activation-evidence binding in `StegVerse-org/StegVerse-SDK`.

## Installed runtime surfaces

```text
stegverse/universal_entry.py
stegverse/universal_entry_dispatch.py
stegverse/universal_entry_handlers.py
stegverse/universal_entry_runtime.py
stegverse/universal_entry_server_runtime.py
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
stegverse/integration_config.py
```

Installed focused tests include all universal-entry routing, dispatch, handler, integration, catalog, continuation, transport, projection, runtime-wrapper, custody, source-reader, governed-conversation, server-runtime, activation-evidence, and integration-configuration suites. The canonical workflow is `.github/workflows/sdk-demo-test.yml`.

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

Every entry adapter must use this same path. Entry adapters do not own provider credentials, repository credentials, custody credentials, execution authority, admissibility, deployment authority, or release authority.

## Server-side composition

```text
UniversalEntryServerConfig
-> disabled-by-default source/provider/custody/readiness switches
-> UniversalEntryServerRuntime
-> optional canonical source collection and catalog construction
-> optional governed provider binding
-> canonical universal-entry execution wrapper
-> optional custody submission and reconstruction verification
-> optional activation-evidence evaluation
```

All live integrations default to disabled. Enabling source collection without an allowlisted source reader, provider use without a governed provider, or custody without a custody client fails closed. Unknown configuration keys fail closed.

Every server-runtime result preserves:

```text
credentials_exposed_to_entry_adapter: false
deployment_authorized: false
activation_performed: false
```

## Non-secret integration configuration

`stegverse/integration_config.py` records external integration identity without embedding credentials or authorizing deployment.

The deterministic configuration packet binds:

```text
environment
source_id -> repository / path / ref
optional expected blob SHA and content digest
read-receipt requirement
credential references, never credential values
provider base URL and required /api/ecosystem-chat path
custody base URL and required /api/custody/universal-entry path
expected service and schema identities
optional same-origin Site route
```

Remote endpoints must use HTTPS. Localhost HTTP is allowed only when explicitly requested for development. Endpoint URLs containing usernames or passwords fail closed. Embedded tokens, API keys, passwords, bearer values, authorization headers, or other credential material fail closed.

The packet always preserves:

```text
credentials_embedded: false
credentials_exposed_to_entry_adapter: false
deployment_authorized: false
activation_performed: false
release_authorized: false
authorizing: false
execution_authority_granted: false
admissibility_determined: false
```

A valid packet is configuration evidence only. It is not proof that an endpoint exists, credentials resolve, transport is live, deployment is authorized, or activation occurred.

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

Each source identifier is bound to one explicit repository, path, and ref. Optional expected blob and content digests are enforced. Unbound sources, repository mismatch, path mismatch, ref mismatch, blob mismatch, empty content, and digest mismatch fail closed.

The fetcher remains dependency-injected and server-side. Connector credentials are not stored by the SDK and must never enter Site JavaScript or portable-node browser storage.

## Governed provider path

```text
bounded local conversation
-> unresolved general conversation only
-> external_information_allowed check
-> GovernedConversationHandler
-> LLMAdapterHTTPTransport
-> LLM-adapter /api/ecosystem-chat
-> provider identity / usage / receipt preservation
-> non-authority guards
-> governed response
```

Provider fallback occurs only for `GENERAL_CONVERSATION_MODEL_NOT_ATTACHED`. Provider attempts to grant authority, execution, custody, mutation, publication, or admissibility fail closed.

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

## Activation evidence

The activation-evidence binder requires one consistent evidence set containing:

```text
SDK current-main validation
Site current-main validation
entry-point parity
non-empty canonical source collection
live provider result and provider receipt
verified provider-usage event
external custody receipt
reconstructability PASS
```

It evaluates readiness only. It cannot deploy, activate, release, grant authority, or determine admissibility. A complete packet may report `ready_for_separate_activation_decision=true`; that is not activation authority.

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
server-side runtime configuration: installed_disabled_by_default
server-side runtime composition: installed
non-secret integration configuration: installed
integration configuration integrity validation: installed
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

The SDK workflow imports and wheel-verifies all universal-entry, collection, source-reader, provider, event, custody, activation-evidence, server-runtime, and integration-configuration modules.

Route validation explicitly includes:

```text
tests/test_integration_config.py
```

alongside the complete existing universal-entry validation set.

A successful current-main run containing commit `7c29ba53af14bd9be74e3c513e4f5b02430d5aff` or later has not yet been independently observed. The GitHub combined-status endpoint returned no status entries for the prior SDK and Site checkpoints, so there is no concrete failing check to repair yet.

## Site boundary

`StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md` remains the Site source of truth. It requires successor Site validation before further Site mutation and keeps live transport disabled. No Site browser transport, deployment, release, or live activation was changed in this SDK block.

## Release boundary

A portable node may declare:

- `ecosystem_read` operational only when a validated packaged catalog or authenticated allowlisted source reader is configured;
- provider-backed conversation or `external_llm` operational only after a live governed provider response, provider receipt, and usage event are verified;
- `RECORDED` only after external custody and reconstruction both pass;
- activation readiness only after all required evidence is present in one validated packet.

Server composition, integration configuration, reader code, transport code, fixtures, local tests, and readiness packets are not deployment, activation, release, custody, admissibility, or execution authority.

## Next task

1. Observe current-main SDK validation containing commit `7c29ba53af14bd9be74e3c513e4f5b02430d5aff` or later and repair only the first exact repository-local failure.
2. Observe the successor Site Task Runner after Site commit `0c076216f980f6b3c91677571d0692153d7ce94f`; do not mutate Site until the next exact failure or successful evidence set is known.
3. Produce a reviewed integration-configuration packet with approved endpoint identities, immutable source refs, and secret-manager references, but no credential values.
4. Supply an explicitly authorized repository fetcher to `AllowlistedRepositorySourceReader` and preserve immutable refs, blob identities, content digests, and read receipts.
5. Supply an authorized deployed LLM-adapter endpoint to `LLMAdapterHTTPTransport` and preserve provider and usage evidence.
6. Supply an authorized Master-Records endpoint to `MasterRecordsCustodyClient` and preserve the external custody receipt and reconstructed chain.
7. Add Site universal-envelope construction and same-origin shared-router submission only after Site handoff gates permit mutation.
8. Build one activation-evidence packet only after SDK validation, Site validation, canonical retrieval, provider use, entry-point parity, custody, and reconstructability PASS are observed together.
9. Do not deploy, activate, release, merge, or tag from this handoff.

## Authority boundary

Retrieval is not authority. A source inventory is not authority. A catalog is not authority. Provider output is not authority. Authenticated transport is not authority. Server composition is not deployment. Integration configuration is not deployment. Continuation events are not proof receipts. Custody-client code is not custody. Activation-evidence readiness is not activation authority. Only separately authorized deployment may activate transport, and neither validation nor custody grants execution authority or admissibility.

## Archive readiness

This handoff preserves the complete universal-entry implementation, server-side composition, integration-configuration contract, authority boundaries, validation posture, external blockers, and next-task state. No future continuation requires access to the conversation that produced these commits.
