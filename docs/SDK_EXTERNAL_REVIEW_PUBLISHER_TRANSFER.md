# External evaluator review: optional Publisher, reviewer-facing default

Shared SDK/Publisher implementation, 2026-09-24. Source owners: existing SDK Manifest Builder / generic manifest route / SDK Publisher return binding and existing Publisher exact artifact-transfer/return path. Consumer: canonical MIR/SV Exp3, `MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003` / COSV `50000000100000`.

## Selection

**Ordinary SDK calls:** Publisher optional, `completion.publisher.required = false` unless explicitly requested. **Review-facing SDK calls:** specify `external_review=True` or CLI `--external-review`. The existing Manifest Builder then sets `completion.publisher.required = true` by default, without selecting another processor, route or authority. Explicit `publisher_required=False` / CLI `--no-publisher` overrides the default and remains valid; the explicit override is visible in the manifest-builder metadata. The existing `--publisher-required` option remains available. Existing serialized manifests and their digests stay unchanged; creating a successor manifest is an explicit new invocation.

Example (source-only construction; the selected existing processor still independently requires its own complete request):

```bash
stegverse manifest build --input source-native.json --processor-request processor-request.json \
  --source-framework StegVerse --source-output-id exp3-review-002 \
  --process ecosystem_diagnostic --external-review --return-depth full-trace \
  --publisher-package-profile stegverse.publisher.evidence-report-package/v1 \
  --output /tmp/reviewer.manifest.json
```

An explicit `--no-publisher` keeps a review-intent manifest non-publishing. A review-intent manifest with Publisher required is **not** a claim of actual Publisher execution.

## Exact original evidence via existing transfer, not a new transport

`stegverse.review_publisher_transfer.prepare_review_transfer(...)` prepares **exact canonical** `stegverse.publisher.artifact-transfer/v1` bytes for the *existing* sovereign Universal InTr destination `GCAT-BCAT-Engine/Publisher`. It consumes a pre-existing source-owner-authorized `stegverse.publisher.evidence-report-package/v1` export. It does not create that authorization, fabricate source custody or substitute for Master Records.

The source export must contain a complete list of original evidence entries under `evidence/`. The exact supplied `evaluator_assets` entries must cover the entire declared list; each original image/PDF retains its exact bytes, SHA-256, media type and attribution. Missing/mutated originals, invalid paths, duplicate identifiers, source digest mismatch, disabled source authorization or publication/release/exec authority expansion fail closed. The prepared packet is explicitly `PREPARED_NOT_TRANSPORTED`.

The existing Publisher `publisher/intr_artifact_transfer.py` (generic reviewer support merged in PR #73) consumes those canonical transfer bytes, invokes the existing Publisher document pipeline, retains exact original assets in the *same* artifact manifest/return, and emits `stegverse.publisher.artifact-return/v1` exact bytes and a source-only rendering receipt. The historical owner-specific MIR round-trip profile remains bound to its **own** task; this generic reviewer path does not misuse that profile simply because a different goal has the same COSV.

`stegverse.review_publisher_transfer.bind_exact_review_return(...)` verifies Publisher return exact bytes, the original transfer ID/export digest, matching original source paths, unchanged original SDK manifest and then delegates to the **existing** SDK `assemble_publisher_return()` and `verify_publisher_return_binding()`. This source binding is not evidence of an authentic transported Publisher run.

## Runtime / custody / outward communication

The order for an *authentic* run remains:

1. Admit the manifest through the existing Universal InTr ingress and execute its declared installed processor. Retain the real org-ledger and required Master Records evidence under existing owners.
2. Supply the **already-authorized** exact source export and originals through the existing SDK review transfer, with an actual transport-bound request/receipt rather than a synthetic local invocation.
3. Publisher produces and returns exact artifacts through the existing InTr connector. Retain actual Publisher destination operation and return receipts and verify original exact-byte readback.
4. SDK assembles the exact returned bytes to the unchanged original manifest and initiator. Complete the declared final StegVerse-side transition, InTr egress and far-side transition only if separately observed.

No local unit test, source-only GitHub Actions run, locally generated PDF, signature check, transport-ready packet or absent source receipt satisfies authentic organizational runtime custody, actual Publisher activation, or far-side receipt.

## MIR/SV Exp3 evaluator inputs

Retain Richard Whitney's original five-page PDF, all ten original screenshots, the separately supplied complete pre-PDF message, the StegVerse assessment, the original immutable SDK source-only manifest and diagnostic result, and their file digest/inventory. The historical screenshot crop limits and the absence of current authentic runtime/physical observations belong next to the claims. **Do not** overwrite the frozen prior source manifest when deriving a reviewer-facing successor. PDF and screenshot bytes supplied to the conversation remain user-provided originals, not repository fixtures and not a claim of native LinkedIn export. Their exact SHA-256 values are in the canonical Experiment 3 handoff, and the full original archive is available to the user.

The code supports this exact package shape; the authentic run-dependent transport/Pubisher/Master Records/far-side receipts for Exp3 remain **NOT_OBSERVED** until read back.

## Exact SDK source-manifest and Publisher receipt binding hardening

The already-authorized `stegverse.publisher.evidence-report-package/v1` source export's `source.verification_root` must equal the exact SHA-256 of the **original wire SDK manifest**, not just any syntactically valid source root. The SDK preparer checks this before generating a transfer. The matching SDK return consumer additionally verifies the returned Publisher artifact-manifest digest, rendering-receipt digest, manifest→receipt link and equal full artifact-path sets, along with original transfer/export and SDK manifest correlation. This prevents a generic return for one evaluation from being rebound to a different manifest or a modified report. Those checks establish byte binding **only**; authentic InTr Publisher transport/ownership and downstream custody still require separately retrieved runtime evidence.
