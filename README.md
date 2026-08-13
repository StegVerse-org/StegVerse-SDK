# StegVerse SDK

The StegVerse SDK is the public developer interface for non-authorizing governance testing, governed submission, replay/reconstruction, receipt verification, bounded routing, and inspectable public requests.

A request, manifest, pull request, validation result, or receipt locator does not by itself grant execution, custody, release, standing, or other authority.

## Quick start

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse governance
```

Canonical governance navigation:

| Option | Meaning |
|---|---|
| `000` | Optional worked transparency/demo sequence |
| `00` | Optional return/explanation preferences |
| `0` | Ordinary governed submission |
| `1` | Replay by `manifest_receipt_id` |
| `2` | Reconstruction by `manifest_receipt_id` |

`000` and `00` are optional. A machine or LLM that already understands `stegverse.ingress-manifest.v1` can use ordinary governed ingress directly.

## Public inspection requests

A contributor can create a distinct, visible inspection request through an ordinary pull request using `.github/PULL_REQUEST_TEMPLATE/public-inspection-request.md` and `inspection/request.schema.json`.

The PR is a submission and discussion record only. It is not the evaluator implementation, execution authority, release authority, or Master Records custody.

### Validate or prepare only

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

Preparation maps the declarative request to ordinary SDK option `0A` and intentionally does not claim a runtime run.

### Run a governed TEST

The governed TEST path uses canonical StegCore and requires Master Records custody. A run is not reported as successfully completed until Master Records confirms `custody_status: RECORDED` for the complete exact-run evidence package.

Python 3.11+ is required because StegCore requires Python 3.11+.

Configure the admitted Master Records endpoint through your authorized environment or pass the equivalent command options:

```bash
export MASTER_RECORDS_URL="<admitted-master-records-base-url>"
export MASTER_RECORDS_AUTH_TOKEN="<authorized-token>"
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run \
  inspection/examples/governed-test-request.json
```

A successful run returns:

```text
governance_state
manifest_receipt_id
transaction_id
chain_verified
master_records_custody_status: RECORDED
master_records_custody_receipt
```

The executor used by this public governed TEST is deliberately simulated and cannot produce an external consequence. The governance transitions themselves are real StegCore TEST transitions and are retained in the exact-run Master Records evidence package before the run is reported successful.

```text
public PR or local request
  -> bounded declarative validation
  -> ordinary SDK option 0A semantics
  -> trusted canonical StegCore TEST governance
  -> complete exact-run evidence package
  -> Master Records custody: RECORDED
  -> governance result + manifest_receipt_id
```

Untrusted PR code is never used as the evaluator/runtime. Inspection requests must remain declarative and must not include secrets, credentials, executable instructions, workflow authority, or authority claims.

Detailed instructions: `docs/PUBLIC_INSPECTION_ENTRY.md`.

## Ordinary governed submission

Option `0` has two forms:

```text
0A — raw/user data; the SDK constructs the governance manifest
0B — preformatted machine manifest conforming to stegverse.ingress-manifest.v1
```

Public inspection requests bind to the ordinary governed semantics; they do not create a separate evaluator implementation.

Caller-facing controls remain separate from custody:

- `return_projection` controls which user-disclosable transition receipts are returned.
- `manifest_labels` controls explanatory labels on the returned package.
- Neither grants governance authority or changes the identity or custody of an exact run.

## Replay and reconstruction are operational

`manifest_receipt_id` is the canonical locator for an exact Master Records-retained run; it is not authority.

Replay does not invoke the original consequence executor and does not mutate the historical exact-run record. The replay operation itself does traverse new ecosystem states. Those state transitions are recorded in Master Records before the replay artifact is returned:

```text
REPLAY_REQUESTED
  -> SOURCE_RESOLVED
  -> EVALUATED
  -> RETURNED
```

```bash
python -m stegverse.public_inspection_runtime replay \
  MR-<SHA256>
```

The replay artifact reports the original and replay dispositions, candidate identity comparison, deterministic disposition comparison, `consequence_reexecuted: false`, `original_record_mutated: false`, an `operation_id`, and the Master Records operation-event receipts proving the replay-return path was recorded.

Reconstruction likewise does not re-execute the original consequence or rewrite the original record. Its own request/derivation/return transitions are new ecosystem states and are recorded:

```text
RECONSTRUCT_REQUESTED
  -> SOURCE_RESOLVED
  -> ARTIFACT_DERIVED
  -> RETURNED
```

```bash
python -m stegverse.public_inspection_runtime reconstruct \
  MR-<SHA256>
```

Reconstruction preserves persisted historical evidence separately from reconstructed material, reports `consequence_reexecuted: false`, and returns its operation-transition custody receipts.

The important distinction is:

```text
original exact run remains immutable
replay/reconstruction do not re-execute original consequence
replay/reconstruction operation state transitions are still recorded in Master Records
```

## Core invariants

```text
submission != execution
manifest validity != ALLOW
public PR != runtime authority
governed run success requires Master Records custody
manifest_receipt_id != authority
return_projection != custody
manifest_labels != authority
replay != historical rewrite
replay != consequence execution
replay state transitions -> Master Records
reconstruction != original consequence re-execution
reconstruction state transitions -> Master Records
```

## Other SDK surfaces

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

Focused surfaces remain available for AdmittedCode receipt verification, admissibility evaluation, LLM-output admissibility, math/formalism posture, universal entry routing, bridge discovery, and entry-point discovery. They are not replacements for the canonical `000/00/0/1/2` navigation.

Console documentation: `docs/SDK_CONSOLE.md`.

## LLM / agent boundary

An LLM may help construct or explain a request. It does not receive special authority by doing so. Provider/runtime translation belongs to `StegVerse-org/LLM-adapter`; protected runtime authority remains outside the public request surface.

## Validate the checkout

```bash
pytest tests/ -v
python scripts/verify_github_fallback_boundary.py
python -m unittest tests.test_github_fallback_boundary
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_public_inspection_runtime
```

Preparation only:

```bash
python -m stegverse.public_inspection inspection/examples/example-request.json
```

Governed run, replay, reconstruction:

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run inspection/examples/governed-test-request.json
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

## Repository control files

Files matching `*_MIRROR_HANDOFF.md` preserve implementation continuity, validation state, and task ownership. They are project-control records, not evaluator commands. The public SDK should remain understandable from this README, installed help, and public documentation without a private instruction channel.
