# AdmittedCode Portable Consumer Mirror Handoff

## Source of truth

This file is the task source of truth for the AdmittedCode portable receipt-consumer slice in `StegVerse-org/StegVerse-SDK`.

## Goal

Consume and independently verify portable AdmittedCode receipts, including source-verification annotations, without turning SDK validation into execution, authority, admissibility, publication, deployment, or Master-Records custody.

## Installed paths

- `stegverse/admittedcode_receipt.py`
- `examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json`
- `examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json`
- `tests/test_admittedcode_receipt.py`
- `tests/test_admittedcode_receipt_fixture.py`
- this handoff

## Invariants

- `sdk_validation_is_execution == false`
- `sdk_intake_is_authority == false`
- `receipt_handoff_is_master_record_installation == false`
- `authority_effect == NONE`

The consumer independently recomputes the canonical base receipt hash and rejects unsupported schemas, authority escalation, tampering, and any DENY/FAIL_CLOSED receipt that claims provider-key access.

The fixture suite now includes both portable outcomes:

- StegVerse source `ALLOW` -> AdmittedCode `ALLOW` -> SDK `ACCEPTED`.
- StegVerse source `QUARANTINE` -> AdmittedCode `DENY` -> SDK `ACCEPTED` as a valid refusal receipt.

`QUARANTINE`, `DENY`, and SDK `ACCEPTED` are deliberately different semantics. SDK acceptance means the receipt is structurally/integrity valid for non-authorizing consumption; it does not convert a denied action into an allowed action.

## Portable contract

`LLM-adapter canonical fixture -> source-bound review_packet -> AdmittedCode source verification + review -> provider_harness_receipt.v1 -> SDK independent hash verification`

## Validation

```bash
pytest tests/test_admittedcode_receipt.py -v
pytest tests/test_admittedcode_receipt_fixture.py -v
pytest tests/ -v
```

## Current evidence

The ALLOW and DENY receipt fixtures were generated from the provider-harness M0-M3 core using a local repository snapshot. Each fixture retains `key_requested=false`, `authority_effect=NONE`, source binding, and source verification metadata. The SDK verifies the canonical base receipt hash independently of those annotations.

## Remaining work

Observe hosted SDK CI for the fixture expansion and merge when green. After the LLM-adapter canonical-binding PR and AdmittedCode source-verification PR are merged, refresh any source commit references needed for a reviewer-facing package. Do not create a second authority-bearing implementation.
