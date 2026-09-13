# StegVerse SDK 1.3.0

Target tag: `v1.3.0`
Package: `stegverse-sdk==1.3.0`
Release state: CANDIDATE_PREPARATION_IN_PROGRESS

## Purpose

SDK 1.3.0 is the first deployable package candidate that includes the processor-generic manifest contract, Manifest Builder, one-command external-framework execution path, caller-selected return projection, receipt/replay/reconstruction flow, and public governed-runtime dependency identities required for anonymous installation.

The separately frozen SDK 1.2.0 release identity remains immutable and is not retargeted by this release.

## Included capability set

- `stegverse.ingress-manifest.v1` processor-generic manifested-data ingress;
- source-native payload preservation;
- explicit `processing.capability` and route binding;
- Manifest Builder;
- `stegverse external-run`;
- credential-free `--prepare-only` portable submission preparation;
- preregistration evidence retained outside governance decision inputs;
- deterministic caller-selected return projection;
- `manifest_receipt_id` output with replay and reconstruction support;
- reproducible ELAN Test 1 external-framework fixture/runbook;
- downstream contamination regression closure for default Ecosystem Chat Conectrr fixture leakage.

## Governed-test deployable dependency set

```text
stegverse-stegcore==0.3.0
stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
stegverse-master-records==0.2.0
```

The StegCore and Master Records distributions must be publicly resolvable without GitHub credentials before this candidate is merge/release ready.

## Release gates

1. `stegverse-stegcore==0.3.0` publicly resolvable from PyPI.
2. `stegverse-master-records==0.2.0` publicly resolvable from PyPI.
3. Anonymous Governed Runtime Install workflow PASS with GitHub credentials absent.
4. ELAN Test 1 complete governed execution PASS.
5. Master Records custody, replay, and reconstruction PASS.
6. Release Dependency Alignment PASS.
7. SDK Package Artifact Validation PASS for package identity 1.3.0.
8. Generic manifest, Manifest Builder, evaluator console, and external-framework public-submission validations PASS on exact candidate head.
9. Release/tag publication evidence retained before any RELEASED claim.

## Current blockers

- StegVerse-Labs/StegCore#198 — publish exact `stegverse-stegcore==0.3.0`.
- master-records/orchestration#88 — publish exact `stegverse-master-records==0.2.0`.

SDK PR #163 remains draft until the anonymous governed-runtime installation gate passes from public distributions.
