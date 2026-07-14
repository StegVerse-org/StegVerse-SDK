# Adapter System-Boundary Fixture Provenance Handoff

## Scope

This bounded handoff records the SDK-side provenance guard for the adapter-produced system-boundary fixture.

Repository-wide authority remains `SDK_MIRROR_HANDOFF.md`.

## Installed files

```text
tests/fixtures/adapter-system-boundary-session-packet.v1.json
tests/fixtures/adapter-system-boundary-session-packet.v1.provenance.json
tests/test_adapter_system_boundary_fixture_provenance.py
receipts/adapter-system-boundary-fixture-provenance-2026-07-14.json
```

## Protected identities

```text
producer repo: StegVerse-org/LLM-adapter
producer fixture commit: dbd6ca0bde250bdf9865532049f58d523269d305
declaration id: sbd:sha256:9b43cec895a07d51e02c59aa4d2779d50e288bfe635d8017fcfdbdde66b73101
receipt hash: sha256:24b454a3426aecca2ff6f46f70b9694807e89124969ecbdad998e4310011d317
```

The guard validates semantic identity and non-authority fields rather than exact whitespace. It fails when the mirrored packet drifts in declaration identity, declaration digest, receipt identity, producer source commit, execution authority, custody, admissibility, production-binding posture, or consciousness/personhood/welfare claim boundaries.

## Required boundaries

```text
authorizing: false
custody_transferred: false
admissibility_determined: false
production_binding_enabled: false
model_has_execution_authority: false
consciousness_claim: not_evaluated
personhood_claim: not_evaluated
welfare_claim: not_evaluated
```

## Current state

```text
adapter-origin fixture ingestion: installed
fixture provenance manifest: installed
fixture provenance validation: installed
installation receipt: installed
workflow observation: pending
production binding: disabled
```

## Next event

Observe `sdk-demo-test` containing commit `f324d8062484d900ab2e2eca9407106ef9bac42d` or later. Repair only the first repository-local failure. After success, preserve the workflow-bound provenance result and propagate verified status to Site, Publisher, admissibility-wiki, and stegguardian-wiki without converting verification into authority or enabling automatic production binding.

## Archive readiness

This handoff, the provenance manifest, validator, and installation receipt preserve the complete SDK-side continuation state. Earlier conversation context is not required.
