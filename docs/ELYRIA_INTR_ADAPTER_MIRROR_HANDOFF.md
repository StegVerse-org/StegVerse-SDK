# Elyria Interlock/InTr Adapter Mirror Handoff

Updated: 2026-09-12
Repository: `StegVerse-org/StegVerse-SDK`
Goal Task ID: `SDK-ELYRIA-INTR-ADAPTER-001`
COSV: `71000000100112`
Canonical coordination handoff: `StegVerse-Labs/.github:docs/SDK_ELYRIA_INTR_ADAPTER_MIRROR_HANDOFF.md`
Status: `ACTIVE / FRAMEWORK CODEC SOURCE IMPLEMENTED / VALIDATION PENDING`

## Reuse boundary

This repository does not create a new evaluator lane or a new Interlock/InTr protocol for Elyria. It reuses:

- `stegverse.ingress-manifest.v1` and the generalized evaluator surface;
- existing processor/route resolution;
- existing Interlock/InTr governed ingress/egress;
- existing receipt/MIR/Master Records return semantics;
- the strict dependency-injected adapter pattern already used by `stegverse/llm_adapter_bridge.py`;
- direct foreign-packet preservation semantics from the system-boundary fixture path.

The only novel source is `stegverse/elyria_framework_adapter.py`, which translates/preserves the public Elyria Admission Runtime movement, assessment receipt, replay, and no-bind evidence shapes.

## Implemented framework-side contract

```text
normalized StegVerse external-framework operation
-> exact source-native Elyria movement body
-> dependency-injected Elyria assess transport
-> exact foreign receipt preservation
-> non-authorizing verdict normalization
-> optional replay normalization
-> optional no-bind evidence normalization
-> existing governed return path
```

The adapter requires Elyria's documented movement fields rather than synthesizing authority, standing, custody, or evidence posture. It fails closed on missing required fields, transition/run identity absence, movement identity mismatch, response input mutation, unsupported verdicts, malformed replay checks, and malformed no-bind evidence.

## Fixed authority semantics

```text
Elyria ADMIT != InTr admission
Elyria HOLD != InTr hold authority
Elyria REFUSE != InTr refusal authority
Elyria NO_PROVABLE_ADMISSION != InTr admission decision
Elyria signed receipt != Master Records custody
Elyria replay PASS != StegVerse replay proof
Elyria route_closure_state=closed != StegVerse-observed route closure
adapter authority = NONE_TRANSLATION_ONLY
```

The adapter intentionally records `foreign_signature_verified_by_stegverse=false` because Elyria's public receipt uses its own signing secret. The foreign signature is preserved byte-for-byte but is not silently reclassified as StegVerse verification.

## Added source/tests

```text
stegverse/elyria_framework_adapter.py
tests/test_elyria_framework_adapter.py
```

Tests cover exact HTTP-body preservation, required source-native evidence fields, all four documented public verdicts, authority non-promotion, movement identity mismatch, original-input mutation, unknown verdicts, replay identity/check fields, no-bind closure assertion handling, dependency-injected transport, and pre-transport identity failure.

## Current proof boundary

```text
framework-side codec source: IMPLEMENTED
framework-specific deterministic tests: ADDED / CI NOT YET OBSERVED
existing StegVerse protocol reuse: SOURCE-DESIGN BOUND
new InTr protocol created: FALSE
authentic public Elyria network round trip: NOT OBSERVED
production private Veritas substrate interoperability: NOT CLAIMED
runtime activation: NOT CLAIMED
```

## Next sequence

1. Run the repository test/validation lanes against the exact branch head.
2. Repair only adapter-local compatibility failures; do not create a new internal route to make the fixture pass.
3. Merge only after required SDK validation is green.
4. Then add an authentic public Elyria transport observation separately if a reachable authorized endpoint is actually exercised; do not infer network/runtime proof from deterministic injected-transport tests.
5. Update canonical Task Registry/handoff with exact PR, head, validation, and merge evidence.

## Manual work

None.
