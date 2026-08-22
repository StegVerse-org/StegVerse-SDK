# ODA3 Evaluation-Boundary Test Plan

Status: **R3 FROZEN TEST INSTANCE — RELEASE + EXACT GOVERNED RUN PENDING**  
Repository: `StegVerse-org/StegVerse-SDK`  
Canonical SDK surface: generalized evaluator/testing manifest ingress  
Canonical handoff: `EVALUATOR_MANIFEST_NON_INTERFERENCE_MIRROR_HANDOFF.md`  
Release-set handoff: `PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md`  
Testing-contract version: `stegverse.sdk-testing-noninterference.v1`

## Architectural rule

ODA3 is one evaluator/test instance submitted through the generalized SDK testing surface. It does not own a dedicated SDK lane, evaluator-specific route, evaluator-specific StegGate semantics, or evaluator-specific release executor.

```text
external evaluator
-> generalized StegVerse SDK manifest surface
-> Core-Lite manifested route carrier
-> StegCore / canonical StegGate
-> Master Records custody
-> governed result returned through the manifested route
```

Evaluator-defined WHAT/HOW/WHY, identity, rationale, and expected observation are retained as experiment/evidence metadata. They do not become StegGate decision inputs. A capability not already published must be developed, versioned, and published generally before this or any other evaluator can request it.

## Research claim under test

For a fixed, versioned StegVerse implementation and governed state, evaluator-supplied experimental metadata may select and compose already-published capabilities, but it cannot add a capability, alter the canonical route or StegGate decision semantics, silently introduce an alternate execution path, or influence the governance result. The declared experiment, exact governance request, returned result, route/custody evidence, replay/reconstruction evidence, and independent verification must remain distinguishable and reconstructable as one bounded transaction.

## Active immutable release set — R3

The historical `1.0.13`-derived experiment coordinates are superseded and must not be published. The active frozen release set is:

