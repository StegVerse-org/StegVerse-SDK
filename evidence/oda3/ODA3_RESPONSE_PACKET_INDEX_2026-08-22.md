# ODA3 Evaluation-Boundary Response Packet Index

Status: ACTIVE / PRE-RUNTIME

This index enumerates the exact evidence classes required for the first ODA3 evaluation-boundary experiment. It is intentionally incomplete until the immutable R3 release set and exact governed SDK-ingress run exist.

## Frozen coordinate

- release set: `EVALUATION-BOUNDARY-2026-08-19-R3`
- SDK: `stegverse-sdk 1.1.0`
- SDK commit: `922d6c5235229e854c36e1a194dc99ed15a31b51`
- SDK tree: `d9ddda3dbe942324c921051d89ec19eec3970b16`
- expected SDK tag: `v1.1.0`
- frozen evaluator input: `evidence/oda3/R3_EXACT_EVALUATION_MANIFEST.json`
- frozen evaluator input commit: `5f8644f7f2daa05793d09c4c505b02dca5b30672`

## Evidence inventory

| Evidence class | Required | Current state |
|---|---:|---|
| SDK source/artifact proof | yes | COMPLETE |
| boundary source tests | yes | COMPLETE |
| independent verifier implementation | yes | COMPLETE |
| source artifact manifest + hashes | yes | COMPLETE |
| frozen evaluator input manifest | yes | COMPLETE_SOURCE / `evidence/oda3/R3_EXACT_EVALUATION_MANIFEST.json` |
| frozen evaluator input validation binding | yes | COMPLETE_SOURCE / workflow-bound at `03131f0239b2793ece9d069468b59ff577e33b2d` |
| exact-run evidence harness | yes | COMPLETE_SOURCE / `scripts/run_oda3_evaluation_boundary_r3.py` |
| exact governance-request model normalization | yes | COMPLETE_SOURCE / `be54722610a3edf8d90503fde460bef850ab43f5` |
| pre-custody independent tuple verification | yes | COMPLETE_SOURCE / harness requires PASS |
| fail-closed reviewer packet builder | yes | COMPLETE_SOURCE / `scripts/build_oda3_response_packet.py` |
| packet completion task | yes | ACTIVE / `tasks/SDK-ODA3-RESPONSE-PACKET-001.json` |
| packet builder regression coverage | yes | COMPLETE_SOURCE / `tests/test_oda3_response_packet.py` |
| packet/harness hosted source validation | yes | PENDING OBSERVATION after latest workflow-bound source |
| four immutable release tag bindings | yes | PENDING TV/TVC |
| R3 aggregate release receipt | yes | PENDING TV/TVC |
| R3 receipt generic suite PASS | yes | PENDING admitted TVC execution |
| R3 receipt guarded suite PASS | yes | PENDING admitted TVC execution |
| R3 receipt dispatcher-state suite PASS | yes | PENDING admitted TVC execution |
| published SDK 1.1.0 artifact verification | yes | PENDING TV/TVC release |
| exact normalized evaluator manifest | yes | PENDING exact run from frozen evaluator input |
| exact model-normalized governance request | yes | PENDING exact run; harness retains runtime-bound representation |
| exact governed result | yes | PENDING exact run |
| pre-custody independent unmodified verification PASS | yes | PENDING exact run |
| SDK/Core-Lite/StegCore route receipts | yes | PENDING exact run |
| Master Records exact-run custody | yes | PENDING exact run |
| reconstruction evidence | yes | PENDING exact run |
| replay evidence | conditional/requested | PENDING |
| independent unmodified verification PASS | yes | PENDING exact run; builder re-verifies it |
| normalized-manifest tamper FAIL | yes | PENDING exact run; builder derives/verifies from real tuple |
| governance-request tamper FAIL | yes | PENDING exact run; builder derives/verifies from real tuple |
| result-binding tamper FAIL | yes | PENDING exact run; builder derives/verifies from real tuple |
| runtime/source correspondence report | yes | PENDING release + exact run |
| access/license note | yes | SOURCE NOTE COMPLETE / finalize actual packet inclusion |
| independent reproduction procedure | yes | SOURCE PROCEDURE COMPLETE; finalize concrete release/run coordinates |

## Automated exact-run and completion gate

After genuine release evidence exists, execute the frozen evaluator input through:

```text
python scripts/run_oda3_evaluation_boundary_r3.py \
  --release-receipt <verified-r3-aggregate-receipt.json> \
  --manifest evidence/oda3/R3_EXACT_EVALUATION_MANIFEST.json \
  --custody-db <exact-r3-custody.db> \
  --run-dir <exact-sdk-ingress-run-evidence-dir> \
  --packet-dir <oda3-evaluation-boundary-r3>
```

The harness refuses to execute without the verified immutable R3 receipt. It retains the normalized manifest, converts the submitted StegGate request through the same `AdmissibilityRequest.model_dump(mode="json", exclude_none=False)` representation used by the frozen runtime, requires both retained input hashes to match the returned runtime bindings, and independently verifies the complete unmodified tuple before exporting custody evidence.

The packet builder then fails closed unless the R3 aggregate receipt has the exact four release coordinates, TV/TVC credential authority, no non-TV/TVC credential use, and retained PASS for the generic aggregate-release suite, guarded one-shot continuation suite, and dispatcher-state suite. It requires real route, Master Records and reconstruction evidence, re-verifies the unmodified tuple, generates copied deliberate tamper cases, requires all three binding failures, and emits a SHA-256/byte-size file manifest.

Neither harness nor builder synthesizes runtime, custody, release, replay or reconstruction evidence.

## Expected final packet structure

```text
oda3-evaluation-boundary-r3/
  RELEASE_SET.json
  FILE_MANIFEST.sha256.json
  README_REPRODUCE.md
  LICENSE_ACCESS_NOTES.md
  run/
    normalized-manifest.json
    governance-request.json
    governed-result.json
    independent-binding-verification.json
    route-receipts/
    master-records/
    reconstruction/
    replay/
  verify/
    independent-pass.json
    manifest-tamper-fail.json
    governance-request-tamper-fail.json
    result-tamper-fail.json
```

The names above define the reviewer-facing packet shape; they do not assert that runtime evidence already exists.

## Next trigger

Consume a verified `stegverse.tvc.aggregate-release-receipt.v1` for R3 from the canonical TV/TVC workstream, then proceed immediately with the exact frozen evaluator input through the SDK-ingress harness. No evaluator-input design, evidence-retention design, or manual packet-assembly design phase remains after those genuine release artifacts arrive. Do not substitute moving branch heads, source-only CI, fixtures, or an evaluator-specific path.
