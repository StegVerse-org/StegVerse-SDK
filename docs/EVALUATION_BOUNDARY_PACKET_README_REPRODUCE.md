# Evaluation-Boundary Reproduction Procedure

This procedure is reviewer-facing and deliberately separates independently runnable verification from the StegVerse-controlled governed runtime.

## Preconditions

Do not begin governed-run verification until the R3 aggregate release receipt proves the complete immutable release set.

Expected release set:

```text
StegVerse-org/StegVerse-SDK@v1.1.0 -> 922d6c5235229e854c36e1a194dc99ed15a31b51
Data-Continuation/core-lite@v0.9.0 -> 018e608018a793ee6dc62f4fdea59a3415e6e80e
StegVerse-Labs/StegCore@v0.2.0 -> 23b388ce23b08097593b5b5593eb4061e0ff5242
master-records/orchestration@v0.1.0 -> 4826f753641cc82bbb885f919494a6c1318fbae4
```

## Independently runnable checks

An external evaluator may independently:

1. inspect the released SDK files and release coordinates;
2. verify artifact hashes against the retained file manifest;
3. install the published SDK artifact into a clean environment;
4. validate the manifest schema and complete representative manifest;
5. inspect the published capability registry;
6. run the non-authorizing evaluation-boundary test suite;
7. recompute submitted-manifest, exact-governance-request and returned-result bindings;
8. run the independent boundary verifier against the unmodified evidence tuple;
9. modify copies of the normalized manifest, exact governance request and returned result and confirm binding verification fails.

These steps grant no runtime, mutation, signing, release, custody or governance authority.

## Governed-run boundary

The actual proposition under test requires the exact request to enter through the ordinary evaluator-facing SDK manifest surface and then traverse the canonical manifested route:

```text
external evaluator
-> StegVerse SDK
-> Core-Lite
-> StegCore / canonical StegGate
-> Master Records
-> governed return through SDK route
```

Direct evaluator submission to Core-Lite, StegCore or StegGate is not an equivalent reproduction and does not satisfy the experiment.

## Evidence tuple to verify

The final packet must provide:

```text
normalized submitted manifest
exact governance request
exact governed result
submitted_manifest_hash
governance_request_hash
result_binding_hash
route receipts
manifest receipt
Master Records exact-run custody evidence
reconstruction evidence
replay evidence when requested
runtime/source release identity evidence
```

## Required expected outcomes

```text
valid published-capability manifest: canonical execution permitted subject to governance result
changed evaluator identity/rationale/expected observation: no decision-semantic influence
undeclared capability: rejected before execution
route/semantic override: rejected
alternate evaluator-accessible path: unavailable or rejected
unmodified evidence tuple: independent verification PASS
normalized-manifest tamper: submitted-manifest binding FAIL
exact governance-request tamper: governance-request binding FAIL
returned-result tamper: result binding FAIL
```

## Research record rule

ALLOW, DENY, REVIEW/defer, rejection, verification failure and inconclusive outcomes are all retained as research evidence. The packet must not suppress an unfavorable or inconclusive result.

## Current state

```text
source implementation: COMPLETE
source boundary tests: COMPLETE
independent verifier implementation: COMPLETE
immutable R3 aggregate release proof: PENDING
exact governed run: PENDING
complete reproduction packet: PENDING
```

Replace no pending state with a completion claim until the corresponding immutable release, runtime, custody or verification artifact actually exists.
