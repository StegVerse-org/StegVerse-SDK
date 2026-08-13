# Public Inspection Entry

The public SDK supports visible declarative inspection requests without creating a person-specific evaluator route.

## What a pull request means

A pull request can retain the request payload, revisions, discussion, and later receipt references. It does **not** itself mean a request was governed, executed, retained, released, or authorized.

Requests use `inspection/request.schema.json` and must remain declarative.

## Validate or prepare only

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

Preparation stops before governed execution and returns no `manifest_receipt_id`.

## Run the sovereign governed TEST

The canonical public-inspection runtime is sovereign/local and uses pinned canonical Core-Lite, StegCore/StegGate, and Master Records implementations.

```bash
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run inspection/examples/governed-test-request.json
```

The default local custody file is `./stegverse-master-records-validation.db`. A different file may be selected with `--custody-db`.

The test consequence is simulated and produces no external side effect. A successful run is returned only after the canonical route and exact-run evidence are recorded locally.

The sovereign path does not require a hosted evaluator and does not use a GitHub token as StegVerse runtime authority.

## Replay — option 1

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

Replay preserves the original exact run and does not invoke its original consequence. Replay itself is new operation history:

```text
REQUESTED -> SOURCE_RESOLVED -> EVALUATED -> RETURNED
```

The replay artifact is returned only after its operation history is recorded.

## Reconstruction — option 2

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

Reconstruction preserves the original exact run and does not re-execute its original consequence. Its operation history is:

```text
REQUESTED -> SOURCE_RESOLVED -> ARTIFACT_DERIVED -> RETURNED
```

## Frozen evaluator evidence

Canonical retained evidence:

```text
validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md
```

The retained T0/T1-A/T1-B run records exact-run custody, manifested-route custody, replay custody, and reconstruction custody as PASS. The three canonical `manifest_receipt_id` values are recorded there and in `SDK_MIRROR_HANDOFF.md`.

## Governing distinction

```text
public PR != runtime authority
manifest_receipt_id != authority
original run remains immutable
replay/reconstruction do not re-execute the original consequence
operation history is retained before return
GitHub != StegVerse runtime authority
```

## Validation

```bash
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_public_inspection_runtime
```

See also `README.md`, `docs/SDK_CONSOLE.md`, and `SDK_MIRROR_HANDOFF.md`.
