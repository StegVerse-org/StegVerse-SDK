# ODA3 Response Packet Mirror Handoff

## Authority

This scoped handoff is subordinate to `SDK_MIRROR_HANDOFF.md`, `EVALUATOR_MANIFEST_NON_INTERFERENCE_MIRROR_HANDOFF.md`, `PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md`, and issue `#47`.

```text
goal_id: SDK-ODA3-RESPONSE-PACKET-001
repository: StegVerse-org/StegVerse-SDK
branch: main
credential_authority: TV/TVC
GitHub token runtime authority: NONE
canonical task: tasks/SDK-ODA3-RESPONSE-PACKET-001.json
```

## Goal

Produce the exact reviewer-facing packet required to answer the ODA3 evaluation-boundary request without substituting prose claims for executable or independently verifiable evidence.

## Packet rule

The packet MUST distinguish:

```text
source/artifact proof != release proof
release proof != governed runtime proof
governed runtime proof != independent verification
```

No packet may claim experiment completion until all required evidence below exists.

## Frozen active experiment coordinate

```text
release_set: EVALUATION-BOUNDARY-2026-08-19-R3
SDK package: stegverse-sdk 1.1.0
SDK commit: 922d6c5235229e854c36e1a194dc99ed15a31b51
SDK tree: d9ddda3dbe942324c921051d89ec19eec3970b16
SDK tag: v1.1.0
```

The experiment is one instance of the generalized evaluator surface. It receives no ODA3-specific route, evaluator, StegGate semantics, or release executor.

## Reviewer-request mapping

The final packet MUST include or point to the following exact materials:

1. exact tagged SDK release and commit;
2. corresponding Core-Lite, StegCore and Master Records immutable release coordinates;
3. manifest schema and complete representative normalized manifest;
4. published capability registry applicable to the frozen release set;
5. canonical route and StegGate semantic/runtime identity;
6. explicit field-influence map separating governance decision inputs from evidence-only evaluator metadata;
7. normalization and binding specification, canonicalization profile, algorithms, key ownership and verification procedure;
8. runnable commands/tests for normal and deliberate boundary-violation conditions;
9. representative route receipts, manifest receipt, Master Records custody, reconstruction material, replay material when requested, and negative-case outputs;
10. method proving tested runtime corresponds to identified source/release versions;
11. applicable licenses and access limitations;
12. exact file manifest, SHA-256 hashes and byte sizes for applicable source/evidence artifacts;
13. execution-arrangement statement identifying what ODA3 can run independently versus what must traverse the canonical StegVerse governed runtime;
14. independent unmodified verification PASS;
15. deliberate tamper FAIL for normalized manifest binding;
16. deliberate tamper FAIL for exact governance-request binding;
17. deliberate tamper FAIL for returned-result binding.

## Evaluation-boundary proposition

For the frozen versioned implementation and governed state, evaluator-supplied experimental metadata may select and compose published capabilities but MUST NOT:

```text
add a capability
alter canonical decision route
alter StegGate decision semantics
create an alternate evaluator-accessible execution path
influence governance disposition through evaluator identity, rationale, or expected observation
modify the normalized proposition after binding without detection
modify exact governance request or returned result after execution without detection
```

The declared experiment, exact governance request and returned result must remain independently verifiable as the same bounded proposition and transaction.

## Required test matrix

```text
T1 valid manifest using published capabilities -> execute through canonical route
T2 equivalent manifest with changed evaluator identity/rationale/expected observation -> governance semantics unchanged
T3 unavailable/undeclared capability -> reject before execution
T4 canonical route or decision-semantic override attempt -> reject
T5 alternate execution-path attempt -> unavailable/reject
T6 post-normalization manifest modification -> independent binding FAIL
T7 exact governance-request modification -> independent binding FAIL
T8 returned-result modification -> independent binding FAIL
T9 unmodified tuple -> independent verification PASS
```

Negative results are research results and MUST be retained rather than suppressed.

## Execution arrangement

Independent ODA3 activity MAY include:

```text
inspect released files
install released SDK
validate schemas/manifests
run source/non-authorizing boundary tests
recompute canonical hashes
run independent verifier
perform deliberate tamper tests against copied evidence
```

The actual governed-runtime proposition MUST traverse:

```text
external evaluator
-> ordinary StegVerse SDK manifest ingress
-> Core-Lite manifested carrier
-> canonical StegCore / StegGate
-> Master Records custody
-> governed return through manifested route
```

