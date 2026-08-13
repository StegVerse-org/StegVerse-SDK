# Public Inspection Entry

The public SDK can be used as a visible inspection-request surface through ordinary pull requests without creating a person-specific evaluator route.

## What a PR means

A pull request can retain a public record of the declarative request payload, revisions, discussion, and receipt identifiers later posted back from a trusted processor.

A PR does **not** itself mean the request has been admitted, governed, executed, retained in production Master Records, released, or activated.

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

That command is useful for inspecting the ingress object but it is not the governed TEST command.

## Run the request and get a governed TEST result

Install the optional governed-test runtime. Python 3.11+ is required because the pinned canonical StegCore revision requires Python 3.11+.

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```

The governed-test fixture contains `input.steggate_request`, a canonical StegCore `AdmissibilityRequest`, plus separate `input.input_data` used to identify the submitted test payload.

The runtime uses the canonical StegCore `run_manifested_transaction(...)` and `ManifestReceiptRegistry` implementations. It does not implement a parallel evaluator. The executor is a side-effect-free TEST executor.

The result contains:

```text
runtime_mode: TEST
governance_state: ALLOW | DENY | REVIEW | FAIL_CLOSED
manifest_receipt_id: MR-...
transaction_id: TX-...
chain_verified: true | false
external_side_effect: false
evidence_package: {...}
reconstruction: {...}
local_exact_run_retained: true
production_master_records_custody: false
```

The returned `manifest_receipt_id` is therefore a real canonical StegCore exact-run locator for that locally retained governed TEST run. It is not fabricated and it can be used against the same local append-only test registry. It is **not** a representation that production Master Records custody occurred.

Default local retained files:

```text
.stegverse/public-inspection/manifest-receipts.jsonl
.stegverse/public-inspection/transaction-receipts.jsonl
```

## Public PR inspection sequence

A public PR can carry `inspection/request.schema.json` data as a visible request record. A reviewer or contributor can then run the exact request with trusted checked-out SDK code rather than code supplied by the PR:

```text
public PR / local JSON request
-> bounded request validation
-> canonical StegCore governed TEST runtime
-> append-only local exact-run registry
-> governance result + manifest_receipt_id + evidence + reconstruction
-> result/locator may be posted back to the PR as an observation
```

GitHub remains the visible collaboration record, not the evaluator or runtime authority.

## Production-custody continuation

The production path is a stronger and separate custody boundary:

```text
trusted governed ingress
-> canonical StegCore governance / consequence boundary
-> full exact-run Master Records custody
-> caller-facing projection
-> production-custodied manifest_receipt_id
```

The local TEST command does not claim that production custody step. Production custody remains dependent on the admitted Master Records transport and its activation/readiness requirements.

## Receipt publication boundary

A receipt locator may be associated with a PR only after the corresponding governed run produced it. When the run is local TEST mode, the record must be labeled as a local TEST exact-run locator. When production Master Records custody is independently verified, the locator may be described as production-custodied. A locator is never permission or authority.

## Validation

```bash
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
```

With the governed-test extra installed:

```bash
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```
