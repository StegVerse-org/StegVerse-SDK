# MIR/SV Experiment 3 — executable SDK manifest (source-scoped)

Canonical Goal: `MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003`; COSV `50000000100000`; owner [StegVerse-Labs/.github#2682](https://github.com/StegVerse-Labs/.github/issues/2682). This is the **present bilateral capability-boundary experiment**, not the future third-framework standing/commit-time experiment.

## Same four dimensions as Richard's document

The complete source-native manifest payload (`inspection/examples/mir-sv-exp3/assessment-input.json`) gives **Observe, Demonstrate, Retain, Reconstruct** individual capability, limit and check fields. It also answers the agreed questions: what was claimed, independently observed, what physical work occurred and what remains unknown. Unknowns, divergent accounts, external coverage declarations and activity-side sampling appear in the **body of the same input**, not a footnote.

MIR original PDF: SHA-256 `1e2f134ab60144bb4c5a4de135c6f76d460f22995a0e0b2df1ef071f7e8c8ffe` (the original in the user-supplied evidence archive; an independently uploaded/re-encoded copy need not have identical bytes). MIR-authored statements are **not** copied as StegVerse measurements. Richard's limits and claimed production figures remain his separately attributed artifact.

## Actual installed SDK route and exact command

Use existing `manifest_builder.build_manifest(..., process="ecosystem_diagnostic")` and the installed `stegverse.route.ecosystem-diagnostic.v1` route; do **not** invent a new governance processor or grant authority by manifest selection.

```bash
python -m scripts.build_mir_sv_exp3_manifest \
  --manifest /tmp/mir-sv-exp3.manifest.json \
  --result /tmp/mir-sv-exp3.diagnostic-result.json
python -m unittest tests.test_mir_sv_exp3_manifest -v
```

The manifest declares `return_depth=full-trace` and a required Publisher stage in the SOUTH completion contract; **the local diagnostic execution does not perform Publisher distribution, Interlock/InTr egress or a far-side receipt.** All four authentic current resident runtime predicates and all physical-world/coverage predicates remain `NOT_OBSERVED` until exact independently checkable evidence is ingested from the existing authorized interfaces. Source-declaration predicates may be `PASS` only for source documentation existence; this is not runtime proof.

## Evidence ingestion and independent review

For an authentic successor run, capture the existing resident organization ledger HEAD and all exact immutable predecessor-linked receipts spanning the sampled run; associate each with its *corresponding* canonical Master Records closure. Include the activity-side sampling frame (or explicitly state none), independently verified external physical measurements (or state none), all missing evidence, and each participant's dissent/unknowns. Put each verified observation into a **new** manifested diagnostic request with exact evidence refs, without rewriting the immutable source-only fixture. A newer manifest cannot claim a completed far-side delivery without its authentic transition receipt.

The SDK process is intentionally **read-only**. It reports supplied observations; its diagnostic processor does **not** fetch the resident ledger, independently remeasure physical work, or validate the cryptographic authenticity of arbitrary input refs. Those independent tests require actual original bytes and reader-side verification.

## Exact existing runtime boundary, discovered by initial CI

The installed public `run-manifest` binding for this route goes through `stegverse.manifest_state_transition_runtime.execute_manifest` and requires configured **authentic Universal InTr ingress**. An initial attempt to call public `run-manifest` from isolated source-only CI correctly failed `UNIVERSAL_INTR_INGRESS_NOT_CONFIGURED`. That is not permission to synthesize an InTr receipt or fall back to a fake runtime. This fixture therefore validates via the actual SDK Manifest Builder and invokes its existing **local read-only** `stegverse.ecosystem_diagnostic_runtime.execute_manifest` to produce a deterministic non-authorizing diagnostic artifact. Only the separately configured real `run-manifest` path can produce authentic governed ingress, and only when actual ingress/custody evidence exists. This source-only diagnostic output is not `run-manifest` completion or a real Publisher/evaluator external delivery.

## 2026-09-25 immutable-wire regression and typed source disposition

Source-level Experiment 3 regression now pins the original canonical-wire JSON SHA-256 `ad9b8b8aab2beeea04bff2aac34fd2e7bfa5915133bcaef9209c16de7d9bea68` as a hard invariant. No frozen original manifest bytes are edited. The SDK client now validates and forwards the existing central generic listener's provenance-scoped correctable `DENY` for `ECOSYSTEM_DIAGNOSTIC_NONWORKER_DISPATCH_UNWIRED` without disguising it as an authenticated InTr verdict, changing Publisher requirement or initiating a retry. Tampered digests, fabricated ALLOW, falsified authentic/custody flags and implicit retry are rejected by source tests. Actual admitted EVENT_EPHEMERAL execution and authenticated organization/Master Records receipt readback remain independent requirements.

### Experiment 3 typed nonterminal diagnostic and terminal fail-closed return

The installed generic SDK client distinguishes three separately bound results from its existing InTr profile: repairable **source/profile DENY** (never an authentic InTr verdict), **terminal source-local FAIL_CLOSED** for an already-attempted ephemeral diagnostic with no automatic retry, and **nonterminal processing ALLOW** only after the central existing-owner consumer supplies exact authenticated admission, EVENT_EPHEMERAL lease binding and organization-first Master Records closure. The ALLOW validator checks frozen original SHA-256, source task/COSV, exact inline diagnostic result JSON bytes, runtime and all reported receipt hashes, and explicitly requires Publisher and far-side still unexecuted. This is not final communication ALLOW, Publisher transport, independent ledger readback or external evaluator delivery. GitHub tests of this contract are source-only with synthetic receipt strings; no native runtime credentials or fabricated sovereign evidence are added.
