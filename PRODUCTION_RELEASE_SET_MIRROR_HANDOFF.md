# Production Release Set Mirror Handoff

Updated: 2026-08-22

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
credential_authority: TV/TVC
non-TV/TVC release credential permitted: false
current_public_package_candidate: 1.1.0
current_public_tag_candidate: v1.1.0
historical_v1.0.13_mutable: false
frozen_sdk_candidate: 922d6c5235229e854c36e1a194dc99ed15a31b51
frozen_sdk_tree: d9ddda3dbe942324c921051d89ec19eec3970b16
active_release_set_id: EVALUATION-BOUNDARY-2026-08-19-R3
active_tvc_task: TVC-EVALUATION-BOUNDARY-AGGREGATE-RELEASE-029
active_tvc_issue: StegVerse-Labs/TVC#78
```

## Governing rule

Every governed evaluator run must identify the exact immutable released component set that participated, retain that set with exact-run custody, and distinguish it from moving source branches and later releases used during replay/reconstruction.

The release-set mechanism is evaluator-neutral. ODA3 is one experiment instance using the generalized SDK testing surface. No evaluator-specific SDK route, StegGate semantic, custody route, or release executor is authorized.

## SDK package/version reconciliation

Historical `v1.0.13` resolves to historical April 2026 source and remains immutable. Modern source had continued to declare package `1.0.13` while legacy `setup.py` separately declared `2.1.0`. PR #50 repaired the split:

```text
PR #50 merge: 459e88f640c36805ae2e24484604f3976809b69f
canonical metadata source: pyproject.toml
canonical modern package version: 1.1.0
legacy setup.py: metadata-free compatibility shim
target public SDK tag: v1.1.0
```

Modern source must not be published as `1.0.13`. Superseded unpublished `v1.0.13-oda3-r1` and `v1.0.13-evaluation-r2` coordinates must not be published.

## Exact SDK 1.1.0 artifact proof

```text
validation workflow: SDK Package Artifact Validation (Non-Authorizing)
validation run: 32251339936
validated PR head: 2d70d6e2279aecc3195d52086e6b259a4629d620
validated tree: d9ddda3dbe942324c921051d89ec19eec3970b16
result: SUCCESS
frozen squash-merge candidate: 922d6c5235229e854c36e1a194dc99ed15a31b51
frozen candidate tree: d9ddda3dbe942324c921051d89ec19eec3970b16
target tag: v1.1.0
```

The proof covered wheel/sdist construction, canonical wheel metadata/dependencies/entry points, setup.py convergence, isolated wheel install/import, installed distribution version `1.1.0`, console smoke, and absence of release credentials. Artifact validation does not grant release/runtime authority.

## Active immutable release set — R3

```text
StegVerse-org/StegVerse-SDK@v1.1.0
  -> 922d6c5235229e854c36e1a194dc99ed15a31b51

Data-Continuation/core-lite@v0.9.0
  -> 018e608018a793ee6dc62f4fdea59a3415e6e80e
  executable parent -> 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8

StegVerse-Labs/StegCore@v0.2.0
  -> 23b388ce23b08097593b5b5593eb4061e0ff5242
  executable parent -> 083557adec1bdbace09ebd10fb0765eb8e9a9d08
  runtime identity -> stegverse:steggate:canonical:three-layer:v1

master-records/orchestration@v0.1.0
  -> 4826f753641cc82bbb885f919494a6c1318fbae4
  executable parent -> 6626c6a7f1df6bf531940c165b2f4db374e08b92
