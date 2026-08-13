# Public Inspection Entry

The public SDK can be used as a visible inspection-request surface through ordinary pull requests without creating a person-specific evaluator route.

## What a PR means

A pull request can retain a public record of the declarative request payload, revisions, discussion, and receipt identifiers later posted back from a trusted processor.

A PR does **not** itself mean the request has been admitted, governed, executed, retained in Master Records, released, or activated.

## Submission shape

Submit one JSON document matching `inspection/request.schema.json`. The request is declarative only. It must not contain executable instructions, workflow authority, secrets, credentials, or an authority claim.

A request can specify a neutral `request_id`, optional public `requester_label`, `case_profile`, bounded input data, requested return projection, optional explanatory labels, and `authority_claim: false`. A personal name is not required.

## Validation and preparation only

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

The preparation adapter converts the request to the ordinary option `0A` raw-data submission descriptor and intentionally returns:

```text
runtime_processing_status: NOT_RUN
master_records_custody_status: NOT_CLAIMED
manifest_receipt_id: null
```

That command is useful for inspecting ingress shape. It is not a governed run.

## Run the request and get a governed result

A governed TEST is an ecosystem state transition. The SDK therefore requires canonical Master Records custody before it will report the run as successfully completed.

Python 3.11+ is required because the governed-test StegCore dependency requires Python 3.11+.

```bash
export MASTER_RECORDS_URL="<admitted-master-records-base-url>"
export MASTER_RECORDS_AUTH_TOKEN="<authorized-token>"
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run \
  inspection/examples/governed-test-request.json
```

The governed-test fixture contains `input.steggate_request`, a canonical StegCore `AdmissibilityRequest`, plus separate `input.input_data` used to identify the submitted test payload.

The runtime uses canonical StegCore `run_manifested_transaction(...)`, `ManifestReceiptRegistry`, and `build_master_records_submission(...)`. It does not implement a parallel evaluator, receipt algorithm, or custody store. The consequence executor is side-effect-free in TEST mode.

A successful result contains:

```text
runtime_mode: TEST
governance_state: ALLOW | DENY | REVIEW | FAIL_CLOSED
manifest_receipt_id: MR-...
transaction_id: TX-...
chain_verified: true
external_side_effect: false
master_records_custody_status: RECORDED
master_records_custody_receipt: {...}
```

The complete exact-run evidence package contains the manifested transaction and its transition receipt chain. Master Records custody occurs before the SDK reports success.

## Public PR inspection sequence

```text
public PR / local JSON request
-> bounded request validation
-> canonical StegCore governed TEST runtime
-> complete exact-run evidence package
-> canonical Master Records custody: RECORDED
-> governance result + manifest_receipt_id
-> locator may be posted back to the PR as an observation
```

GitHub remains the visible collaboration record, not evaluator/runtime/custody authority.

## Replay — option 1

Replay is available through the same SDK surface:

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

The SDK retrieves the exact retained package from Master Records, rebuilds the original canonical StegCore governance request, and re-evaluates it without invoking a consequence executor.

Required replay properties:

```text
deterministic_disposition_match: true | false
candidate_identity_match: true | false
consequence_reexecuted: false
original_record_mutated: false
```

Replay is read-only. Because no ecosystem state is changed, replay does not create a second custody mutation or rewrite the original run.

## Reconstruction — option 2

Reconstruction is also available through the SDK:

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

The SDK calls the canonical Master Records reconstruction route. The response separates persisted historical evidence from reconstructed/derived material and must preserve:

```text
original_record_mutated: false
consequence_reexecuted: false
reconstruction_grants_authority: false
```

Reconstruction is read-only and does not create an ecosystem state change.

## Isolated local Master Records

A tester can run the canonical `master-records/orchestration` service locally instead of using a shared deployment. This keeps the same ownership and custody implementation rather than duplicating Master Records in the SDK.

Example:

```bash
git clone https://github.com/master-records/orchestration.git ../master-records-orchestration
export PYTHONPATH="../master-records-orchestration:${PYTHONPATH}"
export MASTER_RECORDS_AUTH_TOKEN="local-test-token"
export MASTER_RECORDS_RECEIPT_KEY="local-test-receipt-key"
export MASTER_RECORDS_DB="$PWD/.stegverse/master-records.db"
python -m uvicorn services.canonical_custody_app:app --host 127.0.0.1 --port 8787
```

Then in the SDK shell:

```bash
export MASTER_RECORDS_URL="http://127.0.0.1:8787"
export MASTER_RECORDS_AUTH_TOKEN="local-test-token"
```

This is canonical Master Records custody in an isolated test environment; it is not a production-activation claim.

## Receipt publication boundary

A `manifest_receipt_id` may be associated with a PR only after the corresponding governed run produced it **and Master Records confirmed exact-run custody**. The locator is never permission or authority.

## Validation

```bash
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_public_inspection_runtime
```
