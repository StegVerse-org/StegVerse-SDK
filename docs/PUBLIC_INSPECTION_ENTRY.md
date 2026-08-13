# Public Inspection Entry

The public SDK can be used as a visible inspection-request surface through ordinary pull requests without creating a person-specific evaluator route.

## What a PR means

A pull request can retain a public record of the declarative request payload, revisions, discussion, and any receipt identifiers later posted back by a trusted processor.

A PR does **not** mean the request has been admitted, governed, executed, retained in Master Records, released, or activated.

## Submission shape

Submit one JSON document matching `inspection/request.schema.json`. The request is declarative only. It must not contain executable instructions, workflow authority, secrets, credentials, or an authority claim.

A request can specify a neutral `request_id`, optional public `requester_label`, `case_profile`, bounded input data, requested return projection, optional explanatory labels, and `authority_claim: false`. A personal name is not required.

## Validate the request

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m unittest tests.test_public_inspection_request
```

## Bind it to the ordinary governed path

Use the repository adapter:

```bash
python -m stegverse.public_inspection inspection/examples/example-request.json
```

The adapter validates the same bounded request and converts it into the ordinary option `0A` raw-data submission descriptor through `stegverse.governance_navigation.build_raw_submission_descriptor`.

The prepared object identifies:

```text
ordinary_governance_option: 0A
ingress_mode: sdk_manifested_raw_data
source: stegverse-sdk:public-inspection
subject: public-inspection:<request_id>
runtime_processing_status: NOT_RUN
master_records_custody_status: NOT_CLAIMED
manifest_receipt_id: null
authority_claim: false
```

Those last three values are deliberate. Request preparation is not a runtime run and is not custody evidence.

## Processing boundary

```text
public PR or local JSON request
-> bounded request validation
-> ordinary option 0A descriptor
-> trusted admitted SDK / StegGate processing
-> canonical governance and consequence boundary
-> full canonical Master Records custody
-> caller-facing projection
-> resulting manifest_receipt_id may be posted back to the PR
```

The public request therefore becomes a distinct visible entry record without making GitHub the evaluator implementation or an authority surface. Untrusted PR code is never substituted for trusted SDK/StegGate processing.

## Receipt publication boundary

A `manifest_receipt_id` may be associated with the PR only after the actual governed run has produced it. The identifier is a locator for retained evidence, not permission or authority. Posting an identifier to GitHub does not create custody; canonical custody must already exist independently.

## Local binding validation

```bash
python -m unittest tests.test_public_inspection_governed_binding
```
