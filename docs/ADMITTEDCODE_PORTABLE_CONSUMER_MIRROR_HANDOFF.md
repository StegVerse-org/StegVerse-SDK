# AdmittedCode Portable Consumer Mirror Handoff

## Source of truth

This file is the task source of truth for the AdmittedCode portable receipt-consumer slice in `StegVerse-org/StegVerse-SDK`.

## Goal

Consume and independently verify portable AdmittedCode receipts without turning SDK validation into execution, authority, admissibility, publication, deployment, or Master-Records custody.

## Installed paths

- `stegverse/admittedcode_receipt.py`
- `tests/test_admittedcode_receipt.py`
- this handoff

## Invariants

- `sdk_validation_is_execution == false`
- `sdk_intake_is_authority == false`
- `receipt_handoff_is_master_record_installation == false`
- `authority_effect == NONE`

The consumer rejects unsupported schemas, authority escalation, tampered receipt hashes, and any DENY/FAIL_CLOSED receipt that claims the provider key was requested.

## Portable contract

`LLM-adapter review_packet -> AdmittedCode -> provider_harness_receipt.v1 -> SDK verification`

## Validation

```bash
pytest tests/test_admittedcode_receipt.py -v
```

## Remaining work

Observe hosted SDK CI, then add the portable receipt consumer to the existing consolidated validation path if required by the repository's canonical workflow. Do not create a second authority-bearing implementation.
