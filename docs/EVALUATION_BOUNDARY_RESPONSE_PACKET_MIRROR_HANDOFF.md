# Evaluation-Boundary Response Packet Mirror Handoff

Updated: 2026-08-26
Repository: `StegVerse-org/StegVerse-SDK`
Branch: `main`
Goal ID: `SDK-EVALUATION-BOUNDARY-R3-RUN-002`

## Authority and scope

This is the active evaluator-neutral response-packet and exact-run coordination surface for the R3 evaluation-boundary experiment.

```text
credential authority: TV/TVC
GitHub runtime authority: NONE
evaluator-specific route: PROHIBITED
evaluator-specific StegGate semantics: PROHIBITED
moving-main substitution: PROHIBITED
source/release proof != governed runtime proof
```

Historical evaluator-specific filenames and packet artifacts may remain in repository history for reconstruction, but they are not active execution or coordination surfaces and must not be propagated into new artifacts.

## Active exact release coordinate

```text
release_set: EVALUATION-BOUNDARY-2026-08-19-R3
StegVerse SDK: v1.1.0 -> 922d6c5235229e854c36e1a194dc99ed15a31b51
Core-Lite: v0.9.0 -> 018e608018a793ee6dc62f4fdea59a3415e6e80e
StegCore: v0.2.0 -> 23b388ce23b08097593b5b5593eb4061e0ff5242
Master Records: v0.1.0 -> 4826f753641cc82bbb885f919494a6c1318fbae4
```

The active release gate remains owned by `StegVerse-Labs/TVC/docs/AGGREGATE_RELEASE_MIRROR_HANDOFF.md` and task `TVC-EVALUATION-BOUNDARY-AGGREGATE-RELEASE-029`.

## Manifest contract

The experiment input is the manifest supplied by the external evaluator for that run.

The SDK must:

1. receive the supplied manifest at SDK ingress;
2. validate/canonicalize it through the published manifest contract;
3. resolve the route declared by that manifest;
4. reject unsupported, unavailable, conflicting, or authority-violating route declarations;
5. bind current governing state to the resolved route;
6. execute only the resolved installed route;
7. retain the exact submitted/normalized manifest with the run evidence.

No evaluator identity is needed in repository filenames, task IDs, route IDs, test IDs, packet schemas, or runtime code. A repo-local frozen evaluator-specific manifest is not an architectural prerequisite. If a particular external submission must be preserved, its exact bytes belong in the run evidence/custody packet for that experiment.

## Neutral executable tooling

```text
scripts/run_evaluation_boundary_r3.py
scripts/build_evaluation_boundary_response_packet.py
scripts/build_evaluation_boundary_owner_packet.py
tests/test_evaluation_boundary_r3_run_harness.py
tests/test_evaluation_boundary_response_packet.py
docs/EVALUATION_BOUNDARY_PACKET_README_REPRODUCE.md
docs/EVALUATION_BOUNDARY_LICENSE_ACCESS_NOTES.md
tasks/SDK-EVALUATION-BOUNDARY-R3-RUN-002.json
```

The neutral harness adds no evaluator, route, governance engine, custody path, release authority, or credential authority. It requires the verified R3 aggregate receipt before runtime execution.

## Required exact run path

```text
external evaluator manifest
-> SDK ingress
-> manifest validation/canonicalization
-> declared-route resolution
-> governing-state binding
-> Core-Lite manifested carrier
-> StegCore / canonical StegGate
-> Master Records exact-run custody
-> governed return through SDK
```

Direct evaluator injection into Core-Lite, StegCore or StegGate does not satisfy the proposition.

## Required evidence

```text
verified R3 aggregate release receipt
exact submitted + normalized manifest
exact canonical governance request
governed result
submitted_manifest_hash
governance_request_hash
result_binding_hash
route receipts
manifest receipt
Master Records custody evidence
reconstruction
replay when requested
independent unmodified tuple PASS
manifest tamper FAIL
governance-request tamper FAIL
result tamper FAIL
packet file/hash manifest
runtime/source release identity evidence
```

## Current state

```text
neutral runner source: IMPLEMENTED ON ACTIVE CHANGE BRANCH
neutral packet builder source: IMPLEMENTED ON ACTIVE CHANGE BRANCH
neutral reproduction/access docs: IMPLEMENTED ON ACTIVE CHANGE BRANCH
neutral tests: IMPLEMENTED ON ACTIVE CHANGE BRANCH
R3 aggregate release: NOT RELEASED
required R3 tags observed in latest consolidation: 0/4
exact R3 source-validation report: NOT PRESENT
R3 aggregate receipt: NOT PRESENT
exact governed SDK-ingress run: NOT EXECUTED
runtime/custody/replay/reconstruction packet: NOT PRESENT
```

## Next executable boundary

1. validate and merge the neutral tooling change;
2. keep the run blocked until TVC R3 publication/verification produces the exact aggregate receipt;
3. receive the evaluator's manifest through ordinary SDK ingress;
4. execute the neutral R3 harness against that supplied manifest and verified receipt;
5. retain exact-run evidence and build the neutral response packet;
6. propagate release/evidence identities only after immutable evidence exists.

## Completion

This goal is complete only when the neutral tooling is merged and validated, the R3 release set is verified, the actual evaluator-supplied manifest has traversed the canonical declared route, exact custody/reconstruction evidence exists, independent verification/tamper results are retained, and the packet is reproducible without evaluator-specific repository augmentation.
