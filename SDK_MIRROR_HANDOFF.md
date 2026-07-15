# SDK Mirror Handoff

## Source of truth

This file is the current handoff and task source of truth for `StegVerse-org/StegVerse-SDK`.

## Active goal

```text
Goal: governed universal-entry runtime plus SDK-origin transition/SPE progression contracts
Phase: implementation-and-ci-binding-installed-current-main-observation-pending
Result: LOCAL_IMPLEMENTATION_INSTALLED_LIVE_INTEGRATIONS_AND_VALIDATION_EVIDENCE_PENDING
```

The SDK remains non-authorizing. It does not grant execution, delegation, mutation, publication, admissibility, custody, standing, deployment, activation, release, consciousness, personhood, or welfare status.

## Primary architecture

```text
entry adapter
-> universal manifest-bound envelope
-> deterministic capability routing
-> operational lane dispatch
-> bounded or governed-provider conversation
-> governed return
-> linked continuation events
-> optional authenticated Master-Records custody
-> independent reconstruction verification
-> non-authorizing activation-evidence packet
```

Parallel SDK-origin transition path:

```text
SDK_INPUT DECLARED transition candidate
-> deterministic Commitment Candidate
-> transport-neutral SPE intake
-> identity-bound SPE standing receipt
-> progression-only SPE receipt consumer
-> next governed authority boundary
-> master-records/orchestration lifecycle
```

SPE `ALLOW` permits progression only. It is never execution, delegation, mutation, publication, custody, or admissibility.

## Installed universal-entry modules

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
stegverse/github_repository_fetcher.py
stegverse/governed_conversation.py
stegverse/http_transport.py
stegverse/llm_adapter_bridge.py
stegverse/universal_entry_events.py
stegverse/master_records_custody.py
stegverse/master_records_http.py
stegverse/activation_evidence.py
stegverse/integration_config.py
```

Installed behavior:

```text
universal envelope validation: installed
capability and lane routing: installed
restricted fail-closed behavior: installed
operational dispatch: installed
conversation synthesis: installed
bounded arithmetic solver: installed
governed conversation fallback: installed_dependency_injected
authoritative record projection/catalog/retrieval: installed_dependency_injected
allowlisted repository source reader: installed_dependency_injected
GitHub repository contents fetcher: installed_server_side
token resolution: installed_dependency_injected
immutable ref/blob/content validation: installed
GitHub read receipt: installed_deterministic_non_authorizing
LLM-adapter request/return bridge: installed_dependency_injected
authenticated server-side HTTP transport: installed
continuation event chain: installed
Master-Records custody submission/receipt validation: installed
Master-Records HTTPS transport: installed_server_side
Master-Records token resolution: installed_dependency_injected
Master-Records submit/reconstruction routing: installed
independent reconstruction verification: installed
server-side composition: installed_disabled_by_default
non-secret integration configuration packet: installed
activation-evidence binder: installed_non_authorizing
entry-point parity fixtures/tests: installed
```

External runtime status:

```text
GitHub repository credentials: not_configured
live immutable repository read evidence: not_observed
live deployed LLM-adapter endpoint: not_connected
Master-Records credential resolver: not_configured
live Master-Records endpoint: not_connected
external custody receipt: not_observed
external reconstructability PASS: not_observed
Site universal-envelope transport: not_connected
symbolic solver: not_connected
```

## GitHub canonical source path

```text
RepositorySourceBinding
-> GitHubRepositoryFetcher
-> token resolved at call time from credential_ref
-> GitHub contents API at explicit repository/path/ref
-> UTF-8 file content + blob identity
-> deterministic non-authorizing read receipt
-> AllowlistedRepositorySourceReader
-> CanonicalSourceCollector
-> packaged catalog
-> authoritative retrieval
```

`GitHubRepositoryFetcher` accepts only `https://api.github.com`, validates owner/name repository form, URL-encodes path and ref components, requires file responses, verifies path, blob SHA, UTF-8 base64 content, and optional content digest, and returns no credential material.

The token is resolved through a dependency-injected resolver at call time. The token, authorization header, and resolved secret never enter the source binding, read receipt, canonical collection, catalog, governed return, Site, or portable-node browser storage.

The read receipt preserves repository, path, ref, blob SHA, and content digest with:

```text
read_only: true
authorizing: false
custody_transferred: false
credentials_exposed: false
```

A repository read receipt is provenance for retrieval. It is not Master-Records custody, standing, admissibility, execution authority, or deployment evidence.

## Master-Records HTTP custody path

```text
validated continuation event chain
-> build_custody_submission
-> MasterRecordsHTTPTransport.submit
-> token resolved at call time from credential_ref
-> POST /api/custody/universal-entry
-> identity-matched custody receipt
-> MasterRecordsHTTPTransport.reconstruct
-> GET /api/custody/universal-entry/receipts/{receipt_id}/reconstruction
-> independent event-chain reconstruction verification
```

`MasterRecordsHTTPTransport` requires HTTPS for remote services and allows localhost HTTP only when explicitly enabled. It places the resolved bearer token only in the server-side request header, preserves `X-SteGVerse-Session` on custody submission, URL-escapes receipt identities during reconstruction retrieval, requires JSON-object responses, and returns no credential material.

`MasterRecordsHTTPTransport.as_custody_client()` binds the concrete HTTP methods to `MasterRecordsCustodyClient`. The custody client still sets custody and installation fields only after both the returned custody receipt and reconstructed event chain pass independent validation.

Transport implementation is not custody. Endpoint configuration is not custody. A successful HTTP response is not custody until the receipt identity, event digest, event boundaries, reconstruction, and non-authority fields pass.

