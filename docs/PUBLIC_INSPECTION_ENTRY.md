# Public Inspection Entry

The public SDK may be used as a visible inspection-request surface through ordinary pull requests.

## What a PR means

A pull request can retain a public record of the request payload, revisions, discussion, and any receipt identifiers later posted back by a trusted processor.

A PR does **not** mean the request has been admitted, governed, executed, retained in Master Records, released, or activated.

## Submission shape

Submit one JSON document matching `inspection/request.schema.json`. The document is declarative only. It must not contain executable code, workflow changes, credentials, private keys, bearer tokens, provider secrets, TV/TVC identity material, or claims of execution authority.

A request can specify:

- a neutral `request_id`;
- an optional public `requester_label` chosen by the requester;
- a `case_profile`;
- bounded input data;
- requested return projection;
- optional explanatory labels;
- an explicit `authority_claim: false`.

The requester's personal name is not required.

## Processing boundary

The public PR is an observation/submission carrier. Processing must use trusted SDK/StegGate code rather than code supplied by the PR. Any canonical custody operation remains separately governed by the admitted Master Records transport.

## Why this is useful

The PR becomes a distinct, inspectable public entry record without turning GitHub into StegVerse credential or execution authority. A reviewer can see exactly what was requested, what changed during review, and what receipt identifiers were later associated with the request.

## Local validation

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m unittest tests.test_public_inspection_request
```