```text
release_set_id: EVALUATION-BOUNDARY-2026-08-19-R3

StegVerse-org/StegVerse-SDK@v1.1.0
  -> 922d6c5235229e854c36e1a194dc99ed15a31b51
  validated tree: d9ddda3dbe942324c921051d89ec19eec3970b16

Data-Continuation/core-lite@v0.9.0
  -> 018e608018a793ee6dc62f4fdea59a3415e6e80e
  executable parent -> 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8

StegVerse-Labs/StegCore@v0.2.0
  -> 23b388ce23b08097593b5b5593eb4061e0ff5242
  executable parent -> 083557adec1bdbace09ebd10fb0765eb8e9a9d08

master-records/orchestration@v0.1.0
  -> 4826f753641cc82bbb885f919494a6c1318fbae4
  executable parent -> 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

SDK package-artifact validation run `32251339936` succeeded against PR head `2d70d6e2279aecc3195d52086e6b259a4629d620`, tree `d9ddda3dbe942324c921051d89ec19eec3970b16`. Frozen SDK candidate `922d6c5235229e854c36e1a194dc99ed15a31b51` has that exact tree. The validation covered wheel/sdist build, canonical metadata, setup.py metadata convergence, clean wheel install/import, installed version `1.1.0`, console smoke, and absence of release credentials. This is artifact/source evidence, not publication or runtime evidence.

Historical tag `v1.0.13` remains immutable at its historical source. `v1.0.13-evaluation-r2` and all earlier unpublished ODA3-derived coordinates are superseded and must not be published.

## Published evaluator capabilities

The generalized public-inspection/evaluator manifest may request only published capabilities, including:

```text
commit_time_admissibility
bounded_consequence
master_records_custody
replay
reconstruction
```

Representative evidence classes include:

```text
governance_decision
execution_observation
manifest_receipt
route_receipts
exact_run_custody
replay
reconstruction
```

Unknown or unsupported requested capabilities and evaluator attempts to alter production routing/semantic fields fail before execution.

## Manifest fields and decision influence

`evaluation_declaration` may retain:

- `what`
- `how`
- `why`
- `expected_observation`
- `requested_capabilities`
- `requested_evidence`

Evaluator identity (`requester_label`), rationale, and expected observation are evidence metadata. The governed request is derived from `input.steggate_request`; the evaluator declaration is not inserted into the canonical StegGate decision model.

## Canonicalization and independent binding

The sovereign runtime binds:

1. normalized submitted manifest -> `submitted_manifest_hash`;
2. exact normalized governance request -> `governance_request_hash`;
3. returned sovereign result -> `result_binding_hash`.

The independent verifier recomputes these bindings and reports `PASS`, `FAIL`, or `NOT_PROVIDED`. Verification grants no execution or governance authority.

Canonical profile remains `stegverse.sdk-canonical-json.v1`: SHA-256 over UTF-8 JSON with lexicographically sorted object keys, separators `,` and `:`, no insignificant whitespace, and `ensure_ascii=False`.

## Boundary-violation matrix

The first bounded test exercises the generalized contract through this R3 instance:

1. valid manifest using published capabilities -> accepted;
2. changed evaluator identity/rationale/expected observation -> submitted-manifest binding changes while an unchanged governance request remains unchanged;
3. unavailable/undeclared capability -> rejected before execution;
4. attempted canonical-route or StegGate-semantic override -> rejected;
5. attempted alternate evaluator execution path -> rejected/unavailable;
6. post-normalization manifest modification -> independent submitted-manifest binding FAIL;
7. post-execution governance-request or returned-result modification -> corresponding binding FAIL;
8. complete unmodified tuple -> independent verification PASS with no authority grant.

## TVC release gate

Active TVC task:

```text
StegVerse-Labs/TVC/tasks/TVC-EVALUATION-BOUNDARY-AGGREGATE-RELEASE-029.json
StegVerse-Labs/TVC#78
```

Active dispatcher sequence:

```text
tvc.release.aggregate.evaluation_boundary_r3.source_validate
tvc.release.aggregate.evaluation_boundary_r3.readiness
tvc.release.aggregate.evaluation_boundary_r3.execute
tvc.release.aggregate.evaluation_boundary_r3.verify
```

The TVC guard requires a retained exact R3 source-validation report bound to the active policy and exact current TVC source before readiness can become `READY` or release mutation can occur. Publication additionally requires the TVC-managed ephemeral publication capability. Heartbeat state and WorkerCoordinator assignment are not release prerequisites. GitHub Actions is not release/runtime authority. No generic GitHub credential or non-TV/TVC credential may substitute for TV/TVC publication authority.

Required release records:

```text
reports/aggregate_release/EVALUATION-BOUNDARY-2026-08-19-R3/source-validation.json
receipts/aggregate_release/EVALUATION-BOUNDARY-2026-08-19-R3.json
reports/aggregate_release/EVALUATION-BOUNDARY-2026-08-19-R3/latest.json
```

The aggregate receipt must prove all four immutable tag-to-commit bindings, declared source-parent lineages, release objects, accessible release notes, TV/TVC credential authority, and `non_tv_tvc_credential_used=false`.

## Exact governed execution

The experiment may start only after R3 verifies. Mandatory ingress:

```text
external evaluator
-> `stegverse governance --select 0B --manifest <manifest.json>`
-> generalized SDK validation/canonicalization/binding
-> canonical manifested route
-> StegGate evaluation
-> Master Records custody
-> SDK return
```

Direct evaluator injection/submission to Core-Lite, StegCore, or StegGate does not satisfy the proposition and is not an authorized alternate test route.

The exact run must retain:

- normalized submitted manifest;
- exact governance request;
- sovereign governed result;
- submitted-manifest, governance-request, and result binding hashes;
- manifest receipt identifier;
- route receipt chain;
- Master Records exact-run custody evidence;
- reconstruction output;
- replay output when requested;
- canonical StegGate runtime identity `stegverse:steggate:canonical:three-layer:v1`;
- independent unmodified verification PASS;
- modified-manifest binding FAIL;
- modified-governance-request binding FAIL;
- modified-returned-result binding FAIL;
- exact commands, versions, release identities, and exit status.

Source tests/examples must not be mislabeled as exact-run runtime receipts.

## External evidence packet / owner handoff

The owner-facing package is complete only when it contains:

```text
R3 exact release-set receipt
SDK 1.1.0 artifact/release identity
normalized experiment manifest
canonical governed result
route + manifest receipts
Master Records custody evidence
reconstruction/replay evidence
independent PASS verifier output
three deliberate tamper FAIL outputs
runtime identity confirmation
reproduction instructions
```

A favorable result, refusal, negative result, or inconclusive result is an admissible research record if it is preserved truthfully. The package must not imply that source validation, tag readiness, issue assignment, task assignment, or release readiness equals governed execution.

## Later authority-state experiment

Only after this evaluation-boundary exercise is supported by retained exact-run evidence should the research sequence advance to revocation, expiry, changed delegation, stale authorization, unavailable governing state, or another authority-state transition. The later experiment must separately identify the autonomous actor/model version, consequential action, governing inputs, exact StegVerse enforcement point, and consequence executor. The SDK must not be assumed to be that actor unless it genuinely proposes/executes the action.

## Current completion boundary

```text
generalized SDK testing surface: IMPLEMENTED / SOURCE-VALIDATED / MERGED
ODA3-specific SDK lane required: FALSE
active release set: R3 / SDK 1.1.0
SDK 1.1.0 artifact proof: PASS
R3 exact TVC source-validation receipt: PENDING
R3 immutable tag/release publication: PENDING
R3 aggregate receipt: PENDING
exact SDK-ingress governed run: PENDING
exact-run custody/reconstruction/replay evidence: PENDING
independent PASS + tamper FAIL evidence: PENDING
owner-facing evidence packet: PENDING
```

Do not archive or present this test as completed until the immutable R3 release set verifies and the exact governed run plus its retained evidence packet exist.
