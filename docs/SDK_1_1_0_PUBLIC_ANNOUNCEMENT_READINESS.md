# SDK 1.1.0 Public Announcement Readiness

Updated: 2026-08-22

## Purpose

This record distinguishes what may be truthfully announced about StegVerse SDK 1.1.0 from capabilities or release states that have not yet occurred. It is an observer-facing status record only. It grants no release, runtime, execution, credential, or custody authority.

## Current version state

```text
package: stegverse-sdk
version: 1.1.0
stage: RELEASE_CANDIDATE
frozen_candidate: 922d6c5235229e854c36e1a194dc99ed15a31b51
frozen_tree: d9ddda3dbe942324c921051d89ec19eec3970b16
artifact_validation: PASS
target_tag: v1.1.0
tag_publication: NOT_YET_AUTHORIZED
package_publication: NOT_YET_PUBLISHED
aggregate_release_set: EVALUATION-BOUNDARY-2026-08-19-R3
R3_TVC_source_validation: PENDING
R3_aggregate_receipt: NOT_PRESENT
exact_governed_R3_run: PROHIBITED_UNTIL_R3_VERIFIED
```

A public announcement made before the R3 TVC release sequence completes should describe 1.1.0 as a **publicly inspectable release candidate / evaluator preview**, not as an already published PyPI release or fully activated production release.

## What is already real and publicly inspectable

The frozen 1.1.0 source artifact has passed wheel/sdist construction, package metadata, dependency and entry-point checks, isolated wheel installation/import, installed version identity, console smoke testing, and credential-boundary validation.

The public SDK exposes generalized evaluator-facing governance navigation, including ordinary governed submission, raw-request manifesting, preformatted ingress-manifest validation/canonicalization, replay, reconstruction, evaluator contract inspection, focused subsystem experiments, and a local sovereign governed TEST route.

The published evaluator-facing capability identifiers currently include:

```text
commit_time_admissibility
bounded_consequence
master_records_custody
replay
reconstruction
```

Unsupported requested capabilities fail closed rather than being invented or dynamically installed.

## Limitations some users or observers may encounter

### 1. Registry installation is not yet the release path

`stegverse-sdk==1.1.0` is not yet published as the authorized package release. Until TV/TVC publication and verification completes, users should not be told that `pip install stegverse-sdk==1.1.0` is the canonical installation path.

The current public quick-start is repository/source based. The optional `governed-test` extra also references exact pinned Git repository commits, so installation of that full test stack requires Git plus network access to those public source repositories at installation time.

### 2. Python support is bounded

The package declares Python `>=3.9` and currently advertises Python 3.9, 3.10, 3.11, and 3.12 classifiers. Python versions outside the validated/advertised range should not be represented as release-proven.

### 3. The canonical governed TEST does not perform the proposed external consequence

The public sovereign/local governed TEST deliberately uses a simulated consequence executor:

```text
external_side_effect: false
third_party_host_required: false
```

Governance and custody transitions are real TEST evidence, but an observer will not see the test send money, change an external account, publish externally, or otherwise perform the proposed real-world consequence.

### 4. Release-candidate validation is not production activation

Artifact validation, source validation, package build, workflow success, commit pinning, and tag readiness do not establish release or runtime activation. The exact R3 governed evaluator run remains gated on the verified TVC aggregate release receipt.

### 5. Replay and reconstruction need retained prior evidence

Replay and reconstruction require a valid prior `manifest_receipt_id` and the corresponding retained custody evidence. They do not manufacture missing history and do not re-execute the original consequence.

A user with only the SDK source but without the referenced custody record cannot expect arbitrary historical receipt locators to reconstruct successfully.

### 6. Local custody is not automatically shared custody

The public inspection runtime defaults to a local custody database (`./stegverse-master-records-validation.db`). One user's local exact-run evidence is not automatically visible to another observer. Independent observation requires deliberate transfer/publication of the relevant evidence or a separately accessible canonical custody artifact.

### 7. Some ecosystem capabilities are intentionally separate components

The SDK does not duplicate every StegVerse subsystem. Local model discovery/launch/private inference is owned by `StegVerse-002/micro-node-runtime`; provider/runtime translation belongs to `StegVerse-org/LLM-adapter`; protected credential and route semantics remain TV/TVC responsibilities.

A user evaluating only the SDK repository should therefore not expect the repository by itself to provide every provider adapter, private model runtime, protected route, or production credential-bearing capability.

### 8. Unsupported evaluator requests fail closed

Evaluator configuration can select and configure already-published capabilities; it cannot hot-patch the governance engine, dynamically add a new route, or change StegGate semantics. Requests requiring an unpublished capability are rejected before execution.

### 9. A public pull request is not an execution request

The public inspection PR template is a collaboration and inspection-record surface. Opening or merging a PR does not itself execute governance, grant authority, establish custody, or publish a release.

### 10. MCP production-artifact proof still has a bounded pending gate

The MCP lane is source-complete and defect-corrected, and a credential-sanitized source-equivalent integration diagnostic traversed the executable logic successfully. The canonical exact sovereign artifact run is still pending; observers should distinguish that from a completed canonical production-artifact PASS.

### 11. Authority-boundary extension has a remaining exact sovereign execution requirement

The authority-boundary preservation extension has validated source and non-authorizing source validation, but its participant-neutral exact sovereign MR/MRR/MRO execution/custody remains a separate completion gate.

### 12. Historical usage totals are not automatically provenance-complete

SDK usage observation wiring is installed, but historical totals remain `OBSERVED_ONLY` unless deterministic provenance backfill exists. Observer dashboards or totals should not be represented as exhaustive historical execution counts without that provenance.

## Recommended announcement language boundary

Safe claims before publication include:

```text
StegVerse SDK 1.1.0 release candidate is public and inspectable.
The frozen package artifact has passed exact build/install/identity validation.
Evaluators can clone the repository and exercise the published generalized governance/testing surfaces locally.
The governed TEST path requires no third-party runtime host and performs no external consequence.
The immutable v1.1.0 tag/PyPI publication and the exact R3 release-set governed run remain pending TV/TVC release verification.
```

Avoid claims such as:

```text
v1.1.0 is already released on PyPI
v1.1.0 is fully production activated
all evaluator capabilities are dynamically available
public TEST runs perform external consequences
GitHub Actions/workflow success constitutes runtime or release proof
all historical SDK usage totals are provenance-complete
```

## Promotion condition

This document may be revised from release-candidate language to released language only after all of the following are evidenced:

```text
R3 TVC source validation: PASS
R3 publication/readiness: READY and executed under TV/TVC authority
v1.1.0 immutable Git tag resolves to frozen candidate
GitHub Release identity verified
stegverse-sdk 1.1.0 package publication verified
published package metadata/artifact identity matches frozen candidate
R3 aggregate release receipt present and independently verified
exact governed R3 evaluator run completed with required Master Records evidence
```

Canonical release-state sources remain `VERSION.json`, `PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md`, and `SDK_MIRROR_HANDOFF.md`.