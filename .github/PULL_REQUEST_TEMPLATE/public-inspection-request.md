# Public inspection request

Request JSON: `inspection/requests/<request-id>.json`

Please confirm that the PR contains declarative inspection data only, includes no credentials or executable evaluator/runtime code, declares `authority_claim: false`, and uses only a public requester label you intentionally chose to publish.

This PR is a visible submission record. It does not establish execution authority or production Master Records custody.

To validate only:

```bash
python scripts/validate_public_inspection_request.py inspection/requests/<request-id>.json
```

To actually run a governed local TEST and receive `governance_state`, `manifest_receipt_id`, exact-run evidence, and reconstruction, use Python 3.11+ with the trusted SDK checkout:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime inspection/requests/<request-id>.json
```

The governed TEST runtime uses canonical StegCore and a side-effect-free test executor. A result posted back to this PR must be labeled as local governed TEST evidence unless production Master Records custody was separately established and verified.
