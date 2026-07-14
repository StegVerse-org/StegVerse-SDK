# Adapter System-Boundary Fixture Provenance Handoff

## Scope

This bounded handoff records the SDK-side provenance guard, workflow-evidence contract, and joint cross-repository activation gate for the adapter-produced system-boundary fixture.

Repository-wide authority remains `SDK_MIRROR_HANDOFF.md`.

## Installed files

```text
tests/fixtures/adapter-system-boundary-session-packet.v1.json
tests/fixtures/adapter-system-boundary-session-packet.v1.provenance.json
tests/test_adapter_system_boundary_fixture_provenance.py
stegverse/system_boundary_workflow_evidence.py
evidence/system-boundary-workflow-evidence.pending.v0.1.json
tests/test_system_boundary_workflow_evidence.py
stegverse/system_boundary_activation.py
evidence/system-boundary-activation.pending.v0.1.json
tests/test_system_boundary_activation.py
receipts/adapter-system-boundary-fixture-provenance-2026-07-14.json
receipts/adapter-system-boundary-provenance-workflow-binding-2026-07-14.json
receipts/system-boundary-workflow-evidence-contract-2026-07-14.json
receipts/system-boundary-workflow-evidence-binding-2026-07-14.json
receipts/system-boundary-joint-activation-gate-2026-07-14.json
receipts/system-boundary-joint-activation-workflow-binding-2026-07-14.json
.github/workflows/sdk-demo-test.yml
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
pending_is_verified: false
missing_status_becomes_pass: false
release_authorized: false
one_repository_pass_can_verify: false
downstream_propagation_allowed: false
```

## Workflow binding

```text
sdk-demo-test workflow commit: 1e1d58d8da3327c2e7efd1f33c43eca3810cce07
adapter fixture ingestion test: tests/test_adapter_origin_system_boundary_fixture.py
provenance guard: tests/test_adapter_system_boundary_fixture_provenance.py
workflow evidence guard: tests/test_system_boundary_workflow_evidence.py
joint activation guard: tests/test_system_boundary_activation.py
complete test-suite coverage: inherited from pytest tests/
explicit route-validation coverage: installed
```

## Joint activation behavior

```text
PENDING + PENDING -> PENDING
PASS + PENDING -> PENDING
PENDING + PASS -> PENDING
PASS + PASS -> VERIFIED
either FAIL -> FAILED
invalid or authority-escalated evidence -> INVALID_EVIDENCE
```

A single repository result cannot authorize verified propagation. Both repository evidence records must be independently accepted and verified.

## Current state

```text
adapter-origin fixture ingestion: installed
fixture provenance validation: installed
workflow evidence validator: installed
pending evidence record: installed
joint activation gate: installed
joint activation pending record: installed
canonical activation-test binding: installed
workflow observation: pending
combined status observation: no status reported
verified downstream propagation: blocked
production binding: disabled
release authorization: false
```

## Next event

Observe `sdk-demo-test` containing commit `1e1d58d8da3327c2e7efd1f33c43eca3810cce07` or later and the corresponding canonical `LLM-adapter` validation. Repair only the first repository-local failure. A `PENDING` or missing status must not be converted into `PASS`. Record the exact observed commit, run ID, and run URL for both repositories before changing the joint activation record to `VERIFIED` or propagating verified status to Site, Publisher, admissibility-wiki, or stegguardian-wiki.

## Archive readiness

This handoff, the provenance manifests, evidence contracts, activation gate, validators, workflow-binding receipts, and installation receipts preserve the complete SDK-side continuation state. Earlier conversation context is not required.
