# AdmittedCode Portable Consumer Mirror Handoff

## Source of truth

This file is the task source of truth for the AdmittedCode portable receipt-consumer slice in `StegVerse-org/StegVerse-SDK`.

## Goal

Consume and independently verify portable AdmittedCode receipts, including source-verification annotations, without turning SDK validation into execution, authority, admissibility, publication, deployment, or Master-Records custody.

## Status

**COMPLETE AND MERGED.** This slice no longer owns implementation work.

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

The fixture suite includes both portable outcomes:

- StegVerse source `ALLOW` -> AdmittedCode `ALLOW` -> SDK `ACCEPTED`.
- StegVerse source `QUARANTINE` -> AdmittedCode `DENY` -> SDK `ACCEPTED` as a valid refusal receipt.

`QUARANTINE`, `DENY`, and SDK `ACCEPTED` are deliberately different semantics. SDK acceptance means the receipt is structurally/integrity valid for non-authorizing consumption; it does not convert a denied action into an allowed action.

## Portable contract

`LLM-adapter canonical fixture -> source-bound review_packet -> AdmittedCode source verification + review -> provider_harness_receipt.v1 -> SDK independent hash verification`

## Validation

Canonical validation commands:

```bash
pytest tests/test_admittedcode_receipt.py -v
pytest tests/test_admittedcode_receipt_fixture.py -v
pytest tests/ -v
```

PR #12 merged as `6227454a78b9c210a8ec0d3eb5be3f15b977c6e7`. Before merge, the observed SDK validation workflows all completed successfully:

- StegVerse SDK Validation
- validate
- Architecture Guard
- Diagnose Python 3.9 Public Imports
- Validate Provider Usage Ingestion

## Cross-repository completion evidence

- LLM-adapter canonical source binding: PR #122, merge `12eefc095479b325ccb5551c7279b7ecec1d0283`.
- AdmittedCode source verification: provider-harness PR #2, merge `c4eb15c63f4d0869080f59a57207449a8bf629e7`.
- compact external reviewer packet: provider-harness PR #3, merge `b5b942d64cb7d7278b7a4137704fea75f325a77f`.

## Canonical continuation

MERGED INTO: `AdmittedCode/.github/ADMITTEDCODE_MIRROR_HANDOFF.md`

The next ecosystem integration is `StegVerse-Labs/Site`, subject to Site machine admission. The blocked task and release-condition observer live at:

- `AdmittedCode/.github/data/tasks/ADMITTEDCODE-SITE-REVIEW-INTEGRATION.json`
- `AdmittedCode/.github/.github/workflows/site-admission-watch.yml`

No second authority-bearing implementation is permitted. No additional work from this SDK slice is required until the portable receipt contract changes or a canonical downstream consumer requires a versioned compatibility update.
