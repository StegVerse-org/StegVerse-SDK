# AdmittedCode in the StegVerse SDK

AdmittedCode is a first-class, non-authorizing review and receipt-verification surface available to any StegVerse SDK user.

## What this surface does

The SDK can independently verify portable AdmittedCode/provider-harness receipts without turning verification into execution, authority, admissibility, publication, deployment, or Master-Records custody.

```python
import json
from pathlib import Path

from stegverse.admittedcode_receipt import verify_admittedcode_receipt

receipt = json.loads(Path("examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json").read_text())
result = verify_admittedcode_receipt(receipt)
print(result)
```

The same verifier accepts valid refusal receipts while preserving their refusal semantics. SDK `ACCEPTED` means the receipt is structurally and integrity-valid for non-authorizing consumption; it does not convert a denied action into an allowed action.

## Included examples

- `examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json`
- `examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json`

## Validation

```bash
pytest tests/test_admittedcode_receipt.py -v
pytest tests/test_admittedcode_receipt_fixture.py -v
```

## Portable contract

```text
LLM-adapter canonical fixture
-> source-bound review packet
-> AdmittedCode source verification + review
-> provider_harness_receipt.v1
-> SDK independent receipt-hash verification
```

## Boundaries

- SDK validation is not execution.
- SDK intake is not authority.
- Receipt handoff is not Master-Records installation.
- `authority_effect` remains `NONE`.
- `QUARANTINE`, `DENY`, `FAIL_CLOSED`, and SDK `ACCEPTED` remain distinct semantics.

For the implementation source, see `stegverse/admittedcode_receipt.py`. For continuity and completion evidence, see `docs/ADMITTEDCODE_PORTABLE_CONSUMER_MIRROR_HANDOFF.md`.
