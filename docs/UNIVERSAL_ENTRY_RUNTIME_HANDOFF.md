# Universal Entry Runtime Handoff

## Purpose

This document records the first executable implementation of the universal-entry routing contract for `StegVerse-org/StegVerse-SDK`.

Every entry adapter must normalize its input into the same universal entry envelope before any conversational, ecosystem, external-provider, solver, or execution lane is selected.

## Installed files

```text
stegverse/universal_entry.py
tests/test_universal_entry.py
examples/universal_entry/portable_node_capabilities.json
schemas/universal-entry-envelope.schema.v0.1.json
scripts/verify_universal_entry_envelope.py
docs/UNIVERSAL_ENTRY_ROUTING_CONTRACT.md
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
-> governed return envelope
-> deterministic non-authorizing routing receipt
```

## Supported lanes

```text
conversation
ecosystem_query
external_llm
solver
execution
```

The `conversation` lane is the default interpretation and synthesis lane. Ecosystem, external-LLM, and solver requests may select multiple lanes. Restricted execution requests fail closed and do not gain an execution route through universal intake.

## Capability states

Each node declares each capability as one of:

```text
operational
degraded
unavailable
disabled
```

Only `operational` and `degraded` capabilities may be selected. Missing capabilities default to `unavailable`.

A reduced but honest node is permitted. A node must not advertise a capability as operational when only a fixture, display panel, or future interface exists.

## Routing invariants

1. Selected lanes must be present in the manifest's allowed-lane set.
2. `external_llm` requires `external_information_allowed=true`.
3. A selected lane requires an operational or degraded node capability.
4. Restricted credential, destructive, workflow, permission, and force-push requests fail closed.
5. Universal entry routing never grants execution authority.
6. Routing receipts are deterministic for the same canonical request and route decision.
7. Routing receipts do not determine admissibility, transfer custody, or become Master-Records installation.
8. Missing or unavailable capabilities are preserved as explicit degradation rather than silently simulated.

## Current implementation boundary

```text
universal envelope validation: installed
capability registry evaluation: installed
deterministic lane selection: installed
mixed-lane selection: installed
restricted fail-closed behavior: installed
governed return envelope: installed
routing receipt: installed_non_authorizing
conversation engine invocation: not_connected
ecosystem retrieval invocation: not_connected
external LLM invocation: not_connected
solver invocation: not_connected
governed executor invocation: disabled
Master-Records custody: not_connected
entry-point parity verification: not_installed
```

## Release gate

A public portable node must not be released as functional Ecosystem Chat until its declared operational lanes are backed by real engines and pass clean-install parity tests.

Required release demonstrations:

```text
conversation -> conversational response
ecosystem query -> authoritative sourced response
external query -> provider invocation -> governed response
mixed query -> multi-lane synthesis
solver query -> checked solver response
restricted request -> fail closed
provider unavailable -> explicit degradation
routing receipt -> deterministic reconstruction
```

## Next task

1. Export the universal-entry API from the SDK package root.
2. Bind the runtime and tests explicitly into route-validation CI.
3. Add a governed engine-dispatch interface with dependency-injected lane handlers.
4. Implement the conversation lane handler.
5. Implement the ecosystem-read lane handler.
6. Connect the external-LLM lane to `StegVerse-org/LLM-adapter`.
7. Add Site, SDK, API, and portable-node parity fixtures.
8. Add receipt-chain continuation and Master-Records custody adapters.

## Authority boundary

Routing is not execution. Capability availability is not authority. A routing receipt is not a proof receipt, admissibility result, custody transfer, standing determination, or Master-Records installation.