Direct evaluator submission to Core-Lite, StegCore, or StegGate does not satisfy this experiment and an evaluator-accessible bypass is itself a boundary violation.

## Fail-closed packet builder — installed 2026-08-22

The reviewer packet no longer requires a manual assembly step after runtime evidence arrives.

```text
builder: scripts/build_oda3_response_packet.py
regression suite: tests/test_oda3_response_packet.py
task: tasks/SDK-ODA3-RESPONSE-PACKET-001.json
builder install commit: 9ee63248049c9c7989979e51a0bae4bccd5cf51c
builder test install commit: b1f19975734bf6326977aae82c43767209360d62
```

The builder refuses to produce a complete packet unless it receives:

```text
verified stegverse.tvc.aggregate-release-receipt.v1
release_set_id == EVALUATION-BOUNDARY-2026-08-19-R3
exact four R3 repository/tag/commit bindings
credential_authority == TV/TVC
non_tv_tvc_credential_used == false
source_validation.verified == true
source_validation.tests_passed == true
source_validation.guard_tests_passed == true
real normalized-manifest.json
real governance-request.json
real governed-result.json
complete independent unmodified tuple verification PASS
```

It then deterministically creates copied tamper variants and requires all three expected failures before completion:

```text
normalized manifest mutation -> submitted_manifest_binding FAIL
governance request mutation -> governance_request_binding FAIL
governed result mutation -> result_binding FAIL
```

It also emits `FILE_MANIFEST.sha256.json` with path, SHA-256 and byte size for every retained packet file. It does not create or synthesize any governed-runtime evidence; missing runtime inputs fail closed.

Canonical invocation after real release/run evidence exists:

```text
python scripts/build_oda3_response_packet.py \
  --release-receipt <verified-r3-aggregate-receipt.json> \
  --run-dir <exact-sdk-ingress-run-evidence-dir> \
  --output-dir <oda3-evaluation-boundary-r3>
```

## Autonomous-actor second experiment gate

Do not infer an AI/autonomous actor from the governance SDK. A later authority-state-change experiment requires a separately identified:

```text
actor/system
exact actor version
proposed consequential action
pre-transition state
requested transition
exact StegVerse enforcement point capable of ALLOW / DENY / REVIEW-or-defer
resulting custody/evidence expectations
```

That second experiment begins only after the evaluation-boundary packet is complete enough for external review or independent reproduction.

## Current activation gate

The next required upstream result is the verified TV/TVC R3 aggregate-release continuation and receipt. The canonical continuation is owned by `StegVerse-Labs/TVC` task `TVC-EVALUATION-BOUNDARY-AGGREGATE-RELEASE-029` / issue `#78`.

Until that result exists:

```text
SDK v1.1.0 release proof: PENDING
aggregate immutable release proof: PENDING
exact governed SDK-ingress run: PROHIBITED
runtime evidence packet: PENDING
independent full-packet reproduction: PENDING
```

## Immediate continuation after aggregate receipt

Once the verified aggregate receipt exists, continue without a new planning phase:

```text
1 verify all four immutable tag -> commit bindings
2 verify published stegverse-sdk 1.1.0 artifact identity and clean install
3 freeze exact normalized boundary-test manifest
4 execute via ordinary SDK ingress only
5 retain exact submitted manifest + governance request + result
6 retain route/manifest/MR custody chain
7 retain reconstruction and requested replay
8 run scripts/build_oda3_response_packet.py against the real release/run evidence
9 builder independently verifies unmodified tuple -> PASS
10 builder generates three deliberate tamper copies -> expected FAIL x3
11 builder emits reviewer-facing file/hash manifest
12 finalize reproduction commands and access/license notes
13 update issue #47 and all governing handoffs with receipt IDs and packet location
14 propagate pertinent release/evaluation semantics to Site, Publisher, admissibility-wiki and stegguardian-wiki
```

## Completion condition

```text
source implementation complete: TRUE
boundary test implementation complete: TRUE
independent verifier implemented: TRUE
reviewer request mapped: TRUE
packet builder implemented: TRUE
packet completion task installed: TRUE
aggregate release proof complete: FALSE
exact governed runtime run complete: FALSE
complete evidence packet retained: FALSE
ODA3 independent reproduction complete: FALSE
goal state: ACTIVE
```

Durable assignment, readiness, workflow success, source completeness, and machine ownership do not satisfy this goal. Completion requires actual immutable release proof, canonical execution, custody evidence, independent PASS, deliberate tamper FAILs, and a reviewer-usable packet.