```

R2 is retained only for reconstruction and is `SUPERSEDED_DO_NOT_EXECUTE`. R3 is the sole active publication set for this evaluation-boundary experiment.

## TVC guarded publication path

Active TVC dispatcher sequence:

```text
tvc.release.aggregate.evaluation_boundary_r3.source_validate
tvc.release.aggregate.evaluation_boundary_r3.readiness
tvc.release.aggregate.evaluation_boundary_r3.execute
tvc.release.aggregate.evaluation_boundary_r3.verify
```

Generalized implementation:

```text
source-validation/publication guard: tasks/aggregate_release_guarded.py
publication executor: tasks/aggregate_release.py
R3 instance policy: config/evaluation_boundary_aggregate_release_r3.json
R3 instance catalog: config/task_catalog.d/evaluation_boundary_release_r3.json
```

The release may not mutate until the retained exact R3 source-validation report matches the active release-set ID, policy hash, non-authorizing credential boundary, and exact current TVC source commit. Publication additionally requires the TVC-managed ephemeral publication capability. Heartbeat advancement and WorkerCoordinator assignment are not release prerequisites.

On 2026-08-22 an immediate TV/TVC execution request was durably recorded in TVC task `TVC-EVALUATION-BOUNDARY-AGGREGATE-RELEASE-029` at TVC commit `cafb77cd902f4ebcc4045bbc4138c1c8da002276`. This request is not completion evidence.

## Required R3 release evidence

```text
reports/aggregate_release/EVALUATION-BOUNDARY-2026-08-19-R3/source-validation.json
receipts/aggregate_release/EVALUATION-BOUNDARY-2026-08-19-R3.json
reports/aggregate_release/EVALUATION-BOUNDARY-2026-08-19-R3/latest.json
four immutable tags
four GitHub release objects
four exact tag-to-commit bindings
all declared source-parent lineage checks
accessible release notes
SDK 1.1.0 distribution identity matching frozen candidate
credential authority = TV/TVC
non-TV/TVC credential used = false
```

## Release semantics

```text
moving branch != release identity
source validation != released
artifact validation != released
workflow pass != runtime
package build != publication
tag readiness != tag publication
release readiness != released
published package != runtime activation
commit pin != release tag
existing tag must never be retargeted
replay/reconstruction never rewrites original release-set evidence
```

Actual tag, GitHub Release, and package publication remains TV/TVC-governed release-authority work. GitHub Actions is validation/transport only and must not become release/runtime authority. No generic GitHub credential or non-TV/TVC credential may substitute for TV/TVC publication authority.

## Downstream exact-run gate

Only after the R3 aggregate receipt verifies may SDK issue #47 execute the exact evaluator-facing run:

```text
external evaluator
-> generalized SDK 0B manifested ingress
-> Core-Lite manifested route
-> StegCore / canonical StegGate
-> Master Records exact-run custody
-> SDK return
```

The exact-run packet must retain normalized manifest, exact governance request, sovereign result, three binding hashes, manifest/route receipts, Master Records custody, reconstruction/replay evidence, independent unmodified PASS, deliberate manifest/request/result tamper FAIL evidence, runtime identity confirmation, and reproduction instructions.

## Cross-repository coordination

```text
StegVerse-org/StegVerse-SDK#47
StegVerse-Labs/TVC#78
StegVerse-Labs/TVC/tasks/TVC-EVALUATION-BOUNDARY-AGGREGATE-RELEASE-029.json
StegVerse-Labs/TVC/docs/AGGREGATE_RELEASE_MIRROR_HANDOFF.md
Data-Continuation/core-lite/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
master-records/orchestration/PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md
```

## Current status

```text
SDK_GENERALIZED_TESTING_SURFACE: IMPLEMENTED_SOURCE_VALIDATED_MERGED
SDK_HISTORICAL_V1_0_13: IMMUTABLE_PRESERVED
SDK_METADATA_SPLIT: REPAIRED
SDK_CANONICAL_PACKAGE_VERSION: 1.1.0
SDK_1_1_0_ARTIFACT_VALIDATION: PASS
SDK_1_1_0_FROZEN_CANDIDATE: 922d6c5235229e854c36e1a194dc99ed15a31b51
R2: SUPERSEDED_DO_NOT_EXECUTE
R3: ACTIVE
R3_TVC_SOURCE_VALIDATION: PENDING
R3_TAG_PUBLICATION: NOT_RELEASED
R3_AGGREGATE_RECEIPT: NOT_PRESENT
EXACT_GOVERNED_RUN: PROHIBITED_UNTIL_R3_VERIFIED
OWNER_EVIDENCE_PACKET: PENDING_EXACT_RUN
ARCHIVE_ELIGIBILITY: FALSE
```
