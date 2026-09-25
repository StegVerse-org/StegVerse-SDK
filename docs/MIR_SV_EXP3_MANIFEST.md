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

## Private source-evidence Publisher handoff

The generic reviewer default is now exercised by this manifest's `for_external_review=True` builder option without changing the fixed source manifest's declared Publisher requirement. The completed SDK diagnostic and eleven original source files (Richard's original PDF and ten user-supplied screenshots) can be checked and assembled by `stegverse.publisher_review_transfer` into the **existing** Publisher artifact-transfer format, with each original file's exact bytes and SHA-256. The SDK manifest and diagnostic result are separately classified `SDK_SOURCE_VALIDATED_ARTIFACT`. See `docs/SDK_EXTERNAL_REVIEW_PUBLISHER_DEFAULT.md`. This is packet preparation, not authentic resident InTr ingress, Master Records, Publisher-host execution or external delivery.
