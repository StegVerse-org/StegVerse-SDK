# Review-facing SDK manifests: optional Publisher and exact original evidence

Current generic owner: existing SDK Manifest Builder, `manifest_execution`, `publisher_return_binding`, and existing GCAT-BCAT-Engine/Publisher exact artifact-transfer/return. Consumer MIR/SV Experiment 3 canonical Goal `MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003`, COSV `50000000100000`.

## Default policy

Non-review manifests: Publisher is optional (`completion.publisher.required=false` by default). Caller explicitly requests return to a third-party evaluator by `for_external_review=True` or CLI `--for-external-review`; this *defaults* `completion.publisher.required=true`. A caller may intentionally opt out with `publisher_required=False` / `--publisher-optional`. Changing the builder default does not execute Publisher, grant authority, or alter already-frozen manifest bytes. `--publisher-required` is still accepted.

## Existing SDK/Publisher transfer preparation

`stegverse.publisher_review_transfer.build_source_only_review_transfer` consumes a **validated** SDK manifest, the exact local source-scoped diagnostic result, explicit original file bytes and independent expected SHA-256 list, plus a bounded external-review instruction. It rejects missing originals, mutated bytes, corrupted SDK result digests, an undeclared Publisher requirement, absent approval, or missing capability/limit/check text. It then emits the **existing** canonical `stegverse.publisher.artifact-transfer/v1` packet carrying `stegverse.publisher.evidence-report-package/v1` and `evaluator_assets`.

The generic report uses Publisher's already-merged exact-byte document pipeline and original-file passthrough (Publisher PRs #73–#75). The existing MIR-CONNECTION-ROUNDTRIP specialized `roundtrip_binding` remains unchanged and MUST NOT be used for this distinct goal. The local preparation has no assumed SDK-run receipt and no forged governed completion capsule. The PDF and screenshots remain independently attributed to the external contributor and the uploading user, while SDK-generated manifest and diagnostic bytes use `SDK_SOURCE_VALIDATED_ARTIFACT`, not `AUTHENTIC_RETAINED_EVIDENCE`.

On an environment possessing all original files and the existing SDK artifact:

```bash
python -m stegverse.publisher_review_transfer \\
  --manifest mir-sv-exp3.manifest.json \\
  --result mir-sv-exp3.diagnostic-result.json \\
  --original-dir ./mir-sv-exp3-originals \\
  --sha256sums ./SHA256SUMS.txt \\
  --approval-ref explicit-private-evaluator-review-instruction \\
  --output ./mir-sv-exp3.publisher-transfer.json
```

Do **not** commit the transfer packet to a public repository when it contains actual user-supplied screenshots or PDFs; the packet contains their exact base64 bytes. The existing authorized `publisher-artifact-transfer` Universal InTr path is currently KV-originated; SDK-originated review requests require an authentic SDK-qualified sender profile/source acceptance and matching SDK-bound return. Source-level production of a valid transfer is not transport, Publisher receipt, Master Records custody, publication or far-side delivery. No new runtime, scheduler, device or custody plane is authorized by this source generator.

## Current Experiment 3 source artifact

Richard's original PDF plus 10 screenshots are user-supplied private evidence; their SHA-256 inventory is retained in the canonical goal handoff. The original SDK manifest and read-only result are downloadable from workflow #36085026183, SHA-256 `e1b05a082ce19d3d254e3cde1dced03019174a94287724959672c9e65510c8f3` and `5acde471f793546a7a457ab11cbe142aeefa6637e747550390f1db213cfaeaea`, respectively. A source-only prepared packet must not be portrayed as the result of public `run-manifest` or an authentic organization/Master Records chain. Publisher's distinct return and authentic SDK receipt must be obtained before upgrading the stage.
