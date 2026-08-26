# Evaluation-Boundary License and Access Notes

Status: reviewer-facing source note; finalize against the verified immutable R3 release objects before packet completion.

## Release-set scope

```text
EVALUATION-BOUNDARY-2026-08-19-R3
StegVerse-org/StegVerse-SDK@v1.1.0
Data-Continuation/core-lite@v0.9.0
StegVerse-Labs/StegCore@v0.2.0
master-records/orchestration@v0.1.0
```

Repository visibility and software-license rights are separate questions. Public visibility does not itself grant a software license, and private visibility does not alter any rights separately granted by an applicable license or agreement.

## StegVerse SDK

`StegVerse-org/StegVerse-SDK` is a public repository. Its root `LICENSE` is the MIT License. The final packet should include or point to the exact license text associated with the tagged SDK release rather than relying only on this summary.

The public SDK is the ordinary evaluator-facing ingress for this experiment. Public access to SDK source does not grant StegVerse runtime, release, mutation, credential, custody or governance authority.

## Core-Lite

`Data-Continuation/core-lite` is currently public. No root `LICENSE` file was found during this packet-preparation pass. Therefore this packet MUST NOT infer or invent a software license for Core-Lite from repository visibility alone.

Before external distribution of any Core-Lite source beyond material already publicly accessible, the final packet must either:

1. identify the applicable license from the exact immutable release/tag; or
2. state that no independent redistribution license is asserted by this packet and provide only the public release coordinate and evidence necessary for reproduction.

## StegCore

`StegVerse-Labs/StegCore` is currently private. An external evaluator must not be promised private repository access by the SDK packet. The packet may provide the immutable release identity, runtime identity, externally verifiable evidence, public specifications where available, and any specifically authorized artifacts.

Private StegCore source must not be copied into the reviewer packet unless separately authorized under the applicable access/license terms. Lack of private source access must be stated explicitly if independent reproduction is limited to public interfaces plus retained evidence.

## Master Records orchestration

`master-records/orchestration` is currently private. The same access boundary applies: the reviewer packet may expose immutable release coordinates, custody/reconstruction evidence appropriate for independent verification, hashes, receipts and specifically authorized artifacts, but must not silently disclose private repository source.

Master Records custody evidence is required to prove the governed run; repository source access is a separate entitlement.

## Credential and execution access

```text
credential authority: TV/TVC ONLY
GitHub token runtime authority: NONE
non-TV/TVC secret/token substitution: prohibited
reviewer packet grants runtime authority: false
reviewer packet grants release authority: false
reviewer packet grants repository mutation authority: false
reviewer packet grants private repository access: false
reviewer packet grants custody authority: false
```

An evaluator may independently inspect public artifacts, validate hashes and schemas, install the released public SDK where permitted, run non-authorizing tests, and verify the returned evidence tuple. The actual governed proposition must still traverse the canonical StegVerse route and Master Records custody described by the experiment handoff.

## Finalization gate

Before the packet is marked complete, re-check the exact R3 tagged releases and record:

- exact license file or declared license for each distributable public component;
- whether each referenced artifact is public, packet-included under authorization, or available only through a controlled review path;
- any terms that limit copying, redistribution or private-source inspection;
- the fact that access/license limitations do not change the evaluator-boundary proposition or evidence-binding checks.

This document does not create new license rights or access authority.
