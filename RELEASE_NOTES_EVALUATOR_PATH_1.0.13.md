# Evaluator Path Release Notes — stegverse-sdk 1.0.13

Release-set role: `sdk_entry`

Canonical evaluator candidate:

```text
repository: StegVerse-org/StegVerse-SDK
package: stegverse-sdk
version: 1.0.13
tag_to_publish: v1.0.13-oda3-r1
commit: 16c99037a42e4d667b9df4a7a5efbaae9dd7184c
tree: d238131690fdc3833cc861b69b0760e570e2b55a
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

The pre-existing `v1.0.13` tag is historical and resolves to `f219afa17dcb020dc1e13b72f859a86627c5644b`; it must not be moved or reused. The ODA3 aggregate release therefore uses the distinct immutable tag `v1.0.13-oda3-r1` while retaining package version `1.0.13`.

This is the frozen ODA3 evaluator-boundary source candidate. It includes the evaluator-facing SDK manifest/submission boundary, independent binding verifier, deliberate boundary-violation tests, exact-commit artifact manifest support, and the pinned production component set used by the first ODA3 boundary experiment.

The evaluator-facing route begins at the SDK. Direct evaluator submission to Core-Lite, StegCore, or StegGate is not part of the primary experiment and is not an authorized alternate execution surface.

Dependency release targets for the same aggregate release set are:

```text
Data-Continuation/core-lite@v0.9.0 -> 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
StegVerse-Labs/StegCore@v0.2.0 -> 083557adec1bdbace09ebd10fb0765eb8e9a9d08
master-records/orchestration@v0.1.0 -> 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

Aggregate release-set identity: `ODA3-EVALUATOR-PATH-2026-08-18-R1`.

## Release invariant

`v1.0.13-oda3-r1` must resolve exactly to `16c99037a42e4d667b9df4a7a5efbaae9dd7184c`. Later source receipts and documentation commits do not silently move this candidate. A changed runtime/source proposition requires a new candidate, new source receipt, and new release-set identity.

This note prepares release metadata only; actual tag/release publication remains subject to TV/TVC-governed release authority.