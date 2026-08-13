# Public Inspection Entry

The public SDK can be used as a visible inspection-request surface through ordinary pull requests without creating a person-specific evaluator route.

## What a PR means

A pull request can retain a public record of the declarative request payload, revisions, discussion, and receipt identifiers later posted back from a trusted processor.

A PR does **not** itself mean the request has been admitted, governed, executed, retained in Master Records, released, or activated.

## Submission shape

Submit one JSON document matching `inspection/request.schema.json`. The request is declarative only. It must not contain executable instructions, workflow authority, secrets, credentials, or an authority claim.

## Validation and preparation only

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

Preparation intentionally stops before governed execution and returns `NOT_RUN`, `NOT_CLAIMED`, and no `manifest_receipt_id`.

## Run the request and get a governed result

A governed TEST is an ecosystem state transition. The SDK therefore requires canonical Master Records custody before reporting it successfully completed.

Public callers do not manage protected custody credentials. Credential and route authority are owned by TV/TVC. The custody-backed runtime must receive its authenticated Master Records capability through the authorized TV/TVC runtime boundary, not through public SDK arguments, pull requests, manifests, fixtures, or caller-managed environment instructions.

Canonical reconciliation task:

```text
StegVerse-Labs/TVC/tasks/TVC-MASTER-RECORDS-CUSTODY-BROKER-004.json
StegVerse-Labs/TVC/docs/MASTER_RECORDS_CUSTODY_BROKER_MIRROR_HANDOFF.md
```

Until that credential-neutral custody transport is integrated and validated, ordinary local checkouts should use validation/preparation and other credential-free SDK surfaces. Custody-backed run/replay/reconstruction remain authorized-runtime operations.

On an authorized runtime the execution command remains:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run inspection/examples/governed-test-request.json
```

A successful result includes the governance state, canonical `manifest_receipt_id`, transaction ID, chain verification, and a Master Records custody receipt with `custody_status: RECORDED`.

## Replay — option 1

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

Replay does not invoke the original consequence executor and does not mutate the original exact-run record. The replay request itself nevertheless creates ecosystem state transitions. The SDK requires Master Records custody for the full return path:

```text
REQUESTED
-> SOURCE_RESOLVED
-> EVALUATED
-> RETURNED
```

Each transition is recorded under a distinct replay `operation_id`, hash-linked in sequence, and receives a Master Records operation-event receipt. The replay artifact is returned only after `RETURNED` has been recorded.

The returned artifact includes:

```text
operation_id
original_disposition
replay_disposition
deterministic_disposition_match
candidate_identity_match
consequence_reexecuted: false
original_record_mutated: false
operation_transition_custody_status: RECORDED
master_records_operation_receipts
```

## Reconstruction — option 2

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

Reconstruction does not re-execute the original consequence and does not mutate the original exact-run record. Its request, source resolution, derivation, and return are still new ecosystem transitions:

```text
REQUESTED
-> SOURCE_RESOLVED
-> ARTIFACT_DERIVED
-> RETURNED
```

Those transitions are recorded in Master Records before the artifact is returned. The reconstruction response includes its `operation_id`, `operation_transition_custody_status: RECORDED`, operation-event receipts, and the persisted-versus-derived reconstruction material.

## Governing distinction

```text
original_record_mutated: false
original_consequence_reexecuted: false
replay/reconstruction operation transitions exist: true
operation transitions recorded in Master Records: required
caller-managed protected runtime credentials: prohibited
```

A failure to record any required replay/reconstruction transition is a fail-closed condition; no successful artifact is returned.

## Public PR inspection sequence

```text
public PR / local JSON request
-> bounded validation
-> canonical StegCore governed runtime
-> TV/TVC-managed custody transport
-> complete exact-run Master Records custody
-> governance result + manifest_receipt_id
-> later replay/reconstruction request
-> operation transition custody in Master Records
-> returned artifact + operation receipts
```

GitHub remains the visible collaboration record, not evaluator/runtime/custody authority.

## Receipt publication boundary

A `manifest_receipt_id` may be associated with a PR only after the governed run produced it and Master Records confirmed exact-run custody. Replay/reconstruction artifacts may be associated with that public record only after their own operation-transition custody is confirmed. Locators and operation receipts are observations, not authority.

## Validation

```bash
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_public_inspection_runtime
```

Credential boundary: `docs/PUBLIC_CREDENTIAL_BOUNDARY.md`.
