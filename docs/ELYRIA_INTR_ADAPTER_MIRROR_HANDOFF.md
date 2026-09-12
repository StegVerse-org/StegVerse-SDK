# Elyria Interlock/InTr Adapter Mirror Handoff

Updated: 2026-09-12
Repository: `StegVerse-org/StegVerse-SDK`
Goal Task ID: `SDK-ELYRIA-INTR-ADAPTER-001`
COSV: `71000000100112`
Canonical coordination handoff: `StegVerse-Labs/.github:docs/SDK_ELYRIA_INTR_ADAPTER_MIRROR_HANDOFF.md`
Status: `ACTIVE / FRAMEWORK CODEC SOURCE IMPLEMENTED / REUSED SDK VALIDATION GREEN ON PREVIOUS EXACT HEAD / FINAL EXACT-HEAD RERUN PENDING`

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
.github/workflows/package-artifact-validation.yml  # existing workflow reused; no new workflow
```

Tests cover exact HTTP-body preservation, required source-native evidence fields, all four documented public verdicts, authority non-promotion, movement identity mismatch, original-input mutation, unknown verdicts, replay identity/check fields, no-bind closure assertion handling, dependency-injected transport, and pre-transport identity failure.

## Validation evidence

PR `StegVerse-org/StegVerse-SDK#222` reached exact head `ec800a9b1d00508f1cd0dad051208e16b9553403` with existing `SDK Package Artifact Validation (Non-Authorizing)` run `34709082764` SUCCESS. Its `Validate Elyria framework-side translation binding` step passed, together with existing trusted-publisher, portable-governance, self-characterization, build, wheel metadata, isolated-install, and console-smoke steps.

The repository's existing package validation workflow was then extended only to include this adapter test and this handoff in its existing path/validation surface; no new workflow, transport, authority plane, or runtime was created. Because those documentation/validation bindings advance the branch head after run `34709082764`, merge still requires a fresh exact-head SUCCESS.

## README review

Root `README.md` was reviewed. Its existing `Open testing and governed interoperability` and `Generic manifested-data processing contract` sections already state the required generic external-framework model, existing governed interlocks, processor/route separation, and non-authority semantics. No Elyria-specific README path or bespoke protocol description is added because doing so would incorrectly imply a new internal communication path; the framework-specific implementation is documented here while README remains generically accurate.

## Current proof boundary

```text
framework-side codec source: IMPLEMENTED
framework-specific deterministic tests: PASS on SDK run 34709082764 at ec800a9b1d00508f1cd0dad051208e16b9553403
existing StegVerse protocol reuse: SOURCE + CI BOUND
new InTr protocol created: FALSE
final exact-head validation after handoff/workflow binding: PENDING
authentic public Elyria network round trip: NOT OBSERVED
production private Veritas substrate interoperability: NOT CLAIMED
runtime activation: NOT CLAIMED
```

## Next sequence

1. Require the reused SDK validation workflow to pass on the final PR head.
2. Merge PR #222 only after that exact-head success.
3. Update the canonical Task Registry/handoff with the SDK merge and validation evidence.
4. Add an authentic public Elyria transport observation separately only if a real reachable public endpoint is actually exercised; do not infer network/runtime proof from deterministic injected-transport tests.

## Manual work

None.