## SDK-to-SPE commitment and progression

Installed files:

```text
stegverse/transition_candidate.py
stegverse/spe_commitment_intake.py
stegverse/spe_allow_consumer.py
examples/sdk_transition_candidate.json
tests/test_transition_candidate.py
tests/test_spe_commitment_intake.py
tests/test_spe_allow_consumer.py
docs/SDK_TO_SPE_COMMITMENT_INTAKE.md
```

The SPE consumer validates:

```text
transition_id
run_id
candidate_hash
receipt_id
receipt_hash
policy_ref
standing_evidence_ref
decision: ALLOW | DENY | FAIL_CLOSED
```

The progression packet always preserves:

```text
execution_permitted: false
authorizing: false
execution_authority_granted: false
delegation_granted: false
mutation_authorized: false
publication_authorized: false
custody_transferred: false
admissibility_determined: false
fresh_authority_determination_required: true
```

`ALLOW` produces `READY_FOR_NEXT_GOVERNED_BOUNDARY`; `DENY` and `FAIL_CLOSED` produce `PROGRESSION_BLOCKED`.

## Governed LLM and system-boundary path

Installed core artifacts:

```text
schemas/system-boundary-declaration.schema.v0.1.json
stegverse/system_boundary.py
stegverse/system_boundary_round_trip.py
stegverse/governed_llm_manifest.py
stegverse/governed_llm_receipt.py
examples/adapter_governed_llm_session_packet.json
tests/test_system_boundary.py
tests/test_system_boundary_round_trip.py
tests/test_governed_llm_system_boundary_binding.py
tests/test_adapter_origin_manifest_fixture.py
```

The adapter-origin fixture enters manifest and receipt serialization directly from a repository artifact. Test-local packet reconstruction is not required for that path.

Production system-boundary binding remains disabled until separately authorized.

## Capability registry

`sdk.capabilities.json` is reconciled to schema `stegverse.sdk.capabilities.v0.6` and records:

```text
universal-entry runtime surfaces
SDK-to-SPE progression-only consumer
governed LLM/system-boundary surfaces
server runtime disabled-by-default posture
GitHub repository fetcher and read-receipt posture
Master-Records HTTPS transport posture
live integration blockers
current-main validation pending
release readiness false
```

## CI binding

Canonical workflow:

```text
.github/workflows/sdk-demo-test.yml
```

The workflow includes:

```text
full tests/ suite on Python 3.9, 3.11, and 3.12
focused universal-entry route validation
GitHub repository fetcher tests
Master-Records custody and HTTP transport tests
focused SDK-to-SPE and system-boundary validation
SPE ALLOW consumer tests
adapter-origin manifest fixture tests
formal-route validation
dynamic admissibility examples
wheel build and import verification
```

Latest focused integration commits:

```text
54be64fc7850afc39c6f983350d084a9253118e8  Master-Records HTTPS transport
3a5b5b63c752923d0dd1ca13f873df2ec9a88241  Master-Records HTTPS transport tests
f352095c49408d5271e9561da2b34ee7eeb0bb54  Master-Records HTTP CI and wheel binding
83321bfc963c4d27b6f6ada53a74ae89d0511a24  capability registry v0.6
```

A successful current-main workflow containing commit `f352095c49408d5271e9561da2b34ee7eeb0bb54` or later has not yet been independently observed. Do not claim passing tests until workflow evidence exists.

## Site boundary

`StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md` remains the Site source of truth. Site live transport remains disabled and Site mutation is gated by successor current-main validation. No Site browser transport, deployment, activation, release, merge, or tag is authorized here.

## Remaining modules and evidence

```text
1. Observe current-main SDK validation containing f352095c49408d5271e9561da2b34ee7eeb0bb54 or later.
2. Repair only the first exact repository-local failing step, if any.
3. Preserve successful workflow receipts/artifacts after observation.
4. Supply an explicitly authorized GitHub credential resolver to GitHubRepositoryFetcher.
5. Perform and preserve one immutable repository read with ref, blob, digest, and read receipt evidence.
6. Supply an authorized deployed LLM-adapter endpoint to LLMAdapterHTTPTransport.
7. Supply an authorized Master-Records base URL and credential resolver to MasterRecordsHTTPTransport.
8. Perform one custody submission and preserve the external custody receipt and reconstructed chain.
9. Observe successor Site validation before any Site transport mutation.
10. Add Site same-origin universal-envelope submission only after its handoff gate permits it.
11. Build one activation-evidence packet only after SDK validation, Site validation, live canonical retrieval, live provider use, provider usage evidence, custody, and reconstructability PASS exist together.
12. Keep production binding, deployment, activation, release, merge, and tag disabled until separately authorized.
```

## Release posture

```text
release_ready: false
release_or_tag_authorized: false
production_binding_enabled: false
live_transport_verified: false
external_custody_verified: false
current_main_validation_observed: false
```

## Authority boundary

Routing is not execution. A manifest is not authority. A catalog is not authority. A repository read receipt is not custody. Provider output is not authority. SPE `ALLOW` is not execution. A progression packet is not delegation. Continuation events are not custody. Custody HTTP transport is not custody. Custody-client code is not custody. Reconstruction code is not external reconstructability evidence. Activation readiness is not activation authority.

## Archive readiness

This handoff preserves the complete SDK transition/SPE path, universal-entry runtime, GitHub repository fetcher, Master-Records HTTP transport, governed LLM/system-boundary path, CI binding, capability registry, live integration blockers, release posture, and next-task sequence. Earlier conversation context is not required for continuation.
