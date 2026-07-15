# Universal Entry Runtime Handoff

## Purpose

This document is the current runtime continuation source of truth for `StegVerse-org/StegVerse-SDK` universal-entry routing.

Every entry adapter must normalize its input into the same universal entry envelope before any conversational, ecosystem, external-provider, solver, or execution lane is selected. Entry adapters do not directly own provider, repository, solver, custody, or execution authority.

## Installed files

```text
schemas/universal-entry-envelope.schema.v0.1.json
examples/universal_entry/site_chat_good_morning.json
examples/universal_entry/portable_node_capabilities.json
examples/universal_entry/entry_point_parity.json
scripts/verify_universal_entry_envelope.py
stegverse/universal_entry.py
stegverse/universal_entry_dispatch.py
stegverse/universal_entry_handlers.py
tests/test_universal_entry.py
tests/test_universal_entry_dispatch.py
tests/test_universal_entry_handlers.py
tests/test_universal_entry_parity.py
docs/UNIVERSAL_ENTRY_ROUTING_CONTRACT.md
docs/UNIVERSAL_ENTRY_RUNTIME_HANDOFF.md
.github/workflows/sdk-demo-test.yml
```

## Runtime sequence

```text
entry adapter
-> universal entry envelope
-> request and manifest validation
-> declared node capability registry
-> deterministic lane classification
-> allowed-lane and external-information checks
-> capability availability evaluation
-> fail-closed restricted-request handling
-> operational lane dispatch
-> conversation synthesis lane
-> governed return envelope
-> deterministic non-authorizing routing and dispatch receipts
```

## Supported lanes

```text
conversation
ecosystem_query
external_llm
solver
execution
```

`conversation` remains the default interpretation lane. For a multi-lane request, operational lanes run first and conversation runs last so it can synthesize ecosystem, provider, or solver results into one user-facing response.

## Installed operational handlers

### Conversation

The bounded local conversation handler now performs greetings, thanks, capability explanation, and final synthesis of prior lane results. Open-ended general conversation remains honestly `degraded` until a general conversational model is attached.

### Ecosystem query

`EcosystemQueryHandler` consumes a dependency-injected authoritative retriever. It preserves evidence sources and counts. When no retriever is configured it returns `unavailable`; it does not fabricate ecosystem knowledge.

### External LLM

`ExternalLLMHandler` consumes a dependency-injected provider callable and preserves provider name, model, usage metadata, and provider receipt reference. When no provider is configured it returns `unavailable`; it does not substitute fixture output.

### Solver

The local solver performs bounded arithmetic with an AST allowlist. Symbolic algebra, calculus, and unsupported expressions return explicit degradation until a checked symbolic engine is attached.

### Execution

Execution remains disabled. Universal intake does not grant execution authority.

## Capability states

Each node declares every capability as one of:

```text
operational
degraded
unavailable
disabled
```

Only `operational` and `degraded` capabilities may be selected. Missing capabilities default to `unavailable`. A reduced but honest node is permitted. A node must not advertise a capability as operational when only a fixture, display panel, or future interface exists.

## Routing and dispatch invariants

1. Selected lanes must be present in the manifest allowed-lane set.
2. `external_llm` requires `external_information_allowed=true`.
3. A selected lane requires an operational or degraded node capability.
4. Restricted credential, destructive, workflow, permission, and force-push requests fail closed.
5. Universal entry routing and dispatch never grant execution authority.
6. Operational handlers cannot escalate authority, custody, admissibility, or execution fields.
7. Conversation executes last on multi-lane requests for synthesis.
8. Missing handlers and unavailable capabilities remain explicit rather than silently simulated.
9. Routing and dispatch receipts are deterministic for the same canonical request and result set.
10. Receipts produced here are non-authorizing and are not Master-Records custody.

## Entry-point parity

The parity fixture and tests cover:

```text
site_chat
sdk
api
portable_node
stegtalk
agent
external_actor_gateway
```

Equivalent requests must produce equivalent selected lanes, dispatch order, governed status, response content, and authority posture. Entry-point identity remains preserved in each routing receipt, so receipts differ while routing semantics remain equivalent.

## Current implementation boundary

```text
universal envelope validation: installed
capability registry evaluation: installed
deterministic lane selection: installed
mixed-lane selection: installed
restricted fail-closed behavior: installed
governed return envelope: installed
routing receipt: installed_non_authorizing
engine dispatcher: installed
conversation bounded handler: operational_limited
conversation general model: not_connected
ecosystem retrieval interface: installed_dependency_injected
authoritative ecosystem retriever: not_connected
external LLM interface: installed_dependency_injected
live external provider: not_connected
bounded arithmetic solver: operational
symbolic solver: not_connected
conversation synthesis: installed
entry-point parity fixture/tests: installed
Master-Records custody: not_connected
governed executor invocation: disabled
```

## CI binding

The SDK validation workflow imports the universal-entry runtime, dispatcher, and handler registry, runs the runtime/dispatch/handler test suites in route validation, and verifies the built wheel contains the runtime modules. The complete test job also discovers parity tests through `pytest tests/`.

A successful current-main workflow result containing the latest handler and parity commits has not yet been independently observed.

## Release gate

A public portable node must not be released as functional Ecosystem Chat until every capability declared `operational` is backed by a real engine and clean-install parity tests pass.

Required release demonstrations:

```text
conversation -> conversational response
ecosystem query -> authoritative sourced response
external query -> provider invocation -> governed response
mixed query -> multi-lane synthesis
solver query -> checked solver response
restricted request -> fail closed
provider unavailable -> explicit degradation
routing and dispatch receipts -> deterministic reconstruction
```

## Next task

1. Connect an authoritative ecosystem retriever using repository manifests, handoffs, status records, and receipts.
2. Connect `ExternalLLMHandler` to the `StegVerse-org/LLM-adapter` governed provider return contract.
3. Attach a general conversational model through the external/provider lane without bypassing governance.
4. Add a checked symbolic solver adapter.
5. Bind Site browser input to universal envelope construction and shared router transport.
6. Add API, SDK, portable-node, StegTalk, agent, and external-gateway adapter fixtures generated by their actual implementations.
7. Emit routing, retrieval, provider-usage, synthesis, and solver event records into receipt-chain continuation.
8. Connect authenticated Master-Records custody and reconstructability verification.
9. Observe current-main CI and repair only the first exact repository-local failure.

## Authority boundary

Routing is not execution. Capability availability is not authority. Engine completion is not admissibility. A routing or dispatch receipt is not a proof receipt, custody transfer, standing determination, or Master-Records installation.

## Archive readiness

This handoff preserves the universal envelope, router, dispatcher, operational handler interfaces, bounded local handlers, synthesis order, capability honesty, parity verification, CI binding, release gate, and next-task state. Earlier conversation context is not required for continuation.
