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
stegverse/governed_conversation.py
stegverse/http_transport.py
stegverse/llm_adapter_bridge.py
stegverse/universal_entry_events.py
stegverse/master_records_custody.py
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
LLM-adapter request/return bridge: installed_dependency_injected
authenticated server-side HTTP transport: installed
continuation event chain: installed
Master-Records custody receipt validation: installed
independent reconstruction verification: installed
server-side composition: installed_disabled_by_default
non-secret integration configuration packet: installed
activation-evidence binder: installed_non_authorizing
entry-point parity fixtures/tests: installed
```

External runtime status:

```text
live authorized repository fetcher: not_connected
live deployed LLM-adapter endpoint: not_connected
live Master-Records endpoint: not_connected
Site universal-envelope transport: not_connected
symbolic solver: not_connected
```

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

The adapter-origin fixture now enters manifest and receipt serialization directly from a repository artifact. Test-local packet reconstruction is no longer required for that path.

Production system-boundary binding remains disabled until separately authorized.

## Capability registry

`sdk.capabilities.json` is reconciled to schema `stegverse.sdk.capabilities.v0.4` and now records:

```text
universal-entry runtime surfaces
SDK-to-SPE progression-only consumer
governed LLM/system-boundary surfaces
server runtime disabled-by-default posture
live integration blockers
current-main validation pending
release readiness false
```

## CI binding

Canonical workflow:

```text
.github/workflows/sdk-demo-test.yml
```

The workflow now includes:

```text
full tests/ suite on Python 3.9, 3.11, and 3.12
focused universal-entry route validation
focused SDK-to-SPE and system-boundary validation
SPE ALLOW consumer tests
adapter-origin manifest fixture tests
formal-route validation
dynamic admissibility examples
wheel build and import verification
```

Latest focused integration commits:

```text
db376d15d749b24e20caf1daba201ca6f0566def  SPE ALLOW consumer
41a7a3b1ef4b99478586f1bb7af1e5b00b658428  SPE consumer tests
994b66b21afbc21d4280e3dd3507ad6440c5fbf2  adapter-origin session fixture
1e5d9abafdecc6b3f883e8259c5f84f989f7dbda  adapter-origin fixture tests
5457bafd6736cde00e2bcde17f9a4ac03033282a  CI and wheel binding
12900884a1c2079026590cc2765fa87477b97445  capability registry reconciliation
```

A successful current-main workflow containing commit `5457bafd6736cde00e2bcde17f9a4ac03033282a` or later has not yet been independently observed. Do not claim passing tests until workflow evidence exists.

## Site boundary

`StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md` remains the Site source of truth. Site live transport remains disabled and Site mutation is gated by successor current-main validation. No Site browser transport, deployment, activation, release, merge, or tag is authorized here.

## Remaining modules and evidence

```text
1. Observe current-main SDK validation containing 5457bafd6736cde00e2bcde17f9a4ac03033282a or later.
2. Repair only the first exact repository-local failing step, if any.
3. Preserve successful workflow receipts/artifacts after observation.
4. Supply an explicitly authorized repository fetcher to AllowlistedRepositorySourceReader.
5. Supply an authorized deployed LLM-adapter endpoint to LLMAdapterHTTPTransport.
6. Supply an authorized Master-Records endpoint to MasterRecordsCustodyClient.
7. Observe successor Site validation before any Site transport mutation.
8. Add Site same-origin universal-envelope submission only after its handoff gate permits it.
9. Build one activation-evidence packet only after SDK validation, Site validation, live canonical retrieval, live provider use, provider usage evidence, custody, and reconstructability PASS exist together.
10. Keep production binding, deployment, activation, release, merge, and tag disabled until separately authorized.
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

Routing is not execution. A manifest is not authority. A catalog is not authority. Provider output is not authority. SPE `ALLOW` is not execution. A progression packet is not delegation. Continuation events are not custody. Custody-client code is not custody. Reconstruction code is not external reconstructability evidence. Activation readiness is not activation authority.

## Archive readiness

This handoff now preserves the complete SDK transition/SPE path, universal-entry runtime, governed LLM/system-boundary path, CI binding, capability registry, live integration blockers, release posture, and next-task sequence. Earlier conversation context is not required for continuation.
