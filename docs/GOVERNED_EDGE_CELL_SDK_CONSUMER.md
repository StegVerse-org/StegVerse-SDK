# Governed Edge-Cell SDK Consumer

## Purpose

The SDK consumes a source-bound declaration from the canonical governed
edge-cell implementation in:

```text
StegVerse-002/micro-node-runtime
commit c9660dd0dffd97d9ececc9b7428ef165ae212419
```

Canonical SDK fixture:

```text
examples/edge_cell_source_binding.json
```

Canonical SDK validator:

```text
stegverse/edge_cell_consumer.py
```

The consumer verifies compatibility and lineage. It does not execute the
runtime, reproduce its activation decision, grant authority, accept custody,
or publish a deployment claim.

## Accepted source binding

The fixture binds the SDK to:

```text
profile id: stegverse.edge-cell.governed.v1
profile version: 1.0.0
profile path: profiles/governed_edge_cell.v1.json
activation evidence path: examples/edge_cell_activation_evidence.generated.json
profile SHA-256: 0a31dabd5ba8e8f5e526a087b4194eccca1456c693546c742ccf9b2fab945ab1
activation input SHA-256: a90a33fb74205e947146f2098e020a299c9e29a50ddf2c8a9cafad759646ea2c
activation receipt SHA-256: c546a4addf80eebead9cc17324fad7580d6d5050c5347e86969c91d8d9cf7299
```

Changing any of those bindings requires an explicit SDK update and a new
validation cycle. Source drift is rejected rather than silently accepted.

## Capability boundary

The consumer accepts the nine bounded profile capabilities:

```text
LOCAL_INFERENCE
LOCAL_KNOWLEDGE_RETRIEVAL
SENSOR_OBSERVATION
SEGMENTED_STORAGE
RECEIPT_LEDGER
STORE_AND_FORWARD
MESH_RELAY
HEALTH_TELEMETRY
CONTINUITY_RECOVERY
```

These remain transition-specific and are not activated by SDK acceptance:

```text
PHYSICAL_ACTUATION
EXTERNAL_EXPORT
FEDERATED_COMMIT
```

The SDK verifies that direct model actuation and default external export remain
denied, missing evidence fails closed, degraded operation reduces capability,
network loss becomes local-only operation, and federated commit requires a
quorum.

## Result semantics

A successful result has:

```text
accepted = true
status = accepted_for_non_authorizing_sdk_consumption
```

That status means only that the committed fixture matches the SDK's accepted
source contract.

It does not mean:

```text
execution authority
admissibility
physical actuation authority
external export authority
federated commit authority
Master Records custody acceptance
publication acceptance
deployment proof
governed activation at a live node
```

A rejected result has:

```text
accepted = false
status = rejected_fail_closed
```

## Custody posture

The source fixture must retain:

```text
SOURCE_GENERATED_NOT_DESTINATION_ACCEPTED
```

The SDK rejects a fixture that inserts a destination custody receipt. An
independent Master Records consumer must verify the source hashes and issue its
own accept or reject receipt before custody can be claimed.

## Verification

```bash
pytest tests/test_edge_cell_consumer.py -v
python scripts/verify_edge_cell_consumer.py
pytest tests/ -v
```

The consolidated SDK workflow runs the targeted verifier, the complete test
suite, public-import checks, route validation, and package build across its
existing compatibility matrix.
