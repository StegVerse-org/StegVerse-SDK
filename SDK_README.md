# STEGVERSE SDK

This legacy filename is retained for compatibility with older links.

Canonical documentation:

- `README.md` — current public overview and governed TEST quick start
- `docs/SDK_CONSOLE.md` — console/navigation reference
- `docs/PUBLIC_INSPECTION_ENTRY.md` — public inspection request and governed TEST instructions
- `SDK_MIRROR_HANDOFF.md` — repository source of truth

Do not use historical examples from older revisions as the current SDK contract.

For an actual side-effect-free governed TEST using canonical StegCore, Python 3.11+:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime inspection/examples/governed-test-request.json
```

The returned `manifest_receipt_id` identifies the locally retained governed TEST run. Local TEST retention is not production Master Records custody.
