# Public inspection request

Request JSON: `inspection/requests/<request-id>.json`

Please confirm that the PR contains declarative inspection data only, includes no credentials or executable evaluator/runtime code, declares `authority_claim: false`, and uses only a public requester label you intentionally chose to publish.

This PR is a visible submission record. It does not establish execution authority or Master Records organization record.

To validate only:

```bash
python scripts/validate_public_inspection_request.py inspection/requests/<request-id>.json
```

To actually run a governed TEST, use the trusted SDK checkout. The local lane writes its run to the SDK-internal local run record (`stegverse/local_run_record.py`; non-authoritative: authority_effect NONE, completes_transition false; not Master Records authority or custody) at the location you pass with `--records-db`; there is no default location. Master Records only records released organization batch receipts downstream and is not a gate:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run inspection/requests/<request-id>.json --records-db ./my-run-record.db
```

The transition closes on its organization-ledger transition receipt. The current runtime also reports the following identifiers (the Master Records status field is a legacy name for the local run-record status and is not a posting condition; sovereign completion comes only from a verified organization-ledger readback, `stegverse/organization_ledger_evidence.py`):

```text
master_records_organization_record_status: RECORDED
manifest_receipt_id: MR-...
```

Replay and reconstruction of that retained run are available through the same trusted SDK surface:

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256> --records-db ./my-run-record.db
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256> --records-db ./my-run-record.db
```

Both operations are read-only: they do not execute a consequence and do not mutate the retained run record.
