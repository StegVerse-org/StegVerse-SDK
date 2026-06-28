# Decision Vocabulary

The canonical StegVerse decision vocabulary is:

```text
ALLOW
DENY
CONDITIONAL
FAIL_CLOSED
```

## Semantics

- `ALLOW` means execution authority exists at commit time.
- `DENY` means execution authority was evaluated and is not granted.
- `CONDITIONAL` means authority is not established yet. Named conditions must be satisfied before a new standing determination is made.
- `FAIL_CLOSED` means standing cannot be safely reconstructed or required authority, evidence, policy, delegation, context, validity, or recoverability state is missing, inconsistent, stale, or indeterminate. Execution must not proceed.

## Compatibility mapping

- `DEFER` is deprecated. Use `CONDITIONAL` when the result is waiting on named conditions. Use `FAIL_CLOSED` when safe standing cannot be determined.
- `FAIL-CLOSED` is deprecated as a spelling. Use `FAIL_CLOSED`.

This SDK is the normative intake source for packet-family decision vocabulary. Downstream repos may expose compatibility aliases only when they map back to this canonical set.
