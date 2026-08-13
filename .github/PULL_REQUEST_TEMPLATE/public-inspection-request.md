# Public inspection request

Request JSON: `inspection/requests/<request-id>.json`

Please confirm that the PR contains declarative inspection data only, includes no credentials or executable evaluator/runtime code, declares `authority_claim: false`, and uses only a public requester label you intentionally chose to publish.

This PR is a visible submission record. It does not establish execution authority or Master Records custody.

To validate only:

```bash
python scripts/validate_public_inspection_request.py inspection/requests/<request-id>.json
```

To actually run a governed TEST, configure an admitted canonical Master Records endpoint and use the trusted SDK checkout:

```bash
export MASTER_RECORDS_URL="<admitted-master-records-base-url>"
export MASTER_RECORDS_AUTH_TOKEN="<authorized-token>"
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run inspection/requests/<request-id>.json
```

A governed result may be posted back to this PR only after the SDK reports:

```text
master_records_custody_status: RECORDED
manifest_receipt_id: MR-...
```

Replay and reconstruction of that retained run are available through the same trusted SDK surface:

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

Both operations are read-only: they do not execute a consequence and do not mutate the retained Master Record.
