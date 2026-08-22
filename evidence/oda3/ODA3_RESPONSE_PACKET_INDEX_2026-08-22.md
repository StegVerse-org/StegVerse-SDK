# ODA3 Evaluation-Boundary Response Packet Index

Status: ACTIVE / PRE-RUNTIME

This index enumerates the exact evidence classes required for the first ODA3 evaluation-boundary experiment. It is intentionally incomplete until the immutable R3 release set and exact governed SDK-ingress run exist.

## Frozen coordinate

- release set: `EVALUATION-BOUNDARY-2026-08-19-R3`
- SDK: `stegverse-sdk 1.1.0`
- SDK commit: `922d6c5235229e854c36e1a194dc99ed15a31b51`
- SDK tree: `d9ddda3dbe942324c921051d89ec19eec3970b16`
- expected SDK tag: `v1.1.0`

## Evidence inventory

| Evidence class | Required | Current state |
|---|---:|---|
| SDK source/artifact proof | yes | COMPLETE |
| boundary source tests | yes | COMPLETE |
| independent verifier implementation | yes | COMPLETE |
| source artifact manifest + hashes | yes | COMPLETE |
| four immutable release tag bindings | yes | PENDING TV/TVC |
| R3 aggregate release receipt | yes | PENDING TV/TVC |
| published SDK 1.1.0 artifact verification | yes | PENDING TV/TVC release |
| exact normalized evaluator manifest | yes | PENDING exact run |
| exact governance request | yes | PENDING exact run |
| exact governed result | yes | PENDING exact run |
| SDK/Core-Lite/StegCore route receipts | yes | PENDING exact run |
| Master Records exact-run custody | yes | PENDING exact run |
| reconstruction evidence | yes | PENDING exact run |
| replay evidence | conditional/requested | PENDING |
| independent unmodified verification PASS | yes | PENDING exact run |
| normalized-manifest tamper FAIL | yes | PENDING exact run |
| governance-request tamper FAIL | yes | PENDING exact run |
| result-binding tamper FAIL | yes | PENDING exact run |
| runtime/source correspondence report | yes | PENDING release + exact run |
| access/license note | yes | PARTIAL / finalize with packet |
| independent reproduction procedure | yes | PENDING final packet |

## Expected final packet structure

```text
oda3-evaluation-boundary-r3/
  RELEASE_SET.json
  FILE_MANIFEST.sha256.json
  README_REPRODUCE.md
  LICENSE_ACCESS_NOTES.md
  schemas/
  capabilities/
  source-proof/
  run/
    normalized-manifest.json
    governance-request.json
    governed-result.json
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

Consume a verified `stegverse.tvc.aggregate-release-receipt.v1` for R3 from the canonical TV/TVC workstream, then proceed immediately with release verification and the exact SDK-ingress governed run. Do not substitute moving branch heads, source-only CI, or an evaluator-specific path.
